"""
src/rag/embeddings.py
"""

import os
from chromadb.utils import embedding_functions

def get_embedding_function() -> embedding_functions.HuggingFaceHubEmbeddingFunction:
    api_key = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_key:
        print("⚠️ WARNING: HUGGINGFACE_API_TOKEN not found. Vector search will fail.")
    
    return embedding_functions.HuggingFaceHubEmbeddingFunction(
        api_key=api_key,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
