# 🌊 ORCA — Marine Ecosystem Reasoning with Collaborative Agents

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**ORCA** is an operational, real-data marine ecosystem intelligence platform developed for **ISRO SIH26176**. It combines specialized multi-agent reasoning networks, domain machine learning models, geospatial grid-cell risk mapping, and an immutable SQLite evidence ledger to provide decision support over the Indian Marine Zone (Arabian Sea, Bay of Bengal, Indian Ocean, Andaman & Nicobar, Lakshadweep).

---

## 🎯 Problem Statement (SIH26176 - ISRO)
* **Title**: `SIH26176 – ORCA – Marine Ecosystem Reasoning with Collaborative Agents`
* **Organization**: ISRO (Indian Space Research Organisation)
* **Theme**: Miscellaneous / Marine Remote Sensing & Satellite Intelligence
* **Goal**: Provide automated, explainable, real-data ecosystem risk intelligence, spatial risk heatmaps, marine habitat safety classification, and multi-agent collaborative reasoning over satellite & oceanographic observations.

---

## 🏗️ System Architecture

```
                       REAL MARINE DATA CONNECTORS
            (NOAA ERDDAP / Copernicus CMEMS / INCOIS MOSDAC)
                                 │
                                 ▼
                     DATA VALIDATION & QUALITY CONTROL
                (Data Quality Score % & Range Bound Checks)
                                 │
                                 ▼
              SPATIAL GRID MAPPING & INTERPOLATION ENGINE
         (1.5° x 1.5° Resolution Spatial Polygons over Indian Ocean)
                                 │
                                 ▼
                     MACHINE LEARNING ENGINE
        (Random Forest Classifier 95.5% Acc, Isolation Forest Anomaly)
                                 │
                                 ▼
                  SPECIALIZED MULTI-AGENT NETWORK
    (Ocean, Pollution, Marine Life, Climate, Anomaly Detection Agents)
                                 │
                                 ▼
                 EXPLAINABLE AI & EVIDENCE LEDGER
      (Directional Factor Impact Tags & SQLite Audit Log Database)
                                 │
                                 ▼
              FASTAPI REST API & 12-VIEW STREAMLIT DASHBOARD
        (Spatial Grid Polygons, Risk Heatmap, What-If Twins, RAG)
```

---

## 🚀 Key System Features

1. **Geospatial Grid Polygon Risk Engine** (`spatial/grid_engine.py`):
   - Generates $1.5^\circ \times 1.5^\circ$ resolution spatial polygons over the Indian Ocean.
   - Categorizes risk zones: 🟢 `LOW` ($<25$), 🟡 `MODERATE` ($25-49.9$), 🟠 `HIGH` ($50-74.9$), 🔴 `CRITICAL` ($\ge 75$), ⚪ `INSUFFICIENT DATA` ($>500\text{ km}$).
2. **Marine Life & Ecosystem Habitat Safety Classifier** (`core/risk_engine.py`):
   - Classifies habitat safety into `🟢 SAFE HABITAT`, `🟡 STRESSED HABITAT`, `🟠 HIGH ECOLOGICAL RISK`, `🔴 DANGER / CRITICAL` using scientifically cautious indicators.
3. **Specialized Multi-Agent Network** (`agents/`):
   - `Ocean Agent`, `Pollution Agent`, `Marine Life Agent`, `Climate Agent`, `Anomaly Agent`.
4. **Machine Learning & Anomaly Engine** (`models/`):
   - **Random Forest Classifier** ($95.5\%$ accuracy, $0.95$ F1-score) and **Isolation Forest** anomaly detector.
5. **SQLite Evidence Ledger Database** (`database/ledger.py`):
   - Immutable audit logging of observations, predictions, agent findings, and confidence ratings.
6. **Scientific Knowledge Base (RAG)** (`rag/`):
   - Domain literature citations (NOAA Coral Reef Watch, UNEP Marine Hypoxia manuals, IPCC reports).

---

## 🛠️ Local Installation & Launch Guide

### Prerequisites
- Python 3.10+
- Git

### Quickstart Commands

```bash
# 1. Clone repository
git clone https://github.com/parellyvenkatesh/ORCA_SIH26176.git
cd ORCA_SIH26176

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train ML models & initialize metrics
python pipelines/train_models.py

# 4. Run automated test suite
python -m unittest tests/test_orca.py

# 5. Launch Streamlit Web Dashboard
python -m streamlit run app.py
```

Dashboard Access: `http://localhost:8501`

---

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t orca-platform:latest .

# Run container
docker run -d -p 8501:8501 -p 8000:8000 --name orca_app orca-platform:latest

# Or using docker-compose
docker-compose up --build -d
```

---

## 🛰️ FastAPI REST API Endpoints

Launch API Server:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Documentation: `http://localhost:8000/docs`

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/health` | `GET` | Health check endpoint |
| `/api/v1/locations` | `GET` | List supported Indian marine locations |
| `/api/v1/observation/{location}` | `GET` | Retrieve observation & data quality score |
| `/api/v1/assessment/{location}` | `GET` | Execute full multi-agent & ML assessment |
| `/api/v1/ledger` | `GET` | Fetch SQLite audit ledger records |

---

## ☁️ Cloud Deployment Guide

### Streamlit Community Cloud
1. Push repo to GitHub.
2. Connect repo on `share.streamlit.io`.
3. Set entry point to `app.py`.

### AWS EC2 / Azure VM
```bash
sudo apt update && sudo apt install -y docker.io docker-compose
docker-compose up -d
```

---

## 📄 License & Attribution
Distributed under the MIT License. Developed for ISRO SIH26176.
