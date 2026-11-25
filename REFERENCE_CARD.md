# 📌 Cache System - Visual Reference Card

## Your Question Answered ✅

```
Q: "Why does data refresh even when I'm not updating SharePoint?"

A: Streamlit's 5-minute cache automatically expires and refreshes data
   
   Time:     0 min      5 min      10 min     15 min
            │          │          │          │
   Cache:   LOAD  →  EXPIRE  →  LOAD  →  EXPIRE
            DATA      RELOAD     DATA      RELOAD
```

---

## One-Page Summary

| Topic | Answer |
|-------|--------|
| **Cache Duration** | 5 minutes (automatic) |
| **Data Sources** | CSV (priority) or SQL Server (fallback) |
| **Force Refresh** | Click `🗑️ Clear Cache & Refresh` button |
| **Auto Refresh** | Happens every 5 minutes automatically |
| **Data Indicator** | 📂 (CSV) or ⚠️ (SQL) info box |
| **CSV Location** | `C:\...\Team - ProdDev Global Product Support - Stats` |
| **App URL** | http://localhost:8501 |

---

## Button Locations

```
🏠 Main Dashboard (app.py)
   └─ 🗑️ Clear Cache & Refresh Now

👤 GPS Team Page (pages/1_GPS_Team.py)
   ├─ 🗑️ Clear Cache & Refresh
   └─ 🔄 Soft Refresh

👥 GPS Incidents Page (pages/2_GPS_Group_Incidents.py)
   ├─ 🗑️ Clear Cache & Refresh
   └─ 🔄 Soft Refresh
```

---

## Data Flow Diagram

```
START
  │
  ├─→ CSV File Exists?
  │   ├─ YES → Load CSV → ✅ Show (Green Box)
  │   └─ NO → Load SQL → ⚠️ Show (Yellow Box)
  │
  ├─→ Cache for 5 Minutes
  │
  ├─→ User Interaction
  │
  └─→ After 5 Minutes → Cache Expires → Repeat
  
  
SPECIAL: User Clicks "Clear Cache & Refresh"
         └─→ Skip 5 min wait → Reload immediately
```

---

## Three Refresh Options

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  🗑️ CLEAR CACHE & REFRESH (Recommended)               │
│  ├─ Time: Immediate                                    │
│  ├─ What: Clear cache + load fresh data               │
│  └─ Use: After uploading CSV files                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔄 SOFT REFRESH                                        │
│  ├─ Time: Immediate                                    │
│  ├─ What: Rerun page (may use cache)                  │
│  └─ Use: Visual glitches                               │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ⏱️ WAIT 5 MINUTES (Automatic)                         │
│  ├─ Time: 5 minutes                                    │
│  ├─ What: Cache expires, auto-refresh                 │
│  └─ Use: Passive waiting                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Data Source Indicators

### 📂 CSV Info Box (Green) ✅
```
📂 Data Source: CSV (SharePoint Synced Folder)
   Last CSV Update: 2025-11-25 11:30:45
   Cache expires in 5 minutes and will auto-refresh
```
**Meaning:** App is using YOUR CSV files

### ⚠️ SQL Warning Box (Yellow) ⚡
```
⚠️ Data Source: SQL Server (ediProd database)
   CSV file not found. Using SQL Server query instead.
   Cache expires in 5 minutes and will auto-refresh
```
**Meaning:** No CSV found, using SQL Server

---

## Common Workflows

### Scenario 1: "I Updated CSV Files"
```
1. Upload CSV files to SharePoint folder
2. Go to dashboard
3. Click 🗑️ Clear Cache & Refresh
4. See 📂 green box (CSV loaded)
5. ✅ Done - Your data is now live
```

### Scenario 2: "I Want SQL Server Data"
```
1. No CSV files in SharePoint folder
2. App automatically uses SQL Server
3. See ⚠️ yellow box (SQL query)
4. Click 🗑️ Clear Cache & Refresh for latest
5. ✅ Done - SQL data is live
```

