import os
import sys
import json
import time
import pickle
from sentence_transformers import SentenceTransformer

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

INPUT_CHUNKS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "documents", "chunks.json")
OUTPUT_EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "documents", "embeddings.pkl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def generate_and_save_embeddings():
    print("=" * 60)
    print("🚀 EMBEDDING GENERATION PIPELINE")
    print("=" * 60)

    # 1. Load Chunks
    if not os.path.exists(INPUT_CHUNKS_FILE):
        print(f"❌ Input file not found: {INPUT_CHUNKS_FILE}")
        print("Please run scripts/chunk_documents.py first.")
        return

    print(f"📥 Loading chunked documents from: {INPUT_CHUNKS_FILE}...")
    with open(INPUT_CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    total_chunks = len(chunks)
    print(f"✅ Loaded {total_chunks} chunks.")

    # 2. Load Embedding Model
    print(f"\n🧠 Initializing Embedding Model: {MODEL_NAME}...")
    start_time = time.time()
    model = SentenceTransformer(MODEL_NAME)
    
    # 3. Generate Embeddings
    texts = [c["page_content"] for c in chunks]
    print(f"⚡ Generating 384-dimensional embeddings for {total_chunks} text chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    embedding_dims = embeddings.shape[1] if hasattr(embeddings, 'shape') else len(embeddings[0])

    # Combine metadata, content, and vector embedding into serializable objects
    embedded_chunks = []
    for chunk, emb in zip(chunks, embeddings):
        embedded_chunks.append({
            "id": chunk["id"],
            "page_content": chunk["page_content"],
            "metadata": chunk["metadata"],
            "embedding": emb
        })

    # 4. Save to PKL
    os.makedirs(os.path.dirname(OUTPUT_EMBEDDINGS_FILE), exist_ok=True)
    with open(OUTPUT_EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(embedded_chunks, f)

    elapsed_time = time.time() - start_time

    # 5. Display Summary Metrics
    print("\n" + "=" * 60)
    print("📊 EMBEDDING GENERATION SUMMARY")
    print("=" * 60)
    print(f"  • Total Chunks Processed: {total_chunks}")
    print(f"  • Embedding Dimensions:  {embedding_dims}")
    print(f"  • Processing Time:       {elapsed_time:.2f} seconds")
    print(f"  • Output Saved To:       {OUTPUT_EMBEDDINGS_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    generate_and_save_embeddings()
