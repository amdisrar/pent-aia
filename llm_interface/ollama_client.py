# llm_interface/ollama_client.py
import os
import requests
from typing import List, Dict, Any, Optional

# Ollama default is 11434; override with OLLAMA_HOST if needed
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://150.1.7.227:11434")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "mistral")

def _to_ollama_tools(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert /manifest.json tools to Ollama's 'tools' schema.
    """
    out: List[Dict[str, Any]] = []
    for t in mcp_tools:
        out.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}})
            }
        })
    return out

def chat_with_tools(messages: List[Dict[str, Any]],
                    mcp_tools: Optional[List[Dict[str, Any]]] = None,
                    timeout: int = 60) -> Dict[str, Any]:
    """
    Single-turn chat with optional tools enabled.
    """
    payload: Dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }
    if mcp_tools:
        payload["tools"] = _to_ollama_tools(mcp_tools)

    r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def extract_tool_calls(resp: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize tool calls from Ollama.
    """
    msg = resp.get("message") or {}
    return msg.get("tool_calls") or msg.get("toolCalls") or []

def assistant_text(resp: Dict[str, Any]) -> str:
    msg = resp.get("message") or {}
    return msg.get("content", "") or ""
