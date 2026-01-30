#!/bin/bash

# 1. Start the Action Server in the background
# We use '&' to detach it so the script continues
echo "Starting Action Server..."
rasa run actions --port 5055 &

# 2. Wait a few seconds to ensure Action Server handles the startup
sleep 5

# 3. Start the Main Rasa Server
# Hugging Face explicitly requires the app to listen on port 7860
echo "Starting Rasa Core..."
rasa run --enable-api --cors "*" --port 7860 --debug