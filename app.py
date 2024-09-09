import sys
import json
import spacy
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


app.route('/')
def home()
    return {}

@app.route('/predict/vessel_info', methods=['POST'])
def predict_vessel_info():
    return predict('vessel_info')


@app.route('/predict/tonnage_info', methods=['POST'])
def predict_tonnage_info():
    return predict('tonnage_info')


@app.route('/predict/cargo', methods=['POST'])
def predict_cargo():
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



