# llm_interface/ollama_client.py
import requests
import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://150.1.7.227:11555")
MODEL_NAME = "mistral"

def query_ollama(prompt: str):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "[No response from model]")
    except Exception as e:
        return f"⚠️ LLM error: {e}"
