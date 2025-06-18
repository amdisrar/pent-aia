# api/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/manifest.json")
def manifest():
    return {"name": "Pentest AI", "tools": []}
