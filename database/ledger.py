"""
ORCA SQLite Evidence Ledger Database Module
Stores immutable audit records of inputs, model predictions, agent findings, and risk metrics.
"""
import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = "database/orca_ledger.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            observation_date TEXT NOT NULL,
            overall_risk REAL NOT NULL,
            health_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            reasoning_mode TEXT NOT NULL,
            quality_score REAL NOT NULL,
            input_data TEXT NOT NULL,
            agent_findings TEXT NOT NULL,
            recommendations TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def record_assessment(row, result, quality_score=100.0):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    loc = row.get("location", "Unknown Location")
    obs_date = row.get("date", "2026-01-01")
    risk_dict = result.get("risk", {})
    r_level = risk_dict.get("level", "UNKNOWN")
    r_score = risk_dict.get("overall_risk", 0.0)
    h_score = risk_dict.get("health", 100.0)
    mode = result.get("mode", "Analytical Engine")

    input_json = json.dumps(dict(row))
    agent_json = json.dumps(result.get("agents", []))
    recs_json = json.dumps(result.get("reasoning", {}).get("recommendations", []))

    cursor.execute("""
        INSERT INTO evidence_ledger 
        (timestamp, location, observation_date, overall_risk, health_score, risk_level, reasoning_mode, quality_score, input_data, agent_findings, recommendations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ts, loc, obs_date, r_score, h_score, r_level, mode, quality_score, input_json, agent_json, recs_json))

    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_recent_ledger_entries(limit=10):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence_ledger ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
