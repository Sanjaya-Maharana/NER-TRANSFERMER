import math
import json
import spacy
import uvicorn
from fastapi.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import openai

openai.api_type = "azure"
openai.api_base = "https://extractinfo.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "30363b3002684528a6af160e7cb7ae31"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)



@app.post("/translate")
async def translate_html(request: Request):
    data = await request.json()
    return await detect_and_translate_html(data)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop", http="httptools", workers=4)
