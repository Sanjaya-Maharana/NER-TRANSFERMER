import json
from pathlib import Path
import spacy
from spacy.tokens import DocBin

nlp = spacy.blank("en")


def combine_json_files(json_folder, model):
    combined_annotations = []

    for json_file_path in json_folder.glob("*.json"):
        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                combined_annotations.extend(data.get("annotations", []))
        except Exception as e:
            print(f"Error processing file {json_file_path}: {e}")

    combined_data = {
        "classes": data.get("classes", []),
        "annotations": combined_annotations
    }
    output_file = "train.json" if 'train' in str(json_folder).lower() else "dev.json"
    output_path = Path(f"D:/NER-TRANSFERMER/data/{model}")
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / output_file
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(combined_data, outfile, ensure_ascii=False, indent=4)
    print(f"Data saved successfully at {file_path}")
    return combined_data

def convert_json_to_spacy(json_data, output_path):
    doc_bin = DocBin()

    for item in json_data["annotations"]:
        text = item[0]
        entities = item[1]["entities"]
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in entities:
            span = doc.char_span(start, end, label=label)
            if span is None:
                print(f"Skipping entity in : ({start}, {end}, {label})")
            else:
                ents.append(span)

        doc.ents = ents
        doc_bin.add(doc)
    doc_bin.to_disk(output_path)
    print(f"Saved {output_path}")


