import sys
import json
import subprocess
from pathlib import Path
from clean import clean_entity_spans
from convert import combine_json_files, convert_json_to_spacy


print('started')


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


if __name__ == "__main__":
    models = ['cargo']

    for model in models:
        print(f'Starting process for model: {model}')

        config_path = "./config.cfg"
        output_path = f".models/{model}"
        train_data_path = f"./data/{model}/train.spacy"
        dev_data_path = f"./data/{model}/dev.spacy"
        print(f'Paths set for {model}')

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

        print(f"Process completed for model: {model}\n")
