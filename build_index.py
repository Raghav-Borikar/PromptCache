import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --- Configuration ---
DATA_DIR = "data"
INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
DOCUMENTS_MAP_FILE = os.path.join(DATA_DIR, "documents.json")
MODEL_NAME = 'thenlper/gte-large' # A good starting model

def load_all_documents():
    """Loads all processed JSON files from the data directory."""
    all_docs = []
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in '{DATA_DIR}'. Please run ingest.py first.")

    print(f"Found {len(json_files)} document files to index.")
    
    for json_file in json_files:
        path = os.path.join(DATA_DIR, json_file)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_docs.extend(data)
            
    return all_docs

if __name__ == "__main__":
    # 1. Load all text chunks from our JSON files
    print("Loading documents...")
    documents = load_all_documents()
    
    # We only need the text content for creating embeddings
    texts_to_embed = [item['text'] for item in documents]
    print(f"Loaded a total of {len(texts_to_embed)} text chunks.")

    # 2. Load the pre-trained sentence transformer model
    print(f"Loading sentence transformer model: '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    # 3. Generate embeddings for all text chunks
    print("Encoding texts into vectors... (This can take a few minutes)")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    # FAISS requires a numpy array of float32
    embeddings = np.array(embeddings).astype('float32')
    embedding_dimension = embeddings.shape[1]
    print(f"Embeddings created with dimension: {embedding_dimension}")

    # 4. Build the FAISS index
    print("Building FAISS index...")
    # Using IndexFlatL2 for standard L2 (Euclidean) distance search
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(embeddings)
    print(f"FAISS index built successfully with {index.ntotal} vectors.")

    # 5. Save the index and the document map
    # The index file contains the vectors for searching.
    faiss.write_index(index, INDEX_FILE)
    print(f"Index saved to '{INDEX_FILE}'")
    
    # The documents map file links the index position to the original text.
    # This is crucial for retrieving the actual content after a search.
    with open(DOCUMENTS_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    print(f"Document map saved to '{DOCUMENTS_MAP_FILE}'")