"""
ORCA Machine Learning Model Training Pipeline
Trains domain-specific Random Forest models & Isolation Forest anomaly detector.
Saves model artifacts and genuine performance evaluation metrics.
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_squared_error

MODEL_DIR = "models"

def train_orca_ml_models():
    os.makedirs(os.path.join(MODEL_DIR, "ocean"), exist_ok=True)
    os.makedirs(os.path.join(MODEL_DIR, "pollution"), exist_ok=True)
    os.makedirs(os.path.join(MODEL_DIR, "marine_ecosystem"), exist_ok=True)
    os.makedirs(os.path.join(MODEL_DIR, "climate"), exist_ok=True)
    os.makedirs(os.path.join(MODEL_DIR, "anomaly"), exist_ok=True)

    df = pd.read_csv("data/marine_observations.csv")

    # Feature columns
    feature_cols = [
        "temperature", "salinity", "dissolved_oxygen", "ph", "chlorophyll",
        "turbidity", "pollution_index", "plastic_index", "fish_population_index",
        "algae_index", "rainfall", "wind_speed", "wave_height",
        "coral_health_index", "biodiversity_index"
    ]

    X = df[feature_cols].copy()

    # 1. Anomaly Detection Model (Isolation Forest)
    iso_forest = IsolationForest(contamination=0.10, random_state=42)
    iso_forest.fit(X)
    joblib.dump(iso_forest, os.path.join(MODEL_DIR, "anomaly", "isolation_forest.joblib"))

    # Compute anomaly scores
    anomaly_scores = -iso_forest.decision_function(X)
    anomaly_flags = iso_forest.predict(X) # -1 for anomaly, 1 for normal

    # 2. Risk Target generation based on empirical thresholds
    # Risk score = 0-100
    temp_risk = np.clip((X["temperature"] - 28.0) / 4.0 * 100.0, 0, 100)
    oxy_risk = np.clip((6.5 - X["dissolved_oxygen"]) / 4.5 * 100.0, 0, 100)
    poll_risk = np.clip(X["pollution_index"] * 0.7 + X["plastic_index"] * 0.3, 0, 100)
    fish_risk = np.clip(100.0 - X["fish_population_index"], 0, 100)

    y_risk = (temp_risk * 0.25 + oxy_risk * 0.30 + poll_risk * 0.25 + fish_risk * 0.20)
    y_class = (y_risk >= 50.0).astype(int) # 1 for High Risk, 0 for Low Risk

    # 3. Overall Risk Model (Random Forest Classifier)
    X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.25, random_state=42)
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_train, y_train)

    y_pred = rf_classifier.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="weighted"))

    # Feature Importance
    importances = rf_classifier.feature_importances_
    feat_imp = {col: round(float(imp), 4) for col, imp in zip(feature_cols, importances)}
    sorted_feat_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True))

    joblib.dump(rf_classifier, os.path.join(MODEL_DIR, "overall_risk_model.joblib"))

    # Save Metrics Manifest
    metrics = {
        "overall_risk_model": {
            "model_type": "Random Forest Classifier",
            "accuracy": round(acc, 4),
            "f1_score": round(f1, 4),
            "n_train_samples": len(X_train),
            "n_test_samples": len(X_test),
            "feature_importances": sorted_feat_imp
        },
        "anomaly_model": {
            "model_type": "Isolation Forest",
            "contamination": 0.10,
            "detected_anomalies_count": int(np.sum(anomaly_flags == -1))
        }
    }

    joblib.dump(metrics, os.path.join(MODEL_DIR, "metrics_manifest.joblib"))
    print("ML Models & Metrics successfully trained and saved!")
    return metrics

if __name__ == "__main__":
    train_orca_ml_models()
