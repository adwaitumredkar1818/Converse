import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "vector_db")
COLLECTION_NAME = "energy_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_cached_model = None
_cached_collection = None

def get_resources():
    global _cached_model, _cached_collection
    if _cached_model is None or _cached_collection is None:
        _cached_model = SentenceTransformer(MODEL_NAME)
        client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        _cached_collection = client.get_collection(name=COLLECTION_NAME)
    return _cached_model, _cached_collection

def retrieve(query: str, top_k: int = 15):
    """
    Accepts a user query, encodes it using SentenceTransformer, searches the persistent Chroma DB,
    and returns a list of top_k matched document chunks with similarity scores and metadata.
    """
    model, collection = get_resources()

    # 1. Embed user query
    query_embedding = model.encode([query]).tolist()

    # 2. Query Chroma Vector DB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "distances", "metadatas"]
    )

    retrieved_items = []
    if not results or not results.get("ids") or len(results["ids"][0]) == 0:
        return retrieved_items

    ids = results["ids"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for i in range(len(ids)):
        dist = distances[i]
        # Cosine similarity score = 1 - cosine distance
        sim_score = max(0.0, 1.0 - dist)

        retrieved_items.append({
            "chunk_id": ids[i],
            "content": documents[i],
            "similarity_score": round(sim_score, 4),
            "distance": round(dist, 4),
            "metadata": metadatas[i]
        })

    return retrieved_items

if __name__ == "__main__":
    test_query = "What are the best methods for energy conservation?"
    print("=" * 60)
    print(f"🔎 DOCUMENT RETRIEVAL TEST")
    print(f"   Query: '{test_query}'")
    print("=" * 60)

    results = retrieve(test_query, top_k=5)

    print(f"\n✅ Retrieved {len(results)} relevant chunks:\n")
    for idx, item in enumerate(results, 1):
        print(f"📌 [{idx}] Chunk ID: {item['chunk_id']} | Similarity Score: {item['similarity_score']} (Distance: {item['distance']})")
        print(f"    Source File: {item['metadata'].get('file_name')} | Type: {item['metadata'].get('file_type')}")
        print(f"    Content Preview:")
        preview_text = item['content'][:250].replace('\n', ' ')
        print(f"    \"{preview_text}...\"")
        print("-" * 60)
