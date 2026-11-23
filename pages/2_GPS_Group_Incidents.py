"""GPS Group Incidents — All closed incidents fully resolved by GPS/INS members"""

import streamlit as st
import pandas as pd
import altair as alt
import pyodbc
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="GPS Group Incidents · Exception Monitor",
    page_icon=":material/group:",
    layout="wide"
)

# SQL Server Configuration
SQL_SERVER = os.getenv('SQL_SERVER', 'ediprod.db.corporate.cargowise.com')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'ediProd')

def get_sql_connection():
    """Establish connection to SQL Server using Windows Authentication"""
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to SQL Server: {str(e)}")

@st.cache_data(ttl=300, show_spinner=False)
def load_group_incidents(product: str, start_iso: str, end_iso: str) -> tuple[pd.DataFrame, datetime]:
    """All closed incidents fully resolved by GPS/INS members for the given product + window."""
    
    GPS_CAPABILITY_PK = "BF9A2BC9-FC0E-42EC-8D9E-DA9D5915FC5C"
    INS_CAPABILITY_PK = "AC5AEA48-1BD3-412B-B739-644BF9A92C60"
    
    query = f"""
    WITH IncScope AS (
        SELECT IM_PK, IM_IncidentNumber, IM_ProgramArea, IM_SystemCreateTimeUtc
        FROM ediProd.dbo.IncidentMain
        WHERE IM_Product = ?
          AND IM_IncidentType = 'INC'
          AND IM_Status = 'CLS'
          AND IM_SystemCreateTimeUtc >= ?
          AND IM_SystemCreateTimeUtc <  ?
    ),
    Tasks AS (
        SELECT P9.P9_ParentID AS IM_PK,
               P9.P9_PK,
               NULLIF(P9.P9_GS_NKAssignedStaffMember, '') AS StaffCode,
               P9.P9_CompletedTimeUtc
        FROM ediProd.dbo.ProcessTasks P9
        INNER JOIN IncScope S ON P9.P9_ParentID = S.IM_PK
        WHERE P9.P9_ParentTableCode = 'IM'
          AND P9.P9_Status = 'CLS'
          AND P9.P9_Type NOT IN ('EXC','MIL','TRG')
    ),
    TaskMember AS (
        SELECT T.IM_PK, T.StaffCode,
            CASE WHEN T.StaffCode IS NOT NULL AND EXISTS (
                SELECT 1
                FROM ediProd.dbo.GlbResourceCapabilityPivot RCP
                INNER JOIN ediProd.dbo.GlbStaff GS ON RCP.G5_GS_Resource = GS.GS_PK
                WHERE GS.GS_Code = T.StaffCode
                  AND RCP.G5_G4_Capability IN ('{GPS_CAPABILITY_PK}', '{INS_CAPABILITY_PK}')
            ) THEN 1 ELSE 0 END AS IsMember
        FROM Tasks T
    ),
    IncAgg AS (
        SELECT IM_PK,
            COUNT(*)              AS TotalTasks,
            SUM(IsMember)         AS MemberTasks,
            COUNT(DISTINCT StaffCode) AS TotalStaff
        FROM TaskMember
        GROUP BY IM_PK
    )
    SELECT
        S.IM_IncidentNumber               AS "Incident Number",
        S.IM_ProgramArea                  AS "Product Area",
        CASE WHEN EXISTS (
            SELECT 1 FROM ediProd.dbo.IncidentManagementLink L
            WHERE L.INL_IM_Incident = S.IM_PK
        ) THEN 'Linked to ING' ELSE 'Not linked' END AS "ING Link",
        last.ClosedUtc                    AS "Closed",
        last.StaffName                    AS "Last Task Closed By",
        A.TotalStaff                      AS "Total Staff (worked/closed)",
        names.StaffNames                  AS "Staff (closed tasks)",
        names.StaffWorkflow               AS "Staff → Workflow",
        names.Capabilities                AS "Capabilities",
        A.TotalTasks                      AS "Total Tasks"
    FROM IncAgg A
    INNER JOIN IncScope S ON A.IM_PK = S.IM_PK
    OUTER APPLY (
        SELECT
            (SELECT STRING_AGG(x.StaffName, ', ')
             FROM (
                SELECT DISTINCT GS.GS_FullName AS StaffName
                FROM ediProd.dbo.ProcessTasks P9
                LEFT JOIN ediProd.dbo.GlbStaff GS ON P9.P9_GS_NKAssignedStaffMember = GS.GS_Code
                WHERE P9.P9_ParentID = A.IM_PK
                  AND P9.P9_ParentTableCode = 'IM'
                  AND P9.P9_Status = 'CLS'
                  AND P9.P9_Type NOT IN ('EXC','MIL','TRG')
                  AND NULLIF(P9.P9_GS_NKAssignedStaffMember, '') IS NOT NULL
             ) x) AS StaffNames,
            (SELECT STRING_AGG(y.Pair, '; ')
             FROM (
                SELECT DISTINCT GS.GS_FullName + ' closed ' + PH.FH_CompletionStatement AS Pair
                FROM ediProd.dbo.ProcessTasks P9
                LEFT JOIN ediProd.dbo.GlbStaff GS ON P9.P9_GS_NKAssignedStaffMember = GS.GS_Code
                LEFT JOIN ediProd.dbo.ProcessHeader PH ON P9.P9_FH_ProcessHeader = PH.FH_PK
                WHERE P9.P9_ParentID = A.IM_PK
                  AND P9.P9_ParentTableCode = 'IM'
                  AND P9.P9_Status = 'CLS'
                  AND P9.P9_Type NOT IN ('EXC','MIL','TRG')
                  AND NULLIF(P9.P9_GS_NKAssignedStaffMember, '') IS NOT NULL
                  AND NULLIF(PH.FH_CompletionStatement, '') IS NOT NULL
             ) y) AS StaffWorkflow,
            (SELECT STRING_AGG(z.Cap, ',')
             FROM (
                SELECT DISTINCT G4.G4_Code AS Cap
                FROM ediProd.dbo.ProcessTasks P9
                INNER JOIN ediProd.dbo.GlbCapability G4 ON P9.P9_G4_RequiredCapability = G4.G4_PK
                WHERE P9.P9_ParentID = A.IM_PK
                  AND P9.P9_ParentTableCode = 'IM'
                  AND P9.P9_Status = 'CLS'
                  AND P9.P9_Type NOT IN ('EXC','MIL','TRG')
                  AND NULLIF(G4.G4_Code, '') IS NOT NULL
             ) z) AS Capabilities
    ) names
    OUTER APPLY (
        SELECT TOP 1 GS.GS_FullName AS StaffName, P9.P9_CompletedTimeUtc AS ClosedUtc
        FROM ediProd.dbo.ProcessTasks P9
        LEFT JOIN ediProd.dbo.GlbStaff GS ON P9.P9_GS_NKAssignedStaffMember = GS.GS_Code
        WHERE P9.P9_ParentID = A.IM_PK
          AND P9.P9_ParentTableCode = 'IM'
          AND P9.P9_Status = 'CLS'
          AND P9.P9_Type NOT IN ('EXC','MIL','TRG')
        ORDER BY P9.P9_CompletedTimeUtc DESC
    ) last
    WHERE A.TotalTasks > 0
      AND A.MemberTasks = A.TotalTasks
    ORDER BY S.IM_IncidentNumber
    """
    
    conn = get_sql_connection()
    try:
        df = pd.read_sql(query, conn, params=(product, start_iso, end_iso))
        return df, datetime.now()
    finally:
        conn.close()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Header with logo and title
