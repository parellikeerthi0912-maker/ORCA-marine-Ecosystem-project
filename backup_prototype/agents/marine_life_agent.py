
def analyze(row):
    fish = float(row.get("fish_population_index", 80.0))
    coral = float(row.get("coral_health_index", 80.0))
    biodiversity = float(row.get("biodiversity_index", 80.0))
    algae = float(row.get("algae_index", 20.0))

    severities = []
    findings = []

    # Fish Population
    if fish < 40.0:
        findings.append(f"Severe Fish Stock Collapse: Population index at critical {fish:.1f}/100.")
        severities.append("HIGH")
    elif fish < 65.0:
        findings.append(f"Fish Stock Depletion: Population index reduced at {fish:.1f}/100.")
        severities.append("MODERATE")
    else:
        findings.append(f"Fish population index is healthy ({fish:.1f}/100).")
        severities.append("LOW")

    # Coral Reef Health
    if coral < 45.0:
        findings.append(f"Coral Bleaching Crisis: Reef health index depressed at {coral:.1f}/100.")
        severities.append("HIGH")
    elif coral < 70.0:
        findings.append(f"Moderate Coral Stress: Reef health index at {coral:.1f}/100.")
        severities.append("MODERATE")
    else:
        findings.append(f"Coral reef ecosystem is robust ({coral:.1f}/100).")
        severities.append("LOW")

    # Algal Bloom Risk
    if algae >= 65.0:
        findings.append(f"Harmful Algae Bloom (HAB) Warning: Algae bloom index elevated at {algae:.1f}/100.")
        severities.append("HIGH")
    elif algae >= 40.0:
        findings.append(f"Moderate Algal Activity: Algae index at {algae:.1f}/100.")
        severities.append("MODERATE")
    else:
        findings.append(f"Algae growth is contained ({algae:.1f}/100).")

    # Biodiversity
    findings.append(f"Overall Marine Biodiversity Index: {biodiversity:.1f}/100.")

    if "HIGH" in severities:
        status = "HIGH"
    elif "MODERATE" in severities:
        status = "MODERATE"
    else:
        status = "LOW"

    return {
        "agent": "Marine Life Agent",
        "status": status,
        "findings": findings,
        "confidence": 0.88
    }

