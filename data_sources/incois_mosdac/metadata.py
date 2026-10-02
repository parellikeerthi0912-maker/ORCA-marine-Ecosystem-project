"""
INCOIS / MOSDAC (ISRO Marine Satellite Telemetry) Metadata
"""

METADATA = {
    "source_id": "incois_mosdac",
    "source_name": "INCOIS / MOSDAC (ISRO Ocean Science Data Centre)",
    "official_url": "https://www.incois.gov.in / https://www.mosdac.gov.in",
    "dataset_name": "Oceansat-3 & Indian Ocean Coastal Telemetry",
    "variables": {
        "sst": "Sea Surface Temperature (°C)",
        "algae_index": "Algal Bloom Chlorophyll-a Proxy",
        "turbidity": "Coastal Turbidity (NTU)",
        "wave_height": "Significant Wave Height (m)"
    },
    "units": {
        "temperature": "°C",
        "turbidity": "NTU",
        "wave_height": "m"
    },
    "spatial_coverage": {
        "region": "Exclusive Economic Zone (EEZ) of India",
        "min_latitude": 6.0,
        "max_latitude": 24.0,
        "min_longitude": 68.0,
        "max_longitude": 96.0
    },
    "temporal_coverage": "2021-01-01 to Present",
    "update_frequency": "Near-Real-Time (3-hourly / Daily)",
    "access_method": "INCOIS OOS Data Portal / MOSDAC OCM3 GeoTIFF Feed",
    "authentication_required": False,
    "license_restrictions": "Government of India Open Data Policy"
}
