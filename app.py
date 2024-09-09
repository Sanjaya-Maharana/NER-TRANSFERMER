import json
import spacy
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta
import asyncio

# Initialize FastAPI app
app = FastAPI()

# Add GZip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Function to get the current time in IST format
def get_ist_time():
    utc_time = datetime.utcnow()
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# JSON file to store API statistics
stats_file_path = Path('api_status.json')

# Initialize JSON stats file if it doesn't exist
if not stats_file_path.exists():
    initial_data = {
        'timestamp': {'timestamp': get_ist_time()},
        'tonnage': {'count': 0, 'last_called': None},
        'cargo': {'count': 0, 'last_called': None}
    }
    with open(stats_file_path, 'w') as f:
        json.dump(initial_data, f, indent=4)

# Function to update API stats for each API call
def update_api_stats(api_name):
    with open(stats_file_path, 'r+') as f:
        data = json.load(f)
        data[api_name]['count'] += 1
        data[api_name]['last_called'] = get_ist_time()
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

# Load NLP models for vessel_info, tonnage_info, and cargo
vessel_nlp = spacy.load(Path(f"models/vessel_info/model-best"))
tonnage_nlp = spacy.load(Path(f"models/tonnage_info/model-best"))
cargo_nlp = spacy.load(Path(f"models/cargo/model-best"))

# Home route to display the API statistics
@app.get("/")
async def home():
    with open(stats_file_path, 'r') as f:
        data = json.load(f)
    return JSONResponse(content=data)

# POST endpoint for vessel_info and tonnage_info predictions
@app.post("/predict/tonnage")
async def predict_vessel_and_tonnage(request: Request):
    update_api_stats('tonnage')
    data = await request.json()
    return await predict_combined([vessel_nlp, tonnage_nlp], data)

# POST endpoint for cargo predictions
@app.post("/predict/cargo")
async def predict_cargo(request: Request):
    update_api_stats('cargo')
    data = await request.json()
    return await predict_combined([cargo_nlp], data)

# Function to combine predictions from multiple models
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

    return JSONResponse(content={"entities": combined_result})

# Entry point for running the app with Uvicorn
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, workers=4)
