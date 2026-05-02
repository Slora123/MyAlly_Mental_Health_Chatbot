# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Setup Backend ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and database code
COPY backend/ ./backend/
COPY database/ ./database/
RUN mkdir -p database/data/processed database/chroma_db

# Stitch the knowledge dataset parts back together BEFORE building the index
RUN cat database/data/processed/knowledge_part_* > database/data/processed/knowledge_documents.jsonl || true

# Build RAG index during Docker build to avoid runtime timeout
# FORCE_REINDEX=true ensures it doesn't accidentally skip building
RUN PYTHONPATH=/app/backend FORCE_REINDEX=true python database/build_rag_index.py

# Copy the built frontend from Stage 1
# This places the 'dist' folder where the backend expects it (../../frontend/dist)
RUN mkdir -p frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set Environment Variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Expose the port Hugging Face expects
EXPOSE 7860

# Run the app
CMD ["python", "backend/app.py"]
