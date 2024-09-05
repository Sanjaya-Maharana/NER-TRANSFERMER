#!/bin/bash
set -x

LOG_FILE="./train.log"

echo "Filling base configuration..." | tee -a $LOG_FILE
python -m spacy init fill-config ./configs/base_config.cfg ./configs/config.cfg 2>&1 | tee -a $LOG_FILE

if [ $? -ne 0 ]; then
    echo "Error in filling base configuration" | tee -a $LOG_FILE
    exit 1
fi

echo "Starting training..." | tee -a $LOG_FILE
python -m spacy train ./configs/config.cfg --output ./output --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy 2>&1 | tee -a $LOG_FILE

if [ $? -ne 0 ]; then
    echo "Error during training" | tee -a $LOG_FILE
    exit 1
fi

echo "Training completed successfully" | tee -a $LOG_FILE
