"""
DP-700 Exam Prep — LiteLLM Engine
Handles model routing between Gemini and Groq with auto-fallback.
"""

import os
import json
import litellm
from dotenv import load_dotenv

load_dotenv()

# Suppress LiteLLM debug logs
litellm.suppress_debug_info = True
litellm.set_verbose = False

# ---------------------------------------------------------------------------
# Model configs
# ---------------------------------------------------------------------------

MODELS = {
    "gemini": {
        "name": "gemini/gemini-2.0-flash",
        "display": "Gemini 2.0 Flash ⚡",
        "provider": "Google",
        "icon": "✨",
    },
    "groq": {
        "name": "groq/llama-3.3-70b-versatile",
        "display": "Llama 3.3 70B (Groq) 🚀",
        "provider": "Groq",
        "icon": "🚀",
    },
    "nvidia_nim": {
        "name": "nvidia_nim/meta/llama-3.1-70b-instruct",
        "display": "Llama 3.1 70B (NVIDIA NIM) 🟢",
        "provider": "NVIDIA",
        "icon": "🟢",
    },
}

DEFAULT_MODEL = "gemini"
FALLBACK_MODEL = "groq"


def _ensure_keys():
    """Set API keys from environment or Streamlit secrets."""
    try:
        import streamlit as st
        if not os.environ.get("GEMINI_API_KEY") and hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
            if "GROQ_API_KEY" in st.secrets:
                os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
            if "NVIDIA_NIM_API_KEY" in st.secrets:
                os.environ["NVIDIA_NIM_API_KEY"] = st.secrets["NVIDIA_NIM_API_KEY"]
    except Exception:
        pass


def check_api_keys():
    """Check which API keys are configured."""
    _ensure_keys()
    return {
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
        "groq": bool(os.environ.get("GROQ_API_KEY")),
        "nvidia_nim": bool(os.environ.get("NVIDIA_NIM_API_KEY")),
    }


def chat_completion(messages: list, model_key: str = None, temperature: float = 0.7,
                    max_tokens: int = 2048) -> dict:
    """
    Send a chat completion request via LiteLLM.
    Auto-falls back to the other model if the primary fails.

    Returns: {"content": str, "model_used": str, "model_key": str}
    """
    _ensure_keys()

    model_key = model_key or DEFAULT_MODEL
    primary = MODELS[model_key]["name"]
    fallback_key = FALLBACK_MODEL if model_key == DEFAULT_MODEL else DEFAULT_MODEL
    fallback = MODELS[fallback_key]["name"]

    # Try primary model
    try:
        response = litellm.completion(
            model=primary,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "content": response.choices[0].message.content,
            "model_used": MODELS[model_key]["display"],
            "model_key": model_key,
        }
    except Exception as e:
        print(f"[LLM] Primary model {primary} failed: {e}")

    # Try fallback
    try:
        response = litellm.completion(
            model=fallback,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "content": response.choices[0].message.content,
            "model_used": MODELS[fallback_key]["display"] + " (fallback)",
            "model_key": fallback_key,
        }
    except Exception as e2:
        print(f"[LLM] Fallback model {fallback} also failed: {e2}")
        return {
            "content": f"😵 Both models are down right now, fam. Error: {e2}\n\nMake sure your API keys are set in the ⚙️ Settings page!",
            "model_used": "none",
            "model_key": "error",
        }


def generate_quiz_json(prompt: str, model_key: str = None) -> list:
    """
    Generate quiz questions and parse the JSON response.
    Falls back gracefully if JSON parsing fails.
    """
    result = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_key=model_key,
        temperature=0.4,
        max_tokens=4096,
    )
    content = result["content"]

    # Try to extract JSON from the response
    try:
        # Remove markdown code fences if present
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last lines (``` markers)
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            cleaned = cleaned.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON array in the response
        import re
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []


def analyze_weaknesses(prompt: str, model_key: str = None) -> list:
    """Analyze weaknesses and return parsed JSON."""
    result = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_key=model_key,
        temperature=0.3,
        max_tokens=2048,
    )
    content = result["content"]
    try:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        return []
