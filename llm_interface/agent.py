# llm_interface/agent.py
import os
import json
import requests
from typing import Dict, Any, List
from llm_interface.ollama_client import chat_with_tools, extract_tool_calls, assistant_text

PENTEST_API = os.environ.get("PENTEST_API", "http://127.0.0.1:8000")
MCP_URL = f"{PENTEST_API}/mcp"
MANIFEST_URL = f"{PENTEST_API}/manifest.json"

SYSTEM_PROMPT = """
You are the Pentest MCP Agent.

TOOLS USAGE RULES (very important):
- When a tool is available that can help, you MUST invoke it using the function-calling interface (tool_calls).
- Do NOT print function calls in plain text. Do NOT wrap them in backticks. Do NOT return arrays or pseudo-code.
- If you call a tool, your assistant message MUST have an empty 'content' and exactly one tool call with JSON arguments.
- Only if NO tool can help should you answer in plain text.

For Nmap:
- Tool name: nmap_scan
- Arguments schema:
  - target: string (IP/host or CIDR)  [required]
  - flags:  array of strings you choose from this whitelist only:
            -T0 -T1 -T2 -T3 -T4 -T5, -F, -O, -sV, -sC, -sU, -p-, -Pn, -n
            (If ports are specified, include exactly one -p* like -p22,80 or -p1-1024.)

Mapping guidance:
- "quick/fast" → include -T4 and -F
- "all ports/full" → include -p-
- "no ping" → include -Pn
- "no DNS" → include -n
- "service versions / enumerate services" → include -sV (and often -sC)
- "OS detection" → include -O
- "UDP" → include -sU

When using a tool, DO NOT add any natural-language content to that assistant message.
"""

def _load_tools() -> List[Dict[str, Any]]:
    r = requests.get(MANIFEST_URL, timeout=10)
    r.raise_for_status()
    mani = r.json()
    return mani.get("tools", [])

def _call_mcp(method: str, params: Dict[str, Any], call_id: str):
    """
    Execute a tool via /mcp and return (ok, text_result_json).
    """
    body = {"jsonrpc": "2.0", "id": call_id, "method": method, "params": params}
    r = requests.post(MCP_URL, json=body, timeout=180)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        return False, json.dumps({"error": data["error"]})
    return True, json.dumps(data.get("result", {}))

def main():
    print("🔮 LLM Agent (Ollama + MCP tools)\n")
    tools = _load_tools()

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                break

            messages.append({"role": "user", "content": user_input})

            # Ask model (with tools)
            resp = chat_with_tools(messages, tools)
            messages.append(resp.get("message", {"role": "assistant", "content": ""}))

            # Resolve tool calls (up to 3 rounds)
            tool_calls = extract_tool_calls(resp)
            loop_guard = 0
            while tool_calls and loop_guard < 3:
                loop_guard += 1
                for tc in tool_calls:
                    fn = (tc.get("function") or {})
                    name = fn.get("name", "")
                    args_raw = fn.get("arguments", "{}")
                    try:
                        args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
                    except json.JSONDecodeError:
                        args = {}

                    ok, result_text = _call_mcp(name, args, tc.get("id", "call-0"))

                    messages.append({
                        "role": "tool",
                        "content": result_text,
                        "tool_call_id": tc.get("id", "call-0")
                    })

                # Let the model continue with tool outputs
                resp = chat_with_tools(messages, tools)
                messages.append(resp.get("message", {"role": "assistant", "content": ""}))
                tool_calls = extract_tool_calls(resp)

            # Print final assistant answer
            final = assistant_text(resp)
            print(f"\n🤖 LLM: {final}\n")

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
