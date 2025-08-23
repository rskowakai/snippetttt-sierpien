#!/bin/bash
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading SpaCy language models..."
python -m spacy download en_core_web_sm
python -m spacy download pl_core_news_sm

echo "Setup complete!"
