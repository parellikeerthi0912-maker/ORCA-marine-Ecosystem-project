"""
NOAA ERDDAP Data Source Metadata Definition
Official Public Marine Dataset Reference
"""

METADATA = {
    "source_id": "noaa_erddap",
    "source_name": "NOAA ERDDAP (CoastWatch / OceanWatch)",
    "official_url": "https://coastwatch.pfeg.noaa.gov/erddap/index.html",
    "dataset_name": "Global Sea Surface Temperature & Hydrographic Telemetry",
    "variables": {
        "sst": "Sea Surface Temperature (°C)",
        "salinity": "Practical Salinity Unit (PSU)",
        "chlorophyll": "Chlorophyll-a Concentration (mg/m³)",
        "wave_height": "Significant Wave Height (m)",
        "wind_speed": "Surface Wind Velocity (m/s)"
    },
    "units": {
        "temperature": "°C",
        "salinity": "PSU",
        "chlorophyll": "mg/m³",
        "wave_height": "m",
        "wind_speed": "m/s"
    },
    "spatial_coverage": {
        "region": "Indian Ocean / Arabian Sea / Bay of Bengal",
        "min_latitude": 5.0,
        "max_latitude": 25.0,
        "min_longitude": 65.0,
        "max_longitude": 95.0
    },
    "temporal_coverage": "2020-01-01 to Present (Daily / 6-hourly)",
    "update_frequency": "Daily",
    "access_method": "REST API / NetCDF / CSV / ERDDAP Tabledap",
    "authentication_required": False,
    "license_restrictions": "Public Domain (NOAA Open Data Policy)"
}
