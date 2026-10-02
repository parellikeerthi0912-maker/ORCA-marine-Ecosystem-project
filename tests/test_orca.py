"""
ORCA Automated Unit & Integration Test Suite
Validates data ingestion connectors, validation scoring, ML inference, multi-agent pipeline, and ledger logging.
"""
import unittest
import pandas as pd
import os

from pipelines.validation import compute_data_quality_score, validate_dataframe
from core.orchestrator import run_orca
from core.risk_engine import risk_from_row
from database.ledger import record_assessment, get_recent_ledger_entries
from explainability.explainer import explain_prediction
from rag.knowledge_base import retrieve_scientific_context
from data_sources.noaa_erddap.connector import NOAAErddapConnector
from spatial.grid_engine import generate_indian_marine_grid


class TestORCAPlatform(unittest.TestCase):

    def setUp(self):
        self.sample_row = {
            "date": "2026-01-01",
            "location": "Visakhapatnam",
            "latitude": 17.6868,
            "longitude": 83.2185,
            "temperature": 30.4,
            "salinity": 35.2,
            "dissolved_oxygen": 4.8,
            "ph": 7.95,
            "chlorophyll": 7.2,
            "turbidity": 12.8,
            "pollution_index": 72.0,
            "plastic_index": 68.0,
            "fish_population_index": 48.0,
            "algae_index": 64.0,
            "rainfall": 70.0,
            "wind_speed": 17.5,
            "wave_height": 2.3,
            "coral_health_index": 42.0,
            "biodiversity_index": 55.0
        }

    def test_data_validation(self):
        df = pd.DataFrame([self.sample_row])
        missing = validate_dataframe(df)
        self.assertEqual(len(missing), 0)
        q_score = compute_data_quality_score(self.sample_row)
        self.assertGreaterEqual(q_score, 0.0)
        self.assertLessEqual(q_score, 100.0)

    def test_risk_engine(self):
        risk = risk_from_row(self.sample_row)
        self.assertIn("overall_risk", risk)
        self.assertIn("health", risk)
        self.assertIn("level", risk)
        self.assertIn(risk["level"], ["LOW", "MODERATE", "HIGH", "CRITICAL"])

    def test_orchestrator_multi_agent(self):
        res = run_orca(self.sample_row)
        self.assertIn("agents", res)
        self.assertIn("risk", res)
        self.assertIn("reasoning", res)
        self.assertEqual(len(res["agents"]), 5) # Ocean, Pollution, Marine Life, Climate, Anomaly

    def test_xai_explainer(self):
        risk = risk_from_row(self.sample_row)
        expl = explain_prediction(self.sample_row, risk)
        self.assertGreater(len(expl), 0)

    def test_ledger(self):
        res = run_orca(self.sample_row)
        ledger_id = record_assessment(self.sample_row, res)
        self.assertIsNotNone(ledger_id)
        entries = get_recent_ledger_entries(limit=5)
        self.assertGreater(len(entries), 0)

    def test_rag_knowledge(self):
        docs = retrieve_scientific_context("hypoxia oxygen")
        self.assertGreater(len(docs), 0)

    def test_noaa_connector(self):
        conn = NOAAErddapConnector()
        rec = conn.fetch_telemetry("Visakhapatnam")
        self.assertIsNotNone(rec)

    def test_spatial_grid_engine(self):
        df = pd.DataFrame([self.sample_row])
        cells = generate_indian_marine_grid(df, step=5.0)
        self.assertGreater(len(cells), 0)
        self.assertIn("grid_id", cells[0])

if __name__ == "__main__":
    unittest.main()