col_logo, col_title = st.columns([0.1, 0.9])
with col_logo:
    st.markdown("👥")
with col_title:
    st.markdown("## GPS Group Incidents")
    st.caption("Source: IncidentMain · ProcessTasks · Data as of —")

# About this page and Refresh button
col1, col2, col3 = st.columns([0.85, 0.075, 0.075])
with col1:
    with st.expander("ℹ️ Closed incidents where every task was closed by GPS or INS members", expanded=True):
        st.markdown(
            "An incident counts when it's closed and every actionable task on it was closed by a member "
            "of either capability (GPS or INS). Exception, Milestone and Trigger tasks are left out."
        )
with col2:
    if st.button("ℹ️ About", width="stretch", key="about_btn"):
        st.info("GPS Group Incidents - all closed incidents fully resolved by GPS/INS members")
with col3:
    if st.button("🔄 Refresh", width="stretch", key="refresh_btn"):
        st.rerun()

st.divider()

# Filters section
col1, col2, col3 = st.columns([1.2, 1.4, 1])
product = col1.text_input("Product", value="ENT").strip().upper()
start = col2.date_input("Created from", value=date(2026, 7, 1), key="start_date")
window_days = col3.number_input("Window (days)", min_value=1, max_value=90, value=7, step=1)

end = start + timedelta(days=int(window_days))
start_iso = start.strftime("%Y-%m-%d")
end_iso = end.strftime("%Y-%m-%d")

st.caption(
    f"Scope: closed **{product}** incidents created "
    f"**{start:%d %b %Y} – {end - timedelta(days=1):%d %b %Y}** "
    f"({int(window_days)} days) · all tasks closed by **GPS** or **INS** members only."
)

# Load data
try:
    df, fetched_at = load_group_incidents(product, start_iso, end_iso)
except Exception as exc:
    st.error(f"Could not load incidents from ediProd.\n\n{exc}")
    st.stop()

# Additional filters
col1, col2 = st.columns(2)
with col1:
    area_opts = sorted(a for a in df["Product Area"].dropna().unique() if str(a).strip())
    sel_areas = st.multiselect("Filter by product area", area_opts, placeholder="All areas", key="areas_multi")
    
    cap_opts = sorted({
        code.strip()
        for cell in df["Capabilities"].dropna()
        for code in str(cell).split(",")
        if code.strip()
    })
    sel_caps = st.multiselect("Filter by capability", cap_opts, placeholder="All capabilities", key="caps_multi")

