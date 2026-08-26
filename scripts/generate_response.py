import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

SYSTEM_PROMPT = """You are an energy analytics assistant.

Answer the question using the supplied context.

If the user asks about a topic (such as energy conservation) with a specific location (e.g., London) but the context provides general energy principles, strategies, or document excerpts on that topic, summarize the relevant information from the context and note that it covers general principles.

Only if the context contains NO relevant information whatsoever, state:
'I don't have enough information in the available data.'

Never invent facts. Always cite the sources from the context."""

# Model Names
GROQ_MODEL = "openai/gpt-oss-120b"
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"

def call_groq(messages: list) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment.")
    client = Groq(api_key=api_key, max_retries=0, timeout=12.0)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024
    )
    content = response.choices[0].message.content
    if (content is None or content.strip() == "") and hasattr(response.choices[0].message, "reasoning") and response.choices[0].message.reasoning:
        content = response.choices[0].message.reasoning
    return content or ""

def call_openrouter(messages: list) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from environment.")
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        max_retries=0,
        timeout=15.0
    )
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024
    )
    return response.choices[0].message.content

def generate_answer(query: str, document_context: str = "", tabular_context: str = "") -> dict:
    """
    Generates an anti-hallucinated response using Groq as primary LLM,
    with automatic failover to OpenRouter.
    """
    start_time = time.time()

    # Combine context
    combined_context_parts = []
    if document_context.strip():
        combined_context_parts.append(f"--- DOCUMENT CONTEXT ---\n{document_context.strip()}")
    if tabular_context.strip():
        combined_context_parts.append(f"--- TABULAR / METRICS CONTEXT ---\n{tabular_context.strip()}")

    combined_context = "\n\n".join(combined_context_parts) if combined_context_parts else "No relevant context available."

    user_content = f"""CONTEXT:
{combined_context}

USER QUESTION:
{query}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    llm_provider = "Groq"
    model_used = GROQ_MODEL
    fallback_reason = None

    try:
        # 1. Primary: Call Groq
        answer = call_groq(messages)
    except Exception as e_groq:
        fallback_reason = str(e_groq)
        print(f"⚠️ Groq call failed ({e_groq}). Falling back to OpenRouter...")
        llm_provider = "OpenRouter (Fallback)"
        model_used = OPENROUTER_MODEL
        try:
            # 2. Fallback: Call OpenRouter
            answer = call_openrouter(messages)
        except Exception as e_openrouter:
            answer = f"Error generating answer: Groq ({e_groq}), OpenRouter ({e_openrouter})."
            llm_provider = "Failed"

    elapsed_time = time.time() - start_time

    return {
        "query": query,
        "answer": answer,
        "provider": llm_provider,
        "model": model_used,
        "latency_ms": round(elapsed_time * 1000, 2),
        "context_used": combined_context,
        "fallback_reason": str(fallback_reason)
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 TESTING LLM GENERATION LAYER (generate_response.py)")
    print("=" * 60)

    sample_doc_ctx = "Energy conservation refers to efforts made to reduce energy consumption. Ashvin Madanlal Maheshwari authored research on energy conserving chairs."
    sample_tab_ctx = "Total London households: 5566. Mean daily energy consumption: 10.52 kWh."
    sample_q = "Who authored the research on energy conserving chairs, and what is the total London household count?"

    res = generate_answer(sample_q, document_context=sample_doc_ctx, tabular_context=sample_tab_ctx)

    print(f"Query:    '{res['query']}'")
    print(f"Provider:  {res['provider']} ({res['model']})")
    print(f"Latency:   {res['latency_ms']} ms")
    print(f"\nGenerated Answer:\n{res['answer']}")
    print("=" * 60)
