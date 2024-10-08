import json
import requests
from bs4 import BeautifulSoup
from fastapi.responses import HTMLResponse


subscription_key = "4073d25f84ee4db18f700ec8aa6b73c8"
endpoint = "https://api.cognitive.microsofttranslator.com/"
location = "global"


def translate_text(text, target_language="en"):
    path = '/translate?api-version=3.0'
    params = f'&to={target_language}'
    constructed_url = endpoint + path + params
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(constructed_url, headers=headers, json=body)
    response_json = response.json()
    return response_json[0]['translations'][0]['text']


async def translate_html_content(body):
    try:
        target_language = "en"
        soup = BeautifulSoup(body, "html.parser")
        for tag in soup.find_all(text=True):
            original_text = tag.string
            if original_text and original_text.strip():
                translated_text = translate_text(original_text, target_language)
                tag.string.replace_with(translated_text)

        return {"status": True, "text": str(soup)}
    except Exception as e:
        return {"status": False, "text": str(e)}
