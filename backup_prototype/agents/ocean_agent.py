
def analyze(row):
    findings = []
    severities = []
    
    temp = float(row.get("temperature", 28.0))
    oxygen = float(row.get("dissolved_oxygen", 6.5))
    salinity = float(row.get("salinity", 34.0))
    ph = float(row.get("ph", 8.1))

    # Temperature Analysis
    if temp >= 31.0:
        findings.append(f"Critical Thermal Stress: SST is severely elevated at {temp:.2f} °C.")
        severities.append("HIGH")
    elif temp >= 29.0:
        findings.append(f"Moderate Thermal Stress: SST is elevated at {temp:.2f} °C.")
        severities.append("MODERATE")
    else:
        findings.append(f"Sea Surface Temperature is normal ({temp:.2f} °C).")
        severities.append("LOW")

    # Dissolved Oxygen Analysis
    if oxygen < 4.0:
        findings.append(f"Hypoxia Alert: Dissolved Oxygen is dangerously low at {oxygen:.2f} mg/L.")
        severities.append("HIGH")
    elif oxygen < 6.0:
        findings.append(f"Sub-optimal Oxygen: Dissolved Oxygen is below baseline at {oxygen:.2f} mg/L.")
        severities.append("MODERATE")
    else:
        findings.append(f"Dissolved Oxygen is well-oxygenated ({oxygen:.2f} mg/L).")
        severities.append("LOW")

    # pH & Acidification
    if ph < 7.8:
        findings.append(f"Ocean Acidification Risk: pH is depressed at {ph:.2f}.")
        severities.append("MODERATE")
    elif ph > 8.4:
        findings.append(f"Alkaline Anomaly: pH is elevated at {ph:.2f}.")
        severities.append("MODERATE")
    else:
        findings.append(f"pH level is balanced ({ph:.2f}).")
        severities.append("LOW")

    # Salinity
    findings.append(f"Salinity is recorded at {salinity:.1f} PSU.")

    if "HIGH" in severities:
        status = "HIGH"
    elif "MODERATE" in severities:
        status = "MODERATE"
    else:
        status = "LOW"

    return {
        "agent": "Ocean Conditions Agent",
        "status": status,
        "findings": findings,
        "confidence": 0.92
    }

