from fastapi import FastAPI, Request
from tools.nmap_runner import run_nmap
from tools.msf_runner import run_msf_module
from tools.msf_runner import search_msf_modules

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/manifest.json")
def manifest():
    return {
        "name": "Pentest AI",
        "tools": [
            {
                "name": "nmap_scan",
                "description": "Run Nmap scan on target with optional safe flags",
                "params": ["target", "options"],
                "allowed_options": ["-T4", "-F", "-O", "-sV", "-sC", "-sU", "-p-", "-p<port>", "-Pn", "-n"]

            }
        ]
    }

@app.post("/mcp")
async def mcp(req: Request):
    body = await req.json()
    method = body.get("method")
    params = body.get("params", {})
    job_id = body.get("id", "n/a")

    if method == "nmap_scan":
        target = params.get("target")
        options = params.get("options", [])
        if not target:
            return {"error": "Missing target", "id": job_id}
        try:
            result = run_nmap(target, options)
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}
        
    elif method == "msf_run_module":
        module_type = params.get("module_type")
        module_name = params.get("module_name")
        module_args = params.get("module_args", {})
        if not module_type or not module_name:
            return {"error": "Missing module_type or module_name", "id": job_id}
        try:
            result = run_msf_module(module_type, module_name, module_args)
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}

    elif method == "msf_search":
        keyword = params.get("keyword", "")
        try:
            result = search_msf_modules(keyword)
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}
        
    elif method == "msf_exploit":
        exploit_name = params.get("exploit_name")
        payload_name = params.get("payload_name")
        exploit_args = params.get("exploit_args", {})
        payload_args = params.get("payload_args", {})
        if not exploit_name or not payload_name:
            return {"error": "Missing exploit_name or payload_name", "id": job_id}
        try:
            result = exploit_with_payload(exploit_name, payload_name, exploit_args, payload_args)
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}

    elif method == "msf_sessions":
        try:
            result = list_sessions()
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}

    elif method == "msf_session_cmd":
        session_id = params.get("session_id")
        command = params.get("command")
        if session_id is None or not command:
            return {"error": "Missing session_id or command", "id": job_id}
        try:
            result = interact_session(session_id, command)
            return {"result": result, "id": job_id}
        except Exception as e:
            return {"error": str(e), "id": job_id}

    return {"error": "Unknown method", "id": job_id}