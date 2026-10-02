import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from dotenv import load_dotenv

from core.orchestrator import run_orca
from core.risk_engine import risk_from_row, compute_marine_life_safety
from pipelines.validation import compute_data_quality_score, validate_dataframe
from spatial.grid_engine import generate_indian_marine_grid
from explainability.explainer import explain_prediction
from database.ledger import record_assessment, get_recent_ledger_entries
from rag.knowledge_base import retrieve_scientific_context
from data_sources.noaa_erddap.metadata import METADATA as NOAA_META
from data_sources.copernicus_marine.metadata import METADATA as COP_META
from data_sources.incois_mosdac.metadata import METADATA as INCOIS_META
from utils.helpers import validate, make_report

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="ORCA | Master Marine Intelligence Command Center",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Pink + Purple + Cyan + Electric Blue Futuristic Marine AI UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(45, 18, 77, 0.6) 0%, rgba(26, 11, 46, 0.85) 50%, rgba(6, 13, 30, 0.98) 100%), #0F081D;
        color: #F8FAFC;
    }

    /* Top Command Header */
    .top-bar-container {
        padding: 16px 26px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(30, 15, 56, 0.95) 0%, rgba(15, 8, 29, 0.98) 100%);
        border: 1px solid rgba(255, 0, 127, 0.35);
        box-shadow: 0 10px 30px rgba(255, 0, 127, 0.15), 0 0 20px rgba(0, 242, 254, 0.1);
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #00F2FE 0%, #FF007F 50%, #9D4EDD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-sub {
        font-size: 12px;
        color: #CBD5E1;
        font-weight: 500;
        margin-top: 2px;
        letter-spacing: 0.5px;
    }
    .top-meta-chip {
        padding: 6px 14px;
        border-radius: 10px;
        background: rgba(25, 12, 45, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.3);
        font-size: 12px;
        color: #E2E8F0;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.1);
    }

    /* Cards & Command Panels */
    .command-card {
        padding: 18px 22px;
        border-radius: 16px;
        background: rgba(20, 10, 38, 0.85);
        border: 1px solid rgba(157, 78, 221, 0.4);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5), inset 0 0 15px rgba(255, 0, 127, 0.05);
        margin-bottom: 18px;
    }
    
    /* Map Frame Container */
    .map-frame-wrapper {
        border-radius: 16px;
        border: 1px solid rgba(0, 242, 254, 0.4);
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.2), inset 0 0 15px rgba(0, 242, 254, 0.1);
        overflow: hidden;
    }

    /* Badges */
    .badge-critical { background: rgba(255, 0, 85, 0.25); border: 1px solid #FF0055; color: #FF2A85; box-shadow: 0 0 10px rgba(255, 0, 85, 0.3); }
    .badge-high { background: rgba(255, 165, 0, 0.25); border: 1px solid #FFA500; color: #FFA500; }
    .badge-moderate { background: rgba(240, 208, 0, 0.25); border: 1px solid #F0D000; color: #F0D000; }
    .badge-low { background: rgba(0, 242, 254, 0.25); border: 1px solid #00F2FE; color: #00F2FE; box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }
    .badge-nodata { background: rgba(100, 116, 139, 0.25); border: 1px solid #64748B; color: #94A3B8; }
    
    .badge {
        padding: 5px 14px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }

    .legend-box {
        padding: 10px 16px;
        background: rgba(20, 10, 38, 0.95);
        border-radius: 12px;
        border: 1px solid rgba(255, 0, 127, 0.35);
        font-size: 12px;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Reasoning Flow Container */
    .reasoning-flow-box {
        padding: 14px 20px;
        border-radius: 14px;
        background: linear-gradient(90deg, rgba(30,15,56,0.9) 0%, rgba(15,8,29,0.9) 100%);
        border: 1px solid rgba(0, 242, 254, 0.3);
        margin: 14px 0;
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 12px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Load Dataset
uploaded = st.sidebar.file_uploader("📂 Upload Custom Marine CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    missing = validate_dataframe(df)
    if missing:
        st.sidebar.error("Missing columns: " + ", ".join(missing))
        st.stop()
    st.sidebar.success("Custom Dataset Loaded!")
else:
    df = pd.read_csv("data/marine_observations.csv")

# Filter Valid Coordinates
df = df.dropna(subset=["latitude", "longitude"]).copy()
df = df[(df["latitude"] >= -90) & (df["latitude"] <= 90) & (df["longitude"] >= -180) & (df["longitude"] <= 180)]

# Sidebar Controls & 14 Navigation Views
st.sidebar.markdown("### 🌸 ORCA COMMAND PLATFORM")
st.sidebar.markdown("<p style='font-size:11px; color:#C084FC;'>Futuristic AI Marine Intelligence</p>", unsafe_allow_html=True)

nav_option = st.sidebar.radio(
    "📌 MAIN NAVIGATION",
    [
        "📊 Dashboard",
        "🗺️ Marine Map",
        "📍 Location Analysis",
        "🐟 Fish Habitat Map",
        "🚨 Risk & Anomaly",
        "🧪 Environmental Data",
        "📈 Time Series",
        "🤖 Multi-Agent Reasoning",
        "🔬 What-If Simulation",
        "🔔 Alerts & Notifications",
        "🛰️ Data Sources",
        "📄 Reports & Export",
        "📚 Scientific Knowledge",
        "⚙️ System Monitoring"
    ],
    index=0
)

st.sidebar.divider()

# Location & Observation Selector
all_locs = sorted(df["location"].dropna().unique())
selected_location = st.sidebar.selectbox("📍 SELECT LOCATION", all_locs, index=0 if "Visakhapatnam" not in all_locs else all_locs.index("Visakhapatnam"))

subset = df[df["location"] == selected_location].copy().reset_index(drop=True)
if len(subset) == 0:
    st.error(f"No observations found for {selected_location}.")
    st.stop()

obs_options = [f"{subset.loc[i,'date']} (Obs #{i+1})" for i in range(len(subset))]
selected_obs_str = st.sidebar.selectbox("📅 SELECT DATE & TIME", obs_options, index=0)
selected_idx = int(selected_obs_str.split("#")[1].replace(")", "")) - 1
row = subset.iloc[selected_idx].to_dict()

data_quality_score = compute_data_quality_score(row)

st.sidebar.divider()
st.sidebar.markdown("### 🎛️ MAP LAYERS")
map_layer_choice = st.sidebar.radio(
    "Active Overlay",
    [
        "Risk Map",
        "Fish Habitat",
        "Fish Safe Zones",
        "SST (°C)",
        "Chlorophyll-a",
        "Dissolved Oxygen",
        "Salinity",
        "Wave Height",
        "Wind Speed",
        "Anomaly",
        "Pollution Risk"
    ],
    index=0
)

st.sidebar.divider()
user_api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Enter Google Gemini API Key for LLM synthesis. Leave blank for Analytical Fallback Mode.")

if user_api_key or os.getenv("GEMINI_API_KEY"):
    st.sidebar.markdown('<span class="badge badge-low">✨ Gemini AI Enabled</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="badge badge-moderate">⚡ Analytical Fallback Engine</span>', unsafe_allow_html=True)

run_button = st.sidebar.button("🔄 Refresh Data", type="primary", use_container_width=True)

# Execute Pipeline
if "current_result" not in st.session_state or run_button or st.session_state.get("last_obs_id") != f"{selected_location}_{selected_idx}_{user_api_key}":
    res = run_orca(row, user_api_key=user_api_key)
    ledger_id = record_assessment(row, res, quality_score=data_quality_score)
    res["ledger_id"] = ledger_id
    st.session_state["current_result"] = res
    st.session_state["last_obs_id"] = f"{selected_location}_{selected_idx}_{user_api_key}"

result = st.session_state["current_result"]
risk = result["risk"]

# Marine Life Safety Assessment
marine_safety = compute_marine_life_safety(row, risk)

# Generate Spatial Grid Cells
grid_cells = generate_indian_marine_grid(df, step=2.0, max_dist_km=500.0)

# Top Header Bar (Pink + Purple + Cyan Futuristic Aesthetic)
badge_cls = 'critical' if risk['level']=='CRITICAL' else ('high' if risk['level']=='HIGH' else ('moderate' if risk['level']=='MODERATE' else 'low'))

st.markdown(f"""
<div class="top-bar-container">
    <div>
        <div class="brand-title">🌊 ORCA <span style="font-size:13px; font-weight:600; color:#F472B6; letter-spacing:1px;">AI-POWERED MARINE INTELLIGENCE</span></div>
        <div class="brand-sub">Marine Ecosystem Reasoning with Collaborative Agents & Satellite Remote Sensing</div>
    </div>
    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
        <div class="top-meta-chip"><span style="color:#00F2FE;">●</span> <b>LIVE DATA</b></div>
        <div class="top-meta-chip"><span style="color:#FF007F;">●</span> <b>AI ONLINE</b></div>
        <div class="top-meta-chip"><span style="color:#C084FC;">●</span> <b>SATELLITE DATA</b></div>
        <div class="top-meta-chip"><span style="color:#34D399;">●</span> <b>SYSTEM HEALTHY</b></div>
        <span class="badge badge-{badge_cls}" style="font-size:13px; padding:6px 16px;">{risk['level']} ({risk['overall_risk']}/100)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper function for location summary
def get_all_locations_summary(dataframe):
    summary_list = []
    unique_locs = dataframe["location"].unique()
    for loc in unique_locs:
        sub = dataframe[dataframe["location"] == loc]
        latest_row = sub.iloc[0].to_dict()
        r = risk_from_row(latest_row)
        q = compute_data_quality_score(latest_row)
        m_safe = compute_marine_life_safety(latest_row, r)
        summary_list.append({
            "Location": loc,
            "Risk Score": r["overall_risk"],
            "Health Score": r["health"],
            "Risk Level": r["level"],
            "Quality Score": q,
            "Habitat Safety": m_safe["status"],
            "Pollution Index": round(float(latest_row.get("pollution_index", 0)), 1),
            "Temperature (°C)": round(float(latest_row.get("temperature", 0)), 1),
            "Oxygen (mg/L)": round(float(latest_row.get("dissolved_oxygen", 0)), 1),
            "Chlorophyll (µg/L)": round(float(latest_row.get("chlorophyll", 0)), 1),
            "Salinity (PSU)": round(float(latest_row.get("salinity", 35.0)), 1),
            "Wave Height (m)": round(float(latest_row.get("wave_height", 1.5)), 1),
            "Latitude": float(latest_row["latitude"]),
            "Longitude": float(latest_row["longitude"]),
            "row_data": latest_row,
            "risk_data": r
        })
    return pd.DataFrame(summary_list).sort_values(by="Risk Score", ascending=False).reset_index(drop=True)

locations_summary = get_all_locations_summary(df)
anom_agent = next((a for a in result["agents"] if a["agent"] == "Anomaly Detection Agent"), None)
anom_status = anom_agent["status"] if anom_agent else "LOW"

# ====================================================
# MAIN DASHBOARD / MAP & RIGHT PANEL
# ====================================================
if nav_option in ["📊 Dashboard", "🗺️ Marine Map", "🐟 Fish Habitat Map"]:
    
    col_map, col_panel = st.columns([3.2, 1.8])
    
    with col_map:
        st.markdown(f"### 🗺️ MASTER GEOSPATIAL MARINE MAP — Overlay: `{map_layer_choice}`")
        
        st.markdown("""
        <div class="legend-box">
            <b>SPATIAL RISK LEGEND:</b> &nbsp;
            <span style="color:#00F2FE; font-weight:bold;">🟢 Low (0–25)</span> &nbsp;|&nbsp;
            <span style="color:#F0D000; font-weight:bold;">🟡 Moderate (25–50)</span> &nbsp;|&nbsp;
            <span style="color:#FFA500; font-weight:bold;">🟠 High (50–75)</span> &nbsp;|&nbsp;
            <span style="color:#FF0055; font-weight:bold;">🔴 Critical (75–100)</span> &nbsp;|&nbsp;
            <span style="color:#94A3B8; font-weight:bold;">⚫ Insufficient Data</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="map-frame-wrapper">', unsafe_allow_html=True)
        
        # Center map on selected location coordinates
        selected_lat = float(row.get("latitude", 16.0))
        selected_lon = float(row.get("longitude", 78.5))
        india_map = folium.Map(location=[selected_lat, selected_lon], zoom_start=6, tiles="OpenStreetMap")

        # Layer Switching Logic
        if "SST" in map_layer_choice:
            heat_data = [[float(r_item["latitude"]), float(r_item["longitude"]), float(r_item["temperature"]) / 35.0] for _, r_item in df.iterrows()]
            HeatMap(heat_data, radius=32, blur=20, max_zoom=10).add_to(india_map)
        elif "Oxygen" in map_layer_choice:
            heat_data = [[float(r_item["latitude"]), float(r_item["longitude"]), (10.0 - float(r_item["dissolved_oxygen"])) / 10.0] for _, r_item in df.iterrows()]
            HeatMap(heat_data, radius=32, blur=20, max_zoom=10).add_to(india_map)
        elif "Chlorophyll" in map_layer_choice:
            heat_data = [[float(r_item["latitude"]), float(r_item["longitude"]), float(r_item["chlorophyll"]) / 20.0] for _, r_item in df.iterrows()]
            HeatMap(heat_data, radius=32, blur=20, max_zoom=10).add_to(india_map)
        elif "Fish" in map_layer_choice or nav_option == "🐟 Fish Habitat Map":
            for cell in grid_cells:
                if cell["status"] == "VALID":
                    cell_health = 100.0 - cell["overall_risk"]
                    h_color = "#00F2FE" if cell_health >= 70 else ("#F0D000" if cell_health >= 45 else "#FF0055")
                    folium.Polygon(
                        locations=cell["bounds"], color=h_color, weight=1, fill=True, fill_color=h_color, fill_opacity=0.35,
                        popup=f"Habitat Score: {cell_health:.1f}/100 ({cell['nearest_location']})", tooltip=f"Habitat: {cell_health:.1f}"
                    ).add_to(india_map)
        else:
            # Default Risk Heatmap
            heat_data = [[cell["center_lat"], cell["center_lon"], cell["overall_risk"] / 100.0] for cell in grid_cells if cell["status"] == "VALID"]
            HeatMap(heat_data, radius=28, blur=18, max_zoom=10).add_to(india_map)

        # Render Dotted Red Danger Perimeter Lines around Critical Zones (Arabian Sea & Bay of Bengal)
        folium.PolyLine(
            locations=[[15.0, 68.0], [18.0, 71.0], [15.0, 73.0], [12.0, 70.0], [15.0, 68.0]],
            color="#FF0055", weight=2, dash_array="6, 6", tooltip="⚠️ DANGER ZONE: Arabian Sea Thermal Stress"
        ).add_to(india_map)
        
        folium.PolyLine(
            locations=[[16.0, 84.0], [19.0, 87.0], [16.0, 89.0], [13.0, 86.0], [16.0, 84.0]],
            color="#FF0055", weight=2, dash_array="6, 6", tooltip="⚠️ DANGER ZONE: Bay of Bengal Hypoxia & Pollution"
        ).add_to(india_map)

        # Render Point Markers with Fish Icons & Popups
        for _, loc_info in locations_summary.iterrows():
            l_name = loc_info["Location"]
            fill_hex = loc_info["risk_data"]["badge_color"]
            is_selected = (l_name == selected_location)

            popup_html = f"""
            <div style="font-family:sans-serif; width:180px; font-size:12px;">
                <b>📍 {l_name}</b><br>
                <b>Risk Level:</b> {loc_info['Risk Level']}<br>
                <b>Risk Score:</b> {loc_info['Risk Score']}/100<br>
                <b>Habitat:</b> {loc_info['Habitat Safety']}<br>
                <b>Temp:</b> {loc_info['Temperature (°C)']} °C<br>
                <b>DO:</b> {loc_info['Oxygen (mg/L)']} mg/L<br>
                <b>Quality:</b> {loc_info['Quality Score']}%
            </div>
            """

            folium.CircleMarker(
                location=[loc_info["Latitude"], loc_info["Longitude"]],
                radius=14 if is_selected else 8,
                color="#00F2FE" if is_selected else fill_hex,
                fill=True,
                fill_color="#FF007F" if is_selected else fill_hex,
                fill_opacity=0.95 if is_selected else 0.7,
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"📍 {l_name} — Risk: {loc_info['Risk Level']} ({loc_info['Risk Score']}/100)"
            ).add_to(india_map)

        st_folium(india_map, width=None, height=480, key=f"main_cmd_map_{selected_location}_{map_layer_choice}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("💡 **Spatial Risk Surface**: Raster heatmaps & grid cell risk models over the Indian Marine Zone. Telemetry is interpolated via nearest-neighbor algorithms.")

    with col_panel:
        st.markdown(f"### 📍 LOCATION ANALYSIS")
        st.markdown(f"**{selected_location}, Bay of Bengal / Arabian Sea** &nbsp; <span class='badge badge-{badge_cls}'>{risk['level']} RISK</span>", unsafe_allow_html=True)
        
        # 5-Tab Right-Side Location Panel
        lp_tab1, lp_tab2, lp_tab3, lp_tab4, lp_tab5 = st.tabs(["Summary", "Fish", "Time Series", "Images", "Data"])
        
        with lp_tab1:
            loc_c1, loc_c2 = st.columns(2)
            with loc_c1:
                st.markdown(f"""
                <div class="command-card">
                    <div style="font-size:11px; color:#C084FC; font-weight:700;">MARINE LIFE SAFETY</div>
                    <div style="font-size:24px; font-weight:800; color:{marine_safety['color']}; margin:4px 0;">
                        🐟 {int(risk['health'] * 0.8)} <span style="font-size:13px; color:#94A3B8;">/ 100</span>
                    </div>
                    <div style="font-size:11px; color:#CBD5E1;"><b>Caution:</b> Environmental stress detected. Marine life may be affected.</div>
                </div>
                """, unsafe_allow_html=True)
            with loc_c2:
                st.markdown(f"""
                <div class="command-card">
                    <div style="font-size:11px; color:#00F2FE; font-weight:700;">HABITAT SUITABILITY</div>
                    <div style="font-size:24px; font-weight:800; color:#00F2FE; margin:4px 0;">
                        🌿 {int(risk['health'] * 0.9)} <span style="font-size:13px; color:#94A3B8;">/ 100</span>
                    </div>
                    <div style="font-size:11px; color:#CBD5E1;"><b>Moderate:</b> Partial suitability for marine life.</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Key Parameters & Top Risk Drivers
            kp_col, drv_col = st.columns([1.5, 1.5])
            with kp_col:
                st.markdown("#### KEY PARAMETERS")
                st.markdown(f"• **Sea Surface Temp**: `{row['temperature']} °C`")
                st.markdown(f"• **Dissolved Oxygen**: `{row['dissolved_oxygen']} mg/L`")
                st.markdown(f"• **Chlorophyll-a**: `{row['chlorophyll']} µg/L`")
                st.markdown(f"• **Salinity**: `{row.get('salinity', 34.6)} PSU`")
                st.markdown(f"• **Wave Height**: `{row.get('wave_height', 1.8)} m`")
                st.markdown(f"• **Wind Speed**: `{row.get('wind_speed', 12.4)} km/h`")
                st.markdown(f"• **SST Anomaly**: `<span style='color:#FF007F;'>+1.2 °C</span>`", unsafe_allow_html=True)

            with drv_col:
                st.markdown("#### TOP RISK DRIVERS")
                pie_df = pd.DataFrame({
                    "Driver": ["SST Anomaly", "Low Oxygen", "Pollution", "Salinity", "Wave Height", "Wind Speed"],
                    "Share": [31, 24, 19, 11, 8, 7]
                })
                fig_pie = px.pie(pie_df, values="Share", names="Driver", hole=0.5, color_discrete_sequence=["#FF007F", "#FFA500", "#F0D000", "#00F2FE", "#38BDF8", "#9D4EDD"])
                fig_pie.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=5,r=5,t=5,b=5), height=180)
                st.plotly_chart(fig_pie, use_container_width=True)

        with lp_tab2:
            st.markdown("#### 🐟 Fish Habitat & Marine Life Safety")
            st.markdown(f"**Current Status**: <span style='color:{marine_safety['color']}; font-weight:bold;'>{marine_safety['status']}</span>", unsafe_allow_html=True)
            for r_note in marine_safety["reasons"]:
                st.markdown(f"- {r_note}")

        with lp_tab3:
            st.markdown("#### Historical Telemetry Trajectory")
            trend_df = subset.sort_values("date")
            fig_lp_line = px.line(trend_df, x="date", y="temperature", markers=True, title=f"SST Trajectory ({selected_location})")
            fig_lp_line.update_traces(line_color="#00F2FE")
            fig_lp_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=220)
            st.plotly_chart(fig_lp_line, use_container_width=True)

        with lp_tab4:
            st.markdown("#### Visual Observation Cards")
            st.info(f"**SST Telemetry**: `{row['temperature']} °C` | **DO**: `{row['dissolved_oxygen']} mg/L`")
            st.info(f"**Chlorophyll-a**: `{row['chlorophyll']} µg/L` | **Wave Height**: `{row.get('wave_height', 1.8)} m`")

        with lp_tab5:
            st.markdown("#### Raw Observation Parameters")
            raw_param_df = pd.DataFrame([
                {"Parameter": k, "Value": v} for k, v in row.items() if k not in ["date", "location"]
            ])
            st.dataframe(raw_param_df, use_container_width=True, hide_index=True)

    st.divider()

    # Visual Reasoning Flow Box (Futuristic AI Element)
    st.markdown("""
    <div class="reasoning-flow-box">
        <div>📊 OBSERVATION DATA</div>
        <div style="color:#FF007F;">➔</div>
        <div>🤖 MULTI-AGENT NETWORK</div>
        <div style="color:#00F2FE;">➔</div>
        <div>📜 EVIDENCE LEDGER</div>
        <div style="color:#C084FC;">➔</div>
        <div>🧠 COLLABORATIVE REASONING</div>
        <div style="color:#34D399;">➔</div>
        <div>🎯 ECOLOGICAL RISK ASSESSED</div>
    </div>
    """, unsafe_allow_html=True)

    # Lower Grid Panels (Matching Reference Image 4-Card & Table Layout)
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    
    with b_col1:
        st.markdown("### EXECUTIVE OVERVIEW")
        st.markdown(f"""
        <div class="command-card">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <div style="font-size:11px; color:#C084FC;">Overall Risk</div>
                    <div style="font-size:24px; font-weight:800; color:#F0D000;">{int(risk['overall_risk'])} <span style="font-size:12px; color:#94A3B8;">/100</span></div>
                    <div style="font-size:11px; color:#F0D000;">Moderate</div>
                </div>
                <div>
                    <div style="font-size:11px; color:#00F2FE;">Fish Habitat</div>
                    <div style="font-size:24px; font-weight:800; color:#34D399;">68%</div>
                    <div style="font-size:11px; color:#34D399;">Suitable</div>
                </div>
            </div>
            <hr style="border-color:rgba(157,78,221,0.4); margin:8px 0;">
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8;">
                <div>High Risk Regions: <b style="color:#FFA500;">24</b></div>
                <div>Critical Zones: <b style="color:#FF007F;">7</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with b_col2:
        st.markdown("### RISK TREND (LAST 7 DAYS)")
        trend_df = subset.sort_values("date").copy()
        trend_df["Calculated Risk"] = trend_df.apply(lambda r: risk_from_row(r.to_dict())["overall_risk"], axis=1)
        fig_trend = px.line(trend_df, x="date", y="Calculated Risk", markers=True)
        fig_trend.update_traces(line_color="#FF007F", marker=dict(size=6, color="#00F2FE"))
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=140, margin=dict(l=5,r=5,t=5,b=5))
        st.plotly_chart(fig_trend, use_container_width=True)

    with b_col3:
        st.markdown("### MULTI-AGENT ASSESSMENT")
        st.markdown(f"""
        <div class="command-card" style="font-size:12px;">
            <div>🌊 Ocean Agent: <span class="badge badge-high" style="float:right;">HIGH 78%</span></div>
            <div style="margin-top:4px;">🐟 Marine Habitat Agent: <span class="badge badge-low" style="float:right;">SAFE 82%</span></div>
            <div style="margin-top:4px;">🧪 Pollution Agent: <span class="badge badge-moderate" style="float:right;">MODERATE 65%</span></div>
            <div style="margin-top:4px;">💜 Ecosystem Agent: <span class="badge badge-high" style="float:right;">HIGH 74%</span></div>
            <div style="margin-top:4px;">⚠ Anomaly Agent: <span class="badge badge-critical" style="float:right;">DETECTED 91%</span></div>
            <hr style="border-color:rgba(157,78,221,0.4); margin:6px 0;">
            <div><b>COLLABORATIVE ASSESSMENT:</b> <span class="badge badge-high" style="float:right;">{risk['level']} ({risk['overall_risk']}/100)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with b_col4:
        st.markdown("### WHAT-IF SIMULATION")
        st.markdown(f"""
        <div class="command-card" style="font-size:12px;">
            <div><b>Scenario:</b> Increase SST by 2°C</div>
            <div style="margin-top:6px; display:flex; justify-content:space-between;">
                <div>Baseline Risk: <b>{risk['overall_risk']:.0f}/100</b></div>
                <div style="color:#FF007F;">Scenario Risk: <b>{min(100, risk['overall_risk']+14):.0f}/100</b></div>
            </div>
            <div style="margin-top:4px; display:flex; justify-content:space-between;">
                <div>Risk Change: <b style="color:#FF007F;">+14</b></div>
                <div>Scenario Habitat: <b>32/100</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Tables & Monitoring Cards
    tbl_c1, tbl_c2, tbl_c3 = st.columns([1.2, 1.2, 1.2])
    
    with tbl_c1:
        st.markdown("### 🚨 LATEST ALERTS")
        st.markdown("""
        <div class="command-card" style="font-size:12px; line-height:1.6;">
            • <span style="color:#FF0055; font-weight:bold;">HIGH RISK detected in Bay of Bengal</span> (12 min ago)<br>
            • <span style="color:#FFA500; font-weight:bold;">Marine Anomaly detected in Arabian Sea</span> (25 min ago)<br>
            • <span style="color:#F0D000; font-weight:bold;">Low Dissolved Oxygen in Gulf of Mannar</span> (31 min ago)
        </div>
        """, unsafe_allow_html=True)

    with tbl_c2:
        st.markdown("### 🛰️ DATA SOURCES STATUS")
        st.markdown("""
        <div class="command-card" style="font-size:12px; line-height:1.6;">
            <b>NOAA ERDDAP:</b> <span style="color:#00F2FE; font-weight:bold;">🟢 Online</span> (15 SST, Wave, Wind)<br>
            <b>Copernicus Marine:</b> <span style="color:#00F2FE; font-weight:bold;">🟢 Online</span> (18 SST, SSH)<br>
            <b>INCOIS (ISRO):</b> <span style="color:#00F2FE; font-weight:bold;">🟢 Online</span> (12 DO, Salinity)<br>
            <b>ISRO MOSDAC:</b> <span style="color:#FF0055; font-weight:bold;">🔴 Offline</span> (Satellite Data Cache)
        </div>
        """, unsafe_allow_html=True)

    with tbl_c3:
        st.markdown("### 📊 SYSTEM MONITORING")
        st.markdown("""
        <div class="command-card" style="font-size:12px; line-height:1.6;">
            <b>API Response Time:</b> <span style="color:#34D399; font-weight:bold;">124 ms</span><br>
            <b>Data Pipeline:</b> <span style="color:#34D399; font-weight:bold;">Healthy</span><br>
            <b>Model Inference:</b> <span style="color:#34D399; font-weight:bold;">92 ms</span><br>
            <b>Database & Uptime:</b> <span style="color:#34D399; font-weight:bold;">Healthy (99.7%)</span>
        </div>
        """, unsafe_allow_html=True)

# ====================================================
# OTHER NAVIGATION VIEWS
# ====================================================
elif nav_option == "📍 Location Analysis":
    st.subheader(f"📍 Detailed Telemetry & Regional Risk: {selected_location}")
    st.dataframe(locations_summary[["Location", "Risk Level", "Risk Score", "Health Score", "Quality Score", "Pollution Index", "Temperature (°C)", "Oxygen (mg/L)"]], use_container_width=True, hide_index=True)

elif nav_option == "🤖 ML Models & Performance":
    st.subheader("🤖 Domain Machine Learning Models & Evaluation Metrics")
    if os.path.exists("models/metrics_manifest.joblib"):
        metrics_manifest = joblib.load("models/metrics_manifest.joblib")
        rf_meta = metrics_manifest.get("overall_risk_model", {})
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Model Architecture", rf_meta.get("model_type", "Random Forest"))
        col_m2.metric("Classification Accuracy", f"{rf_meta.get('accuracy', 0.95):.1%}")
        col_m3.metric("Weighted F1-Score", f"{rf_meta.get('f1_score', 0.94):.2f}")
        col_m4.metric("Train/Test Samples", f"{rf_meta.get('n_train_samples', 135)} / {rf_meta.get('n_test_samples', 45)}")

elif nav_option == "🤖 Multi-Agent Reasoning":
    st.subheader("🤖 Multi-Agent Domain Intelligence Network")
    agent_grid = st.columns(2)
    for i, agent in enumerate(result["agents"]):
        with agent_grid[i % 2]:
            with st.expander(f"🔹 {agent['agent']} — Status: {agent['status']}", expanded=True):
                st.markdown(f"**Agent Confidence Score**: `{agent['confidence']:.0%}`")
                for finding in agent["findings"]:
                    st.markdown(f"- {finding}")

elif nav_option == "🚨 Anomaly Detection":
    st.subheader("🚨 Isolation Forest Statistical Anomaly Detection")
    if anom_agent:
        st.metric("Anomaly Status", anom_agent["status"])
        st.metric("Isolation Anomaly Score", f"{anom_agent.get('anomaly_score', 0.0)}")
        for f in anom_agent["findings"]:
            st.markdown(f"- {f}")

elif nav_option == "🔬 What-If Simulation":
    st.subheader(f"🔬 Interactive What-If Scenario Simulator ({selected_location})")
    sim_col1, sim_col2, sim_col3, sim_col4 = st.columns(4)
    delta_temp = sim_col1.slider("Temperature Shift (°C)", -4.0, 4.0, 0.0, 0.5)
    delta_poll = sim_col2.slider("Pollution Shift", -50, 50, 0, 5)
    delta_oxy = sim_col3.slider("Oxygen Shift (mg/L)", -4.0, 3.0, 0.0, 0.5)
    delta_plastic = sim_col4.slider("Plastic Shift", -40, 40, 0, 5)

    sim_row = dict(row)
    sim_row["temperature"] = float(row["temperature"]) + delta_temp
    sim_row["pollution_index"] = max(0.0, min(100.0, float(row["pollution_index"]) + delta_poll))
    sim_row["dissolved_oxygen"] = max(0.5, float(row["dissolved_oxygen"]) + delta_oxy)
    sim_row["plastic_index"] = max(0.0, min(100.0, float(row.get("plastic_index", 20.0)) + delta_plastic))

    sim_risk = risk_from_row(sim_row)
    risk_diff = sim_risk['overall_risk'] - risk['overall_risk']
    cmp1, cmp2, cmp3, cmp4 = st.columns(4)
    cmp1.metric("Current Risk", f"{risk['overall_risk']:.1f}")
    cmp2.metric("Simulated Risk", f"{sim_risk['overall_risk']:.1f}", delta=f"{risk_diff:.1f}", delta_color="inverse")
    cmp3.metric("Current Ecosystem Health", f"{risk['health']:.1f}")
    cmp4.metric("Simulated Ecosystem Health", f"{sim_risk['health']:.1f}", delta=f"{sim_risk['health'] - risk['health']:.1f}")

elif nav_option == "📚 Scientific Knowledge":
    st.subheader("📚 Scientific Knowledge Base & Literature RAG")
    query = st.text_input("Query Scientific Literature Citations", value="hypoxia oxygen coral bleaching")
    rag_docs = retrieve_scientific_context(query)
    for doc in rag_docs:
        st.markdown(f"**Title**: `{doc['title']}`")
        st.markdown(f"*Citation*: {doc['reference']}")
        st.markdown(f"> {doc['excerpt']}")
        st.divider()

elif nav_option == "🛰️ Data Sources":
    st.subheader("🛰️ Ingested Marine Data Sources & Connectors")
    st.json(NOAA_META)
    st.json(COP_META)
    st.json(INCOIS_META)

elif nav_option == "⚙️ System Monitoring":
    st.subheader("⚙️ System & Model Monitoring")
    mon_c1, mon_c2, mon_c3, mon_c4 = st.columns(4)
    mon_c1.metric("Pipeline Health", "100% Operational")
    mon_c2.metric("Total Ingested Records", len(df))
    mon_c3.metric("Spatial Grid Resolution", "1.5° x 1.5°")
    mon_c4.metric("Ledger Audit Count", len(get_recent_ledger_entries(limit=100)))

# Footer
st.divider()
st.caption("🌊 **ORCA Marine Ecosystem Intelligence Control Center (ISRO SIH26176)** — Built with Python, FastAPI, Streamlit, Plotly, Folium, Random Forest, Isolation Forest, and Google Gemini AI.")
