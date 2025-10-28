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
    """Checks for a semantically similar prompt in the cache."""
    if not redis_client:
        return None

    prompt_embedding = embedder.get_embedding(prompt)
    
    # Iterate through all cached prompts
    for key in redis_client.keys("prompt:*"):
        cached_data_json = redis_client.get(key)
        cached_data = json.loads(cached_data_json)
        
        cached_embedding = np.array(cached_data['embedding']).astype('float32')
        
        # Calculate Cosine Similarity
        similarity = np.dot(prompt_embedding, cached_embedding) / (np.linalg.norm(prompt_embedding) * np.linalg.norm(cached_embedding))
        
        if similarity > SIMILARITY_THRESHOLD:
            print(f"CACHE HIT! Prompt similar to '{key.split(':')[1]}'. Similarity: {similarity:.2f}")
            return cached_data['results']
            
    print("CACHE MISS!")
    return None

def set_cached_result(prompt: str, results: list):
    """Stores a new prompt and its retrieved results in the cache."""
    if not redis_client:
        return

    prompt_embedding = embedder.get_embedding(prompt)
    key = f"prompt:{prompt}"
    
    data_to_cache = {
        'embedding': prompt_embedding.tolist(),
        'results': results
    }
    
    redis_client.set(key, json.dumps(data_to_cache))