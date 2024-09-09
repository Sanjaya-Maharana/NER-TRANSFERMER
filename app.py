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
        'vessel_info': {'count': 0, 'last_called': None},
        'tonnage_info': {'count': 0, 'last_called': None},
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

@app.route('/predict/vessel_info', methods=['POST'])
def predict_vessel_info():
    update_api_stats('vessel_info')
    return predict('vessel_info')

@app.route('/predict/tonnage_info', methods=['POST'])
def predict_tonnage_info():
    update_api_stats('tonnage_info')
    return predict('tonnage_info')

@app.route('/predict/cargo', methods=['POST'])
def predict_cargo():
    update_api_stats('cargo')
    return predict('cargo')

def predict(model):
    if 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400

    text = request.json['text']
    try:
        nlp = spacy.load(Path(f"models/{model}/model-best"))
    except Exception as e:
        return jsonify({'error': f'Failed to load model {model}: {str(e)}'}), 500

    doc = nlp(text)
    result_dict = []
    for ent in doc.ents:
        result_dict.append({
            "text": ent.text,
            "label": ent.label_
        })
    return jsonify({"entities": result_dict}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
