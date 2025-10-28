from fastapi import FastAPI
from pydantic import BaseModel
import time
from . import cache, retriever, embedder

app = FastAPI(title="PromptCache API")

class QueryRequest(BaseModel):
    prompt: str
    k: int = 3 # Number of results to return

@app.post("/query")
def process_query(request: QueryRequest):
    """
    Processes a user query by first checking the semantic cache, 
    and then falling back to the vector retriever.
    """
    start_time = time.time()
    
    # 1. Check cache first
    cached_results = cache.get_cached_result(request.prompt)
    
    if cached_results:
        latency = (time.time() - start_time) * 1000
        return {
            "source": "cache",
            "results": cached_results,
            "latency_ms": f"{latency:.2f}"
        }
    
    # 2. If miss, embed the prompt and retrieve from FAISS
    prompt_embedding = embedder.get_embedding(request.prompt)
    retrieved_docs = retriever.search(prompt_embedding, k=request.k)
    
    # 3. Store the new result in the cache for future queries
    cache.set_cached_result(request.prompt, retrieved_docs)
    
    latency = (time.time() - start_time) * 1000
    return {
        "source": "retriever",
        "results": retrieved_docs,
        "latency_ms": f"{latency:.2f}"
    }