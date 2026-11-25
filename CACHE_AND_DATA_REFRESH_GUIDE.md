# 📊 Cache & Data Refresh Guide

## Overview

The GPS Dashboard has a **caching system** that automatically manages how often data is refreshed. This guide explains how it works and how to control it.

---

## How Data Flows

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR APP                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────┐
        │   CSV FILES IN SHAREPOINT FOLDER?      │
        └────────────────────────────────────────┘
                 YES ↓          ↓ NO
                     │          │
            ┌────────▼┐    ┌────▼────────┐
            │   CSV   │    │  SQL Server │
            │  LOAD   │    │   QUERY     │
            └────────┬┘    └────┬────────┘
                     │          │
                     └────┬─────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  CACHED FOR  │
                  │  5 MINUTES   │
                  └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  DISPLAY IN  │
                  │   DASHBOARD  │
                  └──────────────┘
```

---

## Three Ways Data Can Change

### 1. **Automatic Refresh (5 Minutes)**
- **What:** After 5 minutes, the cache expires automatically
- **When:** App will reload data on next interaction
- **Source:** CSV first (if exists), then SQL Server fallback
- **You Do:** Nothing! It happens automatically

### 2. **Clear Cache Button**
- **What:** Forces immediate cache clear and data reload
- **Button Location:** `🗑️ Clear Cache & Refresh` on each page
- **When to Use:** 
  - You uploaded new CSV files
  - You want fresh data NOW
  - SQL Server data changed
- **Result:** Page refreshes with latest data immediately

### 3. **Soft Refresh Button**
- **What:** Reruns the page (may use cached data if still valid)
- **Button Location:** `🔄 Soft Refresh` on each page
- **When to Use:** Visual glitches, filters not working
- **Note:** Only clears cache if the 5 minutes have expired

---

## Data Sources Priority

### CSV Files (Primary Source)
✅ **Loaded First** - If files exist in this folder:
```
C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats
```

**Files Used:**
- `gps_team.csv` → GPS Team page
- `group_incidents.csv` → GPS Group Incidents page

**You Can:**
- Copy/paste CSV files here
- Replace/update them anytime
- Delete them (triggers SQL fallback)

**How to Confirm Data is from CSV:**
- Look for 📂 info box saying `"CSV (SharePoint Synced Folder)"`
- Shows the last time CSV was updated

---

### SQL Server (Fallback Source)
⚠️ **Used When:** CSV files don't exist or fail to load

**Database:** `ediProd` on `ediprod.db.corporate.cargowise.com`

**You Can:**
- Change data via SQL Server
- Database updates auto-refresh after 5 minutes

**How to Confirm Data is from SQL:**
- Look for ⚠️ warning box saying `"SQL Server (ediProd database)"`
- Shows data came from live SQL query

---

## Common Questions

### Q: "Why does data refresh even when I don't update files?"
**A:** The 5-minute cache expires automatically. After 5 minutes, the app reloads data:
- If CSV exists → loads from CSV
- If CSV missing → queries SQL Server

### Q: "How do I see ONLY CSV data, not SQL?"
**A:** Upload your CSV files to SharePoint folder. App will use them (not SQL).

### Q: "Data should come from CSV but app shows SQL warning?"
**A:** Possible issues:
1. CSV file not in correct folder: `C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats`
2. CSV filename is wrong (should be `gps_team.csv` or `group_incidents.csv`)
3. CSV file is corrupted - try re-uploading
4. Click `🗑️ Clear Cache & Refresh` to force reload

### Q: "Can I disable the 5-minute auto-refresh?"
**A:** Currently, the 5-minute cache is built-in. You can:
- Click `🗑️ Clear Cache & Refresh` button anytime for immediate refresh
- Wait 5 minutes for automatic refresh
- Manual refresh works instantly

### Q: "What if I want to load 2-3 years of data?"
**A:** No 90-day limit on the "Total Data Window" anymore. You can:
1. Set window to 365+ days in the app
2. App will query that date range
3. For large datasets, consider uploading CSV files to avoid SQL load

---

## Page-by-Page Refresh Locations

### 🏠 Main Dashboard (app.py)
- **Button:** `🗑️ Clear Cache & Refresh Now`
- **Info Section:** Top of page explains cache system

### 👤 GPS Team (pages/1_GPS_Team.py)
- **Button:** `🗑️ Clear Cache & Refresh` + `🔄 Soft Refresh`
- **Data Source:** Shows whether loading from CSV or SQL

### 👥 GPS Group Incidents (pages/2_GPS_Group_Incidents.py)
- **Button:** `🗑️ Clear Cache & Refresh` + `🔄 Soft Refresh`
- **Data Source:** Shows whether loading from CSV or SQL
- **Date Logic:** Creates from today back N days (not forward)

---

## Technical Details

### Cache Configuration
```python
@st.cache_data(ttl=300, show_spinner=False)
def load_data(...):
    # ttl=300 means 5 minutes (300 seconds)
    # show_spinner=False means no "Running..." spinner
```

### How to Clear Cache in Code
```python
st.cache_data.clear()
st.rerun()
```

### Cache Key Factors
- **Product** (ENT, GLW, etc.)
- **Date Range** (start date, end date)
- **Window Days**

Changing any of these creates a new cache entry.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Data looks stale | Click `🗑️ Clear Cache & Refresh` |
| App still shows old data | Wait 5 minutes for auto-refresh |
| CSV not loading | Check folder path and filename |
| Want to force SQL Server | Delete CSV file |
| Need real-time updates | Use `🗑️ Clear Cache` after each change |

---

## Best Practices

✅ **DO:**
- Upload CSV files if you want app to use them
- Click `🗑️ Clear Cache` after uploading new data
- Use `🗑️ Clear Cache` for critical freshness
- Monitor the data source info box (CSV vs SQL)

❌ **DON'T:**
- Expect real-time updates without manual refresh
- Modify CSV files and expect instant changes (wait 5 min or clear cache)
- Keep stale CSV files if you want SQL data

---

## Next Steps

1. **For CSV Loading:**
   - Upload CSV files to: `C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats`
   - Click `🗑️ Clear Cache & Refresh`

2. **For SQL Server:**
   - Just use the app (SQL fallback is automatic)
   - Cache refreshes every 5 minutes

3. **For Manual Control:**
   - Use `🗑️ Clear Cache & Refresh` button on any page
   - App loads fresh data immediately

---

**Last Updated:** 2025 (Cache mechanism implemented)

**Questions?** Check the info boxes on each dashboard page for real-time data source info.
