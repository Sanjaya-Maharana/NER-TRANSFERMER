# Named Entity Recognition (NER) Project

This project uses spaCy to train a Named Entity Recognition (NER) model with a transformer-based architecture.

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

```sh
    python -m spacy convert ./data/train.json ./data/
    python -m spacy convert ./data/dev.json ./data/