with col2:
    staff_opts = sorted({
        name.strip()
        for cell in df["Staff (closed tasks)"].dropna()
        for name in str(cell).split(",")
        if name.strip()
    })
    sel_staff = st.multiselect("Filter by staff (worked/closed)", staff_opts, placeholder="All staff", key="staff_multi")
    
    staff_counts = df["Total Staff (worked/closed)"].astype(int)
    lo, hi = (int(staff_counts.min()), int(staff_counts.max())) if not df.empty else (0, 0)
    if hi > lo:
        sel_range = st.slider("Total staff (worked/closed)", lo, hi, (lo, hi), key="staff_range")
    else:
        st.caption(f"Total staff (worked/closed): every incident has **{lo}**.")
        sel_range = (lo, hi)

sel_ing = st.selectbox("Filter by ING link", ["All", "Linked to ING", "Not linked"], key="ing_link")

# Apply filters
view = df
if sel_areas:
    view = view[view["Product Area"].isin(sel_areas)]
if sel_staff:
    wanted = set(sel_staff)
    view = view[view["Staff (closed tasks)"].apply(
        lambda cell: bool({n.strip() for n in str(cell or "").split(",")} & wanted)
    )]
if sel_caps:
    wanted_caps = set(sel_caps)
    view = view[view["Capabilities"].apply(
        lambda cell: bool({c.strip() for c in str(cell or "").split(",")} & wanted_caps)
    )]
if sel_ing != "All":
    view = view[view["ING Link"] == sel_ing]
view = view[view["Total Staff (worked/closed)"].astype(int).between(sel_range[0], sel_range[1])]

st.divider()

# KPI Tiles with circular metric-style visualization
kpi_count = len(view)
total_staff = int(view["Total Staff (worked/closed)"].sum()) if not view.empty else 0
total_tasks = int(view["Total Tasks"].sum()) if not view.empty else 0
filtered = bool(sel_areas or sel_staff or sel_caps or sel_ing != "All" or sel_range != (lo, hi))

col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Qualifying incidents",
        f"{kpi_count:,}",
        help="closed only by GPS / INS"
    )
    if filtered:
        st.caption(f"of {len(df):,} in scope")
    else:
        st.caption("closed only by GPS / INS")

with col2:
    st.metric(
        "Staff engagements",
        f"{total_staff:,}",
        help="across those incidents"
    )
    st.caption("across those incidents")

st.divider()

# Tab-style analytics
st.subheader("Closure analytics")

closed_dt = pd.to_datetime(view["Closed"], errors="coerce") if not view.empty else pd.Series(dtype="datetime64[ns]")
chart_df = view.assign(**{"Close Month": closed_dt.dt.strftime("%Y-%m")}) if not view.empty else view
per_staff = chart_df.groupby("Last Task Closed By").size().sort_values(ascending=False)
no_closer = int(chart_df["Last Task Closed By"].isna().sum()) if not view.empty else 0

if view.empty:
    st.info("No incidents to chart for the current filters.")
elif per_staff.empty:
    st.info("No closing staff names for the current filters.")
else:
    view_choice = st.segmented_control(
        "View", ["By staff", "By month", "Distribution"], default="By staff",
        required=True, key="view_choice", label_visibility="collapsed"
    ) or "By staff"
    
    if view_choice == "By staff":
        top_n = st.slider("Show top N staff", 5, 40, max(5, min(20, len(per_staff))), key="topn")
        top_staff = per_staff.head(top_n).index.tolist()
        by_sm = (
            chart_df[chart_df["Last Task Closed By"].isin(top_staff)]
            .groupby(["Last Task Closed By", "ING Link"]).size()
            .reset_index(name="Incidents closed")
        )
        st.caption("Incidents closed per staff (last-task closer), split by ING link.")
        
        staff_order = per_staff.head(top_n).index.tolist()
        chart = (
            alt.Chart(by_sm)
            .mark_bar()
            .encode(
                y=alt.Y("Last Task Closed By:N", sort=staff_order, title="Staff"),
                x=alt.X("sum(Incidents closed):Q", title="Incidents closed"),
                color=alt.Color(
                    "ING Link:N", title="ING link",
                    scale=alt.Scale(domain=["Linked to ING", "Not linked"],
                                    range=["#1f77b4", "#ff7f0e"]),
                ),
            )
        )
        st.altair_chart(chart)
    
    elif view_choice == "By month":
        by_month = chart_df.groupby("Close Month").size().reset_index(name="Incidents closed")
        st.caption("Total incidents closed per month.")
        st.bar_chart(by_month, x="Close Month", y="Incidents closed")
    
    elif view_choice == "Distribution":
        dist = per_staff.value_counts().sort_index().rename_axis("Incidents closed").reset_index(name="Number of staff")
        st.caption("Distribution — how many staff closed N incidents.")
        st.bar_chart(dist, x="Incidents closed", y="Number of staff")

st.divider()

# Incident detail section
st.subheader("Incident detail")
if view.empty:
    st.info("No incidents match the current scope.")
else:
    st.dataframe(view, hide_index=True)
    st.download_button(
        "📥 Download CSV",
        view.to_csv(index=False),
        file_name=f"gps_group_incidents_{product}_{start_iso}.csv",
        mime="text/csv",
    )
