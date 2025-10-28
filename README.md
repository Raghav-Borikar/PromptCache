# 🧠 PromptCache: A Latency-Optimized RAG System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PromptCache** is a complete, end-to-end **Retrieval-Augmented Generation (RAG)** system designed to reduce latency and operational costs by implementing a novel **semantic caching layer**.  
Traditional RAG systems perform redundant, costly vector database queries even for semantically similar prompts.  
PromptCache intelligently intercepts these queries, reusing previously retrieved context to deliver answers up to **95% faster** while significantly reducing computational load.

This project is built from scratch with a strong focus on **MLOps best practices**, including **data versioning with DVC** and **full containerization** with **Docker and Docker Compose**.  
The knowledge base is powered by the text of the *Harry Potter* book series.

---

## ✨ Key Features

- **Full RAG Pipeline:** Ingests text from PDF documents, creates vector embeddings, and retrieves relevant context to answer user queries.  
- **Novel Semantic Caching:** Utilizes a Redis-based cache that stores prompt embeddings. If a new query is semantically similar (cosine similarity > 0.95) to a cached one, it returns the stored context instantly, bypassing the expensive vector search.  
- **Containerized Services:** The entire application stack (FastAPI backend, Redis cache, Streamlit frontend) is orchestrated by Docker Compose, allowing for a one-command launch.  
- **MLOps Ready:** Implements version control for both code (Git) and data (DVC), ensuring reproducibility and a solid foundation for future CI/CD and deployment.  
- **Interactive Frontend:** A user-friendly web interface built with Streamlit allows easy interaction and displays real-time performance metrics like cache hit rate and latency.

---

## 🏗️ Architecture

The system is composed of **three main containerized services** that work together:  
a frontend UI, a backend API, and a Redis cache.  
Data ingestion and indexing are handled by preliminary scripts.

+-----------------------------------------------------------------------+
| Docker Environment |
| |
| +-----------------------+ +-----------------------+ |
| | Frontend Service | | Backend Service | |
| | (Streamlit Container) |---->| (FastAPI /query) | |
| +-----------------------+ +-----------+-----------+ |
| | |
| +-----------------------|------------------+ |
| | v (Cache Miss) | |
| | | |
| +-----------------------+ +-----------------------+ |
| | Cache Layer |<--->| Retriever Layer | |
| | (Redis Container) | | (SentenceTransformer | |
| | - Stores prompt | | + FAISS Index) | |
| | embeddings & results| | - Searches documents | |
| +-----------------------+ +-----------------------+ |
| |
+-----------------------------------------------------------------------+

---

### ⚙️ How the Semantic Cache Works

#### **1. Cache Miss (First-time or Unique Query)**
- The user's prompt is received by the FastAPI backend.  
- The backend checks Redis — no semantically similar prompt is found.  
- The prompt is converted into a vector embedding.  
- The FAISS index is searched using this embedding to find top-K relevant text chunks.  
- The retrieved chunks are returned to the user.  
- The prompt’s embedding and its retrieved chunks are **stored as a new entry in Redis**.

#### **2. Cache Hit (Similar Subsequent Query)**
- A new prompt (e.g., “Tell me about Dumbledore”) is received.  
- The backend checks Redis, generates an embedding for the new prompt, and calculates cosine similarity with all stored embeddings.  
- If a cached embedding has a **similarity > 0.95**,  
  the corresponding stored context chunks are **instantly retrieved** and returned, skipping the FAISS search.

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | FastAPI, Uvicorn |
| **Frontend** | Streamlit, Pandas |
| **Caching** | Redis |
| **Vector Search** | FAISS (Facebook AI) |
| **Embedding Model** | `all-MiniLM-L6-v2` (Sentence-Transformers) |
| **Data Processing** | PyPDF |
| **MLOps & Orchestration** | Git (code), DVC (data), Docker, Docker Compose |

---

## 📁 Project Structure
PromptCache/
├── backend/
│ ├── Dockerfile # Recipe for backend container
│ ├── requirements.txt # Backend Python dependencies
│ ├── init.py # Package initialization
│ ├── main.py # FastAPI application logic
│ ├── cache.py # Semantic caching with Redis
│ ├── embedder.py # Handles text embeddings
│ └── retriever.py # FAISS-based retrieval
│
├── data/
│ ├── book1.pdf # Example source data
│ ├── book1.json # Processed text chunks
│ ├── documents.json # Master chunk mapping
│ └── faiss_index.bin # FAISS vector index
│
├── frontend/
│ ├── Dockerfile # Frontend container setup
│ ├── requirements.txt # Frontend dependencies
│ └── app.py # Streamlit UI application
│
├── ingest.py # PDF → JSON processing script
├── build_index.py # FAISS index builder
├── docker-compose.yml # Multi-container orchestration
└── README.md # This file

---

## 🚀 Getting Started

Follow these steps to get the full PromptCache application running **locally** or on a **remote server**.

### 🧩 Prerequisites

- Git  
- Python 3.8+  
- Docker & Docker Compose  

---

### 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd PromptCache

2️⃣ Set Up Data and Environment

Place your source PDF files (e.g., Harry Potter books) in the data/ directory.

Create and activate a virtual environment:

python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate

pip install pypdf sentence-transformers faiss-cpu dvc

3️⃣ Ingest and Index the Data

Run the following scripts (only once initially):

# 1. Process PDFs into structured JSON
python ingest.py

# 2. Create the FAISS vector index
python build_index.py

4️⃣ Configure the Frontend

Edit frontend/app.py and update the server address:

# frontend/app.py

# If running locally:
SERVER_IP_ADDRESS = "127.0.0.1"

# If running remotely:
SERVER_IP_ADDRESS = "<YOUR_SERVER_IP_ADDRESS>"

5️⃣ Launch the Application

With Docker running, start the entire stack:

docker-compose up --build

This will:

Build Docker images for both frontend and backend

Start containers for Frontend, Backend, and Redis

Connect them over a shared Docker network

6️⃣ Access the Application

Frontend UI: http://<YOUR_SERVER_IP_ADDRESS>:8501

Backend API Docs: http://<YOUR_SERVER_IP_ADDRESS>:8000/docs

📈 Future Improvements

PromptCache serves as a robust foundation. The following features are planned for enhancement:

Adaptive Compression: Use bfloat16 compression for embeddings in Redis to reduce memory.

CI/CD Pipeline: Automate Docker builds and tests via GitHub Actions.

Cloud Deployment: Support GCP (Cloud Run + Memorystore) and AWS (ECS + ElastiCache).

Live Monitoring: Integrate Prometheus + Grafana for real-time performance dashboards.

LLM Integration: Add a layer where retrieved context is fed into an LLM (e.g., GPT or LLaMA) for natural conversational answers.
