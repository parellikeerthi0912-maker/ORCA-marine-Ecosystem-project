"""
Copernicus Marine Schema & Range Constraints
"""

SCHEMA = {
    "required_columns": ["latitude", "longitude", "temperature", "salinity", "dissolved_oxygen", "ph"],
    "range_bounds": {
        "temperature": (5.0, 38.0),
        "dissolved_oxygen": (0.1, 15.0),
        "ph": (6.5, 9.0)
    }
}
