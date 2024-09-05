import sys
import json
import spacy
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from clean import clean_entity_spans
from convert import combine_json_files, convert_json_to_spacy

app = Flask(__name__)


UPLOAD_FOLDER = './dataset'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def download_spacy_model():
    try:
        command = [
            sys.executable,
            "-m", "spacy", "download", "en_core_web_trf"
        ]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            for line in process.stdout:
                print(line, end='')

            for line in process.stderr:
                print(f"ERROR: {line}", end='')

        returncode = process.wait()

        if returncode == 0:
            print("Model 'en_core_web_trf' downloaded successfully!")
        else:
            print(f"Failed to download 'en_core_web_trf'. Return code: {returncode}")

    except Exception as e:
        print(f"Error during downloading 'en_core_web_trf': {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'model' not in request.form:
        return jsonify({'error': 'Model not specified'}), 400

    model = request.form['model']
    if model not in ['tonnage_info', 'vessel_info', 'cargo']:
        return jsonify({'error': 'Invalid model specified'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    files = request.files.getlist('file')
    upload_folder = Path(app.config['UPLOAD_FOLDER']) / model / 'train'
    upload_folder.mkdir(parents=True, exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(upload_folder / filename)

    return jsonify({'message': f'Files successfully uploaded for model {model}'}), 200


@app.route('/train', methods=['POST'])
def train_model():
    download_spacy_model()
    model = request.form.get('model')
    if model not in ['tonnage_info', 'vessel_info', 'cargo']:
        return jsonify({'error': 'Invalid model specified'}), 400

    config_path = "./config.cfg"
    output_path = f"./models/{model}"
    train_data_path = f"./data/{model}/train.spacy"
    dev_data_path = f"./data/{model}/dev.spacy"

    train_json_folder = Path(f"./dataset/{model}/train")
    train_output_folder = Path(f"./dataset/{model}/cleaned_train")
    test_json_folder = Path(f"./dataset/{model}/test")
    test_output_folder = Path(f"./dataset/{model}/cleaned_test")

    clean_entity_spans(train_json_folder, train_output_folder)
    clean_entity_spans(test_json_folder, test_output_folder)

    train_data = combine_json_files(train_output_folder, model)
    test_data = combine_json_files(test_output_folder, model)

    train_output_path = Path(f"./data/{model}/train.spacy")
    test_output_path = Path(f"./data/{model}/dev.spacy")

    convert_json_to_spacy(train_data, train_output_path)
    convert_json_to_spacy(test_data, test_output_path)

    run_spacy_train(config_path, output_path, train_data_path, dev_data_path)

    return jsonify({'message': f'Training started for model {model}'}), 200


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
    text = text.replace('\n\n', '       ').replace('\n', '  ')
    print(text)
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

def run_spacy_train(config_path, output_path, train_data_path, dev_data_path):
    try:
        print(f'Command start executing for model: {output_path}')
        command = [
            sys.executable,
            "-m", "spacy", "train", config_path,
            "--output", output_path,
            "--paths.train", train_data_path,
            "--paths.dev", dev_data_path
        ]

        print(f'Running command: {" ".join(command)}')
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            for line in process.stdout:
                print(line, end='')

            for line in process.stderr:
                print(f"ERROR: {line}", end='')

        returncode = process.wait()

        if returncode == 0:
            print(f"Training completed successfully for model: {output_path}!")
        else:
            print(f"Training failed for model: {output_path} with return code: {returncode}")

    except Exception as e:
        print(f"Error during training for model {output_path}: {e}")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
