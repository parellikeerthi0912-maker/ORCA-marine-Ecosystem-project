"""
NOAA ERDDAP Schema & Range Constraints
"""

SCHEMA = {
    "required_columns": ["time", "latitude", "longitude", "sst", "salinity", "chlorophyll", "wave_height", "wind_speed"],
    "column_mapping": {
        "time": "date",
        "sst": "temperature",
        "salinity": "salinity",
        "chlorophyll": "chlorophyll",
        "wave_height": "wave_height",
        "wind_speed": "wind_speed"
    },
    "range_bounds": {
        "sst": (10.0, 36.0),         # Sea Surface Temp °C
        "salinity": (25.0, 42.0),    # Salinity PSU
        "chlorophyll": (0.01, 50.0), # mg/m³
        "wave_height": (0.0, 15.0),  # meters
        "wind_speed": (0.0, 50.0)    # m/s
    }
}
