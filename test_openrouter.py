from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="meta-llama/llama-3.3-70b-instruct",
    messages=[
        {
            "role": "user",
            "content": "Explain artificial intelligence in simple words."
        }
    ]
)

print(response.choices[0].message.content)