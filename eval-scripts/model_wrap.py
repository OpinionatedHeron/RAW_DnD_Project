# Allows all models to be used in the same way for evaluation
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

import time
import os

# Importing Antrhopic - will be using Clade Opus 4.6 for evaluation
import anthropic

# Importing OpenAI - will be using GPT-5.4 for evaluation
from openai import OpenAI

"""
# Importing Google GenAI - will be using Gemini 3.1 Pro Preview for evaluation
from google import genai
from google.genai import types
"""

# Cost Per 1 Million Tokens in USD according to model pricing site as of March 2026
PRICING = {
    "claude-opus-4-6": {"input": 5.00, "output": 25.00},
    "gpt-5.4": {"input": 2.50, "output": 15.00},
    "gemini-3.1-pro-preview": {"input": 4.00, "output": 18.00},
}


def call_gpt(prompt: str, system: str = "") -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    start = time.time()
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=500,  # Adjust as needed
        temperature=0.3,  # Adjust as needed - lower is more factual, higher is more creative
    )
    latency = (time.time() - start) * 1000  # Convert to milliseconds
    usage = response.usage
    price = PRICING["gpt-5.4"]
    cost = (
        usage.prompt_tokens * price["input"] + usage.completion_tokens * price["output"]
    ) / 1_000_000
    return {
        "answer": response.choices[0].message.content,
        "finish_reason": response.choices[0].finish_reason,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "latency_ms": round(latency, 1),
        "cost": round(cost, 6),
    }


def call_claude(prompt: str, system: str = "") -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    start = time.time()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,  # Adjust as needed
        temperature=0.3,  # Adjust as needed
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = (time.time() - start) * 1000
    usage = response.usage
    price = PRICING["claude-opus-4-6"]
    cost = (
        usage.input_tokens * price["input"] + usage.output_tokens * price["output"]
    ) / 1_000_000
    return {
        "answer": response.content[0].text,
        "finish_reason": response.stop_reason,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "latency_ms": round(latency, 1),
        "cost": round(cost, 6),
    }


"""
Commenting out due to rate limit issues with Gemini Pro Preview - would not be able to set rate limit high enough to run all evaluations

def call_gemini(prompt: str, system: str = "") -> dict:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    start = time.time()
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=500,  # Adjust as needed
            temperature=0.3,  # Adjust as needed
        ),
    )
    latency = (time.time() - start) * 1000
    meta = response.usage_metadata
    price = PRICING["gemini-3.1-pro-preview"]
    cost = (
        meta.prompt_token_count * price["input"]
        + meta.candidates_token_count * price["output"]
    ) / 1_000_000
    return {
        "answer": response.text,
        "finish_reason": response.candidates[0].finish_reason,
        "input_tokens": meta.prompt_token_count,
        "output_tokens": meta.candidates_token_count,
        "latency_ms": round(latency, 1),
        "cost": round(cost, 6),
    }
"""
