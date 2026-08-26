import os
import sys
import json

# Ensure project root is in sys.path for robust imports regardless of CWD or entrypoint
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from scripts.load_documents import load_all_documents
except ModuleNotFoundError:
    from load_documents import load_all_documents

# Directories
PROCESSED_DOCS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "documents")
OUTPUT_CHUNKS_FILE = os.path.join(PROCESSED_DOCS_DIR, "chunks.json")

# Chunking Strategy Configuration & Rationale:
# ----------------------------------------------------
# CHUNK_SIZE = 500 characters (~100-120 words / ~130 tokens)
# CHUNK_OVERLAP = 100 characters (~20% overlap)
#
# Rationale:
# 1. Optimal Embedding Window: Models like BAAI/bge-base-en-v1.5 and sentence-transformers/all-MiniLM-L6-v2
#    have optimal context windows around 256–512 tokens. A 500-character chunk ensures tight, high-density
#    semantic representations without diluting vector similarity.
# 2. Paragraph Integrity: Energy conservation tips and academic abstracts consist of concise bullet points
#    and short paragraphs. 500 characters captures 1-2 complete points.
# 3. 20% Overlap (100 chars): Prevents context fragmentation across boundaries (e.g., splitting a sentence
#    about "motion sensors" or "energy conserving chairs").

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def create_and_save_chunks():
    print("📥 Loading documents for chunking...")
    documents = load_all_documents()

    if not documents:
        print("❌ No documents found to chunk.")
        return []

    print(f"\n✂️ Initializing RecursiveCharacterTextSplitter...")
    print(f"   • Chunk Size: {CHUNK_SIZE} chars")
    print(f"   • Chunk Overlap: {CHUNK_OVERLAP} chars")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    total_chunks = len(chunks)
    total_chars = sum(len(c.page_content) for c in chunks)
    avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0

    print("\n" + "=" * 50)
    print("📊 CHUNKING RESULTS SUMMARY")
    print("=" * 50)
    print(f" Total Chunks Generated: {total_chunks}")
    print(f"📏 Average Chunk Size:   {avg_chunk_size:.1f} characters")
    print("=" * 50)

    # Preview sample chunk
    if chunks:
        print("\n🔍 SAMPLE CHUNK PREVIEW:")
        sample = chunks[0]
        print(f"Source File: {sample.metadata.get('file_name')} | Type: {sample.metadata.get('file_type')}")
        print("-" * 50)
        print(sample.page_content)
        print("-" * 50)

    # Ensure output directory exists
    os.makedirs(PROCESSED_DOCS_DIR, exist_ok=True)

    # Save chunks as serializable JSON list of dicts
    serializable_chunks = [
        {
            "id": i,
            "page_content": c.page_content,
            "metadata": c.metadata
        }
        for i, c in enumerate(chunks)
    ]

    with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved {total_chunks} chunks successfully to: {OUTPUT_CHUNKS_FILE}")
    return chunks

if __name__ == "__main__":
    create_and_save_chunks()
