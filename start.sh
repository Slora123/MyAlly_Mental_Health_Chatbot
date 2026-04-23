#!/usr/bin/env bash

# 1. Set the Python Path so the system can find your backend modules
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend

# 2. Start the FastAPI server
# This server is already configured in chat_api.py to serve the 
# frontend files from the 'frontend/dist' folder created during build.
echo "🚀 Starting MyAlly (Serving Frontend + Backend)..."

uvicorn src.app.chat_api:app --host 0.0.0.0 --port ${PORT:-8000}
