import streamlit as st
import pandas as pd
import folium
import json
import random
from streamlit_folium import st_folium

st.set_page_config(page_title="Virtue Foundation: Healthcare Intelligence", layout="wide", page_icon="🌍")

# Static coordinates for Ghana regions
GHANA_ZONES = {
    "Accra": [5.6037, -0.1870], "Kumasi": [6.6885, -1.6244],
    "Tamale": [9.4008, -0.8393], "Takoradi": [4.8963, -1.7553],
    "Cape Coast": [5.1053, -1.2466], "Sunyani": [7.3399, -2.3267],
    "Ho": [6.6119, 0.4703], "Koforidua": [6.0945, -0.2591]
}

# --- LIVE DATA LOADER ---
# ttl=2 means Streamlit will check the JSON file for new data every 2 seconds!
@st.cache_data(ttl=2)
def load_processed_data():
    try:
        with open("processed_ghana_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_processed_data()

# --- SIDEBAR & CONTROLS ---
st.sidebar.header("🔍 Infrastructure Query")

if st.sidebar.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()

search_term = st.sidebar.text_input("Search by Name, Specialty, or Equipment...")
filter_anomaly = st.sidebar.toggle("Highlight Scarce Zones (Anomalies)")

# --- DASHBOARD HEADER & KPIs ---
st.title("🌍 Virtue Foundation: Healthcare Intelligence Dashboard")

if not data:
    st.warning("⚠️ Database is empty. Please run `python build_database.py` in your terminal to start extracting data.")
    st.stop()

# Calculate global metrics from the LIVE data
total_processed = len(data)
total_anomalies = sum(1 for d in data if d['audit']['is_flagged'])
total_clean = total_processed - total_anomalies

# Display the KPI Cards at the top
col1, col2, col3 = st.columns(3)
col1.metric("Facilities Processed (Live)", total_processed)
col2.metric("Scarce/Anomaly Zones", total_anomalies, delta=total_anomalies, delta_color="inverse")
col3.metric("Verified Good Zones", total_clean)
st.divider()

# --- FILTER LOGIC ---
highlighted_data = []
background_data = []

for item in data:
    text_to_search = f"{item['name']} {item['description']} {str(item['facts'])}".lower()
    is_match = search_term.lower() in text_to_search
    
    # If the toggle is on, only highlight anomalies
    if filter_anomaly and not item['audit']['is_flagged']:
        is_match = False
        
    if is_match:
        highlighted_data.append(item)
    else:
        background_data.append(item)

# --- MAP VISUALIZATION ---
st.subheader("🗺️ Medical Desert & Zone Analysis")
m = folium.Map(location=[7.9465, -1.0232], zoom_start=7, tiles="cartodbpositron")

# Draw Background Data (Faded grey dots so you don't lose the big picture)
for res in background_data:
    base_coords = GHANA_ZONES.get(res['city'], [5.6037, -0.1870])
    # Wide jitter (0.3) so unknown cities don't stack directly on Accra
    coords = [base_coords[0] + random.uniform(-0.3, 0.3), base_coords[1] + random.uniform(-0.3, 0.3)]
    
    folium.CircleMarker(
        location=coords,
        radius=3,
        color="#D3D3D3", 
        fill=True,
        opacity=0.3
    ).add_to(m)

# Draw Highlighted Data (Red/Green Zones)
for res in highlighted_data:
    base_coords = GHANA_ZONES.get(res['city'], [5.6037, -0.1870])
    coords = [base_coords[0] + random.uniform(-0.3, 0.3), base_coords[1] + random.uniform(-0.3, 0.3)]
    
    is_anomaly = res['audit']['is_flagged']
    zone_color = "#ff4b4b" if is_anomaly else "#00cc66" 
    
    folium.Circle(
        location=coords,
        radius=8000 if is_anomaly else 4000,
        color=zone_color,
        fill=True,
        fill_opacity=0.5,
        tooltip=f"<b>{res['name']}</b><br>Type: {res['type']}",
        popup=f"Audit Status: {'Scarce Zone' if is_anomaly else 'Verified Good'}"
    ).add_to(m)

# returned_objects=[] stops the map from lagging out the Streamlit UI
st_folium(m, width=1200, height=500, returned_objects=[])
st.divider()

# --- RESULTS TABLE ---
st.subheader(f"📊 Query Results ({len(highlighted_data)} matching facilities)")
if highlighted_data:
    df_display = pd.DataFrame([
        {
            "Name": r["name"],
            "Registry Type": r["type"],
            "Audit Flags": ", ".join(r["audit"]["flags"]) if r["audit"]["is_flagged"] else "CLEAN",
            "Extracted Specialties": ", ".join(r["facts"].get("specialties", []))
        } for r in highlighted_data
    ])
    st.dataframe(df_display, width='stretch')
