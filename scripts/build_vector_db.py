import os
import sys
import pickle
import chromadb

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

INPUT_EMBEDDINGS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "documents", "embeddings.pkl")
VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "vector_db")
COLLECTION_NAME = "energy_documents"

def build_chroma_vector_db():
    print("=" * 60)
    print("🗄️ PERSISTENT VECTOR DB INGESTION (ChromaDB)")
    print("=" * 60)

    # 1. Load Precomputed Embeddings
    if not os.path.exists(INPUT_EMBEDDINGS_FILE):
        print(f"❌ Input embeddings file not found: {INPUT_EMBEDDINGS_FILE}")
        print("Please run scripts/build_embeddings.py first.")
        return

    print(f"📥 Loading precomputed embeddings from: {INPUT_EMBEDDINGS_FILE}...")
    with open(INPUT_EMBEDDINGS_FILE, "rb") as f:
        embedded_chunks = pickle.load(f)

    total_vectors = len(embedded_chunks)
    print(f"✅ Loaded {total_vectors} embedded chunks.")

    # 2. Initialize Persistent Chroma Client
    print(f"\n📂 Initializing Persistent Chroma DB at directory: {VECTOR_DB_DIR}...")
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

    # Re-create collection to ensure clean state
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"  • Existing collection '{COLLECTION_NAME}' reset.")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # 3. Format Data for Insertion
    ids = [f"chunk_{item['id']}" for item in embedded_chunks]
    documents = [item["page_content"] for item in embedded_chunks]
    metadatas = [item["metadata"] for item in embedded_chunks]
    
    # Convert numpy arrays to float lists if necessary
    embeddings = [
        item["embedding"].tolist() if hasattr(item["embedding"], "tolist") else item["embedding"]
        for item in embedded_chunks
    ]

    # 4. Insert into Vector Database
    print(f"⚡ Ingesting {total_vectors} vectors into collection '{COLLECTION_NAME}'...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    # 5. Sanity Check Similarity Search
    print("\n🔍 Verification: Executing similarity search test...")
    sample_query_embedding = embeddings[0]
    test_search = collection.query(
        query_embeddings=[sample_query_embedding],
        n_results=1
    )
    top_match_id = test_search["ids"][0][0]
    top_doc_snippet = test_search["documents"][0][0][:120].replace('\n', ' ')

    print(f"  • Test Top Match ID: {top_match_id}")
    print(f"  • Snippet: {top_doc_snippet}...")

    # 6. Display Summary Metrics
    print("\n" + "=" * 60)
    print("📊 VECTOR DB INGESTION SUMMARY")
    print("=" * 60)
    print(f"  • Collection Name:        {COLLECTION_NAME}")
    print(f"  • Number of Vectors Stored: {collection.count()}")
    print(f"  • Database Location:       {os.path.abspath(VECTOR_DB_DIR)}")
    print(f"  • Similarity Metric:       Cosine Distance")
    print("=" * 60)

if __name__ == "__main__":
    build_chroma_vector_db()
