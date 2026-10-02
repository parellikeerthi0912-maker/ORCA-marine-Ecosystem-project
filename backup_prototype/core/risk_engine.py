
def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, float(x)))

def risk_from_row(row):
    """
    Computes Ecosystem Risk Score (0-100) and Ecosystem Health Score (0-100)
    from observation parameters based on prototype reference limits.
    """
    temp = float(row.get("temperature", 28))
    oxygen = float(row.get("dissolved_oxygen", 6))
    pollution = float(row.get("pollution_index", 20))
    plastic = float(row.get("plastic_index", 20))
    fish = float(row.get("fish_population_index", 80))
    algae = float(row.get("algae_index", 20))
    coral = float(row.get("coral_health_index", 80))
    ph = float(row.get("ph", 8.1))

    # Calculate sub-risk components (0 to 100)
    temp_risk = clamp(max(0, (temp - 28.0) / 4.0 * 100.0))
    oxygen_risk = clamp(max(0, (6.5 - oxygen) / 4.5 * 100.0))
    pollution_risk = clamp(pollution * 0.7 + plastic * 0.3)
    fish_risk = clamp(100.0 - fish)
    algae_risk = clamp(algae)
    coral_risk = clamp(100.0 - coral)
    ph_risk = clamp(abs(8.1 - ph) / 0.8 * 100.0)

    # Weighted Overall Ecosystem Risk
    overall = (
        temp_risk * 0.15 +
        oxygen_risk * 0.20 +
        pollution_risk * 0.20 +
        fish_risk * 0.15 +
        algae_risk * 0.10 +
        coral_risk * 0.15 +
        ph_risk * 0.05
    )
    health = clamp(100.0 - overall)

    if overall >= 75:
        level = "CRITICAL"
        badge_color = "#FF4B4B"
    elif overall >= 50:
        level = "HIGH"
        badge_color = "#FFA500"
    elif overall >= 25:
        level = "MODERATE"
        badge_color = "#F0D000"
    else:
        level = "LOW"
        badge_color = "#00CC96"

    return {
        "overall_risk": round(overall, 1),
        "health": round(health, 1),
        "level": level,
        "badge_color": badge_color,
        "factors": {
            "Temperature Stress": round(temp_risk, 1),
            "Oxygen Depletion": round(oxygen_risk, 1),
            "Pollution & Plastic": round(pollution_risk, 1),
            "Fish Stock Stress": round(fish_risk, 1),
            "Algae Bloom Risk": round(algae_risk, 1),
            "Coral Degradation": round(coral_risk, 1),
            "pH Acidification": round(ph_risk, 1),
        }
    }

