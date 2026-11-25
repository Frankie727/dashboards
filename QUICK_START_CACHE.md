# 🎯 Quick Start Guide - Cache & Refresh System

## The Answer to Your Question

**Q: "Why does data refresh even when I'm not updating SharePoint?"**

**A: Every 5 minutes, the app automatically refreshes data because of Streamlit's cache timeout.**

```
Time 0:00 → Load data → Show on dashboard
Time 5:00 → Cache expires → Load data again → Show on dashboard
Time 10:00 → Cache expires → Load data again → Show on dashboard
```

---

## What You Need to Know

### 1️⃣ Data Always Comes From One of Two Places

```
CSV File Exists?
├─ YES → Use CSV file (faster, your data)
└─ NO  → Use SQL Server (slower, database query)
```

**Your CSV Folder:**
```
C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats
```

### 2️⃣ Cache Timer Automatically Resets Every 5 Minutes

The app saves data in memory for **5 minutes** to avoid repeated queries. After 5 minutes:
- Cache expires automatically
- App loads fresh data
- Either from CSV or SQL Server

### 3️⃣ You Can Skip the Wait with One Click

**On ANY dashboard page, click:**
```
🗑️ Clear Cache & Refresh
```

This instantly clears the cache and loads fresh data (no 5-minute wait).

---

## Three Scenarios

### Scenario 1: "I Updated CSV Files"
1. Copy/paste files to SharePoint folder
2. Go to dashboard
3. Click `🗑️ Clear Cache & Refresh`
4. App immediately loads your CSV
5. ✅ Done! You'll see 📂 blue info box saying "CSV"

### Scenario 2: "Database Changed, No CSV Files"
1. SQL Server has new data
2. Either:
   - Wait 5 minutes (auto-refresh)
   - Click `🗑️ Clear Cache & Refresh` (immediate)
3. ✅ App loads from SQL Server

### Scenario 3: "Data Looks Wrong"
1. Click `🗑️ Clear Cache & Refresh`
2. App reloads everything
3. Try again
4. If still wrong, check console for errors

---

## Where to Click

### 🏠 Main Dashboard (app.py)
```
⚡ Cache & Data Refresh
  └─ 🗑️ Clear Cache & Refresh Now
  └─ Cache TTL: 5 minutes
```

### 👤 GPS Team Page (pages/1_GPS_Team.py)
```
📊 Data Source & Caching
  └─ 🗑️ Clear Cache & Refresh
  └─ 🔄 Soft Refresh
```

### 👥 GPS Incidents Page (pages/2_GPS_Group_Incidents.py)
```
📊 Data Source & Caching
  └─ 🗑️ Clear Cache & Refresh
  └─ 🔄 Soft Refresh
```

---

## Two Types of Refresh Buttons

### 🗑️ Clear Cache & Refresh (Recommended)
- **What:** Clears cache + loads fresh data
- **Time:** Immediate
- **Use:** After uploading CSV files
- **Best For:** Critical freshness needs

### 🔄 Soft Refresh
- **What:** Reruns page (may use cache if still valid)
- **Time:** Immediate
- **Use:** Visual glitches, filters not working
- **Best For:** Quick rerun

---

## Data Source Indicators

### 📂 CSV Info Box (Green)
```
📂 Data Source: CSV (SharePoint Synced Folder)
   Last CSV Update: 2025-11-25 11:30:45
   Cache expires in 5 minutes and will auto-refresh
```
**Means:** Data is coming from your CSV files ✅

### ⚠️ SQL Warning Box (Yellow)
```
⚠️ Data Source: SQL Server (ediProd database)
   CSV file not found. Using SQL Server query instead.
   Cache expires in 5 minutes and will auto-refresh
```
**Means:** Data is from database (CSV not found) ⚠️

---

## Common Questions Answered

**Q: Can I turn off the 5-minute cache?**
A: No, it's built into Streamlit. But you can click "Clear Cache" anytime.

**Q: Why does data look the same after 5 minutes if nothing changed?**
A: Because it IS the same (CSV or SQL didn't change). That's correct!

**Q: Will the cache affect my data if I'm using CSV?**
A: No. Cache just stores it in memory. Your CSV file is the source of truth.

**Q: What happens if I delete my CSV file?**
A: App falls back to SQL Server automatically.

**Q: Can I have 2-3 years of data?**
A: Yes! No 90-day limit anymore. Set "Window" to 365+ days.

**Q: Does cache slow down the app?**
A: No, it speeds it up! Avoids repeated database queries.

---

## The Complete Picture

```
┌─────────────────────────────────────────────────────────────┐
│                     DASHBOARD APP                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │   CHECK CACHE (5 min)    │
              └──────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
         ┌────────────────┐  ┌────────────────┐
         │  CACHE VALID?  │  │ CACHE EXPIRED? │
         │   (< 5 min)    │  │  (> 5 min)     │
         └────────────────┘  └────────────────┘
                 │YES                │NO
                 ▼                   ▼
         ┌────────────────┐  ┌────────────────────┐
         │  USE CACHE     │  │  LOAD FRESH DATA   │
         │  (Display)     │  │  (CSV or SQL)      │
         └────────────────┘  │  Then → Cache      │
                             │  Then → Display    │
                             └────────────────────┘

USER ACTION:
  Click "🗑️ Clear Cache & Refresh"
         ↓
  Immediately jump to "LOAD FRESH DATA" step
         ↓
  Reload dashboard
```

---

## Your Action Plan

### Step 1: Understand the System (5 minutes)
- Read this quick guide ✅
- Read CACHE_SYSTEM_SUMMARY.md

### Step 2: Test the Buttons (5 minutes)
- Go to `http://localhost:8501`
- Click "🗑️ Clear Cache & Refresh Now"
- Observe what happens
- Navigate to GPS Team
- Click refresh buttons
- See green (CSV) or yellow (SQL) box

### Step 3: Use CSV Files (Optional)
- Create/get your CSV files
- Save to: `C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats`
- Filenames: `gps_team.csv`, `group_incidents.csv`
- Click "Clear Cache & Refresh"
- Verify green box appears (CSV loaded)

### Step 4: Monitor & Adjust
- Use app normally
- Click refresh buttons when needed
- Let 5-minute auto-refresh work
- Read logs to confirm data source

---

## Most Important Thing

**You now have FULL CONTROL over when data refreshes!**

```
Before:  "Why is data changing??"  😕
After:   Click button → Instant refresh → See blue/yellow box ✅
```

---

## Need More Details?

📖 **For complete technical guide:** Read `CACHE_AND_DATA_REFRESH_GUIDE.md`

📋 **For summary:** Read `CACHE_SYSTEM_SUMMARY.md`

📊 **For implementation details:** Read `IMPLEMENTATION_SUMMARY.md`

---

## Status

✅ System implemented and tested
✅ App running on http://localhost:8501
✅ All buttons working
✅ Clear data source indicators
✅ Documentation complete

**You're ready to use the cache system! 🚀**
