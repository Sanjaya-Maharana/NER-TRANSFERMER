import json
from pathlib import Path


def clean_entity_spans(input_json_folder, output_json_folder):
    print(f"Cleaning files from {input_json_folder} and saving to {output_json_folder}")
    output_json_folder.mkdir(parents=True, exist_ok=True)

    for json_file_path in input_json_folder.glob("*.json"):
        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            for annotation in data["annotations"]:
                text = annotation[0].replace("\n", " ").replace("\t", " ")
                entities = annotation[1]["entities"]
                valid_entities = []

                for entity in entities:
                    start, end, label = entity
                    entity_text = text[start:end]
                    trimmed_text = entity_text.strip()
                    trimmed_text = trimmed_text.replace("\r\n", " ").replace("\r", "").replace("\n", " ").replace("\t", " ").replace("  ", "").strip()

                    if (label == "LOAD_PORT" and ' // S' in trimmed_text) or \
                       (label == "COMPANY" and '= H' in trimmed_text) or \
                       (label == "LOAD_PORT" and ' ORE ' == trimmed_text) or \
                       (label == "CARGO_SIZE" and '/- 5' == trimmed_text) or \
                       (label == "CARGO_SIZE" and '/- 5' == trimmed_text) or \
                       (label == "CARGO_SIZE" and 'L TO FIX: ACCT ' == trimmed_text):
                        print(f"Skipping incorrect '{label}' from index {start} to {end}: '{entity_text}'")
                        continue
                    if entity_text != trimmed_text:
                        new_start = start + len(entity_text) - len(trimmed_text.lstrip())
                        new_end = end - len(entity_text) + len(trimmed_text.rstrip())
                        entity[0] = new_start
                        entity[1] = new_end


                    valid_entities.append(entity)

                    print(f"Entity '{label}' from index {start} to {end}: '{entity_text}'")
                    print(f"Trimmed text from index {entity[0]} to {entity[1]}: '{text[entity[0]:entity[1]]}'\n")

                annotation[1]["entities"] = valid_entities

            output_file_path = output_json_folder / json_file_path.name
            print(f"Saving cleaned file to {output_file_path}")
            with open(output_file_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing file {json_file_path}: {e}")


