import math
import json
import spacy
import uvicorn
import traceback
import numpy as np
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from sklearn.linear_model import LinearRegression
from fastapi.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime
from googletrans import Translator
import openai

openai.api_type = "azure"
openai.api_base = "https://extractinfo.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "30363b3002684528a6af160e7cb7ae31"

JWT_USER_SECRET_KEY = "asdgcvsdcv@@@#$@%@!~!~!!)(U*@*fdbvjblejhfvhgvsjfgv$@%&*(W&!)W(!SDHQWFUWKDDOY@TEF@&ETO!*E@(T@(ET!QDXWFBCWJWFGEKUFEUE"
ADMIN_SECRET_JWT_TOKEN = "rtawdchvscfbdhfvbjkdfnvhdgfjhhHHHHH@@!$@#(%*#$@(*)#!()@*$73y8277"
JWT_ENCODE_ALGO = "HS256"

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_body_size=10 * 1024 * 1024  # 10 MB
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

translator = Translator()

def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, ADMIN_SECRET_JWT_TOKEN, algorithms=[JWT_ENCODE_ALGO])
        return decoded_token
    except ExpiredSignatureError:
        return {"error": "Token has expired"}
    except InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception:
        try:
            decoded_token = jwt.decode(token, JWT_USER_SECRET_KEY, algorithms=[JWT_ENCODE_ALGO])
            return decoded_token
        except ExpiredSignatureError:
            return {"error": "Token has expired"}
        except InvalidTokenError:
            return {"error": "Invalid token"}
        except Exception as e:
            return {"error": str(e)}

def get_ist_time():
    utc_time = datetime.utcnow()
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')


stats_file_path = Path('api_status.json')

if not stats_file_path.exists():
    initial_data = {
        'timestamp': {'timestamp': get_ist_time()},
        'tonnage': {'count': 0, 'last_called': None},
        'cargo': {'count': 0, 'last_called': None}
    }
    with open(stats_file_path, 'w') as f:
        json.dump(initial_data, f, indent=4)


# Function to update API stats
def update_api_stats(api_name):
    with open(stats_file_path, 'r+') as f:
        data = json.load(f)
        if api_name not in data:
            data[api_name] = {'count': 0, 'last_called': None}
        data[api_name]['count'] += 1
        data[api_name]['last_called'] = get_ist_time()
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

vessel_nlp = spacy.load(Path(f"models/vessel_info/model-best"))
tonnage_nlp = spacy.load(Path(f"models/tonnage_info/model-best"))
cargo_nlp = spacy.load(Path(f"models/cargo/model-best"))


# MongoDB client initialization
client = AsyncIOMotorClient('mongodb+srv://theoceann:UPYLXvOujwCeARDO@oceannmail-staging.tamt4.mongodb.net/')

# Pydantic model for request data validation
class PlotDataRequest(BaseModel):
    type: str
    client: str = None
    vessel_name: str = None
    vessel_type: str = None
    sub_vessel_type: str = None
    new_open_port: str = None
    new_open_date: str = None
    cargo_name: str = None
    cargo_type: str = None
    load_port: str = None
    laycan: str = None
    token: str = None

# Helper function to create bins for DWT or Cargo Size
def create_bins_and_labels(min_value, max_value, step=500001):
    min_value = 0
    max_value = math.ceil(max_value / step) * step
    bins = list(range(min_value, max_value + step, step))
    labels = [f'{bins[i]}-{bins[i + 1] - 1} MT' for i in range(len(bins) - 1)]
    return bins, labels

# Helper function for predicting future weeks using linear regression
def predict_next_weeks(df, target_column='dwt', num_weeks=3):
    df['Date_ordinal'] = pd.to_datetime(df['Date']).apply(lambda x: x.toordinal())
    X = df['Date_ordinal'].values.reshape(-1, 1)
    y = df[target_column].values
    model = LinearRegression()
    model.fit(X, y)
    last_date = df['Date'].max()
    future_dates = [(last_date + timedelta(weeks=i)).toordinal() for i in range(1, num_weeks + 1)]
    future_dates = np.array(future_dates).reshape(-1, 1)
    predictions = model.predict(future_dates)
    rounded_predictions = np.round(predictions).astype(int)

    future_predictions = {
        str(last_date + timedelta(weeks=i)): prediction
        for i, prediction in enumerate(rounded_predictions, 1)
    }

    return future_predictions

