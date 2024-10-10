Named Entity Recognition (NER) Project
This project uses spaCy to train a Named Entity Recognition (NER) model using a transformer-based architecture for vessel information extraction.

Project Structure
configs/: Contains configuration files for spaCy training.
base_config.cfg: Base configuration template for the model.
config.cfg: Final configuration file filled with default values for training.
data/: Directory to store the training and development datasets.
train.spacy: Training dataset.
dev.spacy: Development (validation) dataset.
scripts/: Shell scripts for various tasks.
train.sh: Script to train the NER model.
.gitignore: Specifies files and directories to be ignored by Git.
README.md: Project documentation.
Setup and Usage
Follow these steps to set up the environment, convert the datasets, and train the model.

Install dependencies: First, install spaCy and spaCy-transformers by running:

sh
Copy code
pip install spacy spacy-transformers
Convert JSON data to spaCy’s format: Convert your training and development data from JSON format to spaCy’s .spacy format:

sh
Copy code
python -m spacy convert ./data/train.json ./data/
python -m spacy convert ./data/dev.json ./data/
Download the transformer model: Download the transformer model that will be used for training the NER model:

sh
Copy code
spacy download en_core_web_trf
Train the NER model: Finally, train the model using the configuration file:

sh
Copy code
spacy train ./config.cfg --output ./models/vessel_info --paths.train ./data/vessel_info/train.spacy --paths.dev ./data/vessel_info/dev.spacy
The trained model will be saved in the ./models/vessel_info directory.

License
This project is licensed under the MIT License. See the LICENSE file for more details.

Author

[Sanjaya Maharana](https://www.linkedin.com/in/sanjaya-maharana-363189137/)

