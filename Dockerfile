# --- Stage 1: Build the React Frontend ---
FROM node:20 AS build-stage
WORKDIR /app/frontend
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend ./
RUN npm run build

# --- Stage 2: Setup the FastAPI Backend ---
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY ./backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the rest of the backend code
COPY ./backend ./backend

# Copy the built frontend files to the expected location
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# Copy project-level files needed (like empty .env if needed, but secrets should be env vars)
# COPY .env . (Usually handled by deployment secrets)

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=7860

# Hugging Face Spaces runs on port 7860
EXPOSE 7860

# Run the application
CMD ["python3", "-m", "src.app.chat_api"]
