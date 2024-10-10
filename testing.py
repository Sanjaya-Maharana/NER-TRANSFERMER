
import requests
import json
from bs4 import BeautifulSoup

# Azure Translator API credentials and endpoints
subscription_key = "4073d25f84ee4db18f700ec8aa6b73c8"  # Key 1
endpoint = "https://api.cognitive.microsofttranslator.com/"  # Text Translation endpoint
location = "global"  # Region provided

# Function to translate text using Azure Translator API
def translate_text(text, target_language="en"):
    path = '/translate?api-version=3.0'
    params = f'&to={target_language}'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    response = requests.post(constructed_url, headers=headers, json=body)
    response_json = response.json()
    return response_json[0]['translations'][0]['text']

# Load and parse the HTML file
with open(r"/test/test.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Translate all text content inside the HTML
for tag in soup.find_all(text=True):
    original_text = tag.string
    if original_text and original_text.strip():  # Skip empty or whitespace text
        translated_text = translate_text(original_text, target_language="en")
        tag.string.replace_with(translated_text)

# Save the translated HTML content to a new file
with open("translated_file.html", "w", encoding="utf-8") as file:
    file.write(str(soup))

print("Translation complete. Translated HTML saved to 'translated_file.html'.")
