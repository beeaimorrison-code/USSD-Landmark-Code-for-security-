import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- 1. SYSTEM CONFIGURATION & DYNAMIC THEME ---
st.set_page_config(page_title="Abuja USSD Security Framework", layout="wide")

# background logic based on login status
if 'personnel_auth' not in st.session_state or not st.session_state.personnel_auth:
    page_bg = "#800000"  # Institutional Maroon
    content_color = "#FFFFFF"
else:
    page_bg = "#F0F2F6"  # Professional Responder Grey
    content_color = "#000000"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {page_bg};
    }}
    h1, h2, h3, p, span, .stMarkdown {{
        color: {content_color} !important;
    }}
    /* USSD Mobile UI Simulation */
    .ussd-container {{
        background-color: #000000;
        color: #00FF00;
        padding: 30px;
        border-radius: 35px;
        border: 8px solid #333333;
        max-width: 380px;
        margin: auto;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0px 20px 40px rgba(0,0,0,0.6);
    }}
    /* Custom Button Styling */
    .stButton>button {{
        background-color: #5a0000;
        color: white;
        border: 1px solid #ffffff;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND DATA & ABUJA LANDMARK GEOGRAPHY ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Incident", "Location", "Weight", "Time", "Device_ID", "lat", "lon"])
if 'audit_trail' not in st.session_state:
    st.session_state.audit_trail = pd.DataFrame(columns=["Timestamp", "Personnel", "Action"])
if 'personnel_auth' not in st.session_state:
    st.session_state.personnel_auth = False

# Coordinate mapping for Abuja Landmarks (FCT Sector)
LANDMARKS = {
    "Wuse II Central": [9.0778, 7.4767],
    "Garki District": [9.0333, 7.4833],
    "Maitama Sector": [9.0883, 7.5022],
    "Asokoro Extension": [9.0483, 7.5147],
    "Gwarinpa Estate": [9.1097, 7.4042],
    "Kubwa Hub": [9.1558, 7.3271],
    "Nyanya Sector": [9.0167, 7.5667]
}

# --- 3. SIDEBAR: PERSONNEL ACCESS ---
st.sidebar.title("👮 Personnel Command")
if not st.session_state.personnel_auth:
    with st.sidebar.form("personnel_login"):
        p_id = st.text_input("Personnel ID", placeholder="Enter Name or ID")
        p_key = st.text_input("Access Key", type="password")
        if st.form_submit_button("Enter Abuja Dashboard"):
            if p_key.lower() == "thesis2026":
                st.session_state.personnel_auth = True
                st.session_state.current_user = p_id
                log = pd.DataFrame([{"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                     "Personnel": p_id, "Action": "Accessed Abuja Tactical View"}])
                st.session_state.audit_trail = pd.concat([st.session_state.audit_trail, log], ignore_index=True)
                st.rerun()
            else:
                st.sidebar.error("Invalid Personnel Key")
else:
    st.sidebar.success(f"Active Session: {st.session_state.current_user}")
    if st.sidebar.button("Log Out"):
        st.session_state.personnel_auth = False
        st.rerun()

# --- 4. PORTAL ROUTING ---

# SCENARIO A: Public Access (Common Citizens - No Password)
if not st.session_state.personnel_auth:
    st.title("🛡️ Hybrid USSD Security Mapping Framework")
    st.subheader("Simulating Zero-Data Offline Incident Reporting (Abuja Sector)")
    st.divider()

    col_sim, col_doc = st.columns([1, 1.2])

    with col_sim:
        st.markdown('<div class="ussd-container">', unsafe_allow_html=True)
        st.markdown("### GSM TERMINAL")
        st.markdown("**Session: *123#**")
        st.markdown("---")
        st.markdown("1. Robbery<br>2. Kidnapping<br>3. Suspicious Activity", unsafe_allow_html=True)
        
        with st.form("ussd_report", clear_on_submit=True):
            user_input = st.text_input("Select Option (1-3)")
            user_loc = st.selectbox("Current Landmark", list(LANDMARKS.keys()))
            if st.form_submit_button("SEND SIGNAL"):
                mapping = {"1": "Robbery", "2": "Kidnapping", "3": "Suspicious Activity"}
                weights = {"1": 15, "2": 25, "3": 10}
                
                if user_input in mapping:
                    report = pd.DataFrame([{
                        "Incident": mapping[user_input],
                        "Location": user_loc,
                        "Weight": weights[user_input],
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Device_ID": "FCT_SIM_PROX",
                        "lat": LANDMARKS[user_loc][0],
                        "lon": LANDMARKS[user_loc][1]
                    }])
                    st.session_state.db = pd.concat([st.session_state.db, report], ignore_index=True)
                    st.success(f"✔ Emergency signal sent from {user_loc}")
                else:
                    st.error("Invalid Input")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_doc:
        st.markdown("### Dissertation Simulation Logic")
        st.write("""
        - **Barrier-Free Reporting:** Abuja citizens access this terminal instantly without passwords.
        - **FCT Mapping:** Each district landmark is geofenced to internal coordinates.
        - **Accountability:** Unique Device IDs are captured via the GSM layer to track reporting trends.
        """)
        st.info("The Responder Dashboard is restricted. Please use the sidebar to log in as security personnel.")

# SCENARIO B: Personnel Access (Security Dashboard & Map)
else:
    st.title(f"👮 Abuja Command Center: {st.session_state.current_user}")
    
    t1, t2 = st.tabs(["🗺️ FCT Tactical Map", "📑 Audit & Accountability"])
    
    with t1:
        if not st.session_state.db.empty:
            # 1. 3D Column Layer (Visualizes intensity)
            column_layer = pdk.Layer(
                'ColumnLayer', data=st.session_state.db, get_position='[lon, lat]',
                get_elevation='Weight * 200', radius=500,
                get_fill_color='[128, 0, 0, 180]', pickable=True, auto_highlight=True
            )
            
            # 2. Heatmap Layer (Visualizes density)
            heatmap_layer = pdk.Layer(
                "HeatmapLayer", data=st.session_state.db, opacity=0.9,
                get_position='[lon, lat]', get_weight="Weight"
            )

            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v10',
                initial_view_state=pdk.ViewState(latitude=9.0765, longitude=7.3986, zoom=11, pitch=45),
                layers=[heatmap_layer, column_layer],
                tooltip={"text": "{Incident} reported at {Location}"}
            ))
        else:
            st.info("System Online. Standing by for signals from FCT districts...")

    with t2:
        st.subheader("Live Abuja Incident Database")
        st.dataframe(st.session_state.db.iloc[::-1], use_container_width=True)
        st.divider()
        st.subheader("Personnel Activity Logs")
        st.table(st.session_state.audit_trail.iloc[::-1])
