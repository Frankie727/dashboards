"""GPS Team — List of GPS team staff members"""

import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="GPS Team · Exception Monitor",
    page_icon=":material/support_agent:",
    layout="wide"
)

# SQL Server Configuration
SQL_SERVER = os.getenv('SQL_SERVER', 'ediprod.db.corporate.cargowise.com')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'ediProd')

# Data cache location (synced with SharePoint)
DATA_CACHE_DIR = Path(r"C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats")
if not DATA_CACHE_DIR.exists():
    DATA_CACHE_DIR = Path(__file__).parent.parent / ".data_cache"

def get_sql_connection():
    """Establish connection to SQL Server using Windows Authentication"""
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to SQL Server: {str(e)}")

@st.cache_data(ttl=300, show_spinner=False)
def load_gps_team_members() -> tuple[pd.DataFrame, datetime]:
    """Load GPS team members from CSV, fallback to SQL"""
    
    csv_file = DATA_CACHE_DIR / "gps_team.csv"
    data_source = "Unknown"
    
    # Try to load from CSV first
    if csv_file.exists():
        try:
            df = pd.read_csv(csv_file)
            fetched_at = datetime.fromtimestamp(csv_file.stat().st_mtime)
            data_source = "CSV (SharePoint Synced Folder)"
            st.info(
                f"📂 **Data Source:** {data_source}\n\n"
                f"**Last CSV Update:** {fetched_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"*Cache expires in 5 minutes and will auto-refresh*"
            )
            return df, fetched_at
        except Exception as e:
            st.warning(f"Could not load CSV: {e}. Switching to SQL Server...")
    
    # Fallback to SQL if CSV doesn't exist
    data_source = "SQL Server (ediProd database)"
    GPS_CAPABILITY_PK = "BF9A2BC9-FC0E-42EC-8D9E-DA9D5915FC5C"
    
    query = f"""
    SELECT DISTINCT
        GS.GS_FullName AS "Staff Name",
        GS.GS_Code AS "Staff Code",
        GS.GS_IsActive AS "Is Active"
    FROM ediProd.dbo.GlbResourceCapabilityPivot RCP
    INNER JOIN ediProd.dbo.GlbStaff GS ON RCP.G5_GS_Resource = GS.GS_PK
    WHERE RCP.G5_G4_Capability = '{GPS_CAPABILITY_PK}'
    ORDER BY GS.GS_FullName ASC
    """
    
    conn = get_sql_connection()
    try:
        df = pd.read_sql(query, conn)
        st.warning(
            f"⚠️ **Data Source:** {data_source}\n\n"
            f"CSV file not found. Using SQL Server query instead.\n\n"
            f"*Cache expires in 5 minutes and will auto-refresh*"
        )
        return df, datetime.now()
    finally:
        conn.close()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Header with logo and title
col_logo, col_title = st.columns([0.1, 0.9])
with col_logo:
    st.markdown("👤")
with col_title:
    st.markdown("## GPS Team")
    st.caption("Source: GlbStaff · GlbResourceCapabilityPivot")

# Cache & Refresh Info
st.info(
    "**📊 Data Source & Caching:**\n\n"
    "- Data loaded from **CSV files** in your SharePoint folder\n"
    "- Falls back to **SQL Server** if CSV unavailable\n"
    "- **Cache TTL:** 5 minutes (auto-refreshes)\n"
    "- Use buttons below to manage refresh"
)

col_refresh1, col_refresh2 = st.columns(2)
with col_refresh1:
    if st.button("🗑️ Clear Cache & Refresh", key="clear_cache_team", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_refresh2:
    if st.button("🔄 Soft Refresh", key="soft_refresh_team", use_container_width=True):
        st.rerun()

# About this page and Refresh button
col1, col2, col3 = st.columns([0.85, 0.075, 0.075])
with col1:
    with st.expander("ℹ️ GPS team staff members", expanded=True):
        st.markdown(
            "List of all staff members who belong to the GPS (Global Product Support) capability."
        )
with col2:
    if st.button("ℹ️ About", key="about_btn", use_container_width=True):
        st.info("GPS Team - Staff members in the GPS capability")
with col3:
    pass

st.divider()

# Load data
try:
    df, fetched_at = load_gps_team_members()
except Exception as exc:
    st.error(f"Could not load team members from ediProd.\n\n{exc}")
    st.stop()

# Display stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total team members", len(df))
with col2:
    active_count = int((df["Is Active"] == 1).sum())
    st.metric("Active members", active_count)
with col3:
    inactive_count = int((df["Is Active"] == 0).sum())
    st.metric("Inactive members", inactive_count)

st.divider()

# Filters
st.subheader("Filters")
col1, col2 = st.columns(2)
with col1:
    show_active = st.checkbox("Show active members only", value=True)
with col2:
    search_name = st.text_input("Search by name", placeholder="Type staff name...")

# Apply filters
view = df.copy()
if show_active:
    view = view[view["Is Active"] == 1]
if search_name:
    view = view[view["Staff Name"].str.contains(search_name, case=False, na=False)]

st.divider()

# Display team members
st.subheader("Team Members")
if view.empty:
    st.info("No team members match the current filters.")
else:
    # Display as a simple table
    display_df = view[["Staff Name", "Staff Code", "Is Active"]].copy()
    display_df["Status"] = display_df["Is Active"].apply(lambda x: "✅ Active" if x == 1 else "⏸️ Inactive")
    display_df = display_df[["Staff Name", "Staff Code", "Status"]]
    
    st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    # Download button
    st.download_button(
        "📥 Download CSV",
        view.to_csv(index=False),
        file_name=f"gps_team_members_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )

st.caption(f"Data as of {fetched_at.strftime('%Y-%m-%d %H:%M:%S')}")