# Helper function to convert numpy data types to standard Python types
def convert_numpy_to_python(data):
    """
    Recursively converts numpy data types to Python types to ensure JSON serialization.
    """
    if isinstance(data, dict):
        return {key: convert_numpy_to_python(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_python(item) for item in data]
    elif isinstance(data, np.generic):
        return data.item()
    else:
        return data

@app.get("/")
async def home():
    return {"message": "Hello World"}

@app.get("/data")
async def data():
    with open(stats_file_path, 'r') as f:
        data = json.load(f)
    return {'data': data}

@app.post("/predict/tonnage")
async def predict_vessel_and_tonnage(request: Request):
    update_api_stats('tonnage')
    data = await request.json()
    return await predict_combined([vessel_nlp, tonnage_nlp], data)

@app.post("/predict/cargo")
async def predict_cargo(request: Request):
    update_api_stats('cargo')
    data = await request.json()
    return await predict_combined([cargo_nlp], data)

async def detect_and_translate_html(data):
    text = data['text']
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text provided")
    try:
        response = await openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that detects and translates the text to English while preserving the HTML structure. "
                        "Translate any non-English text within the HTML content but ensure the HTML tags remain unchanged."
                        "Response must have only html no other text"
                    )
                },
                {
                    "role": "user",
                    "content": f"Here is the HTML content to translate:\n\n{text}"
                }
            ],
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        if response and "choices" in response and response["choices"]:
            translated_content = response["choices"][0]["message"]["content"]
            return {"translated_text": translated_content}
        else:
            return {"translated_text": text}
    except Exception as e:
        return {"translated_text": text}

async def predict_combined(models, request_data):
    if 'text' not in request_data:
        raise HTTPException(status_code=400, detail="No text provided")

    text = request_data['text']
    combined_result = []

    for model in models:
        doc = model(text)
        for ent in doc.ents:
            combined_result.append({
                "text": ent.text,
                "label": ent.label_
            })

    return {"entities": combined_result}


