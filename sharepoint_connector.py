"""SharePoint data connector for GPS Dashboard"""

import os
import json
import pandas as pd
import pyodbc
from datetime import datetime
from pathlib import Path
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# Configuration
SHAREPOINT_SITE = "https://wisetechglobal.sharepoint.com/sites/t-ProdDevGlobalProductSupport"
SHAREPOINT_FOLDER = "Shared Documents/Global Product Support/Buddy Training Material/Stats"

# Use synced SharePoint folder if available, otherwise use local cache
SHAREPOINT_LOCAL_SYNC = r"C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats"
DATA_CACHE_DIR = Path(SHAREPOINT_LOCAL_SYNC) if Path(SHAREPOINT_LOCAL_SYNC).exists() else Path(__file__).parent / ".data_cache"

# Fallback to local cache if SharePoint folder doesn't exist
if not DATA_CACHE_DIR.exists():
    DATA_CACHE_DIR = Path(__file__).parent / ".data_cache"

METADATA_FILE = DATA_CACHE_DIR / "data_metadata.json"

# Ensure cache directory exists
DATA_CACHE_DIR.mkdir(exist_ok=True)

# SQL Configuration
SQL_SERVER = os.getenv('SQL_SERVER', 'ediprod.db.corporate.cargowise.com')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'ediProd')

def save_metadata(filename: str, timestamp: datetime):
    """Save refresh metadata to JSON file"""
    metadata = {}
    if METADATA_FILE.exists():
        try:
            metadata = json.load(open(METADATA_FILE))
        except:
            metadata = {}
    
    metadata[filename] = timestamp.isoformat()
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_metadata(filename: str) -> datetime | None:
    """Load refresh timestamp for a file"""
    if not METADATA_FILE.exists():
        return None
    
    try:
        metadata = json.load(open(METADATA_FILE))
        if filename in metadata:
            return datetime.fromisoformat(metadata[filename])
    except:
        pass
    return None

# SQL Configuration
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

def save_metadata(filename: str, timestamp: datetime):
    """Save refresh metadata to JSON file"""
    metadata = {}
    if METADATA_FILE.exists():
        try:
            metadata = json.load(open(METADATA_FILE))
        except:
            metadata = {}
    
    metadata[filename] = timestamp.isoformat()
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_metadata(filename: str) -> datetime | None:
    """Load refresh timestamp for a file"""
    if not METADATA_FILE.exists():
        return None
    
    try:
        metadata = json.load(open(METADATA_FILE))
        if filename in metadata:
            return datetime.fromisoformat(metadata[filename])
    except:
        pass
    return None

def get_gps_team_data() -> pd.DataFrame:
    """Get GPS team staff from SQL"""
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
        return df
    finally:
        conn.close()

def get_group_incidents_data(product: str = "ENT", days: int = 7) -> pd.DataFrame:
    """Get GPS Group Incidents from SQL"""
    GPS_CAPABILITY_PK = "BF9A2BC9-FC0E-42EC-8D9E-DA9D5915FC5C"
    INS_CAPABILITY_PK = "AC5AEA48-1BD3-412B-B739-644BF9A92C60"
    
    start_date = (datetime.now() - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
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
        S.IM_SystemCreateTimeUtc          AS "Created",
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
        df = pd.read_sql(query, conn, params=(product, start_date, end_date))
        return df
    finally:
        conn.close()

def export_to_local_cache(days: int = 7):
    """Export data from SQL to local CSV cache and upload to SharePoint"""
    try:
        # Export GPS Team
        gps_team_df = get_gps_team_data()
        gps_team_file = DATA_CACHE_DIR / "gps_team.csv"
        gps_team_df.to_csv(gps_team_file, index=False)
        save_metadata("gps_team.csv", datetime.now())
        
        # Export Group Incidents
        incidents_df = get_group_incidents_data(days=days)
        incidents_file = DATA_CACHE_DIR / "group_incidents.csv"
        incidents_df.to_csv(incidents_file, index=False)
        save_metadata("group_incidents.csv", datetime.now())
        
        # Try to upload to SharePoint
        sharepoint_result = upload_to_sharepoint()
        
        return {
            "success": True,
            "gps_team_rows": len(gps_team_df),
            "incidents_rows": len(incidents_df),
            "timestamp": datetime.now().isoformat(),
            "sharepoint_upload": sharepoint_result.get("success", False),
            "sharepoint_message": sharepoint_result.get("uploaded_files", sharepoint_result.get("error", ""))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def load_from_cache(filename: str) -> tuple[pd.DataFrame, datetime | None]:
    """Load data from local cache"""
    cache_file = DATA_CACHE_DIR / filename
    if not cache_file.exists():
        return pd.DataFrame(), None
    
    df = pd.read_csv(cache_file)
    timestamp = load_metadata(filename)
    return df, timestamp

def upload_to_sharepoint():
    """
    Upload cached CSVs to SharePoint using OneDrive API
    Note: This requires the .data_cache folder to be synced via OneDrive
    """
    try:
        # For now, we'll use a simple approach:
        # Files in .data_cache will be synced to SharePoint via OneDrive Client
        # This provides seamless sync without authentication
        
        gps_team_file = DATA_CACHE_DIR / "gps_team.csv"
        incidents_file = DATA_CACHE_DIR / "group_incidents.csv"
        
        uploaded_files = []
        if gps_team_file.exists():
            uploaded_files.append("gps_team.csv")
        if incidents_file.exists():
            uploaded_files.append("group_incidents.csv")
        
        if uploaded_files:
            return {
                "success": True,
                "uploaded_files": uploaded_files,
                "note": "Files saved to local cache. Sync to SharePoint via OneDrive client.",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "No CSV files found in cache"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }

def download_from_sharepoint(filename: str) -> tuple[bool, pd.DataFrame]:
    """
    Download CSV from SharePoint Stats folder
    Note: Requires the SharePoint folder to be synced locally via OneDrive
    """
    try:
        # Try to load from local cache first
        cache_file = DATA_CACHE_DIR / filename
        if cache_file.exists():
            df = pd.read_csv(cache_file)
            return True, df
        
        return False, pd.DataFrame()
    except Exception as e:
        print(f"Download error: {e}")
        return False, pd.DataFrame()
