
import pandas as pd

REQUIRED = [
    "date","location","latitude","longitude","temperature","salinity",
    "dissolved_oxygen","ph","chlorophyll","turbidity","pollution_index",
    "plastic_index","fish_population_index","algae_index","rainfall",
    "wind_speed","wave_height","coral_health_index","biodiversity_index"
]

def validate(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    return missing

def make_report(row, result):
    r = result["risk"]
    x = result["reasoning"]
    
    lines = [
        "# 🌊 ORCA Marine Ecosystem Assessment Report",
        "**Smart India Hackathon 2026 (SIH26176) — Decision Support Intelligence**",
        "---",
        "## 📍 Location & Telemetry Metadata",
        f"- **Marine Region**: {row['location']}",
        f"- **Observation Date**: {row['date']}",
        f"- **Coordinates**: Latitude {float(row['latitude']):.4f}°, Longitude {float(row['longitude']):.4f}°",
        f"- **Reasoning Engine Mode**: {result['mode']}",
        "",
        "## 📊 Executive Health & Risk Summary",
        f"- **Ecosystem Health Score**: **{r['health']} / 100**",
        f"- **Overall Risk Score**: **{r['overall_risk']} / 100**",
        f"- **Risk Level Classification**: **{r['level']}**",
        "",
        "### Risk Breakdown by Environmental Factor",
        "| Environmental Factor | Sub-Risk Level (0-100) | Status |",
        "| :--- | :--- | :--- |"
    ]
    
    for factor, score in r.get("factors", {}).items():
        status_tag = "🔴 Critical" if score >= 75 else ("🟧 High" if score >= 50 else ("🟨 Moderate" if score >= 25 else "🟩 Low"))
        lines.append(f"| {factor} | {score}% | {status_tag} |")

    lines += [
        "",
        "---",
        "## 🤖 Specialized Agent Network Findings"
    ]

    for a in result["agents"]:
        status_badge = f"**[{a['status']}]**"
        lines.append(f"### {a['agent']} {status_badge}")
        lines.append(f"- *Agent Confidence*: {a.get('confidence', 0.9):.0%}")
        lines.append("- *Key Observations*:")
        for f in a["findings"]:
            lines.append(f"  - {f}")
        lines.append("")

    lines += [
        "---",
        "## 🧠 Collaborative Synthesis & Cross-Domain Reasoning",
        f"**Executive Synthesis**: {x.get('summary', 'Assessment completed.')}",
        "",
        "### 🔎 Cross-Domain Relationships & Impact Patterns"
    ]
    for rel in x.get("possible_relationships", []):
        lines.append(f"- {rel}")

    lines += [
        "",
        "### ✅ Actionable Conservation Recommendations"
    ]
    for rec in x.get("recommendations", []):
        lines.append(f"1. {rec}")

    lines += [
        "",
        "### ⚠️ Uncertainties & Prototype Disclaimers"
    ]
    for unc in x.get("uncertainties", []):
        lines.append(f"- {unc}")

    lines += [
        "",
        "---",
        "*Report generated automatically by ORCA Marine Ecosystem Intelligence System.*"
    ]

    return "\n".join(lines)

