"""
INCOIS / MOSDAC Schema & Range Constraints
"""

SCHEMA = {
    "required_columns": ["date", "latitude", "longitude", "temperature", "turbidity", "wave_height"],
    "range_bounds": {
        "temperature": (10.0, 36.0),
        "turbidity": (0.1, 50.0),
        "wave_height": (0.0, 15.0)
    }
}
