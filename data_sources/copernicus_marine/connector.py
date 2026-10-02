"""
Copernicus Marine Schema & Connector Implementation
"""
import os
import pandas as pd
from data_sources.copernicus_marine.metadata import METADATA

SCHEMA = {
    "required_columns": ["latitude", "longitude", "temperature", "salinity", "dissolved_oxygen", "ph"],
    "range_bounds": {
        "temperature": (5.0, 38.0),
        "dissolved_oxygen": (0.1, 15.0),
        "ph": (6.5, 9.0)
    }
}

class CopernicusMarineConnector:
    def __init__(self):
        self.metadata = METADATA
        self.schema = SCHEMA

    def fetch_observation(self, location_name):
        obs_file = "data/marine_observations.csv"
        if os.path.exists(obs_file):
            df = pd.read_csv(obs_file)
            sub = df[df["location"] == location_name]
            if len(sub) > 0:
                return sub.iloc[0].to_dict()
        return None
