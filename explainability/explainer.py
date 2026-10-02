"""
ORCA Explainable AI (XAI) Explainer
Calculates directional factor contributions (Increasing vs Decreasing risk) for predictions.
"""

def explain_prediction(row, risk_dict):
    """
    Analyzes observation parameters and returns directional impact tags for key drivers.
    """
    explanations = []
    
    temp = float(row.get("temperature", 28.0))
    oxy = float(row.get("dissolved_oxygen", 6.5))
    poll = float(row.get("pollution_index", 20.0))
    plastic = float(row.get("plastic_index", 20.0))
    fish = float(row.get("fish_population_index", 80.0))
    algae = float(row.get("algae_index", 20.0))

    if temp >= 29.5:
        explanations.append({"factor": "Sea Surface Temp", "value": f"{temp:.1f} °C", "direction": "↑ Increased Risk", "severity": "High" if temp>=31 else "Moderate"})
    else:
        explanations.append({"factor": "Sea Surface Temp", "value": f"{temp:.1f} °C", "direction": "↓ Normal/Reduced Risk", "severity": "Low"})

    if oxy <= 5.5:
        explanations.append({"factor": "Dissolved Oxygen", "value": f"{oxy:.1f} mg/L", "direction": "↑ Increased Depletion Risk", "severity": "High" if oxy<4.0 else "Moderate"})
    else:
        explanations.append({"factor": "Dissolved Oxygen", "value": f"{oxy:.1f} mg/L", "direction": "↓ Well-Oxygenated Baseline", "severity": "Low"})

    if poll >= 40.0 or plastic >= 40.0:
        explanations.append({"factor": "Pollution & Microplastics", "value": f"P:{poll:.0f} | Pl:{plastic:.0f}", "direction": "↑ Increased Ecotoxic Risk", "severity": "High" if poll>=70 else "Moderate"})
    else:
        explanations.append({"factor": "Pollution & Microplastics", "value": f"P:{poll:.0f} | Pl:{plastic:.0f}", "direction": "↓ Low Contamination", "severity": "Low"})

    if fish <= 60.0:
        explanations.append({"factor": "Fish Stock Density", "value": f"{fish:.0f}/100", "direction": "↑ Depletion Stress", "severity": "Moderate"})
    else:
        explanations.append({"factor": "Fish Stock Density", "value": f"{fish:.0f}/100", "direction": "↓ Healthy Population", "severity": "Low"})

    return explanations
