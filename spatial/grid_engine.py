"""
ORCA Spatial Grid Engine & Telemetry Interpolator
Generates spatial grid cells over the Indian Marine Region (Arabian Sea, Bay of Bengal, Indian Ocean)
and performs nearest-neighbor / inverse-distance telemetry interpolation.
"""
import numpy as np
import pandas as pd
from core.risk_engine import risk_from_row
from core.orchestrator import run_orca
from pipelines.validation import compute_data_quality_score

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Computes approximate distance in kilometers between two coordinates.
    """
    R = 6371.0 # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return R * c

def generate_indian_marine_grid(df, step=2.0, max_dist_km=500.0):
    """
    Generates spatial grid polygons across Indian marine bounds (Lat: 5.0 to 24.0, Lon: 65.0 to 95.0).
    Interpolates nearest marine observations for each cell and computes risk scores.
    """
    lat_min, lat_max = 5.0, 24.0
    lon_min, lon_max = 65.0, 95.0

    lats = np.arange(lat_min, lat_max, step)
    lons = np.arange(lon_min, lon_max, step)

    obs_records = df.to_dict(orient="records")
    grid_cells = []

    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            cell_center_lat = lat + step / 2.0
            cell_center_lon = lon + step / 2.0

            # Find nearest observation
            distances = []
            for obs in obs_records:
                d_km = haversine_distance(cell_center_lat, cell_center_lon, float(obs["latitude"]), float(obs["longitude"]))
                distances.append((d_km, obs))

            distances.sort(key=lambda x: x[0])
            min_dist, nearest_obs = distances[0]

            cell_id = f"GRID_{i:02d}_{j:02d}"
            polygon = [
                [float(lat), float(lon)],
                [float(lat + step), float(lon)],
                [float(lat + step), float(lon + step)],
                [float(lat), float(lon + step)]
            ]

            if min_dist <= max_dist_km:
                # Interpolated parameter dictionary based on nearest observation
                cell_row = dict(nearest_obs)
                cell_row["latitude"] = round(cell_center_lat, 4)
                cell_row["longitude"] = round(cell_center_lon, 4)
                
                risk_res = risk_from_row(cell_row)
                q_score = compute_data_quality_score(cell_row)
                
                # Confidence degrades slightly with distance
                dist_penalty = min(30.0, (min_dist / max_dist_km) * 30.0)
                confidence = max(50.0, round(92.0 - dist_penalty, 1))

                grid_cells.append({
                    "grid_id": cell_id,
                    "center_lat": round(cell_center_lat, 4),
                    "center_lon": round(cell_center_lon, 4),
                    "bounds": polygon,
                    "nearest_location": nearest_obs["location"],
                    "distance_km": round(min_dist, 1),
                    "status": "VALID",
                    "overall_risk": risk_res["overall_risk"],
                    "health_score": risk_res["health"],
                    "risk_level": risk_res["level"],
                    "badge_color": risk_res["badge_color"],
                    "data_quality": q_score,
                    "confidence": confidence,
                    "row_data": cell_row,
                    "risk_data": risk_res
                })
            else:
                grid_cells.append({
                    "grid_id": cell_id,
                    "center_lat": round(cell_center_lat, 4),
                    "center_lon": round(cell_center_lon, 4),
                    "bounds": polygon,
                    "nearest_location": "N/A",
                    "distance_km": round(min_dist, 1),
                    "status": "INSUFFICIENT DATA",
                    "overall_risk": 0.0,
                    "health_score": 0.0,
                    "risk_level": "INSUFFICIENT DATA",
                    "badge_color": "#64748B",
                    "data_quality": 0.0,
                    "confidence": 0.0,
                    "row_data": {},
                    "risk_data": {}
                })

    return grid_cells
