import time
import sys

print("Loading pipeline...", flush=True)
t0 = time.time()
from scripts.pipeline import answer
print(f"Pipeline module loaded in {time.time() - t0:.2f}s", flush=True)

queries = [
    "How does temperature affect energy consumption?",
    "How does temperature affect energy consumption?",
    "How does the energy conserving chair work?",
    "Using the available London energy consumption, household demographic, and weather data, explain the relationship between temperature and electricity consumption. Include the correlation, seasonal patterns, and any available household or tariff evidence. Only use information supported by the available data.",
    "What will tomorrow's energy consumption be?"
]

for i, q in enumerate(queries):
    print(f"\n======================================")
    if i == 0:
        print(f"TEST 1: COLD START QUERY")
    elif i == 1:
        print(f"TEST 2: WARM IDENTICAL QUERY")
    else:
        print(f"TEST {i+1}: QUERY {i}")
    print(f"Q: {q}")
    
    t_start = time.time()
    res = answer(q)
    t_end = time.time()
    
    cat = res.get('category', 'unknown')
    prov = res.get('provider', 'unknown')
    lats = res.get('latencies_ms', {})
    
    print(f"Router: {lats.get('router', 0)} ms")
    print(f"Document Retrieval: {lats.get('document_retrieval', 0)} ms")
    print(f"Tabular Retrieval: {lats.get('tabular_retrieval', 0)} ms")
    print(f"LLM: {lats.get('llm_generation', 0)} ms")
    print(f"Total: {lats.get('end_to_end', 0)} ms")
    print(f"Provider: {prov}")
    print(f"Category: {cat}")
    print(f"Answer snippet: {res.get('answer', '')[:100]}...")

