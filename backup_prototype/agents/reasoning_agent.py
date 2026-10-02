
import os
import json
import re

def fallback_reasoning(row, agent_results, risk):
    """
    Rule-based Analytical Synthesis Engine for ORCA multi-agent correlation.
    """
    temp = float(row.get("temperature", 28.0))
    oxygen = float(row.get("dissolved_oxygen", 6.5))
    pollution = float(row.get("pollution_index", 20.0))
    plastic = float(row.get("plastic_index", 20.0))
    fish = float(row.get("fish_population_index", 80.0))
    algae = float(row.get("algae_index", 20.0))
    coral = float(row.get("coral_health_index", 80.0))
    rainfall = float(row.get("rainfall", 50.0))
    turbidity = float(row.get("turbidity", 5.0))

    relationships = []
    recommendations = []

    # 1. Thermal & Hypoxia Compound Stress
    if temp >= 29.5 and oxygen <= 5.5:
        relationships.append("Compound Thermal/Hypoxic Stress: Higher sea surface temperatures reduce oxygen solubility while accelerating organism metabolic rates, creating compound physiological stress for marine fauna.")
    elif temp >= 29.5:
        relationships.append("Thermal Stress Pattern: Elevated sea surface temperature is the primary environmental driver in this observation.")
    elif oxygen <= 5.5:
        relationships.append("Oxygen Depletion Pattern: Reduced dissolved oxygen indicates potential stagnant water circulation or high biological oxygen demand.")

    # 2. Pollution & Ecotoxic Habitat Stress
    if (pollution >= 45.0 or plastic >= 45.0) and (fish <= 60.0 or coral <= 60.0):
        relationships.append("Ecotoxic Pollution-Habitat Cascade: High chemical pollution or plastic accumulation directly correlates with lowered fish stock density and coral reef stress.")
    elif pollution >= 50.0 or plastic >= 50.0:
        relationships.append("Pollution Accumulation: Chemical or microplastic contamination levels exceed baseline reference thresholds.")

    # 3. Eutrophication & Algal Bloom Cascade
    if algae >= 50.0 and oxygen <= 5.5:
        relationships.append("Eutrophication & Anoxia Risk: Rapid algal bloom proliferation creates high organic loading, leading to oxygen depletion as algae decays.")
    elif algae >= 50.0:
        relationships.append("Algal Bloom Proliferation: High algal index detected, requiring monitoring for potential bloom evolution.")

    # 4. Watershed Runoff & Sedimentation
    if rainfall >= 75.0 and turbidity >= 8.0:
        relationships.append("Land-based Runoff & Sedimentation: Heavy rainfall combined with high turbidity suggests land runoff introducing suspended solids into coastal waters.")

    if not relationships:
        relationships.append("Balanced Marine State: Environmental parameters are within stable ecological baselines with minimal cross-domain stress interactions.")

    # Recommendations based on risk drivers
    if risk["level"] in ["CRITICAL", "HIGH"]:
        recommendations.append("Alert Regional Marine Authorities: Initiate immediate high-priority monitoring and water sampling protocols.")
        if pollution >= 40.0:
            recommendations.append("Contamination Control: Restrict industrial/coastal effluent discharge into the affected marine zone.")
        if oxygen <= 5.0 or algae >= 50.0:
            recommendations.append("Eutrophication Abatement: Deploy aeration/circulation systems and monitor nutrient loading sources.")
        if fish <= 55.0 or coral <= 55.0:
            recommendations.append("Fishery & Habitat Protection: Implement temporary fishing restrictions and coral reef protection buffer zones.")
    elif risk["level"] == "MODERATE":
        recommendations.append("Enhanced Surveillance: Schedule bi-weekly environmental sampling to monitor parameter trends.")
        recommendations.append("Pollution Mitigation: Conduct local waste management inspections to suppress plastic and runoff accumulation.")
    else:
        recommendations.append("Routine Monitoring: Maintain regular satellite and buoy telemetry tracking.")
        recommendations.append("Conservation Buffer: Preserve existing biological refugia and coral protection zones.")

    summary = f"ORCA Collaborative Reasoning Engine assesses {row.get('location', 'Region')} at {risk['level']} Ecosystem Risk ({risk['overall_risk']}/100) with Ecosystem Health Score of {risk['health']}/100."

    # Identify dominant risk factors
    sorted_factors = sorted(risk["factors"].items(), key=lambda item: item[1], reverse=True)
    top_factors = [f"{k} ({v}%)" for k, v in sorted_factors if v > 20.0]

    return {
        "summary": summary,
        "key_factors": top_factors if top_factors else [f"{sorted_factors[0][0]} ({sorted_factors[0][1]}%)"],
        "possible_relationships": relationships,
        "recommendations": recommendations,
        "confidence": "High (Analytical Multi-Agent Engine)",
        "uncertainties": [
            "Synthetic/demo dataset indicators represent decision-support estimations, not official scientific proof.",
            "Hydrodynamic dispersion and subsurface ocean currents are modeled empirically."
        ]
    }

def gemini_reasoning(row, agent_results, risk, api_key):
    """
    LLM-powered Collaborative Reasoning Engine using Google Gemini API.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try available Gemini models in sequence
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
        response_text = None
        
        prompt = f"""
You are ORCA, an advanced multi-agent Marine Ecosystem Reasoning System for SIH 2026.
Synthesize the provided observations and specialized agent findings into a cohesive, scientific assessment.

OBSERVED DATA:
{dict(row)}

SPECIALIZED AGENT FINDINGS:
{agent_results}

ECOSYSTEM RISK METRICS:
{risk}

Instructions:
1. Explain environmental relationships between variables (e.g., temperature rise + low oxygen = compound stress).
2. Distinguish empirical facts from plausible causal relationships.
3. Provide actionable, practical conservation and management recommendations.
4. Return ONLY a valid JSON object with the following exact keys:
   "summary": string,
   "key_factors": list of strings,
   "possible_relationships": list of strings,
   "recommendations": list of strings,
   "confidence": string,
   "uncertainties": list of strings
"""

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                res = model.generate_content(prompt)
                if res and res.text:
                    response_text = res.text
                    break
            except Exception:
                continue

        if not response_text:
            return fallback_reasoning(row, agent_results, risk)

        # Extract JSON from response string
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
            parsed = json.loads(clean_text)
            return parsed
        else:
            return fallback_reasoning(row, agent_results, risk)
    except Exception:
        return fallback_reasoning(row, agent_results, risk)

def analyze(row, agent_results, risk, user_api_key=None):
    """
    Main entry point for Collaborative Reasoning Agent.
    Supports user-provided API key from UI, environment variable, or analytical fallback mode.
    """
    key = user_api_key or os.getenv("GEMINI_API_KEY")
    if key and key.strip():
        try:
            res = gemini_reasoning(row, agent_results, risk, key.strip())
            if res and isinstance(res, dict) and "summary" in res:
                return res, "✨ Gemini AI Engine"
        except Exception:
            pass
    return fallback_reasoning(row, agent_results, risk), "⚡ Analytical Fallback Engine"

