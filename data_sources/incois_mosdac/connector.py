"""
INCOIS / MOSDAC (ISRO Marine Satellite Telemetry) Connector
"""
import os
import pandas as pd
from data_sources.incois_mosdac.metadata import METADATA
from data_sources.incois_mosdac.schema import SCHEMA

class IncoisMosdacConnector:
    def __init__(self):
        self.metadata = METADATA
        self.schema = SCHEMA

    def get_metadata(self):
        return self.metadata

    def fetch_observation(self, location_name):
        obs_file = "data/marine_observations.csv"
        if os.path.exists(obs_file):
            df = pd.read_csv(obs_file)
            sub = df[df["location"] == location_name]
            if len(sub) > 0:
                return sub.iloc[0].to_dict()
        return None
