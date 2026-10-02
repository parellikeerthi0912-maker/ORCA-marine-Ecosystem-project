import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

from core.orchestrator import run_orca
from core.risk_engine import risk_from_row
from utils.helpers import validate, make_report

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="ORCA | India Marine Intelligence & Ecosystem Reasoning",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Ocean Aesthetic & Glassmorphism
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #040D18;
        color: #E2E8F0;
    }
    
    /* Hero Banner */
    .hero-container {
        padding: 24px 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(8, 43, 58, 0.9) 0%, rgba(11, 23, 36, 0.95) 100%);
        border: 1px solid rgba(0, 242, 254, 0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(0, 242, 254, 0.05);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 40px;
        font-weight: 700;
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0;
    }
    .hero-subtitle {
        font-size: 17px;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .hero-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background: rgba(0, 242, 254, 0.1);
        border: 1px solid rgba(0, 242, 254, 0.3);
        color: #00F2FE;
        font-size: 13px;
        font-weight: 600;
    }

    /* Cards & Containers */
    .card {
        padding: 20px;
        border-radius: 16px;
        background: rgba(13, 35, 48, 0.7);
        border: 1px solid rgba(28, 67, 85, 0.8);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 16px;
    }
    .agent-card {
        padding: 16px 20px;
        border-radius: 14px;
        background: rgba(11, 29, 41, 0.85);
        border: 1px solid rgba(27, 61, 77, 0.9);
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }
    .agent-card:hover {
        border-color: rgba(0, 242, 254, 0.4);
    }
    
    /* Badges */
    .badge-critical { background: rgba(255, 75, 75, 0.2); border: 1px solid #FF4B4B; color: #FF4B4B; }
    .badge-high { background: rgba(255, 165, 0, 0.2); border: 1px solid #FFA500; color: #FFA500; }
    .badge-moderate { background: rgba(240, 208, 0, 0.2); border: 1px solid #F0D000; color: #F0D000; }
    .badge-low { background: rgba(0, 204, 150, 0.2); border: 1px solid #00CC96; color: #00CC96; }
    
    .badge {
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    /* Metric Formatting */
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #94A3B8 !important;
    }
    .legend-box {
        padding: 8px 14px;
        background: rgba(15, 23, 42, 0.8);
        border-radius: 10px;
        border: 1px solid rgba(51, 65, 85, 0.8);
        font-size: 13px;
        display: inline-block;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Locations Metadata (12 Target Demo Locations)
TARGET_LOCATIONS = [
    "Mumbai", "Goa", "Kochi", "Gulf of Mannar", "Chennai", "Visakhapatnam",
    "Paradip", "Sundarbans", "Bay of Bengal", "Arabian Sea", "Lakshadweep", "Andaman & Nicobar"
]

# Load Dataset
uploaded = st.sidebar.file_uploader("📂 Upload Custom Marine CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    missing = validate(df)
    if missing:
        st.sidebar.error("Missing columns: " + ", ".join(missing))
        st.stop()
    st.sidebar.success("Custom Dataset Loaded!")
else:
    df = pd.read_csv("data/marine_observations.csv")

# Sidebar Header & Controls
st.sidebar.markdown("## 🌊 ORCA Control Center")
st.sidebar.markdown("<p style='font-size:12px; color:#94A3B8;'>SIH26176 Marine Intelligence Control</p>", unsafe_allow_html=True)

# Location Selection Control (Synchronized)
all_locs = sorted(df["location"].dropna().unique())
selected_location = st.sidebar.selectbox("📍 Select Marine Location", all_locs, index=0 if "Visakhapatnam" not in all_locs else all_locs.index("Visakhapatnam"))

subset = df[df["location"] == selected_location].copy().reset_index(drop=True)
if len(subset) == 0:
    st.error(f"No observations found for {selected_location}.")
    st.stop()

# Observation Selector
obs_options = [f"{subset.loc[i,'date']} (Obs #{i+1})" for i in range(len(subset))]
selected_obs_str = st.sidebar.selectbox("📅 Select Observation Date", obs_options, index=0)
selected_idx = int(selected_obs_str.split("#")[1].replace(")", "")) - 1
row = subset.iloc[selected_idx].to_dict()

st.sidebar.divider()

# API Key & Mode Setup
st.sidebar.markdown("### 🤖 Reasoning Engine Settings")
user_api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Enter Google Gemini API Key for LLM synthesis. Leave blank for Analytical Fallback Mode.")

if user_api_key or os.getenv("GEMINI_API_KEY"):
    st.sidebar.markdown('<span class="badge badge-low">✨ Gemini AI Enabled</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="badge badge-moderate">⚡ Analytical Fallback Engine</span>', unsafe_allow_html=True)

run_button = st.sidebar.button("🧠 Run ORCA Multi-Agent Pipeline", type="primary", use_container_width=True)

st.sidebar.divider()
st.sidebar.caption("💡 **Prototype Note**: Demo synthetic observations for prototype demonstration. Not real-time measurements.")

# Execute ORCA Pipeline for selected observation
if "current_result" not in st.session_state or run_button or st.session_state.get("last_obs_id") != f"{selected_location}_{selected_idx}_{user_api_key}":
    st.session_state["current_result"] = run_orca(row, user_api_key=user_api_key)
    st.session_state["last_obs_id"] = f"{selected_location}_{selected_idx}_{user_api_key}"

result = st.session_state["current_result"]
risk = result["risk"]

# Hero Banner
st.markdown(f"""
<div class="hero-container">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 class="hero-title">🌊 ORCA</h1>
            <div class="hero-subtitle">Marine Ecosystem Reasoning with Collaborative Agents</div>
            <div>
                <span class="hero-tag">SIH 2026 Prototype</span>
                <span class="hero-tag" style="margin-left:8px; border-color:rgba(56,189,248,0.4); color:#38BDF8;">📍 Location: {selected_location}</span>
                <span class="hero-tag" style="margin-left:8px; border-color:rgba(148,163,184,0.4); color:#CBD5E1;">📅 {row['date']}</span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px; color:#94A3B8; margin-bottom:4px;">ECOSYSTEM RISK LEVEL</div>
            <span class="badge badge-{'critical' if risk['level']=='CRITICAL' else ('high' if risk['level']=='HIGH' else ('moderate' if risk['level']=='MODERATE' else 'low'))}" style="font-size:18px; padding:6px 16px;">
                {risk['level']} ({risk['overall_risk']}/100)
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Tab Navigation
tab_map, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🇮🇳 India Marine Intelligence Map",
    "🌊 Executive Overview",
    "🤖 Specialized Multi-Agent Network",
    "📊 Analytics & Spatial Telemetry",
    "🔬 What-If Simulation Sandbox",
    "📄 Decision Support Report Export"
])

# Helper function to compute location latest summary table
def get_all_locations_summary(dataframe):
    summary_list = []
    unique_locs = dataframe["location"].unique()
    for loc in unique_locs:
        sub = dataframe[dataframe["location"] == loc]
        latest_row = sub.iloc[0].to_dict()
        r = risk_from_row(latest_row)
        summary_list.append({
            "Location": loc,
            "Risk Score": r["overall_risk"],
            "Health Score": r["health"],
            "Risk Level": r["level"],
            "Pollution Index": round(float(latest_row.get("pollution_index", 0)), 1),
            "Temperature (°C)": round(float(latest_row.get("temperature", 0)), 1),
            "Oxygen (mg/L)": round(float(latest_row.get("dissolved_oxygen", 0)), 1),
            "Latitude": float(latest_row["latitude"]),
            "Longitude": float(latest_row["longitude"]),
            "row_data": latest_row,
            "risk_data": r
        })
    sum_df = pd.DataFrame(summary_list).sort_values(by="Risk Score", ascending=False).reset_index(drop=True)
    return sum_df

locations_summary = get_all_locations_summary(df)

# ====================================================
# TAB: 🇮🇳 INDIA MARINE INTELLIGENCE MAP (PRIMARY FEATURE)
# ====================================================
with tab_map:
    st.subheader("🇮🇳 India & Indian Ocean Marine Intelligence Map")
    st.markdown("Interactive spatial risk map displaying marine telemetry and ORCA multi-agent risk classifications across key coastal and oceanic zones.")
    
    st.markdown("""
    <div class="legend-box">
        <b>Ecosystem Risk Legend:</b> &nbsp;
        <span style="color:#00CC96; font-weight:bold;">🟢 LOW (&lt;25)</span> &nbsp;|&nbsp;
        <span style="color:#F0D000; font-weight:bold;">🟡 MODERATE (25-49.9)</span> &nbsp;|&nbsp;
        <span style="color:#FFA500; font-weight:bold;">🟠 HIGH (50-74.9)</span> &nbsp;|&nbsp;
        <span style="color:#FF4B4B; font-weight:bold;">🔴 CRITICAL (≥75)</span>
    </div>
    """, unsafe_allow_html=True)

    # Render India Centered Map with free OpenStreetMap tiles (No API Key required)
    india_map = folium.Map(location=[16.0, 78.5], zoom_start=5, tiles="OpenStreetMap")
    
    for _, loc_info in locations_summary.iterrows():
        l_name = loc_info["Location"]
        l_risk_level = loc_info["Risk Level"]
        l_risk_score = loc_info["Risk Score"]
        l_health_score = loc_info["Health Score"]
        r_data = loc_info["row_data"]

        # Determine marker color based on ORCA risk level
        if l_risk_level == "CRITICAL":
            marker_color = "red"
            fill_hex = "#FF4B4B"
        elif l_risk_level == "HIGH":
            marker_color = "orange"
            fill_hex = "#FFA500"
        elif l_risk_level == "MODERATE":
            marker_color = "yellow"
            fill_hex = "#F0D000"
        else:
            marker_color = "green"
            fill_hex = "#00CC96"

        is_selected = (l_name == selected_location)

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 220px; color: #1e293b;">
            <h4 style="margin:0 0 6px 0; color:#0f172a; border-bottom:1px solid #cbd5e1; padding-bottom:4px;">📍 {l_name}</h4>
            <div style="font-size:12px; line-height:1.5;">
                <b>🌡 Temperature:</b> {r_data.get('temperature', 0):.1f} °C<br>
                <b>💧 Dissolved Oxygen:</b> {r_data.get('dissolved_oxygen', 0):.1f} mg/L<br>
                <b>☣ Pollution Index:</b> {r_data.get('pollution_index', 0):.0f}/100<br>
                <b>🐟 Fish Stock:</b> {r_data.get('fish_population_index', 0):.0f}/100<br>
                <b>🌿 Algae Index:</b> {r_data.get('algae_index', 0):.0f}/100<br>
                <b>🪸 Coral Health:</b> {r_data.get('coral_health_index', 0):.0f}/100<br>
                <hr style="margin:6px 0;">
                <b>⚠ Ecosystem Risk:</b> <span style="color:{fill_hex}; font-weight:bold;">{l_risk_level} ({l_risk_score:.1f}/100)</span><br>
                <b>❤️ Ecosystem Health:</b> <b>{l_health_score:.1f}/100</b>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[loc_info["Latitude"], loc_info["Longitude"]],
            radius=12 if is_selected else 8,
            color="#00F2FE" if is_selected else fill_hex,
            fill=True,
            fill_color=fill_hex,
            fill_opacity=0.9 if is_selected else 0.7,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{l_name} — Risk: {l_risk_level} ({l_risk_score}/100)"
        ).add_to(india_map)

    st_folium(india_map, width=None, height=480)
    st.caption("💡 **Demo data**: synthetic observations for prototype demonstration. Not real-time measurements.")

    st.divider()

    # Selected Location Analysis Section
    st.markdown(f"### 📍 Selected Location Analysis: `{selected_location}`")
    loc_row_meta = subset.iloc[selected_idx]
    
    m_col1, m_col2, m_col3 = st.columns([1.5, 3, 1.5])
    with m_col1:
        st.markdown(f"""
        **Coordinates**: `{float(loc_row_meta['latitude']):.4f}° N, {float(loc_row_meta['longitude']):.4f}° E`  
        **Observation Date**: `{loc_row_meta['date']}`  
        **Reasoning Engine**: `{result['mode']}`
        """)
    with m_col2:
        loc_kpi_cols = st.columns(4)
        loc_kpi_cols[0].metric("❤️ Health", f"{risk['health']}/100")
        loc_kpi_cols[1].metric("⚠ Risk Score", f"{risk['overall_risk']}/100")
        loc_kpi_cols[2].metric("☣ Pollution", f"{loc_row_meta['pollution_index']:.0f}/100")
        loc_kpi_cols[3].metric("💧 Oxygen", f"{loc_row_meta['dissolved_oxygen']:.1f} mg/L")

    with m_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧠 Run ORCA Analysis for This Location", type="primary", use_container_width=True):
            st.session_state["current_result"] = run_orca(row, user_api_key=user_api_key)
            st.rerun()

    # Domain Agent Findings & Collaborative Reasoning Output
    st.markdown("#### 🤖 Specialized Agent Evaluation & Collaborative Synthesis")
    ag_cols = st.columns(4)
    for c, ag in zip(ag_cols, result["agents"]):
        c_color = "critical" if ag['status']=='HIGH' else ('moderate' if ag['status']=='MODERATE' else 'low')
        with c:
            st.markdown(f"""
            <div class="agent-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; color:#38BDF8;">{ag['agent']}</div>
                    <span class="badge badge-{c_color}">{ag['status']}</span>
                </div>
                <div style="font-size:12px; color:#CBD5E1; margin-top:8px;">
                    • {ag['findings'][0] if ag['findings'] else 'Stable'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    r_panel_l, r_panel_r = st.columns([3, 2])
    with r_panel_l:
        st.markdown("##### 🧠 Collaborative ORCA Reasoning Synthesis")
        st.info(result["reasoning"].get("summary", ""))
        
        st.markdown("##### 🔎 Possible Cross-Domain Relationships")
        for rel in result["reasoning"].get("possible_relationships", []):
            st.markdown(f"- {rel}")
            
        st.markdown("##### ✅ Recommended Action Plan")
        for rec in result["reasoning"].get("recommendations", []):
            st.markdown(f"1. **{rec}**")

    with r_panel_r:
        st.markdown("##### ⚠️ Risk Factors & Uncertainties")
        f_df = pd.DataFrame({
            "Factor": list(risk["factors"].keys()),
            "Sub-Risk (%)": list(risk["factors"].values())
        }).sort_values(by="Sub-Risk (%)", ascending=True)
        
        fig_f = px.bar(f_df, x="Sub-Risk (%)", y="Factor", orientation="h", range_x=[0, 100], color="Sub-Risk (%)", color_continuous_scale="Reds")
        fig_f.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=260, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig_f, use_container_width=True)

        st.caption("⚠️ **Uncertainty & Disclaimer**:")
        for unc in result["reasoning"].get("uncertainties", []):
            st.caption(f"• {unc}")

    st.divider()

    # Location Risk Overview Table
    st.subheader("🌊 India Marine Risk Overview")
    st.caption("Comparative risk summary across all 12 Indian marine telemetry locations (sorted from highest ecosystem risk to lowest).")
    
    overview_table = locations_summary[["Location", "Risk Level", "Risk Score", "Health Score", "Pollution Index", "Temperature (°C)", "Oxygen (mg/L)"]]
    
    # Styled Dataframe display
    st.dataframe(
        overview_table,
        use_container_width=True,
        column_config={
            "Risk Score": st.column_config.ProgressColumn("Risk Score", format="%.1f", min_value=0, max_value=100),
            "Health Score": st.column_config.ProgressColumn("Health Score", format="%.1f", min_value=0, max_value=100)
        },
        hide_index=True
    )

    st.divider()

    # Production Data Integration Architecture Section
    st.subheader("🛰️ Production Data Integration")
    st.markdown("""
    **Data Ingestion Architecture & Real-World Telemetry Readiness**:
    - **Current Demonstration Layer**: ORCA currently operates over synthetic marine observations for hackathon demonstration.
    - **Modular Ingestion Pipeline**: Designed so that data feeds can be connected directly to production APIs:
      - 🌊 **INCOIS / NOAA Ocean Telemetry**: Sea Surface Temperature (SST), Dissolved Oxygen, Salinity.
      - 🛰️ **ISRO Oceansat & Sentinel-3 Satellites**: Chlorophyll-a concentration & Turbidity feeds.
      - 🛥️ **Coastal Buoy & Autonomous Sensors**: Real-time pH, plastic density, and hydrological surge data.
      - 🌦️ **IMD Weather Services**: Rainfall runoff, wind velocity, and wave height telemetry.
    """)

# ====================================================
# TAB 1: EXECUTIVE OVERVIEW (PRESERVED)
# ====================================================
with tab1:
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("🧠 Collaborative AI Synthesis")
        st.info(f"**Reasoning Engine**: {result['mode']} | **Confidence**: {result['reasoning'].get('confidence', 'High')}")
        st.markdown("#### Executive Summary")
        st.write(result["reasoning"].get("summary", ""))
        st.markdown("#### 🔎 Cross-Domain Relationships Identified")
        for rel in result["reasoning"].get("possible_relationships", []):
            st.markdown(f"- {rel}")
        st.markdown("#### ✅ Recommended Conservation & Action Plan")
        for rec in result["reasoning"].get("recommendations", []):
            st.markdown(f"1. **{rec}**")

    with col_right:
        st.subheader("⚠️ Key Risk Factor Breakdown")
        factors_df = pd.DataFrame({
            "Factor": list(risk["factors"].keys()),
            "Sub-Risk (%)": list(risk["factors"].values())
        }).sort_values(by="Sub-Risk (%)", ascending=True)
        
        fig_bar = px.bar(factors_df, x="Sub-Risk (%)", y="Factor", orientation="h", range_x=[0, 100], color="Sub-Risk (%)", color_continuous_scale="Reds", title="Ecosystem Risk Contributors")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

# ====================================================
# TAB 2: SPECIALIZED MULTI-AGENT NETWORK (PRESERVED)
# ====================================================
with tab2:
    st.subheader("🤖 Multi-Agent Domain Intelligence Network")
    st.caption("ORCA delegates marine analysis across 4 specialized autonomous agents operating over specific ocean parameters.")
    agent_grid = st.columns(2)
    for i, agent in enumerate(result["agents"]):
        with agent_grid[i % 2]:
            st_color = "critical" if agent['status']=='HIGH' else ('moderate' if agent['status']=='MODERATE' else 'low')
            with st.expander(f"🔹 {agent['agent']} — Status: {agent['status']}", expanded=True):
                st.markdown(f"**Agent Confidence Score**: `{agent['confidence']:.0%}`")
                st.markdown("**Key Domain Findings:**")
                for finding in agent["findings"]:
                    st.markdown(f"- {finding}")

# ====================================================
# TAB 3: ANALYTICS & SPATIAL TELEMETRY (PRESERVED)
# ====================================================
with tab3:
    col_map, col_chart = st.columns([1, 1])
    with col_map:
        st.subheader("🗺️ Local Observation Map")
        map_center = [float(row["latitude"]), float(row["longitude"])]
        m_local = folium.Map(location=map_center, zoom_start=6, tiles="OpenStreetMap")
        folium.CircleMarker(
            location=map_center, radius=10, color="#00F2FE", fill=True, fill_color="#00F2FE", fill_opacity=0.9,
            popup=f"<b>{selected_location}</b><br>Temp: {row['temperature']} °C<br>Pollution: {row['pollution_index']}"
        ).add_to(m_local)
        st_folium(m_local, width=None, height=400, key="local_map")

    with col_chart:
        st.subheader("📊 Temporal Parameter Trends")
        selected_metric = st.selectbox("Telemetry Metric", ["temperature", "dissolved_oxygen", "pollution_index", "fish_population_index", "algae_index", "coral_health_index", "ph", "plastic_index"])
        trend_df = subset.sort_values("date")
        fig_line = px.line(trend_df, x="date", y=selected_metric, markers=True, title=f"{selected_metric.replace('_',' ').title()} over Time ({selected_location})")
        fig_line.update_traces(line_color="#00F2FE", marker=dict(size=8, color="#38BDF8"))
        fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=350)
        st.plotly_chart(fig_line, use_container_width=True)

# ====================================================
# TAB 4: WHAT-IF SIMULATION SANDBOX (PRESERVED & EXTENDED)
# ====================================================
with tab4:
    st.subheader(f"🔬 Interactive What-If Scenario Simulator ({selected_location})")
    st.caption("Modify environmental factors for the selected location to test dynamic intervention impact.")
    
    sim_col1, sim_col2, sim_col3, sim_col4 = st.columns(4)
    with sim_col1:
        delta_temp = st.slider("Temperature Shift (°C)", -4.0, 4.0, 0.0, 0.5)
    with sim_col2:
        delta_poll = st.slider("Pollution Shift", -50, 50, 0, 5)
    with sim_col3:
        delta_oxy = st.slider("Oxygen Shift (mg/L)", -4.0, 3.0, 0.0, 0.5)
    with sim_col4:
        delta_plastic = st.slider("Plastic Shift", -40, 40, 0, 5)

    sim_row = dict(row)
    sim_row["temperature"] = float(row["temperature"]) + delta_temp
    sim_row["pollution_index"] = max(0.0, min(100.0, float(row["pollution_index"]) + delta_poll))
    sim_row["dissolved_oxygen"] = max(0.5, float(row["dissolved_oxygen"]) + delta_oxy)
    sim_row["plastic_index"] = max(0.0, min(100.0, float(row.get("plastic_index", 20.0)) + delta_plastic))

    sim_risk = risk_from_row(sim_row)
    sim_result = run_orca(sim_row, user_api_key=user_api_key)

    risk_diff = sim_risk['overall_risk'] - risk['overall_risk']
    diff_str = f"Risk increased by {abs(risk_diff):.1f} points" if risk_diff > 0 else (f"Risk decreased by {abs(risk_diff):.1f} points" if risk_diff < 0 else "No risk change")

    st.markdown("#### Scenario Impact Comparison")
    cmp1, cmp2, cmp3, cmp4 = st.columns(4)
    cmp1.metric("Current Risk", f"{risk['overall_risk']:.1f}")
    cmp2.metric("Simulated Risk", f"{sim_risk['overall_risk']:.1f}", delta=f"{risk_diff:.1f}", delta_color="inverse")
    cmp3.metric("Current Ecosystem Health", f"{risk['health']:.1f}")
    cmp4.metric("Simulated Ecosystem Health", f"{sim_risk['health']:.1f}", delta=f"{sim_risk['health'] - risk['health']:.1f}")

    if risk_diff > 0:
        st.warning(f"⚠️ **Scenario Result**: {diff_str}")
    elif risk_diff < 0:
        st.success(f"✅ **Scenario Result**: {diff_str}")

# ====================================================
# TAB 5: REPORT & PRESENTATION EXPORT (PRESERVED)
# ====================================================
with tab5:
    st.subheader("📄 ORCA Decision Support Report Generator")
    st.caption("Generate and download a comprehensive markdown report for SIH presentations or stakeholder briefing.")
    report_md = make_report(row, result)
    st.download_button(
        label="📥 Download Official ORCA Markdown Report",
        data=report_md,
        file_name=f"ORCA_Report_{selected_location.replace(' ', '_')}_{row['date']}.md",
        mime="text/markdown",
        type="primary"
    )
    st.markdown("### Report Preview")
    st.markdown(report_md)

# Footer
st.divider()
st.caption("🌊 **ORCA (SIH26176 Prototype)** — Smart India Hackathon 2026. Built with Python, Streamlit, Plotly, Folium, and Google Gemini AI.")
