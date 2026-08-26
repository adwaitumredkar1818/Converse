import os
import sys
import time
import json
import traceback
from dotenv import load_dotenv

# Initialize results
results = {
    "environment": {},
    "embedding": {},
    "chromadb": {},
    "small_queries": [],
    "large_queries": [],
    "anti_hallucination": [],
    "router": [],
    "tabular": {}
}

# 1. ENVIRONMENT TEST
print("Running Environment Test...")
load_dotenv()
env_vars = ["GROQ_API_KEY", "OPENROUTER_API_KEY"]
for v in env_vars:
    results["environment"][v] = "PASS" if os.getenv(v) else "FAIL"

files_to_check = [
    "data/processed/tables/analytical_dataset.csv",
    "data/processed/documents/chunks.json",
    "data/processed/documents/embeddings.pkl",
    "vector_db"
]
json_files = [
    "seasonal_stats.json", "consumption_stats.json", "weather_stats.json",
    "tariff_stats.json", "household_stats.json", "acorn_stats.json", "holiday_stats.json"
]
for jf in json_files:
    files_to_check.append(f"data/processed/metrics/{jf}")

for f in files_to_check:
    results["environment"][f] = "PASS" if os.path.exists(f) else "FAIL"

# 2. EMBEDDING TEST
print("Running Embedding Test...")
try:
    from scripts.retrieve_documents import get_resources
    t0 = time.time()
    model, col = get_resources()
    load_time = time.time() - t0
    emb = model.encode(["test"])
    dim = len(emb[0])
    results["embedding"] = {
        "status": "PASS",
        "dimension": dim,
        "load_time_ms": round(load_time * 1000, 2)
    }
except Exception as e:
    results["embedding"] = {"status": "FAIL", "error": str(e)}

# 3. CHROMADB TEST
print("Running ChromaDB Test...")
try:
    count = col.count()
    results["chromadb"] = {
        "status": "PASS",
        "vector_count": count,
        "queries": []
    }
    
    test_queries = [
        "energy conservation methods",
        "household demographics",
        "temperature effects",
        "smart meters",
        "tariffs"
    ]
    for q in test_queries:
        q_emb = model.encode([q]).tolist()
        t0 = time.time()
        res = col.query(query_embeddings=q_emb, n_results=5, include=["documents", "distances", "metadatas"])
        latency = time.time() - t0
        
        distances = res["distances"][0]
        sims = [max(0.0, 1.0 - d) for d in distances]
        results["chromadb"]["queries"].append({
            "query": q,
            "top_cosine": round(sims[0], 4) if sims else 0,
            "avg_cosine": round(sum(sims)/len(sims), 4) if sims else 0,
            "latency_ms": round(latency * 1000, 2),
            "top_chunk_id": res["ids"][0][0] if res["ids"] and res["ids"][0] else None,
            "top_source": res["metadatas"][0][0].get("file_name") if res["metadatas"] and res["metadatas"][0] else None
        })
except Exception as e:
    results["chromadb"] = {"status": "FAIL", "error": str(e)}

# Load Pipeline
print("Loading Pipeline...")
from scripts.pipeline import answer

def run_query_test(q_list, test_category):
    for q in q_list:
        print(f"Running query: {q}")
        t0 = time.time()
        try:
            res = answer(q)
            res["actual_latency_ms"] = round((time.time() - t0) * 1000, 2)
            results[test_category].append(res)
        except Exception as e:
            results[test_category].append({"query": q, "error": str(e)})

# 4. SMALL QUERIES
print("Running Small Queries...")
small_qs = [
    "What is the average energy consumption in winter?",
    "What is the average energy consumption in summer?",
    "How does temperature affect energy consumption?",
    "Which season has the highest consumption?",
    "What is the temperature-energy correlation?"
]
run_query_test(small_qs, "small_queries")

# 5. LARGE QUERIES
print("Running Large Queries...")
large_qs = [
    "Using the available London energy data, explain the relationship between temperature and household energy consumption, identify which season has the highest and lowest average daily consumption, compare the available tariff consumption values, and explain whether the provided data gives enough evidence to conclude that household characteristics influence energy usage.",
    "Analyze the available London energy dataset and explain how seasonal consumption differs between winter, spring, summer, and autumn. Include the temperature-energy correlation, compare Standard and ToU tariff consumption, and mention any household ACORN information available in the dataset. Clearly distinguish between facts directly supported by the data and conclusions that cannot be established from the available evidence.",
    "Based only on the available data and documents, provide a comprehensive analysis of London's household energy consumption patterns, including seasonal trends, temperature relationship, tariff differences, household characteristics, and supporting document evidence. Do not introduce external facts or predictions."
]
run_query_test(large_qs, "large_queries")

# 6. ANTI-HALLUCINATION
print("Running Anti-Hallucination Tests...")
ah_qs = [
    "What will London's electricity consumption be tomorrow?",
    "What is the electricity price per kWh tomorrow?",
    "How much energy will each household consume next year?",
    "What will the weather be in London next month?",
    "Who will have the highest electricity consumption tomorrow?"
]
run_query_test(ah_qs, "anti_hallucination")

# 7. ROUTER TEST
print("Running Router Test...")
router_qs = {
    "How can households reduce energy conservation methods?": "document",
    "What is the average temperature?": "weather",
    "How many households are in the dataset?": "household",
    "What is the average winter consumption?": "consumption",
    "How does temperature affect winter energy consumption?": "hybrid"
}
try:
    from scripts.query_router import route_query
    for q, expected in router_qs.items():
        res = route_query(q)
        actual_cat = res["category"]
        results["router"].append({
            "query": q,
            "expected": expected,
            "actual": actual_cat,
            "pass": actual_cat == expected
        })
except Exception as e:
    results["router"].append({"error": str(e)})

# 8. TABULAR RETRIEVAL TEST
print("Running Tabular Retrieval Test...")
try:
    from scripts.load_tables import get_tabular_context
    t0 = time.time()
    tab_res = get_tabular_context("consumption")
    latency = time.time() - t0
    context_str = tab_res.get("context", "")
    results["tabular"]["consumption"] = {
        "status": "PASS" if "consumption" in context_str.lower() else "FAIL",
        "latency_ms": round(latency * 1000, 2)
    }
except Exception as e:
    results["tabular"]["error"] = str(e)

# Output results
with open("audit_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Audit complete.")
