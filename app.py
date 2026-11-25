"""GPS Dashboard - Dashboard Overview"""

import streamlit as st
from datetime import datetime, timedelta, date
from sharepoint_connector import export_to_local_cache, load_metadata, download_from_sharepoint

st.set_page_config(
    page_title="GPS Dashboard",
    page_icon=":material/dashboard:",
    layout="wide"
)

st.title("🚀 GPS Dashboard")
st.write("""
Welcome to the GPS Dashboard. Use the navigation in the sidebar to explore:

- **GPS Team** — GPS staff member directory
- **GPS Group Incidents** — Closed incidents handled by GPS/INS members
""")

st.divider()

# Cache Management Section
st.subheader("⚡ Cache & Data Refresh")
st.info(
    "**How data refresh works:**\n\n"
    "1. Data is loaded from **CSV files** in your SharePoint synced folder\n"
    "2. If CSV doesn't exist, falls back to **SQL Server query**\n"
    "3. Data is **cached for 5 minutes** to improve performance\n"
    "4. After 5 minutes, cache expires and data refreshes automatically\n"
    "5. Use **Clear Cache** button below to force immediate refresh"
)

col_cache1, col_cache2 = st.columns(2)
with col_cache1:
    if st.button("🗑️ Clear Cache & Refresh Now", key="clear_cache_btn", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_cache2:
    st.metric("Cache TTL", "5 minutes", "Auto-refreshes after expiry")

st.divider()

# Data Management Section
st.subheader("📊 Data Management")

col1, col2, col3 = st.columns([1.2, 1.4, 1])

window_days = col3.number_input("Days window", min_value=1, value=7, step=1)

with col1:
    if st.button("🔄 Update Data from SQL", key="update_btn", use_container_width=True):
        with st.spinner("Exporting data from SQL Server and uploading to SharePoint..."):
            result = export_to_local_cache(days=int(window_days))
            if result["success"]:
                st.success(f"""
                ✅ Data updated successfully!
                - GPS Team: {result['gps_team_rows']} members
                - Group Incidents: {result['incidents_rows']} incidents
                - Updated at: {result['timestamp']}
                """)
                if result.get('sharepoint_upload'):
                    st.info(f"✅ Uploaded to SharePoint: {', '.join(result.get('sharepoint_message', []))}")
                else:
                    st.warning(f"⚠️ SharePoint upload: {result.get('sharepoint_message', 'Could not connect')}")
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

with col2:
    if st.button("📥 Load from SharePoint", key="download_btn", use_container_width=True):
        with st.spinner("Downloading data from SharePoint..."):
            gps_success, gps_df = download_from_sharepoint("gps_team.csv")
            incidents_success, incidents_df = download_from_sharepoint("group_incidents.csv")
            
            if gps_success or incidents_success:
                st.success(f"""
                ✅ Data loaded from SharePoint!
                """)
                if gps_success:
                    st.info(f"✅ GPS Team: {len(gps_df)} members loaded")
                if incidents_success:
                    st.info(f"✅ Group Incidents: {len(incidents_df)} incidents loaded")
            else:
                st.error("❌ Could not load data from SharePoint. Using local cache if available.")

with col3:
    pass

st.divider()

# Data Status
st.subheader("📋 Data Status")

col1, col2 = st.columns(2)

with col1:
    gps_team_time = load_metadata("gps_team.csv")
    if gps_team_time:
        st.metric(
            "GPS Team Data",
            "✅ Ready",
            f"Last updated: {gps_team_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        st.metric("GPS Team Data", "⏳ Pending", "No data yet")

with col2:
    incidents_time = load_metadata("group_incidents.csv")
    if incidents_time:
        st.metric(
            "Group Incidents Data",
            "✅ Ready",
            f"Last updated: {incidents_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        st.metric("Group Incidents Data", "⏳ Pending", "No data yet")

st.divider()

st.info("👉 Select a page from the sidebar to view data.")
