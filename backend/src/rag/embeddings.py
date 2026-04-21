"""
src/rag/embeddings.py
"""

import torch
from chromadb.utils import embedding_functions

MODEL_NAME = "all-MiniLM-L6-v2"

def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def get_embedding_function() -> embedding_functions.SentenceTransformerEmbeddingFunction:
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME,
        device=get_device(),
    )
