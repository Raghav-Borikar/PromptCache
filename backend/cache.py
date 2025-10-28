import redis
import numpy as np
import json
import os
from . import embedder

# --- Configuration ---
# Use environment variables or default to localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379
SIMILARITY_THRESHOLD = 0.95  # The τ value for semantic similarity

# --- Connect to Redis ---
print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    redis_client.ping() # Check the connection
    print("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

def get_cached_result(prompt: str):
    """
    Checks for a semantically similar prompt in the cache.
    If found, returns the PREVIOUSLY GENERATED ANSWER.
    """
    if not redis_client: return None
    prompt_embedding = embedder.get_embedding(prompt)
    
    for key in redis_client.keys("prompt:*"):
        cached_data = json.loads(redis_client.get(key))
        cached_embedding = np.array(cached_data['embedding']).astype('float32')
        
        # --- MODIFICATION HERE ---
        # Calculate norms
        prompt_norm = np.linalg.norm(prompt_embedding)
        cached_norm = np.linalg.norm(cached_embedding)
        
        # Add a small epsilon to prevent division by zero
        epsilon = 1e-9
        
        # Calculate Cosine Similarity safely
        similarity = np.dot(prompt_embedding, cached_embedding) / ((prompt_norm * cached_norm) + epsilon)
        
        if similarity > SIMILARITY_THRESHOLD:
            print(f"CACHE HIT! Similarity: {similarity:.2f}")
            # IMPORTANT: Return the whole dictionary now
            return cached_data
            
    print("CACHE MISS!")
    return None

def set_cached_result(prompt: str, context: list, generated_answer: str):
    """
    Stores a new prompt, its context, and the final generated answer.
    """
    if not redis_client: return
    prompt_embedding = embedder.get_embedding(prompt)
    key = f"prompt:{prompt}"
    
    data_to_cache = {
        'embedding': prompt_embedding.tolist(),
        'results': context,
        'generated_answer': generated_answer # NEW: Store the answer
    }
    
    redis_client.set(key, json.dumps(data_to_cache))