@app.post("/plot_data/")
async def plot_data(request_data: PlotDataRequest):
    try:
        if request_data.token:
            decoded_token = decode_jwt_token(request_data.token)
            company = decoded_token.get("company_name", None)
            if company:
                db_name = company.lower()
            else:
                db_name = 'theoceann'
        else:
            db_name = request_data.client if request_data.client else 'theoceann'
        update_api_stats(db_name)
        database = client[db_name]

        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=6)
        from_unix = int(start_date.timestamp())
        to_unix = int(end_date.timestamp())

        # Date filter for MongoDB
        date_filter = {
            'Formatted_Date': {
                '$gte': from_unix,
                '$lte': to_unix
            }
        }

        if request_data.type == 'tonnage':
            collection = database['tonnage']
            if request_data.vessel_name:
                date_filter['vessel_name'] = request_data.vessel_name.lower()
            if request_data.vessel_type:
                date_filter['vessel_type'] = request_data.vessel_type
            if request_data.sub_vessel_type:
                date_filter['sub_vessel_type'] = request_data.sub_vessel_type
            if request_data.new_open_port:
                date_filter['new_open_port'] = request_data.new_open_port
            if request_data.new_open_date:
                from_date, to_date = request_data.new_open_date.split('/')
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                date_filter['new_open_date'] = {
                    '$gte': int(from_dt.timestamp()),
                    '$lte': int(to_dt.timestamp())
                }

            date_filter['dwt'] = {"$lt": 10000000}

            tonnage_data = await collection.find(
                date_filter,
                {'_id': 0, 'vessel_name': 1, 'vessel_type': 1, 'Formatted_Date': 1, 'dwt': 1, 'new_open_port': 1}
            ).limit(50000).to_list()

            if not tonnage_data:
                return JSONResponse(status_code=200, content={"data": {}, "status": False, "message": "No data found"})

            df = pd.DataFrame(tonnage_data)

            if 'Formatted_Date' in df.columns:
                df['Formatted_Date'] = pd.to_datetime(df['Formatted_Date'], unit='s', errors='coerce').fillna(pd.NaT)
            else:
                return JSONResponse(status_code=200, content={"data": {}, "status": True, "message": "Data not found"})

            df['dwt'] = pd.to_numeric(df['dwt'], errors='coerce').fillna(0)
            df['Date'] = df['Formatted_Date'].dt.date
            df['Week'] = pd.to_datetime(df['Formatted_Date']).dt.to_period('W').apply(lambda r: r.start_time)

            min_dwt = df['dwt'].min()
            max_dwt = df['dwt'].max()
            bins, labels = create_bins_and_labels(min_dwt, max_dwt, step=2000001)

            df['dwt_bins'] = pd.cut(df['dwt'], bins=bins, labels=labels)
            grouped_data = {}
            for week, group in df.groupby('Week'):
                week_group = {}
                for label in labels:
                    vessels_in_bin = group[group['dwt_bins'] == label].to_dict(orient='records')
                    week_group[label] = vessels_in_bin
                grouped_data[str(week.date())] = week_group

            predictions = predict_next_weeks(df, target_column='dwt')

            # Convert any numpy data types to Python types
            grouped_data = convert_numpy_to_python(grouped_data)
            predictions = convert_numpy_to_python(predictions)

            return {"data": grouped_data, "predictions": predictions, "status": True, "type": "tonnage"}

        elif request_data.type == 'cargo':
            collection = database['cargo']
            if request_data.cargo_name:
                date_filter['cargo'] = request_data.cargo_name
            if request_data.cargo_type:
                date_filter['cargo_type'] = request_data.cargo_type
            if request_data.load_port:
                date_filter['load_port.port'] = request_data.load_port

            date_filter['cargo_size'] = {"$lt": 10000000}

            cargo_data = await collection.find(date_filter, {
                '_id': 0, 'cargo': 1, 'cargo_type': 1, 'Formatted_Date': 1, 'cargo_size': 1, 'load_port': 1
            }).limit(50000).to_list()

            if not cargo_data:
                return JSONResponse(status_code=200, content={"data": {}, "status": False, "message": "No data found"})

            df = pd.DataFrame(cargo_data)

            if 'Formatted_Date' in df.columns:
                df['Formatted_Date'] = pd.to_datetime(df['Formatted_Date'], unit='s', errors='coerce').fillna(pd.NaT)
            else:
                return JSONResponse(status_code=200, content={"data": {}, "status": True, "message": "Data not found"})
            df['cargo_size'] = pd.to_numeric(df['cargo_size'], errors='coerce').fillna(0)
            df['Date'] = df['Formatted_Date'].dt.date
            df['Week'] = pd.to_datetime(df['Formatted_Date']).dt.to_period('W').apply(lambda r: r.start_time)

            min_cargo_size = df['cargo_size'].min()
            max_cargo_size = df['cargo_size'].max()
            bins, labels = create_bins_and_labels(min_cargo_size, max_cargo_size, step=2000001)
            df['cargo_bins'] = pd.cut(df['cargo_size'], bins=bins, labels=labels)
            grouped_data = {}
            for week, group in df.groupby('Week'):
                week_group = {}
                for label in labels:
                    cargos_in_bin = group[group['cargo_bins'] == label].to_dict(orient='records')
                    week_group[label] = cargos_in_bin
                grouped_data[str(week.date())] = week_group
            predictions = predict_next_weeks(df, target_column='cargo_size')
            grouped_data = convert_numpy_to_python(grouped_data)
            predictions = convert_numpy_to_python(predictions)

            return {"data": grouped_data, "predictions": predictions, "status": True, "type": "cargo"}

        else:
            raise HTTPException(status_code=400, detail="Invalid request type")

    except Exception as e:
        print(traceback.print_exc())
        return {"error": str(e), "status": False}


@app.post("/translate")
async def translate_html(request: Request):
    update_api_stats('translate')
    data = await request.json()
    return await detect_and_translate_html(data)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop", http="httptools", workers=4, timeout_keep_alive=300)
