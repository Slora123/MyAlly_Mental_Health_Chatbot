#!/usr/bin/env bash
# exit on error
set -o errexit

# --- 1. Build Frontend ---
echo "Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# --- 2. Build Backend ---
echo "Installing Backend dependencies..."
pip install -r backend/requirements.txt

# --- 3. Prep Data (Build Vector Index) ---
# We run the index builder to ensure the database is ready.
# We set PYTHONPATH to include 'backend' so imports like 'src.rag' work.
echo "Initializing RAG index..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
python database/build_rag_index.py

echo "Build complete!"
