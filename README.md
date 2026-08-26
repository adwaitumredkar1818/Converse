# ⚡ VoltIQ - Energy Intelligence RAG

An AI-powered **Hybrid RAG (Retrieval-Augmented Generation)** system for answering energy-related questions using both **unstructured documents** and **structured energy datasets**.

![VoltIQ UI Placeholder](https://via.placeholder.com/800x450.png?text=VoltIQ+Chat+Interface)

The system combines document retrieval, tabular analytics, vector search, query routing, and an LLM to provide data-driven answers through a custom, fast, and responsive web interface.

---

## 🚀 Features

- **Custom Web Interface**: Modern, responsive UI built with pure HTML/CSS/JS served via FastAPI.
- **Low-Memory Footprint**: Uses `fastembed` for blazing-fast, local embedding generation without the massive PyTorch overhead, making it perfect for free-tier deployments.
- **Intelligent Query Routing**: Dynamically routes questions between document retrieval and tabular analytics.
- **Hybrid LLM Backend**: Primary reasoning powered by Groq, with an automatic failover to OpenRouter.
- **Persistent Vector Search**: Built-in ChromaDB for fast and reliable document retrieval.
- **Energy Analytics**: Understands energy conservation, consumption analytics, weather impacts, and tariff comparisons.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Vector Database**: ChromaDB
- **Embedding Engine**: FastEmbed (BAAI/bge-small-en-v1.5)
- **LLM Providers**: Groq API, OpenRouter API
- **Data Processing**: Pandas

---

## 🧠 System Architecture

```text
                     User Question (Web UI)
                               │
                               ▼
                        FastAPI Server
                               │
                               ▼
                        Query Router
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
         Document Queries                Data Queries
                │                             │
                ▼                             ▼
  FastEmbed (bge-small-en-v1.5)        Pandas Analytics
                │                             │
                ▼                             ▼
         Chroma Vector DB                Data Processing
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    Combined Context / Data
                               │
                               ▼
                       LLM Generation
                (Groq -> Fallback OpenRouter)
                               │
                               ▼
                        Generated Answer
                               │
                               ▼
                          VoltIQ UI
```

---

## 🚀 Deployment (Render Free Tier)

This application is highly optimized to run on **Render's Free Tier (512MB RAM)**. By migrating away from heavy ML frameworks like PyTorch and utilizing `fastembed`, the application stays well within the memory limits while still providing powerful local embeddings.

### Steps to Deploy on Render

1. Create a new **Web Service** on [Render](https://render.com/).
2. Connect this GitHub repository.
3. Use the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python scripts/build_embeddings.py && python scripts/build_vector_db.py`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
4. Add your Environment Variables (see below).
5. Click **Deploy**.

---

## ⚙️ Environment Variables

To run the application (locally or on Render), you need to configure the following environment variables. Create a `.env` file in the root directory:

```env
# Required for primary fast LLM responses
GROQ_API_KEY=your_groq_api_key_here

# Required for fallback LLM responses
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## 💻 Local Setup

If you want to run the project locally on your machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/adwaitumredkar1818/Converse.git
   cd Converse
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the Vector Database:**
   ```bash
   python scripts/build_embeddings.py
   python scripts/build_vector_db.py
   ```

4. **Start the FastAPI server:**
   ```bash
   python app.py
   # Or using uvicorn directly:
   # uvicorn api:app --host 127.0.0.1 --port 8501
   ```

5. **Open your browser** and navigate to `http://127.0.0.1:8501`.