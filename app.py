import sys
import json
import spacy
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

stats_file_path = Path('api_stats.json')

if not stats_file_path.exists():
    initial_data = {
        'timestamp': {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        'tonnage': {'count': 0, 'last_called': None},
        'cargo': {'count': 0, 'last_called': None}
    }
    with open(stats_file_path, 'w') as f:
        json.dump(initial_data, f, indent=4)

def update_api_stats(api_name):
    with open(stats_file_path, 'r+') as f:
        data = json.load(f)
        data[api_name]['count'] += 1
        data[api_name]['last_called'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

@app.route('/')
def home():
    with open(stats_file_path, 'r') as f:
        data = json.load(f)
    return render_template('index.html', stats=data)

@app.route('/predict/tonnage', methods=['POST'])
def predict_vessel_and_tonnage():
    update_api_stats('tonnage')
    return predict_combined(['vessel_info', 'tonnage_info'])

@app.route('/predict/cargo', methods=['POST'])
def predict_cargo():
    update_api_stats('cargo')
    return predict_combined(['cargo'])

def predict_combined(models):
    if 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400

    text = request.json['text']
    combined_result = []

    for model in models:
        try:
            nlp = spacy.load(Path(f"models/{model}/model-best"))
        except Exception as e:
            return jsonify({'error': f'Failed to load model {model}: {str(e)}'}), 500

        doc = nlp(text)
        for ent in doc.ents:
            combined_result.append({
                "text": ent.text,
                "label": ent.label_
            })

    return jsonify({"entities": combined_result}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
