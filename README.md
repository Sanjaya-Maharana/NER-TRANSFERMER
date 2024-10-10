Named Entity Recognition (NER) Project

This project uses spaCy to train a Named Entity Recognition (NER) model with a transformer-based architecture.

Project Structure

configs/: Configuration files for the spaCy training.
base_config.cfg: Base configuration template.
config.cfg: Final configuration filled with default values.
data/: Directory to store training and development datasets.
train.spacy: Training dataset.
dev.spacy: Development dataset.
scripts/: Shell scripts for various tasks.
train.sh: Script to train the NER model.
.gitignore: Git ignore file.
README.md: Project documentation.


Setup and Usage
Install dependencies:
 pip install spacy spacy-transformers
  python -m spacy convert ./data/train.json ./data/
  python -m spacy convert ./data/dev.json ./data/

```sh
  spacy download en_core_web_trf

  spacy train ./config.cfg --output ./models/vessel_info --paths.train ./data/vessel_info/train.spacy --paths.dev ./data/vessel_info/dev.spacy


## License

SM

## Author

[Sanjaya Maharana](https://www.linkedin.com/in/sanjaya-maharana-363189137/)

