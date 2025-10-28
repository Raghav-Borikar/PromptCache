from fastapi import FastAPI
from pydantic import BaseModel
import time
import mlflow
import os
from . import cache, retriever, embedder
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
    with mlflow.start_run(): # NEW: Start an MLflow run
        start_time = time.time()
        
        mlflow.log_param("prompt", request.prompt) # NEW: Log the input prompt
        
        cached_results = cache.get_cached_result(request.prompt)
        
        if cached_results:
            latency = (time.time() - start_time) * 1000
            mlflow.log_metric("latency_ms", latency) # NEW
            mlflow.log_metric("cache_hit", 1.0) # NEW
            return {"source": "cache", "results": cached_results, "latency_ms": f"{latency:.2f}"}
        
        prompt_embedding = embedder.get_embedding(request.prompt)
        retrieved_docs = retriever.search(prompt_embedding, k=request.k)
        
        cache.set_cached_result(request.prompt, retrieved_docs)
        
        latency = (time.time() - start_time) * 1000
        mlflow.log_metric("latency_ms", latency) # NEW
        mlflow.log_metric("cache_hit", 0.0) # NEW
        return {"source": "retriever", "results": retrieved_docs, "latency_ms": f"{latency:.2f}"}