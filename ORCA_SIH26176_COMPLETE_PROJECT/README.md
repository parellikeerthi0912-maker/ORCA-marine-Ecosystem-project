# ORCA – Marine Ecosystem Reasoning with Collaborative Agents

SIH26176 prototype for Smart India Hackathon 2026.

## What it does
ORCA combines marine observations with specialized agents:
- Ocean Conditions Agent
- Pollution Agent
- Marine Life Agent
- Climate & Weather Agent
- Collaborative Reasoning Agent

The agents produce independent findings, then ORCA combines them into an ecosystem risk assessment and recommendations.

## Run
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Optional Gemini
Copy `.env.example` to `.env` and add:
`GEMINI_API_KEY=...`

Without a key, the app automatically uses Fallback Analytical Mode.

## Important
The included dataset is synthetic/demo data. Prototype thresholds are illustrative and are not official scientific limits.
