import faiss
import json
import numpy as np

# --- Load data artifacts at startup ---
print("Loading retriever index and documents...")
index = faiss.read_index("data/faiss_index.bin")
with open("data/documents.json", 'r', encoding='utf-8') as f:
    documents = json.load(f)
print("Retriever loaded successfully.")

def search(query_embedding: np.ndarray, k: int = 3):
    """Searches the index and returns the top k document chunks."""
    distances, indices = index.search(query_embedding.reshape(1, -1), k)
    # Retrieve the original document info using the indices
    return [documents[i] for i in indices[0]]