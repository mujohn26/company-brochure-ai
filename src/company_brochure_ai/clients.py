"""
LLM clients for every supported model.

All providers expose an OpenAI-compatible API, so a single OpenAI client
class works for each of them; only the base URL, key and model name change.
Clients are created on demand, so a missing key for one provider
doesn't stop the others from working.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

# Display name in the UI -> provider settings
MODELS = {
    "GPT": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "model": "openai/gpt-oss-120b",
    },
    "OLLAMA": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "api_key_env": None,  # local Ollama doesn't need a key
        "model": "llama3.2",
    },
}


def get_model(name):
    """Return (client, model_name) for a model listed in MODELS."""
    if name not in MODELS:
        raise ValueError(f"Unknown model '{name}'. Choose one of: {', '.join(MODELS)}")

    config = MODELS[name]
    if config["api_key_env"]:
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            raise ValueError(f"{config['api_key_env']} is not set. Add it to your .env file.")
    else:
        api_key = "ollama"  # any non-empty string works for Ollama

    client = OpenAI(api_key=api_key, base_url=config["base_url"])
    return client, config["model"]