# ⚡ Energy Intelligence RAG

An AI-powered **Hybrid RAG (Retrieval-Augmented Generation)** system for answering energy-related questions using both **unstructured documents** and **structured energy datasets**.

The system combines document retrieval, tabular analytics, vector search, query routing, and an LLM to provide data-driven answers through an interactive Streamlit interface.

---

## 🚀 Features

- 🔎 Document-based RAG
- 📊 Energy consumption analytics
- 🌦️ Weather and energy analysis
- 🏠 Household-level analytics
- 💰 Tariff comparison
- 📅 Bank holiday analysis
- 🧠 Intelligent query routing
- 🗄️ Chroma vector database
- 🤖 LLM-powered response generation
- ⚡ Streamlit interactive dashboard
- 📈 Pipeline performance monitoring

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
       Chroma Vector DB       Pandas / Data Processing
             │                       │
             └───────────┬───────────┘
                         ▼
                    Context/Data
                         │
                         ▼
                      LLM
                         │
                         ▼
                 Generated Answer
                         │
                         ▼
                   Streamlit UI