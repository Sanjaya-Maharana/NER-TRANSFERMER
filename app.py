import json
import threading

import spacy
import uvicorn
import traceback
from typing import Optional
from pathlib import Path
from django.templatetags.i18n import language
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.analytics import plot_data_fun, handle_data
from src.fbx import fetch_fbx_data, fetch_all_fbx_filters
from src.models import predict_combined
from src.status import update_api_stats

from src.translate import translate_html_content
import warnings

from src.website_chat import get_chatbot_response

warnings.filterwarnings("ignore", category=FutureWarning)

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

class FBXRequest(BaseModel):
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    key: Optional[str] = "all"
    index: Optional[str] = None

class UserInput(BaseModel):
    message: str
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

@app.post("/plot_data")
async def plot_data(request_data: PlotDataRequest):
    return await plot_data_fun(request_data)

@app.post("/plot_data_filter")
async def plot_data_filter(request_data: PlotDataRequest):
    return handle_data(request_data)


@app.post("/translate")
async def translate_html(request: Request):
    data = await request.json()
    body = data.get('text', None)
    if not body:
        raise HTTPException(status_code=400, detail="No body provided")
    language = data.get('language', 'english')
    return await translate_html_content(body, language)

@app.post("/fetch_fbx_data")
def fetch_fbx(request: FBXRequest):
    from_date = request.from_date
    to_date = request.to_date
    key = request.key
    index = request.index
    return fetch_fbx_data(from_date, to_date, key, index)


@app.get("/fetch_fbx_filter")
def fetch_fbx_filter():
    return fetch_all_fbx_filters()


@app.post("/chat")
async def chat(user_input: UserInput):
    if not user_input.message:
        raise HTTPException(status_code=400, detail="No input provided")

    response = get_chatbot_response(user_input.message)
    return {"query": user_input.message,"response": response}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4, timeout_keep_alive=600)
