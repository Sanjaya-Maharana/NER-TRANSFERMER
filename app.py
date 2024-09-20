import uvicorn
import json
import spacy
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)


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

def update_api_stats(api_name):
    with open(stats_file_path, 'r+') as f:
        data = json.load(f)
        data[api_name]['count'] += 1
        data[api_name]['last_called'] = get_ist_time()
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

vessel_nlp = spacy.load(Path(f"models/vessel_info/model-best"))
tonnage_nlp = spacy.load(Path(f"models/tonnage_info/model-best"))
cargo_nlp = spacy.load(Path(f"models/cargo/model-best"))

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


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=6000, loop="uvloop", http="httptools", workers=4)
