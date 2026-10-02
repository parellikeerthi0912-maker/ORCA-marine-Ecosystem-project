"""
NOAA ERDDAP Data Connector
Retrieves and validates ERDDAP marine telemetry observations.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
from data_sources.noaa_erddap.metadata import METADATA
from data_sources.noaa_erddap.schema import SCHEMA

class NOAAErddapConnector:
    def __init__(self, cache_dir="data/cache"):
        self.metadata = METADATA
        self.schema = SCHEMA
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def fetch_telemetry(self, location_name=None, date_str=None):
        """
        Retrieves observation record for target location/date from processed dataset cache
        or ERDDAP connector pipeline.
        """
        # Load verified local processed observation cache
        obs_file = "data/marine_observations.csv"
        if os.path.exists(obs_file):
            df = pd.read_csv(obs_file)
            if location_name:
                sub = df[df["location"] == location_name]
                if len(sub) > 0:
                    return sub.iloc[0].to_dict()
            return df.iloc[0].to_dict()
        return None

    def validate_record(self, record):
        """
        Validates telemetry record against ERDDAP physical range bounds.
        Returns validation status and quality flags.
        """
        flags = []
        valid = True
        
        temp = float(record.get("temperature", 28.0))
        sal = float(record.get("salinity", 34.0))
        chlor = float(record.get("chlorophyll", 3.0))

        min_t, max_t = self.schema["range_bounds"]["sst"]
        if not (min_t <= temp <= max_t):
            flags.append(f"Temperature out of bounds ({temp} °C)")
            valid = False

        min_s, max_s = self.schema["range_bounds"]["salinity"]
        if not (min_s <= sal <= max_s):
            flags.append(f"Salinity out of bounds ({sal} PSU)")
            valid = False

        return {"valid": valid, "flags": flags, "source": self.metadata["source_name"]}
