import os
import sys
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DOCS_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "documents")

def load_all_documents(docs_dir: str = DOCS_DIR):
    """
    Loads all PDF and TXT documents from the specified directory
    and attaches standard metadata (source, file_name, file_type).
    """
    all_documents = []

    if not os.path.exists(docs_dir):
        print(f"❌ Directory {docs_dir} does not exist.")
        return all_documents

    for file_name in os.listdir(docs_dir):
        file_path = os.path.join(docs_dir, file_name)

        if file_name.startswith("."):
            continue

        if file_name.endswith(".pdf"):
            print(f"📄 Loading PDF document: {file_name}...")
            loader = PyPDFLoader(file_path)
            pdf_docs = loader.load()
            for doc in pdf_docs:
                doc.metadata["file_name"] = file_name
                doc.metadata["file_type"] = "pdf"
            all_documents.extend(pdf_docs)

        elif file_name.endswith(".txt"):
            print(f"📝 Loading TXT document: {file_name}...")
            loader = TextLoader(file_path, encoding="utf-8")
            txt_docs = loader.load()
            for doc in txt_docs:
                doc.metadata["file_name"] = file_name
                doc.metadata["file_type"] = "txt"
            all_documents.extend(txt_docs)

    return all_documents

if __name__ == "__main__":
    docs = load_all_documents()
    print("\n" + "=" * 50)
    print(f"✅ Successfully loaded {len(docs)} document page/section items.")
    print("=" * 50)
    
    if docs:
        print("\n🔍 Sample Document Preview:")
        print(f"Source: {docs[0].metadata.get('file_name')} | Type: {docs[0].metadata.get('file_type')}")
        print("-" * 50)
        print(docs[0].page_content[:400] + "...")
