
from agents.ocean_agent import analyze as ocean
from agents.pollution_agent import analyze as pollution
from agents.marine_life_agent import analyze as marine_life
from agents.climate_agent import analyze as climate
from agents.reasoning_agent import analyze as reasoning
from core.risk_engine import risk_from_row

def run_orca(row, user_api_key=None):
    """
    Executes the ORCA multi-agent pipeline:
    1. Evaluates specialized domain agents (Ocean, Pollution, Marine Life, Climate).
    2. Computes ecosystem risk score and health score.
    3. Synthesizes collaborative reasoning via Gemini AI or Analytical Fallback Engine.
    """
    results = [
        ocean(row),
        pollution(row),
        marine_life(row),
        climate(row)
    ]
    risk = risk_from_row(row)
    final, mode = reasoning(row, results, risk, user_api_key=user_api_key)
    return {
        "agents": results,
        "risk": risk,
        "reasoning": final,
        "mode": mode
    }

