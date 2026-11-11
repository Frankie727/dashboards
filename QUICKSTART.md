# Quick Start Guide - Defect Dashboard

## 5-Minute Setup

### Step 1: Open Command Prompt
```
Windows Key + R
Type: cmd
Press Enter
```

### Step 2: Navigate to Dashboard Directory
```cmd
cd "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
```

### Step 3: Run the Setup Script
```cmd
run_dashboard.bat
```

### Step 4: Select Option A (Fetch Data)
```
Press A
Press Enter
```

The script will:
- ✓ Check Python installation
- ✓ Check Node.js installation  
- ✓ Fetch work items from ediprod
- ✓ Generate `dashboard_data.json`

### Step 5: Select Option C (Open Dashboard)
```
Press C
Press Enter
```

Your default browser will open with the dashboard!

---

## What You'll See

### Dashboard Overview
```
┌─────────────────────────────────────────────────────┐
│                 📊 Defect Dashboard                  │
│  Real-time defect tracking and analysis from ediprod│
└─────────────────────────────────────────────────────┘

[Search Box] [Status Filter] [Area Filter] [Apply] [Refresh] [Export] [Reset]

┌─────────────┐ ┌──────────────┐ ┌──────────────┐
│ 📈 Total    │ │ ⚠️ Defects   │ │ ✅ Resolution│
│ Defects: 20 │ │ Introduced:15│ │ Rate: 35%    │
└─────────────┘ └──────────────┘ └──────────────┘

┌───────────────────────────────────────────────────────┐
│ Work Items Grid                                       │
├─────────────────────────────────────────────────────┤
│ ID     │ Summary         │ Status │ Defect WI      │
├─────────────────────────────────────────────────────┤
│ WD0001 │ Fix in Login    │ Open   │ WI00155391     │
│ WD0002 │ Payment Error   │ In Pro │ WI00148567     │
│ ...    │ ...             │ ...    │ ...            │
└─────────────────────────────────────────────────────┘
```

---

## First Time Usage

### 1. Explore the Data
- Scroll through the work items grid
- Look for "Defect Introduced in WI" column (shows what introduced the defect)
- Look for "Defect Introduced in Check-in" column (shows where it was introduced)

### 2. Try Filtering
- Search for a work item ID (e.g., "WD151292")
- Filter by status "Open" or "In Progress"
- Select a product area

### 3. Sort Data
- Click "Status" header to see all Open items at top
- Click "Created Time" to see newest first

### 4. Export Results
- Apply your filters
- Click "📥 Export CSV"
- Opens in Excel/Google Sheets for analysis

### 5. Refresh Latest Data
- Click "🔄 Refresh from ediprod"
- Fetches newest work items from ediprod
- Updates dashboard automatically

---

## Common Tasks

### View All Open Defects
1. Status Filter → "Open"
2. Change Type → "FIX"
3. Click "Apply Filters"

### Find Which WI Introduced the Defect
1. Look at "Defect Introduced in WI" column
2. Click on the Work Item number
3. (Future feature: link to ediprod details)

### Track Resolution Progress
1. Check "Resolution Rate" stat (top card)
2. Export CSV to track over time
3. Compare across product areas

### Analyze by Product Area
1. Filter by Product Area dropdown
2. Check statistics for that area
3. Sort by "Related Incidents" to see impact

### Get Data for Report
1. Apply any filters needed
2. Click "📥 Export CSV"
3. Open in Excel
4. Create pivot tables or charts

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl + F` | Search on page (browser) |
| `Ctrl + S` | Save page (if needed) |
| `F12` | Open developer tools (for debugging) |
| `Ctrl+F5` | Hard refresh (reload dashboard) |

---

## Troubleshooting

### "Python not found"
**Fix:** Install Python from https://www.python.org/

### "No data available" in dashboard
**Fix:** 
```cmd
python fetch_ediprod_data.py
```
Then refresh browser (Ctrl+F5)

### Dashboard loads slowly
**Fix:** 
- Wait for data to load (initial load can take a few seconds)
- Click "Apply Filters" to refresh view
- Close other browser tabs

### Want to use a different product?
```cmd
python fetch_ediprod_data.py --product RAT --change-type FIX
```

---

## Next Steps

### Advanced Features
- See README.md for full documentation
- Backend API for real-time sync (requires Node.js)
- Custom product/area filters
- Scheduled data refresh

### Integration
- Embed dashboard in your tools
- API calls to ediprod from your scripts
- Automation with Python scripts

### Customization
- Change colors and theme
- Add new columns
- Create custom reports

---

## Support

**Need help?**
1. Check README.md for detailed documentation
2. Review error messages in command prompt
3. Look at browser console (F12 → Console tab)
4. Try the Troubleshooting section in README.md

**Questions about data?**
- Contact your ediprod administrator
- Check work item details in ediprod directly

---

Enjoy your dashboard! 📊✨
