# SharePoint Integration Setup Guide

## Overview
The GPS Dashboard syncs data between SQL Server and a SharePoint folder. This allows:
- **You**: Update data from SQL Server and share via SharePoint
- **Frankie**: Access shared data without needing SQL Server access

## Architecture

```
SQL Server (Your PC) 
    ↓ (Update Data from SQL)
Local Cache (.data_cache/)
    ↓ (OneDrive Sync)
SharePoint Folder (Stats)
    ↓ (Load from SharePoint)
Remote User (Frankie's PC)
```

## Setup Instructions

### For You (SQL Server Access)

1. **Sync SharePoint folder to your PC:**
   - Open SharePoint: https://wisetechglobal.sharepoint.com/sites/t-ProdDevGlobalProductSupport
   - Navigate to: Shared Documents → Global Product Support → Buddy Training Material → Stats
   - Click **"Sync"** button in the top menu
   - Choose a local folder (e.g., `C:\SharePoint\GPS-Stats`)

2. **Configure OneDrive Desktop Sync:**
   - Open OneDrive settings on your PC
   - Ensure the Stats folder is synced

3. **Run the Dashboard:**
   ```bash
   cd dashboards
   python -m streamlit run app.py
   ```

4. **Click "🔄 Update Data from SQL":**
   - Exports data from SQL Server to `.data_cache/`
   - OneDrive automatically syncs to SharePoint
   - Files appear in SharePoint Stats folder

---

### For Frankie (No SQL Access)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Frankie727/dashboards.git
   cd dashboards
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

3. **Configure .data_cache sync:**
   - Option A: Create a symlink to your synced SharePoint folder
     ```bash
     mklink /d .data_cache "C:\SharePoint\GPS-Stats"
     ```
   - Option B: Manually sync the SharePoint folder and copy files to `.data_cache/`

4. **Run the Dashboard:**
   ```bash
   python -m streamlit run app.py
   ```

5. **Click "📥 Load from SharePoint":**
   - Loads data from the synced files
   - Dashboard displays GPS Team and Incidents data
   - Data is typically 1 week old (acceptable for Frankie's use case)

---

## File Structure

```
dashboards/
├── .data_cache/              # Local cache (synced via OneDrive)
│   ├── gps_team.csv
│   ├── group_incidents.csv
│   └── data_metadata.json    # Timestamps
├── pages/
│   ├── 01_GPS_Team.py
│   └── 02_GPS_Group_Incidents.py
├── app.py                    # Main dashboard
├── sharepoint_connector.py   # Data sync logic
└── requirements_streamlit.txt
```

---

## Data Flow

### Update from SQL (Your PC)
```
1. Click "🔄 Update Data from SQL"
2. Queries run on SQL Server
3. Data exported to .data_cache/gps_team.csv
4. Data exported to .data_cache/group_incidents.csv
5. Timestamps saved to .data_cache/data_metadata.json
6. OneDrive syncs files to SharePoint (automatic)
```

### Load from SharePoint (Frankie's PC)
```
1. Click "📥 Load from SharePoint"
2. Reads from synced .data_cache/ folder
3. Data loads into dashboard
4. Displays with last-refresh timestamp
```

---

## Troubleshooting

### "Could not load data from SharePoint"
- Ensure .data_cache folder is synced with SharePoint
- Check OneDrive sync status
- Verify files exist in SharePoint Stats folder

### "No files found"
- Click "🔄 Update Data from SQL" first (requires SQL access)
- Wait for OneDrive sync to complete
- Check .data_cache folder for CSV files

### SharePoint folder not syncing
- Open OneDrive settings
- Verify folder sync is enabled
- Try re-syncing the SharePoint folder

---

## Notes

- **Data Freshness**: Frankie's data is typically 1 week old (acceptable per requirements)
- **No Auth Required**: Uses OneDrive client sync, no additional authentication needed
- **Scalable**: Can add more data sources following the same pattern
- **Privacy**: All data remains within WiseTech infrastructure

