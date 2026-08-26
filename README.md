# ⚡ Converse: Energy Intelligence RAG

An AI-powered **Hybrid RAG (Retrieval-Augmented Generation)** system for answering energy-related questions using both **unstructured documents** and **structured energy datasets**.

The system combines document retrieval, tabular analytics, vector search, query routing, and dual-provider LLM support to provide data-driven answers through a custom, highly-optimized interactive web interface.

---

## 🚀 Features

- 🔎 **Document-based RAG**: Semantic search using lightweight, memory-efficient `fastembed`.
- 📊 **Energy Analytics**: Understand consumption, weather, household data, and tariffs.
- 🧠 **Intelligent Query Routing**: Dynamically decides whether to query documents or databases.
- 🗄️ **Chroma Vector Database**: Persistent vector search engine for ultra-fast document retrieval.
- 🤖 **Dual-Provider LLM Generation**: High-speed primary generation via **Groq** with automatic failover to **OpenRouter**.
- ⚡ **Custom Web Dashboard**: Lightning-fast, responsive HTML/JS/Vanilla CSS frontend powered by a FastAPI backend.
- ☁️ **Cloud-Ready**: Optimized to run on memory-constrained platforms like Render's Free Tier (< 512MB RAM) by completely eliminating PyTorch dependencies.

---

## 🧠 System Architecture

```text
                     User Query
                         │
                         ▼
                  ┌──────────────┐
                  │ Query Router │
                  └──────┬───────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      Document Queries        Data Queries
             │                       │
             ▼                       ▼
      Document Retrieval      Tabular Analytics
             │                       │
             ▼                       ▼
 FastEmbed & Chroma DB     Pandas / Data Processing
             │                       │
             └───────────┬───────────┘
                         ▼
                    Context/Data
                         │
                         ▼
            LLM (Groq / OpenRouter Fallback)
                         │
                         ▼
                 Generated Answer
                         │
                         ▼
          FastAPI Backend & Custom Web UI
```

---

## 🛠️ Setup & Local Development

### 1. Prerequisites
- Python 3.10+
- An API key from **Groq** and **OpenRouter** (Optional).

### 2. Installation
Clone the repository and install the lightweight requirements:
```bash
git clone https://github.com/adwaitumredkar1818/Converse.git
cd Converse
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 4. Build the Database (If modifying documents)
If you add new documents to `data/raw/documents`, rebuild the embeddings and vector database:
```bash
python scripts/chunk_documents.py
python scripts/build_embeddings.py
python scripts/build_vector_db.py
```

### 5. Start the Application
Run the FastAPI backend server:
```bash
python api.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## ☁️ Deployment

This repository is heavily optimized for free-tier cloud deployment platforms like **Render**:
- PyTorch and HuggingFace Transformers have been removed in favor of `fastembed` (< 100MB RAM usage).
- The Streamlit dependency was replaced with a fully decoupled frontend and lightweight FastAPI server.
- Simply connect this GitHub repository to Render (or a similar platform) to instantly deploy as a Web Service.