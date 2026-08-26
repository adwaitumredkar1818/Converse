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

