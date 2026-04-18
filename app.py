import streamlit as st
import pandas as pd
import sqlite3
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- INITIAL SETUP ---
st.set_page_config(page_title="ResiliPath AI | Global Logistics", layout="wide", page_icon="🌐")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeading h1 { color: #4facfe; }
    .stButton>button { background-color: #4facfe; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 ResiliPath AI: Resilient Logistics Engine")
st.markdown("### Google Solution Challenge 2026 | Smart Supply Chains (SDG 12)")

# Initialize Gemini 3 Flash Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-3-flash-preview" 

# --- DATABASE ENGINE ---
def get_connection():
    # Fresh DB name to ensure clean initialization
    conn = sqlite3.connect("resilipath_v2.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS shipments (id INTEGER PRIMARY KEY, cargo_id TEXT, route TEXT, status TEXT, priority TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY, asset_type TEXT, capacity INTEGER, location TEXT)")
    
    # Seeding initial data for the demo
    if conn.execute("SELECT COUNT(*) FROM shipments").fetchone() == 0:
        conn.execute("INSERT INTO shipments (cargo_id, route, status, priority) VALUES ('SHP-X102', 'Mumbai -> Dubai', 'In Transit', 'Critical')")
        conn.execute("INSERT INTO shipments (cargo_id, route, status, priority) VALUES ('SHP-A991', 'Singapore -> Mumbai', 'Port Delay', 'High')")
        conn.execute("INSERT INTO assets (asset_type, capacity, location) VALUES ('Cargo Drone Fleet', 50, 'JNPT Port')")
        conn.execute("INSERT INTO assets (asset_type, capacity, location) VALUES ('Electric Hauler', 120, 'Navi Mumbai Hub')")
    conn.commit()
    conn.close()

init_db()

# --- UI LAYERS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚛 Global Shipment Tracker")
    conn = get_connection()
    ship_df = pd.read_sql_query("SELECT * FROM shipments", conn)
    st.dataframe(ship_df, hide_index=True, use_container_width=True)
    
    st.subheader("🛠️ Fleet & Asset Capacity")
    asset_df = pd.read_sql_query("SELECT * FROM assets", conn)
    st.dataframe(asset_df, hide_index=True, use_container_width=True)
    conn.close()

with col2:
    st.subheader("🧠 Resilient AI Optimization")
    st.info("Report a disruption to generate a pivot plan.")
    
    disruption = st.text_area("Disruption Signal", height=150, placeholder="e.g., 'Heavy rain at Mumbai port'...")
    
    if st.button("Generate Optimization Plan"):
        if disruption:
            with st.spinner("Gemini 3 Flash calculating..."):
                try:
                    ship_ctx = ship_df.to_string()
                    asset_ctx = asset_df.to_string()
                    
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=f"CONTEXT:\nShipments:\n{ship_ctx}\n\nAssets:\n{asset_ctx}\n\nDISRUPTION: {disruption}",
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are ResiliPath AI. Provide a strategic optimization plan "
                                "to re-route cargo during disruptions. Focus on SDG 12.3 (waste reduction)."
                            )
                        )
                    )
                    st.success("Optimization Plan Ready")
                    st.markdown(response.text)
                except Exception as e:
                    st.error("AI connection failed. Check your API Key or try again.")
        else:
            st.warning("Please describe a disruption first.")

st.divider()
st.caption("Developed by Pixel Paradox | Sardar Patel Institute of Technology")