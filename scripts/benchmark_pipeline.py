import os
import sys
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.pipeline import answer

BENCHMARK_QUERIES = [
    # Document Queries
    "What are the main lighting system tips for industrial energy savings?",
    "How does an energy conserving chair work according to research?",
    "Who authored the paper on energy conserving chairs?",
    "What operational changes are recommended for peak demand management?",

    # Weather Queries
    "What was the maximum temperature recorded in London?",
    "How many rainy days were logged in the weather dataset?",
    "What was the average daily relative humidity?",
    "What weather conditions were logged during winter months?",

    # Household Queries
    "How many total households are in the London dataset?",
    "What is the breakdown of Time-of-Use vs Standard tariffs?",
    "Which ACORN demographic group has the most households?",
    "How many households are classified under Adversity?",

    # Consumption Queries
    "What is the average daily household energy consumption in kWh?",
    "Which exact date recorded the highest total citywide energy usage?",
    "What is the 90th percentile daily energy consumption?",
    "What was the peak daily energy consumed across all London households?",

    # Hybrid Queries
    "What energy conservation tips apply to households during cold temperature days?",
    "Do Time-of-Use households consume less energy during peak summer weather?",
    "How does daily temperature correlate with energy usage for Affluent households?",
    "What is the impact of bank holidays and weather on daily energy consumption?"
]

def run_benchmark():
    print("=" * 80)
    print("📊 STARTING AUTOMATED END-TO-END PIPELINE BENCHMARK (20 QUERIES)")
    print("=" * 80)

    results_list = []
    router_latencies = []
    retrieval_latencies = []
    llm_latencies = []
    total_latencies = []

    for idx, q in enumerate(BENCHMARK_QUERIES, 1):
        print(f"\n[{idx:02d}/20] Processing Query: '{q}'...")
        res = answer(q)
        
        lats = res["latencies_ms"]
        router_latencies.append(lats["router"])
        retrieval_latencies.append(max(lats["document_retrieval"], lats["tabular_retrieval"]))
        llm_latencies.append(lats["llm_generation"])
        total_latencies.append(lats["end_to_end"])

        results_list.append(res)
        print(f"     ➔ Category: {res['category'].upper()} | LLM: {res['provider']} | Latency: {lats['end_to_end']} ms")

    avg_router = sum(router_latencies) / len(router_latencies)
    avg_retrieval = sum(retrieval_latencies) / len(retrieval_latencies)
    avg_llm = sum(llm_latencies) / len(llm_latencies)
    avg_total = sum(total_latencies) / len(total_latencies)

    print("\n" + "=" * 80)
    print("📈 END-TO-END PIPELINE BENCHMARK RESULTS")
    print("=" * 80)
    print(f"  • Total Benchmark Queries Tested : {len(BENCHMARK_QUERIES)}")
    print(f"  • Average Router Latency        : {avg_router:.2f} ms")
    print(f"  • Average Retrieval Latency     : {avg_retrieval:.2f} ms")
    print(f"  • Average LLM Latency           : {avg_llm:.2f} ms")
    print(f"  • Average End-to-End Latency    : {avg_total:.2f} ms ({avg_total/1000:.2f} seconds)")
    print("=" * 80)

    return results_list

if __name__ == "__main__":
    run_benchmark()
