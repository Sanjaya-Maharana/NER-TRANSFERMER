import json
import spacy
import uvicorn
import traceback
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.analytics import plot_data_fun
from src.models import predict_combined
from src.status import update_api_stats


JWT_USER_SECRET_KEY = "asdgcvsdcv@@@#$@%@!~!~!!)(U*@*fdbvjblejhfvhgvsjfgv$@%&*(W&!)W(!SDHQWFUWKDDOY@TEF@&ETO!*E@(T@(ET!QDXWFBCWJWFGEKUFEUE"
ADMIN_SECRET_JWT_TOKEN = "rtawdchvscfbdhfvbjkdfnvhdgfjhhHHHHH@@!$@#(%*#$@(*)#!()@*$73y8277"
JWT_ENCODE_ALGO = "HS256"

stats_file_path = Path('api_status.json')

vessel_nlp = spacy.load(Path(f"models/vessel_info/model-best"))
tonnage_nlp = spacy.load(Path(f"models/tonnage_info/model-best"))
cargo_nlp = spacy.load(Path(f"models/cargo/model-best"))
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

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

@app.post("/plot_data/")
async def plot_data(request_data: PlotDataRequest):
    return await plot_data_fun(request_data)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4, timeout_keep_alive=600)
