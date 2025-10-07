#!/bin/bash

echo "Starting Telegram Colorization Bot..."
echo

# Set your bot token here
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
export MODEL_PATH="models/colorization_release_v2.caffemodel"
export PROTOTXT_PATH="models/colorization_deploy_v2.prototxt"

# Create models directory if it doesn't exist
mkdir -p models

echo "Bot Token: $BOT_TOKEN"
echo "Model Path: $MODEL_PATH"
echo "Prototxt Path: $PROTOTXT_PATH"
echo

# Run the bot
python bot.py

