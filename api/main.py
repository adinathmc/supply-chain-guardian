"""Lightweight FastAPI proxy to call the deployed Reasoning Engine.

Expose POST /query with JSON payload {"input": "..."} and forward to
Vertex AI Reasoning Engine using service account credentials available to
this service (e.g., Cloud Run with Workload Identity).
"""
from fastapi import FastAPI
from pydantic import BaseModel
import os
import vertexai
from vertexai.preview import reasoning_engines

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
RESOURCE = os.environ.get("REASONING_ENGINE_RESOURCE")

if not PROJECT or not RESOURCE:
    raise RuntimeError("GOOGLE_CLOUD_PROJECT and REASONING_ENGINE_RESOURCE must be set")

vertexai.init(project=PROJECT, location=LOCATION)
agent = reasoning_engines.ReasoningEngine(RESOURCE)

app = FastAPI(title="Supply Chain Guardian API", version="1.0.0")


class Query(BaseModel):
    input: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def query(payload: Query):
    """Forward user query to the deployed Reasoning Engine."""
    response = agent.query(input=payload.input)
    return {"response": response}
