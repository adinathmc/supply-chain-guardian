# ================================
# Supply Chain Guardian – Backend
# SAFE MODE (NO AGENT EXECUTION)
# ================================

from fastapi import FastAPI
from pydantic import BaseModel
import os

# -------------------------------
# App initialization
# -------------------------------
app = FastAPI(title="Supply Chain Guardian")

# -------------------------------
# Request schema
# -------------------------------
class QueryRequest(BaseModel):
    query: str

# -------------------------------
# Health check endpoint
# -------------------------------
@app.get("/")
def health():
    return {
        "status": "running",
        "service": "Supply Chain Guardian",
        "mode": "safe (agent disabled)"
    }

# -------------------------------
# Analyze endpoint (SAFE)
# -------------------------------
@app.post("/analyze")
def analyze(q: QueryRequest):
    return {
        "received": q.query,
        "message": "Backend is working. Agent execution will be enabled next."
    }

# -------------------------------
# Local run support (optional)
# -------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
