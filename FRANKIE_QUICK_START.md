# 🎯 FRANKIE'S QUICK START - EXECUTE THIS

## TL;DR - Just Do This

### Step 1: Run These Commands (Copy & Paste)

```powershell
# Open PowerShell and run:
cd "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"
.\.venv\Scripts\activate.ps1
streamlit run app.py
```

### Step 2: Browser Opens
- Wait for: `Local URL: http://localhost:8501`
- Click the link or type in browser
- **Dashboard is now running** ✅

---

## What Frankie Needs to Know

### Before Running
- [ ] Repository cloned (already done)
- [ ] Virtual environment exists
- [ ] Python 3.8+ installed
- [ ] SQL Server accessible
- [ ] SharePoint folder synced

### After Running
- Dashboard opens at http://localhost:8501
- See "Cache & Data Refresh" section
- Click buttons to test
- Data comes from CSV or SQL (see status box)

### To Stop
- Press `Ctrl+C` in PowerShell terminal

---

## Three Ways to Run

### Option 1: PowerShell (What I showed above)
```powershell
cd "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"
.\.venv\Scripts\activate.ps1
streamlit run app.py
```

### Option 2: Batch File (Easier)
Create file: `C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards\RUN_APP.bat`

```batch
@echo off
cd /d "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"
call .venv\Scripts\activate.ps1
streamlit run app.py
```

Then just **double-click RUN_APP.bat** to start! ✨

### Option 3: Python Direct (If venv exists)
```powershell
cd "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"
python -m streamlit run app.py
```

---

## First Time Checklist

After running the app, verify:

- [ ] Dashboard page loads (http://localhost:8501)
- [ ] See "⚡ Cache & Data Refresh" section
- [ ] Click `🗑️ Clear Cache & Refresh Now` → Page refreshes
- [ ] Go to "GPS Team" in sidebar → Page loads
- [ ] Go to "GPS Group Incidents" in sidebar → Page loads
- [ ] See either 📂 (CSV) or ⚠️ (SQL) status box
- [ ] All buttons are clickable
- [ ] No red error messages

**If all ✅, you're ready!**

---

## If Something Goes Wrong

### Error: `streamlit: not recognized`
```powershell
# Did you forget to activate venv? Run:
.\.venv\Scripts\activate.ps1
# Then try again:
streamlit run app.py
```

### Error: `No module named 'streamlit'`
```powershell
# Install dependencies:
pip install -r requirements_streamlit.txt
```

### Error: `Failed to connect to SQL Server`
```powershell
# Check .env file exists with:
# SQL_SERVER=ediprod.db.corporate.cargowise.com
# SQL_DATABASE=ediProd

# Then verify connection:
python -c "import pyodbc; conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ediprod.db.corporate.cargowise.com;DATABASE=ediProd;Trusted_Connection=yes;'); print('✅ SQL OK'); conn.close()"
```

### Nothing Works?
👉 Read: [COMPLETE_RUNBOOK_FOR_FRANKIE.md](./COMPLETE_RUNBOOK_FOR_FRANKIE.md) → Part 8: Troubleshooting

---

## URLs to Remember

```
Main Dashboard:    http://localhost:8501
GPS Team:          http://localhost:8501/GPS_Team  
GPS Incidents:     http://localhost:8501/GPS_Group_Incidents
```

---

## CSV Data Files (Optional)

To use your own data instead of SQL Server:

1. Create: `gps_team.csv` and `group_incidents.csv`
2. Put in: `C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats`
3. Click: `🗑️ Clear Cache & Refresh Now`
4. See: Green 📂 box (CSV loaded)

👉 For details: [COMPLETE_RUNBOOK_FOR_FRANKIE.md](./COMPLETE_RUNBOOK_FOR_FRANKIE.md) → Part 3: Prepare Data Sources

---

## Full Documentation

**For complete setup guide:** [COMPLETE_RUNBOOK_FOR_FRANKIE.md](./COMPLETE_RUNBOOK_FOR_FRANKIE.md)

**For quick reference:** [REFERENCE_CARD.md](./REFERENCE_CARD.md)

**For cache understanding:** [QUICK_START_CACHE.md](./QUICK_START_CACHE.md)

**For all docs:** [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)

---

## Summary

```
✅ Run these 3 lines in PowerShell:
   cd "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"
   .\.venv\Scripts\activate.ps1
   streamlit run app.py

✅ Wait for: "Local URL: http://localhost:8501"

✅ Open browser → Dashboard works!

✅ Click buttons to test cache system

✅ Done! 🎉
```

---

## Support

| Issue | Read This |
|-------|-----------|
| **Won't start** | Troubleshooting in COMPLETE_RUNBOOK_FOR_FRANKIE.md |
| **Don't understand cache** | QUICK_START_CACHE.md |
| **Need full setup** | COMPLETE_RUNBOOK_FOR_FRANKIE.md Part 1-7 |
| **Quick reference** | REFERENCE_CARD.md |
| **All documents** | DOCUMENTATION_INDEX.md |

---

## Commands Summary

```powershell
# 1. Navigate
cd "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards"

# 2. Activate virtual environment
.\.venv\Scripts\activate.ps1

# 3. Run app
streamlit run app.py

# 4. Wait for "Local URL" message
# 5. Browser opens or click link
# 6. ✅ App is running!

# To stop: Ctrl+C in terminal
```

---

**That's it! This is your 2-minute quick start.** ⚡

For everything else, read the full runbook: [COMPLETE_RUNBOOK_FOR_FRANKIE.md](./COMPLETE_RUNBOOK_FOR_FRANKIE.md)

---

**Status:** Ready to Execute ✅
**Next Step:** Run the 3 PowerShell commands above
