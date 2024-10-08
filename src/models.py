import spacy
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException



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