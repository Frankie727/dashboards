"""GPS Dashboard - Dashboard Overview"""

import streamlit as st

st.set_page_config(
    page_title="GPS Dashboard",
    page_icon=":material/dashboard:",
    layout="wide"
)

st.title("🚀 GPS Dashboard")
st.write("""
Welcome to the GPS Dashboard. Use the navigation in the sidebar to explore:

- **GPS Team** — Closed ENT incidents fully resolved by GPS/INS members
- **GPS Group Incidents** — All GPS/INS-closed incidents with group analytics
""")

st.info("Select a page from the sidebar to begin.")
