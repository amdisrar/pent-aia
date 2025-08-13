# main.py
from fastapi import FastAPI, Request
from typing import Any, Dict
from dotenv import load_dotenv

from tools.nmap_runner import run_nmap
from tools.msf_runner import (
    run_msf_module,
    search_msf_modules,
    exploit_with_payload,
    interact_session,
    list_sessions,
)

load_dotenv()
app = FastAPI()

# Whitelist guardrails for Nmap
ALLOWED_NMAP_FLAGS = {
    "-T0","-T1","-T2","-T3","-T4","-T5",
    "-F","-O","-sV","-sC","-sU","-p-","-Pn","-n"
}

@app.get("/manifest.json")
def manifest():
    return {
        "schema_version": "1.0",
        "name": "pentest-ai-mcp",
        "description": "Pentest tools exposed via MCP-style JSON-RPC over HTTP.",
        "tools": [
            {
                "name": "nmap_scan",
                "description": (
                    "LLM should translate natural language into Nmap flags and call this tool. "
                    "Use ONLY flags from the whitelist: -T0..-T5, -F, -O, -sV, -sC, -sU, -p-, -Pn, -n. "
                    "If ports are specified, include exactly one -p* like -p22,80 or -p1-1024."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "IP/host or CIDR"},
                        "flags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Model-selected Nmap flags from whitelist (optionally one -p*)."
                        }
                    },
                    "required": ["target"],
                    "additionalProperties": False
                }
            },
            {
                "name": "msf_run_module",
                "description": "Run a Metasploit module with given arguments.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "module_type": {"type": "string", "enum": ["auxiliary", "exploit", "post", "encoder", "nop", "payload"]},
                        "module_name": {"type": "string"},
                        "module_args": {"type": "object", "additionalProperties": True}
                    },
                    "required": ["module_type", "module_name"]
                }
            },
            {
                "name": "msf_search",
                "description": "Search Metasploit modules by keyword.",
                "input_schema": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string"}},
                    "required": ["keyword"]
                }
            },
            {
                "name": "msf_exploit",
                "description": "Run an exploit with a payload and arguments.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "exploit_name": {"type": "string"},
                        "payload_name": {"type": "string"},
                        "exploit_args": {"type": "object", "additionalProperties": True},
                        "payload_args": {"type": "object", "additionalProperties": True}
                    },
                    "required": ["exploit_name", "payload_name"]
                }
            },
            {
                "name": "msf_sessions",
                "description": "List active Metasploit sessions.",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "msf_session_cmd",
                "description": "Send a command to a Metasploit session.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "integer"},
                        "command": {"type": "string"}
                    },
                    "required": ["session_id", "command"]
                }
            }
        ]
    }

def _jsonrpc_result(result: Any, id_: Any):
    return {"jsonrpc": "2.0", "id": id_, "result": result}

def _jsonrpc_error(msg: str, id_: Any):
    return {"jsonrpc": "2.0", "id": id_, "error": msg}

@app.post("/mcp")
async def mcp(req: Request):
    body: Dict[str, Any] = await req.json()
    method = body.get("method")
    params = body.get("params", {}) or {}
    job_id = body.get("id", "n/a")

    try:
        if method == "nmap_scan":
            target = params.get("target")
            flags  = params.get("flags", []) or []
            if not target:
                return _jsonrpc_error("Missing target", job_id)

            # Validate flags: whitelist + allow a single -p*
            sanitized = []
            p_seen = False
            for f in flags:
                if isinstance(f, str) and (f in ALLOWED_NMAP_FLAGS or f.startswith("-p")):
                    if f.startswith("-p"):
                        if p_seen:
                            continue
                        p_seen = True
                    sanitized.append(f)

            # Safe defaults if model didn't supply any flags
            if not sanitized:
                sanitized = ["-T4", "-F"]

            output = run_nmap(target, sanitized)
            return _jsonrpc_result({"target": target, "flags": sanitized, "output": output}, job_id)

        elif method == "msf_run_module":
            module_type = params.get("module_type")
            module_name = params.get("module_name")
            module_args = params.get("module_args", {}) or {}
            if not module_type or not module_name:
                return _jsonrpc_error("Missing module_type or module_name", job_id)
            res = run_msf_module(module_type, module_name, module_args)
            return _jsonrpc_result(res, job_id)

        elif method == "msf_search":
            keyword = params.get("keyword", "")
            res = search_msf_modules(keyword)
            return _jsonrpc_result(res, job_id)

        elif method == "msf_exploit":
            exploit_name = params.get("exploit_name")
            payload_name = params.get("payload_name")
            exploit_args = params.get("exploit_args", {}) or {}
            payload_args = params.get("payload_args", {}) or {}
            if not exploit_name or not payload_name:
                return _jsonrpc_error("Missing exploit_name or payload_name", job_id)
            res = exploit_with_payload(exploit_name, payload_name, exploit_args, payload_args)
            return _jsonrpc_result(res, job_id)

        elif method == "msf_sessions":
            res = list_sessions()
            return _jsonrpc_result(res, job_id)

        elif method == "msf_session_cmd":
            session_id = params.get("session_id")
            command = params.get("command")
            if session_id is None or not command:
                return _jsonrpc_error("Missing session_id or command", job_id)
            res = interact_session(session_id, command)
            return _jsonrpc_result(res, job_id)

        else:
            return _jsonrpc_error("Unknown method", job_id)

    except Exception as e:
        return _jsonrpc_error(str(e), job_id)
