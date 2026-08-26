import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
for path in [PROJECT_ROOT, SCRIPTS_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    from scripts.query_router import route_query
    from scripts.retrieve_documents import retrieve
    from scripts.load_tables import get_tabular_context
    from scripts.generate_response import generate_answer
except ModuleNotFoundError as e:
    if e.name in ["scripts", "scripts.query_router", "scripts.retrieve_documents", "scripts.load_tables", "scripts.generate_response"]:
        from query_router import route_query
        from retrieve_documents import retrieve
        from load_tables import get_tabular_context
        from generate_response import generate_answer
    else:
        raise e

def answer(query: str) -> dict:
    """
    Complete End-to-End RAG + Tabular Pipeline Execution:
    1. Route query (document, weather, household, consumption, hybrid).
    2. Conditionally retrieve document vector chunks (ChromaDB) and/or tabular context (JSON/DuckDB).
    3. Generate anti-hallucinated response using Groq / OpenRouter failover.
    4. Return final structured dictionary with latency metrics.
    """
    total_start = time.time()

    # 1. Route Query
    t0 = time.time()
    router_res = route_query(query)
    category = router_res["category"]
    router_latency = round((time.time() - t0) * 1000, 2)

    doc_context_str = ""
    tab_context_str = ""
    retrieved_chunks = []
    tabular_metadata = {}
    doc_latency = 0.0
    tab_latency = 0.0

    # 2. Retrieve Document Context (if category is document or hybrid)
    if category in ["document", "hybrid"]:
        t_doc = time.time()
        retrieved_chunks = retrieve(query, top_k=15)
        doc_latency = round((time.time() - t_doc) * 1000, 2)

        doc_parts = []
        for idx, item in enumerate(retrieved_chunks, 1):
            doc_parts.append(
                f"[{idx}] Source: {item['metadata'].get('file_name')} (Page {item['metadata'].get('page', 1)}) | Similarity: {item['similarity_score']}\nText: {item['content']}"
            )
        doc_context_str = "\n\n".join(doc_parts)

    # 3. Retrieve Tabular Context (if category is weather, household, consumption, or hybrid)
    if category in ["weather", "household", "consumption", "hybrid"]:
        t_tab = time.time()
        tabular_metadata = get_tabular_context(query)
        tab_latency = round((time.time() - t_tab) * 1000, 2)
        tab_context_str = tabular_metadata.get("context", "")

    # 4. Generate Answer via LLM
    t_llm = time.time()
    llm_res = generate_answer(query, document_context=doc_context_str, tabular_context=tab_context_str)
    llm_latency = round((time.time() - t_llm) * 1000, 2)

    total_latency = round((time.time() - total_start) * 1000, 2)

    return {
        "query": query,
        "category": category,
        "answer": llm_res["answer"],
        "provider": llm_res["provider"],
        "model": llm_res["model"],
        "latencies_ms": {
            "router": router_latency,
            "document_retrieval": doc_latency,
            "tabular_retrieval": tab_latency,
            "llm_generation": llm_latency,
            "end_to_end": total_latency
        },
        "sources": {
            "document_chunks_count": len(retrieved_chunks),
            "tabular_source": tabular_metadata.get("source", "N/A"),
            "retrieved_chunks": retrieved_chunks
        }
    }
if __name__ == "__main__":

    print("=" * 70)
    print("🚀 Energy Analytics Assistant")
    print("Type 'exit' to quit.")
    print("=" * 70)

    while True:

        query = input("\nAsk a question: ")

        if query.lower() == "exit":
            break

        res = answer(query)

        print("\n" + "=" * 70)
        print(f"Category: {res['category'].upper()}")
        print(f"Provider: {res['provider']}")
        print("-" * 70)
        print(res["answer"])
        print("=" * 70)