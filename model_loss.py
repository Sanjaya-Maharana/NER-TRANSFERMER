import sys
import subprocess
import spacy
from spacy.training import Example
import random
import os


def run_spacy_train_with_early_stopping(config_path, output_path, train_data_path, dev_data_path, patience=3):
    try:
        print(f'Command start executing for model: {output_path}')

        nlp = spacy.load("en_core_web_trf")  # Load model
        optimizer = nlp.create_optimizer()

        # Load train and dev data
        train_data = spacy.util.load_data(train_data_path)
        dev_data = spacy.util.load_data(dev_data_path)

        best_score = 0.52  # Set the initial highest accuracy
        patience_counter = 0  # Counter for early stopping

        for iteration in range(100):  # Set a max iteration limit if needed
            random.shuffle(train_data)  # Shuffle the training data
            losses = {}

            # Train on batches of data
            for batch in spacy.util.minibatch(train_data, size=8):
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    nlp.update([example], sgd=optimizer, losses=losses)

            # Evaluate model on dev set
            dev_loss = 0.0
            for text, annotations in dev_data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                dev_loss += nlp.evaluate([example], losses=losses)

            current_score = losses["ner"]  # Replace with the appropriate metric you're tracking

            print(f"Iteration {iteration}: Current NER score: {current_score}")

            # Early stopping logic
            if current_score > best_score:
                best_score = current_score
                patience_counter = 0  # Reset patience if performance improves
                print(f"New best score: {best_score}. Saving model...")
                nlp.to_disk(output_path)  # Save the model if accuracy improves
            else:
                patience_counter += 1
                print(f"Performance declined, patience count: {patience_counter}")

                if patience_counter >= patience:
                    print("Early stopping triggered. No improvement for several iterations.")
                    break

        print(f"Training stopped with the best score: {best_score}")

    except Exception as e:
        print(f"Error during training for model {output_path}: {e}")


if __name__ == "__main__":
    model = 'cargo'

    config_path = ("./config.cfg")
    output_path = f"D:/NER-TRANSFERMER/models/{model}"
    train_data_path = f"./data/{model}/train.spacy"
    dev_data_path = f"./data/{model}/dev.spacy"
    print(f'Paths set for {model}')

    run_spacy_train_with_early_stopping(config_path, output_path, train_data_path, dev_data_path)
