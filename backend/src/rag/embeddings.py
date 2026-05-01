"""
src/rag/embeddings.py
"""

import os
from chromadb.utils import embedding_functions

def get_embedding_function():
    api_key = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
    if not api_key:
        print("⚠️ WARNING: Hugging Face API Token not found in environment.")
    
    return embedding_functions.HuggingFaceEmbeddingFunction(
        api_key=api_key,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
