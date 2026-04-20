import streamlit as st
import pandas as pd
import os
import requests
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- ENTERPRISE LOGGING & SECURITY ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

st.set_page_config(page_title="ResiliPath AI | Global Logistics", layout="wide", page_icon="🌐")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeading h1 { color: #4facfe; }
    .stButton>button { background-color: #4facfe; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    .metric-card { background-color: #1e2130; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #4facfe; }
    </style>
    """, unsafe_allow_html=True)

st.title("ResiliPath AI", help="A resilient logistics optimization engine powered by Gemini Flash.")
st.markdown("### Virtual: PromptWars Submission | Smart Supply Chains (SDG 12.3)")

# --- AI CACHING (EFFICIENCY) ---
@st.cache_resource
def get_ai_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("Security Alert: GOOGLE_API_KEY not found.")
        return None
    return genai.Client(api_key=api_key)

client = get_ai_client()
MODEL_ID = "gemini-2.0-flash"

# --- LIVE CLOUD DB INGESTION (INTERNAL DATA) ---
@st.cache_data(ttl=60)
def load_live_shipments() -> pd.DataFrame:
    try:
        # ⚠️ REPLACE WITH YOUR ACTUAL GOOGLE SHEET ID ⚠️
        sheet_id = https://docs.google.com/spreadsheets/d/1-rqM-_dN1Bho_6ABF_1cHeMpoXr9n7H9cDC2QpVd-9M/edit?usp=sharing
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        return pd.read_csv(csv_url)
    except Exception as e:
        logger.error(f"Live Feed Sync Failed: {e}")
        return pd.DataFrame([{"cargo_id": "SYS-OFFLINE", "route": "N/A", "status": "Offline", "priority": "None"}])

# --- LIVE OSINT INGESTION (EXTERNAL INTERNET DATA) ---
@st.cache_data(ttl=300) # Fetches live weather from the internet every 5 mins
def get_live_port_weather():
    """Fetches real-time weather data for major logistics hubs via public OSINT."""
    ports = {
        "JNPT Mumbai (IN)": {"lat": 18.95, "lon": 72.95},
        "Rotterdam (NL)": {"lat": 51.95, "lon": 4.10},
        "Los Angeles (US)": {"lat": 33.74, "lon": -118.26}
    }
    
    weather_data = {}
    try:
        for port, coords in ports.items():
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather_data[port] = {
                    "temp_c": data['current_weather']['temperature'],
                    "wind_kmh": data['current_weather']['windspeed']
                }
        return weather_data
    except Exception as e:
        logger.error(f"OSINT Weather API Failed: {e}")
        return {"Error": "Live weather feed offline"}

# --- SECURITY SANITIZATION ---
def sanitize_input(user_input: str) -> str:
    return str(user_input).replace("\n", " ").replace("<script>", "").strip()[:500]

# --- UI LAYERS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚛 Live Shipment Feed (Google Sheets)", help="Internal Ledger: Synced every 60s.")
    ship_df = load_live_shipments()
    st.dataframe(ship_df, hide_index=True, use_container_width=True)
    
    st.subheader("📡 Live Port Telemetry (OSINT)", help="External Internet Data: Real-time satellite weather conditions.")
    live_weather = get_live_port_weather()
    for port, metrics in live_weather.items():
        if port != "Error":
            # Using custom HTML for enterprise UI feel
            st.markdown(f"""
                <div class="metric-card">
                    <strong>{port}</strong><br>
                    🌡️ Temp: {metrics['temp_c']}°C | 💨 Wind: {metrics['wind_kmh']} km/h
                </div>
            """, unsafe_allow_html=True)

with col2:
    st.subheader("🧠 Resilient AI Optimization")
    disruption = st.text_area("Disruption Signal", height=100, placeholder="e.g., 'Wind speeds at JNPT exceeding safe limits...'")
    
    if st.button("Generate Optimization Plan"):
        if not client:
            st.error("Configuration Error: Ensure GOOGLE_API_KEY is configured.")
        elif disruption:
            clean_disruption = sanitize_input(disruption)
            with st.spinner("Gemini processing Internal Ledger + External OSINT..."):
                try:
                    # Fusing Internal + External data for the AI context
                    prompt_ctx = f"CONTEXT:\nInternal Shipments:\n{ship_df.to_string()}\n\nLive External Port Weather:\n{str(live_weather)}\n\nDISRUPTION SIGNAL: {clean_disruption}"
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=prompt_ctx,
                        config=types.GenerateContentConfig(
                            system_instruction="You are ResiliPath AI. Use the live weather telemetry and shipment ledger to reroute cargo and minimize food/agricultural waste (SDG 12.3). Explain your 'Resilience Reasoning'.",
                            temperature=0.2
                        )
                    )
                    st.success("Dynamic Optimization Plan (DOP) Ready")
                    st.markdown(response.text)
                except Exception as e:
                    logger.error(f"AI Error: {e}")
                    st.error("AI service temporarily unavailable. Securely logged.")
        else:
            st.warning("Please describe a disruption first.")

st.divider()
st.caption("Developed by Vedant Patil | SPIT Mumbai | Dual-Stream OSINT Architecture")
