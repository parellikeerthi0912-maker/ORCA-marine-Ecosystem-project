"""
Copernicus Marine Environment Monitoring Service (CMEMS) Metadata
"""

METADATA = {
    "source_id": "copernicus_marine",
    "source_name": "Copernicus Marine Service (CMEMS / EU Earth Observation)",
    "official_url": "https://marine.copernicus.eu/",
    "dataset_name": "Global Ocean Physics & Biogeochemistry Reanalysis",
    "variables": {
        "thetao": "Sea Water Temperature (°C)",
        "so": "Sea Water Salinity (PSU)",
        "o2": "Dissolved Oxygen Concentration (mmol/m³)",
        "chl": "Chlorophyll-a (mg/m³)",
        "ph": "pH in Sea Water"
    },
    "units": {
        "temperature": "°C",
        "salinity": "PSU",
        "dissolved_oxygen": "mg/L",
        "chlorophyll": "mg/m³",
        "ph": "pH scale"
    },
    "spatial_coverage": {
        "region": "Indian Ocean North & Coastal Zones",
        "min_latitude": 0.0,
        "max_latitude": 30.0,
        "min_longitude": 60.0,
        "max_longitude": 100.0
    },
    "temporal_coverage": "2018-01-01 to Present",
    "update_frequency": "Daily / Monthly Assimilation",
    "access_method": "Copernicus Marine Toolbox / NetCDF API",
    "authentication_required": True,
    "license_restrictions": "CC-BY 4.0 Open Copernicus License"
}
