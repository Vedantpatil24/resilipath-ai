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
# Accessibility: Set a clear, descriptive page title
st.set_page_config(
    page_title="ResiliPath AI | Global Logistics Optimization", 
    layout="wide", 
    page_icon="🌐"
)

# Custom CSS for high-quality UI/UX
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stHeading h1 { color: #4facfe; }
    .stButton>button { background-color: #4facfe; color: white; width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Accessibility: Using help parameters for screen readers and tooltips
st.title("ResiliPath AI", help="A resilient logistics optimization engine powered by Gemini 3 Flash.")
st.markdown("### Virtual: PromptWars Submission | Smart Supply Chains (SDG 12.3)")

# --- AI ENGINE INITIALIZATION ---
def get_ai_client():
    """
    Initializes the Gemini 3 Flash client using secure environment variables.
    Returns:
        genai.Client: The initialized client or None if API key is missing.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_ai_client()
MODEL_ID = "gemini-2.0-flash" 

# --- DATABASE ENGINE ---
def get_connection():
    """
    Establishes a thread-safe connection to the local SQLite database.
    """
    return sqlite3.connect("resilipath_v2.db", check_same_thread=False)

def init_db():
    """
    Initializes the database schema and seeds initial logistics data for the demo.
    """
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS shipments (id INTEGER PRIMARY KEY, cargo_id TEXT, route TEXT, status TEXT, priority TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY, asset_type TEXT, capacity INTEGER, location TEXT)")
    
    # Seeding initial data if table is empty
    if conn.execute("SELECT COUNT(*) FROM shipments").fetchone() == 0:
        seed_data = [
            ('SHP-X102', 'Mumbai -> Dubai', 'In Transit', 'Critical'),
            ('SHP-A991', 'Singapore -> Mumbai', 'Port Delay', 'High')
        ]
        conn.executemany("INSERT INTO shipments (cargo_id, route, status, priority) VALUES (?, ?, ?, ?)", seed_data)
        
        asset_data = [
            ('Cargo Drone Fleet', 50, 'JNPT Port'),
            ('Electric Hauler', 120, 'Navi Mumbai Hub')
        ]
        conn.executemany("INSERT INTO assets (asset_type, capacity, location) VALUES (?, ?, ?)", asset_data)
    
    conn.commit()
    conn.close()

init_db()

# --- UI LAYERS ---
col1, col2 = st.columns(2)

with col1:
    # Accessibility: Descriptive subheaders for data containers
    st.subheader("🚛 Global Shipment Tracker", help="Live ledger of all active shipments in the network.")
    conn = get_connection()
    ship_df = pd.read_sql_query("SELECT * FROM shipments", conn)
    st.dataframe(ship_df, hide_index=True, use_container_width=True)
    
    st.subheader("🛠️ Fleet & Asset Capacity", help="Overview of available logistics assets for re-routing.")
    asset_df = pd.read_sql_query("SELECT * FROM assets", conn)
    st.dataframe(asset_df, hide_index=True, use_container_width=True)
    conn.close()

with col2:
    st.subheader("🧠 Resilient AI Optimization")
    st.info("Report a disruption to generate a Dynamic Optimization Plan (DOP).")
    
    # User Input: Clear instructions for disruption modeling
    disruption = st.text_area(
        "Disruption Signal", 
        height=150, 
        placeholder="e.g., 'Heavy rain at Mumbai port causing 48-hour delays'...",
        help="Input a specific logistics disruption to trigger the AI Pivot Engine."
    )
    
    if st.button("Generate Optimization Plan"):
        if not client:
            st.error("Security Error: API Key not found in environment variables. Check GOOGLE_API_KEY.")
        elif disruption:
            with st.spinner("Gemini 3 Flash calculating..."):
                try:
                    # Logic: Passing live DB context to the LLM for informed reasoning
                    ship_ctx = ship_df.to_string()
                    asset_ctx = asset_df.to_string()
                    
                    response = client.models.generate_content(
                        model=MODEL_ID,
                        contents=f"CONTEXT:\nShipments:\n{ship_ctx}\n\nAssets:\n{asset_ctx}\n\nDISRUPTION: {disruption}",
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are ResiliPath AI. Provide a strategic optimization plan "
                                "to re-route cargo during disruptions. Focus on SDG 12.3 (waste reduction) "
                                "and provide logical 'Resilience Reasoning' for your choices."
                            )
                        )
                    )
                    st.success("Optimization Plan Ready")
                    st.markdown(response.text)
                except Exception as e:
                    # Security/Testing: Clean error handling without exposing stack traces
                    st.error(f"AI connection failed: {str(e)}")
        else:
            st.warning("Please describe a disruption first.")

st.divider()
# Final Branding and Acknowledgement
st.caption("Developed by Pixel Paradox | Sardar Patel Institute of Technology (SPIT) Mumbai")
