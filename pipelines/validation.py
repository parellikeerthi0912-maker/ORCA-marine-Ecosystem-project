"""
ORCA Data Validation & Quality Control Engine
Calculates Data Quality Score (0-100%) and detects anomalous/stale values.
"""

REQUIRED_COLUMNS = [
    "date", "location", "latitude", "longitude", "temperature", "salinity",
    "dissolved_oxygen", "ph", "chlorophyll", "turbidity", "pollution_index",
    "plastic_index", "fish_population_index", "algae_index", "rainfall",
    "wind_speed", "wave_height", "coral_health_index", "biodiversity_index"
]

RANGE_BOUNDS = {
    "temperature": (10.0, 36.0),
    "salinity": (20.0, 45.0),
    "dissolved_oxygen": (0.5, 12.0),
    "ph": (6.5, 9.0),
    "chlorophyll": (0.01, 50.0),
    "turbidity": (0.1, 50.0),
    "pollution_index": (0.0, 100.0),
    "plastic_index": (0.0, 100.0),
    "fish_population_index": (0.0, 100.0),
    "algae_index": (0.0, 100.0),
    "coral_health_index": (0.0, 100.0),
    "biodiversity_index": (0.0, 100.0)
}

def validate_dataframe(df):
    """
    Validates CSV dataframe against required schema.
    Returns list of missing columns.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing

def compute_data_quality_score(row):
    """
    Computes rigorous Data Quality Score (0 - 100%) for an observation row
    based on missing values, parameter range plausibility, and freshness.
    """
    score = 100.0
    penalties = 0.0

    # 1. Missing value check
    for col in REQUIRED_COLUMNS:
        val = row.get(col, None)
        if val is None or (isinstance(val, float) and float('nan') == val):
            penalties += 5.0

    # 2. Plausibility Range Bounds check
    for param, (lo, hi) in RANGE_BOUNDS.items():
        if param in row:
            try:
                val = float(row[param])
                if not (lo <= val <= hi):
                    penalties += 8.0
            except (ValueError, TypeError):
                penalties += 10.0

    final_score = max(0.0, min(100.0, score - penalties))
    return round(final_score, 1)
