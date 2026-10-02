
def analyze(row):
    pollution = float(row.get("pollution_index", 20.0))
    plastic = float(row.get("plastic_index", 20.0))
    turbidity = float(row.get("turbidity", 5.0))
    chlorophyll = float(row.get("chlorophyll", 3.0))

    severities = []
    findings = []

    # Chemical Pollution
    if pollution >= 70.0:
        findings.append(f"Severe Chemical Pollution: Index at {pollution:.1f}/100.")
        severities.append("HIGH")
    elif pollution >= 40.0:
        findings.append(f"Moderate Chemical Contamination: Index at {pollution:.1f}/100.")
        severities.append("MODERATE")
    else:
        findings.append(f"Chemical pollution levels are low ({pollution:.1f}/100).")
        severities.append("LOW")

    # Plastic Contamination
    if plastic >= 70.0:
        findings.append(f"High Microplastic Concentration: Index at {plastic:.1f}/100.")
        severities.append("HIGH")
    elif plastic >= 40.0:
        findings.append(f"Moderate Microplastic Density: Index at {plastic:.1f}/100.")
        severities.append("MODERATE")
    else:
        findings.append(f"Plastic debris index is within low range ({plastic:.1f}/100).")
        severities.append("LOW")

    # Water Clarity & Turbidity
    if turbidity >= 10.0:
        findings.append(f"High Turbidity Alert: Water clarity reduced ({turbidity:.1f} NTU), impairing light penetration.")
        severities.append("MODERATE")
    else:
        findings.append(f"Turbidity is normal ({turbidity:.1f} NTU).")
        severities.append("LOW")

    if chlorophyll >= 6.0:
        findings.append(f"Elevated Chlorophyll-a concentration ({chlorophyll:.1f} µg/L) signals high organic/nutrient loading.")

    if "HIGH" in severities:
        status = "HIGH"
    elif "MODERATE" in severities:
        status = "MODERATE"
    else:
        status = "LOW"

    return {
        "agent": "Pollution Agent",
        "status": status,
        "findings": findings,
        "confidence": 0.90
    }

