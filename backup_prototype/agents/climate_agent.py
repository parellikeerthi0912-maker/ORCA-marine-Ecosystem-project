
def analyze(row):
    temp = float(row.get("temperature", 28.0))
    rainfall = float(row.get("rainfall", 50.0))
    wave = float(row.get("wave_height", 1.5))
    wind = float(row.get("wind_speed", 15.0))

    severities = []
    findings = []

    # Thermal Marine Heatwave Risk
    if temp >= 30.5:
        findings.append(f"Marine Heatwave Threat: SST elevated at {temp:.1f} °C.")
        severities.append("HIGH")
    elif temp >= 28.5:
        findings.append(f"Thermal Anomaly: Ambient ocean temperature is {temp:.1f} °C.")
        severities.append("MODERATE")
    else:
        findings.append(f"Thermal conditions are stable ({temp:.1f} °C).")
        severities.append("LOW")

    # Wave & Hydrodynamics
    if wave >= 3.0:
        findings.append(f"Rough Sea State: Wave height is high at {wave:.1f} m, causing sediment agitation.")
        severities.append("MODERATE")
    else:
        findings.append(f"Wave height is moderate ({wave:.1f} m).")
        severities.append("LOW")

    # Rainfall & Runoff
    if rainfall >= 80.0:
        findings.append(f"Heavy Coastal Rainfall ({rainfall:.1f} mm): Risk of high land-based pollutant runoff.")
        severities.append("MODERATE")
    else:
        findings.append(f"Precipitation is normal ({rainfall:.1f} mm).")

    findings.append(f"Wind speed is measured at {wind:.1f} knots.")

    if "HIGH" in severities:
        status = "HIGH"
    elif "MODERATE" in severities:
        status = "MODERATE"
    else:
        status = "LOW"

    return {
        "agent": "Climate & Weather Agent",
        "status": status,
        "findings": findings,
        "confidence": 0.85
    }

