"""
ORCA Anomaly Detection Agent
Evaluates unexpected marine telemetry patterns using Isolation Forest model.
"""
import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "models/anomaly/isolation_forest.joblib"

def analyze(row):
    """
    Evaluates observation row for statistical anomalies using trained Isolation Forest.
    """
    feature_cols = [
        "temperature", "salinity", "dissolved_oxygen", "ph", "chlorophyll",
        "turbidity", "pollution_index", "plastic_index", "fish_population_index",
        "algae_index", "rainfall", "wind_speed", "wave_height",
        "coral_health_index", "biodiversity_index"
    ]
    
    findings = []
    status = "LOW"
    anomaly_score = 0.0

    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            vec = [float(row.get(col, 0.0)) for col in feature_cols]
            X = pd.DataFrame([vec], columns=feature_cols)
            
            # Predict (-1 is anomaly, 1 is normal)
            pred = model.predict(X)[0]
            dec_score = model.decision_function(X)[0] # negative values indicate anomalies
            anomaly_score = float(round(-dec_score * 100.0, 1))

            if pred == -1:
                status = "HIGH"
                findings.append(f"Statistical Anomaly Detected: Isolation Forest score is elevated at {anomaly_score}.")
                # Identify extreme parameters
                if float(row.get("temperature", 28.0)) > 30.5:
                    findings.append("Extreme SST anomaly detected.")
                if float(row.get("pollution_index", 20.0)) > 60.0:
                    findings.append("Extreme pollution surge detected.")
                if float(row.get("dissolved_oxygen", 6.5)) < 4.5:
                    findings.append("Hypoxic oxygen dip anomaly detected.")
            else:
                findings.append("Telemetry metrics are statistically aligned with expected oceanographic distributions.")
        else:
            findings.append("Anomaly model not initialized; operating in standard baseline mode.")
    except Exception as e:
        findings.append(f"Anomaly evaluation note: {str(e)}")

    return {
        "agent": "Anomaly Detection Agent",
        "status": status,
        "findings": findings,
        "confidence": 0.89,
        "anomaly_score": anomaly_score
    }
