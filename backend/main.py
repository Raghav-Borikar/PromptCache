from fastapi import FastAPI
from pydantic import BaseModel
import time
import mlflow
import os
from . import cache, retriever, embedder, generator 
from prometheus_fastapi_instrumentator import Instrumentator

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
if MLFLOW_TRACKING_URI:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("PromptCache Queries")

app = FastAPI(title="PromptCache API")

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    print("Starting up... connecting resources etc.")
    
class QueryRequest(BaseModel):
    prompt: str
    k: int = 3 # Number of results to return

@app.post("/query")
def process_query(request: QueryRequest):
    start_time = time.time()
    
    # 1. Check cache first
    cached_data = cache.get_cached_result(request.prompt)
    
    if cached_data:
        latency = (time.time() - start_time) * 1000
        return {
            "source": "cache",
            "generated_answer": cached_data['generated_answer'], # Return cached answer
            "results": cached_data['results'],
            "latency_ms": f"{latency:.2f}"
        }
    
    # --- CACHE MISS: Perform full RAG pipeline ---
    
    # 2. Retrieve context
    prompt_embedding = embedder.get_embedding(request.prompt)
    retrieved_docs = retriever.search(prompt_embedding, k=request.k)
    
    # 3. Generate the final answer using the LLM
    final_answer = generator.generate_answer(request.prompt, retrieved_docs)
    
    # 4. Store the new result (context AND answer) in the cache
    cache.set_cached_result(request.prompt, retrieved_docs, final_answer)
    
    latency = (time.time() - start_time) * 1000
    return {
        "source": "retriever+generator", # NEW: Updated source
        "generated_answer": final_answer, # NEW: Add the answer to the response
        "results": retrieved_docs,
        "latency_ms": f"{latency:.2f}"
    }