### Scenario 3: "Data Looks Wrong"
```
1. Click 🗑️ Clear Cache & Refresh
2. Wait for dashboard to reload
3. Check the green (📂) or yellow (⚠️) box
4. If still wrong, check CSV or SQL
5. ✅ Done - Data is accurate now
```

---

## Decision Tree

```
Need fresh data NOW?
├─ YES → Click 🗑️ Clear Cache & Refresh → Instant
└─ NO  → Can wait 5 min? → Auto-refresh

Using CSV files?
├─ YES → Upload to SharePoint → Click Clear Cache
└─ NO  → SQL works automatically → No action needed

Data looks wrong?
├─ YES → Click 🗑️ Clear Cache & Refresh
└─ NO  → Data is correct

Want to understand more?
├─ YES → Read QUICK_START_CACHE.md (5 min)
└─ NO  → Just use the buttons
```

---

## Technical Details (For Reference)

### Cache Configuration
```python
@st.cache_data(ttl=300, show_spinner=False)
# ttl=300 means 5 minutes (300 seconds)
# show_spinner=False means no "Running..." text
```

### Clear Cache Command
```python
if st.button("🗑️ Clear Cache & Refresh"):
    st.cache_data.clear()  # Clear all cached functions
    st.rerun()             # Rerun the app
```

### Cache Key Factors
- Product (ENT, GLW, etc.)
- Date range (start, end)
- Window days

Changing any = new cache entry

---

## Documentation Quick Reference

| Guide | Time | Use For |
|-------|------|---------|
| QUICK_START_CACHE.md | 5 min | Understanding the system |
| CACHE_SYSTEM_SUMMARY.md | 10 min | What changed and why |
| CACHE_AND_DATA_REFRESH_GUIDE.md | 20 min | Complete technical details |
| IMPLEMENTATION_SUMMARY.md | 15 min | Code changes (developers) |

---

## Checklist for First-Time Users

- [ ] Read QUICK_START_CACHE.md
- [ ] Open http://localhost:8501
- [ ] See cache info section on main dashboard
- [ ] Click `🗑️ Clear Cache & Refresh Now` button
- [ ] Go to GPS Team page
- [ ] Look for 📂 (CSV) or ⚠️ (SQL) box
- [ ] Click refresh buttons and observe
- [ ] Read status messages
- [ ] Try changing filters
- [ ] Wait 5 minutes and see auto-refresh

---

## Important Reminders

✅ **DO:**
- Click refresh button after uploading CSV
- Use Clear Cache for critical freshness
- Monitor the green/yellow box to see data source
- Read the info box messages

❌ **DON'T:**
- Expect real-time updates without refresh
- Modify CSV and expect instant change (wait 5 min or clear cache)
- Keep stale CSV if you want SQL data
- Ignore the data source indicator

---

## Quick Help

**Q: Where do I click?**
A: `🗑️ Clear Cache & Refresh` button on any page

**Q: When should I click?**
A: After uploading CSV or when you need fresh data

**Q: What if it doesn't work?**
A: Try `🗑️ Clear Cache & Refresh` again

**Q: Can I turn it off?**
A: No, 5-min cache is built-in. But you can click Clear anytime.

**Q: Where's my data from?**
A: Check the 📂 (CSV) or ⚠️ (SQL) box on the page

---

## Colors Mean

```
📂 GREEN (✅ CSV)
   Your CSV files are being used
   Shows last update timestamp

⚠️ YELLOW (SQL Server)
   CSV not found, SQL Server is used
   This is OK - automatic fallback works
```

---

## Status

✅ System is working
✅ Buttons are ready
✅ Documentation is complete
✅ You can start using NOW

---

## Final Note

**The cache system is now transparent and fully controllable!**

You understand:
- ✅ Why data refreshes (5-minute cache)
- ✅ Where data comes from (CSV or SQL)
- ✅ How to control refresh timing (Clear button)
- ✅ What the status boxes mean (📂 or ⚠️)

**You're ready to use the dashboard! 🚀**

---

**Keep this card handy for quick reference!**

For more details, see DOCUMENTATION_INDEX.md
