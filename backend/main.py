"""
ORCA FastAPI REST API Backend
Exposes production REST endpoints for health, telemetry observations, ML predictions, risk assessments, and evidence ledger.
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import os

from core.orchestrator import run_orca
from core.risk_engine import risk_from_row
from pipelines.validation import compute_data_quality_score
from database.ledger import get_recent_ledger_entries, record_assessment

app = FastAPI(
    title="ORCA Marine Ecosystem Intelligence API",
    description="Production REST API for ORCA SIH26176 Marine Multi-Agent Intelligence System",
    version="2.0.0"
)

DATASET_PATH = "data/marine_observations.csv"

def load_data():
    if os.path.exists(DATASET_PATH):
        return pd.read_csv(DATASET_PATH)
    raise HTTPException(status_code=404, detail="Marine observations dataset not found.")

@app.get("/")
def root():
    return {
        "service": "ORCA Marine Intelligence API",
        "status": "Online",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "service": "ORCA-API"}

@app.get("/api/v1/locations")
def get_locations():
    df = load_data()
    locs = sorted(df["location"].dropna().unique())
    return {"count": len(locs), "locations": locs}

@app.get("/api/v1/observation/{location_name}")
def get_observation(location_name: str):
    df = load_data()
    sub = df[df["location"] == location_name]
    if len(sub) == 0:
        raise HTTPException(status_code=404, detail=f"Location {location_name} not found.")
    row = sub.iloc[0].to_dict()
    q_score = compute_data_quality_score(row)
    return {"location": location_name, "quality_score": q_score, "observation": row}

@app.get("/api/v1/assessment/{location_name}")
def get_assessment(location_name: str, api_key: Optional[str] = Query(None)):
    df = load_data()
    sub = df[df["location"] == location_name]
    if len(sub) == 0:
        raise HTTPException(status_code=404, detail=f"Location {location_name} not found.")
    row = sub.iloc[0].to_dict()
    
    result = run_orca(row, user_api_key=api_key)
    q_score = compute_data_quality_score(row)
    
    # Audit log entry
    ledger_id = record_assessment(row, result, quality_score=q_score)
    result["ledger_audit_id"] = ledger_id
    result["data_quality_score"] = q_score
    return result

@app.get("/api/v1/ledger")
def get_ledger(limit: int = 10):
    entries = get_recent_ledger_entries(limit=limit)
    return {"count": len(entries), "ledger_entries": entries}
