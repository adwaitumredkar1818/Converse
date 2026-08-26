import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Rule-Based Keyword Dictionaries
KEYWORDS = {
    "document": [
        "energy conservation", "lighting", "hvac", "air conditioner", 
        "refrigerator", "computer", "microwave", "industrial energy", 
        "energy saving", "paper", "author", "chair", "research", 
        "abstract", "jetir", "insulation", "tips", "sensor",
        "appliance", "efficiency guide", "methods for energy conservation"
    ],
    "weather": [
        "temperature", "humidity", "rain", "rainy", "wind", "weather",
        "climate", "precipitation", "overcast", "dew", "pressure",
        "snow", "cloud", "darksky", "temp", "cold", "hot", "warm"
    ],
    "household": [
        "household", "acorn", "tariff", "tariffs", "consumer", "customer",
        "tou", "std", "lclid", "demographic", "cluster", "affluent",
        "adversity", "comfortable", "time-of-use", "standard tariff"
    ],
    "consumption": [
        "energy consumption", "electricity usage", "power usage", 
        "peak usage", "daily consumption", "kwh", "kw", "median", 
        "total energy", "aggregate", "trend", "usage", "maximum energy",
        "consumption", "electricity", "power", "energy usage", "daily energy",
        "average energy", "max energy", "min energy", "percentile",
        "season", "seasonal", "winter", "summer", "spring", "autumn",
        "holiday", "bank holiday", "christmas", "new year", "boxing day", "easter"
    ]
}

def route_query(query: str) -> dict:
    """
    Classifies an incoming user query into one of five categories:
    1. document
    2. weather
    3. household
    4. consumption
    5. hybrid (if matching multiple categories)
    """
    query_lower = query.lower()
    matched_categories = []

    for category, keywords in KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            matched_categories.append(category)

    # Classification logic
    if len(matched_categories) > 1:
        chosen_category = "hybrid"
    elif len(matched_categories) == 1:
        chosen_category = matched_categories[0]
    else:
        # Default fallback to document QA if no explicit tabular keywords match
        chosen_category = "document"

    return {
        "query": query,
        "category": chosen_category,
        "matched_sources": matched_categories if matched_categories else ["default_document"]
    }

if __name__ == "__main__":
    test_queries = [
        # Document Queries
        "What are the best tips for industrial energy saving?",
        "How does an energy conserving chair work?",
        "Who is the author of the energy paper?",
        "What lighting system recommendations are in the guide?",

        # Weather Queries
        "What was the maximum temperature recorded in London?",
        "How many rainy days were recorded in DarkSky logs?",
        "What was the average daily humidity level?",
        "Show weather climate trends for winter months.",

        # Household Queries
        "How many households are in the ACORN Affluent group?",
        "What is the ratio of ToU to Standard tariff households?",
        "How many total consumers are registered in the dataset?",
        "Show household demographic distribution by cluster.",

        # Consumption Queries
        "What is the average daily consumption in kWh?",
        "Which day had the highest peak usage citywide?",
        "What is the median electricity usage across households?",
        "Show peak electricity usage trends.",

        # Hybrid Queries (Multi-Category)
        "How does daily temperature affect energy consumption for ACORN households?",
        "Do ToU tariff households consume less electricity usage on rainy weather days?",
        "What energy conservation tips apply to households on cold temperature days?",
        "How does wind speed impact daily peak consumption in Affluent households?"
    ]

    print("=" * 70)
    print("🚦 QUERY ROUTER BENCHMARK SUITE (20 TEST QUERIES)")
    print("=" * 70)

    category_counts = {}
    for idx, q in enumerate(test_queries, 1):
        res = route_query(q)
        cat = res["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print(f"[{idx:02d}] Category: {cat.upper():<11} | Query: '{q}'")

    print("\n" + "=" * 70)
    print("📊 ROUTER DISTRIBUTION SUMMARY")
    print("=" * 70)
    for cat, count in category_counts.items():
        print(f"  • {cat.capitalize():<12}: {count} queries")
    print("=" * 70)
