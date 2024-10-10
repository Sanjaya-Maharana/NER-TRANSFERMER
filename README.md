# Custom Named Entity Recognition (CNER) Project

This project uses spaCy to train a Custom Named Entity Recognition (NER) model with a transformer-based architecture.

## Project Structure

- `configs/`: Configuration files for the spaCy training.
  - `base_config.cfg`: Base configuration template.
  - `config.cfg`: Final configuration filled with default values.
- `data/`: Directory to store training and development datasets.
  - `train.spacy`: Training dataset.
  - `dev.spacy`: Development dataset.
- `scripts/`: Shell scripts for various tasks.
  - `train.sh`: Script to train the NER model.
- `.gitignore`: Git ignore file.
- `README.md`: Project documentation.

## Setup and Usage

1. Install dependencies:
   ```sh
    pip install spacy spacy-transformers
    
    python spacy download en_core_web_trf

2. Process Data
   ```sh
    python -m spacy convert ./data/train.json ./data/
    python -m spacy convert ./data/dev.json ./data/

3. Generate Config File
   ```sh
   python -m spacy init fill-config ./configs/base_config.cfg ./configs/config.cfg

4. Run and Train the model
   ```sh
   python spacy train ./config.cfg --output ./models/vessel_info --paths.train ./data/vessel_info/train.spacy --paths.dev ./data/vessel_info/dev.spacy

## License

This project is licensed under the SM License. See the LICENSE file for more details.

## Author

Sanjaya Maharana


[Email](SanjayaMaharana145@gmail.com), 
[Linkedin](https://www.linkedin.com/in/sanjaya-maharana-363189137/), 
[Git-Hub](https://github.com/Sanjaya-Maharana/)
