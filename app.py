import uvicorn
import json
import spacy
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from datetime import datetime, timedelta
import asyncio
import subprocess
import platform

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)


def check_and_install_java():
    try:
        java_version = subprocess.run(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if java_version.returncode == 0:
            version_info = java_version.stderr.decode().split('\n')[0]
            return {"message": "Java is already installed", "java_version": version_info}

    except FileNotFoundError:
        try:
            distro = platform.linux_distribution()[0].lower()

            if 'ubuntu' in distro or 'debian' in distro:
                print("Installing Java on Ubuntu/Debian...")
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'default-jre'], check=True)

            elif 'centos' in distro or 'fedora' in distro or 'rhel' in distro:
                print("Installing Java on CentOS/Fedora/RHEL...")
                subprocess.run(['sudo', 'yum', 'install', '-y', 'java-11-openjdk'], check=True)

            else:
                return {"message": "Unsupported Linux distribution. Please install Java manually."}

            java_version = subprocess.run(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if java_version.returncode == 0:
                version_info = java_version.stderr.decode().split('\n')[0]
                return {"message": "Java installed successfully", "java_version": version_info}

        except subprocess.CalledProcessError as e:
            return {"error": f"An error occurred during installation: {e}"}

    except Exception as ex:
        return {"error": f"Unexpected error: {ex}"}

@app.get("/install_java")
def install_java():
    return check_and_install_java()


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


@app.post("/check_text")
async def check_text(request: Request):
    import language_tool_python
    tool = language_tool_python.LanguageTool('en-US')
    data = await request.json()
    text = data.get('text', '')
    matches = tool.check(text)
    incorrect_words = []
    corrected_words = []
    corrected_sentence = list(text)

    try:
        offset_correction = 0
        for match in matches:
            incorrect_word = text[match.offset:match.offset + match.errorLength]
            suggestion = match.replacements[0] if match.replacements else incorrect_word

            incorrect_words.append(incorrect_word)
            corrected_words.append(suggestion)

            corrected_sentence[
            match.offset + offset_correction:match.offset + match.errorLength + offset_correction] = suggestion

            offset_correction += len(suggestion) - len(incorrect_word)

        corrected_sentence = ''.join(corrected_sentence)

        return {
            'incorrect_words': incorrect_words,
            'corrected_words': corrected_words,
            'corrected_sentence': corrected_sentence
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'incorrect_words': incorrect_words,
            'corrected_words': corrected_words,
            'corrected_sentence': ''.join(corrected_sentence),
            'error': str(e)
        }


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop", http="httptools", workers=4)
