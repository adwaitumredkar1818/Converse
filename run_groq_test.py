import time
import sys

from scripts.pipeline import answer
from scripts.generate_response import generate_answer

query = "What is the average energy consumption in winter and summer?"

print("======================================")
print(f"TEST QUERY: {query}")

t_start = time.time()
res = answer(query)
t_end = time.time()

cat = res.get('category', 'unknown')
prov = res.get('provider', 'unknown')
model = res.get('model', 'unknown')
lats = res.get('latencies_ms', {})
fallback_reason = res.get('fallback_reason', 'None')

print(f"Router: {lats.get('router', 0)} ms")
print(f"Document Retrieval: {lats.get('document_retrieval', 0)} ms")
print(f"Tabular Retrieval: {lats.get('tabular_retrieval', 0)} ms")
print(f"LLM Latency: {lats.get('llm_generation', 0)} ms")
print(f"Total Latency: {lats.get('end_to_end', 0)} ms")
print(f"Provider: {prov}")
print(f"Model: {model}")
print(f"Category: {cat}")
print(f"Answer snippet: {res.get('answer', '')[:100]}...")

