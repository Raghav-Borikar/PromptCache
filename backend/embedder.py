"""backend/embedder.py"""
from sentence_transformers import SentenceTransformer
import numpy as np

# This ensures the model is loaded only once when the module is imported.
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded.")

def get_embedding(text: str) -> np.ndarray:
    """Generates an embedding for a given text."""
    embedding = model.encode(text)
    return np.array(embedding).astype('float32')