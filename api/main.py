from fastapi import FastAPI, Request
from tools.nmap_runner import run_nmap
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

    return {"error": "Unknown method", "id": job_id}