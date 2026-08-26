import time
from scripts.pipeline import answer

queries = [
    "How does temperature affect energy consumption?",
    "How does the energy conserving chair work?",
    "Using the available London energy consumption, household demographic, and weather data, explain how weather conditions, particularly temperature, are related to household electricity consumption. Discuss the temperature-energy correlation, its strength, seasonal patterns if available, and whether household characteristics or tariffs may also influence consumption. Use only available evidence and do not make predictions."
]

for i, q in enumerate(queries):
    print(f"\n--- QUERY {i} ---")
    res = answer(q)
    print(f"Provider: {res['provider']}")
    print(f"LLM Latency: {res['latencies_ms']['llm_generation']} ms")
    print(f"Total Latency: {res['latencies_ms']['end_to_end']} ms")
    print(f"Answer snippet: {res['answer'][:100]}...")
