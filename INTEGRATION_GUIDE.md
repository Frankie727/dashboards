# EDI-Prod Dashboard Integration Guide

## ✅ Installation Complete!

All dashboard files have been successfully created in:
```
C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\
```

## 📁 Created Files

### Core Files
1. **defect_dashboard.html** (21 KB)
   - Main interactive web dashboard
   - Responsive design with charts and filters
   - Multiple data source support (JSON file, API, MCP)

2. **fetch_ediprod_data.py** (10.6 KB)
   - Python script to fetch data from ediprod
   - Enriches work items with defect information
   - Exports to JSON format
   - Command-line configurable

3. **backend.js** (3 KB)
   - Optional Node.js Express server
   - RESTful API for work items
   - CORS enabled for cross-origin requests

### Setup & Documentation
4. **run_dashboard.bat** (2.7 KB)
   - Interactive Windows batch script
   - Checks dependencies
   - Fetches data or starts server
   - Opens dashboard in browser

5. **package.json** (504 B)
   - Node.js dependencies configuration
   - Express and CORS packages

6. **README.md** (9.9 KB)
   - Comprehensive documentation
   - Installation & usage instructions
   - API endpoints reference
   - Troubleshooting guide

7. **QUICKSTART.md** (4.8 KB)
   - 5-minute quick start guide
   - Common tasks & keyboard shortcuts
   - Beginner-friendly instructions

## 🚀 Getting Started

### Option 1: Fastest Way (Recommended)
```batch
cd "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
run_dashboard.bat
```
Then:
- Select **A** to fetch data from ediprod
- Select **C** to open dashboard in browser

### Option 2: Manual Commands
```bash
# Fetch data
python fetch_ediprod_data.py --limit 20

# Open in browser
start defect_dashboard.html
```

### Option 3: With Backend API
```bash
# Terminal 1: Start backend
node backend.js

# Terminal 2: Open dashboard
start defect_dashboard.html
```

## 🔄 Data Flow Architecture

```
┌──────────────────┐
│  ediprod MCP     │ (https://ediprod.mcp.wtg.zone/)
│  Server          │
└────────┬─────────┘
         │
         ├─→ EDI-Prod-filter-workitems
         ├─→ EDI-Prod-get-job-workflows  
         ├─→ EDI-Prod-get-workflow-tasks
         └─→ EDI-Prod-get-issue-details
         │
    ┌────▼──────────────┐
    │ fetch_ediprod_    │ Python CLI Tool
    │ data.py           │
    └────┬──────────────┘
         │
         ├─→ dashboard_data.json (cached)
         │
    ┌────▼─────────────────┐
    │ defect_dashboard.html │ Browser App
    │                       │
    │ ┌─────────────────┐   │
    │ │ Statistics      │   │
    │ ├─────────────────┤   │
    │ │ Total Defects   │   │
    │ │ Introduced      │   │
    │ │ Resolution Rate │   │
    │ └─────────────────┘   │
    │ ┌─────────────────┐   │
    │ │ Data Grid       │   │
    │ ├─────────────────┤   │
    │ │ 10 Columns      │   │
    │ │ Sortable        │   │
    │ │ Filterable      │   │
    │ │ Searchable      │   │
    │ └─────────────────┘   │
    │ ┌─────────────────┐   │
    │ │ Export/Refresh  │   │
    │ └─────────────────┘   │
    └─────────────────────┘
```

## 📊 Dashboard Features

### Data Grid Columns
1. **Work Item #** - Unique identifier
2. **Summary** - Description of change/defect
3. **Status** - Open, In Progress, Closed
4. **Change Type** - FIX, PRD, PRJ, etc.
5. **Product Area** - High-level category
6. **Created Time** - Creation timestamp
7. **Defect Introduced in WI** ⭐ - Which WI introduced it
8. **Defect Introduced in Check-in** ⭐ - Which checkin introduced it
9. **Module** - Affected component
10. **Related Incidents** - Impact count

### Interactive Features
- 🔍 **Search** - By ID, summary, or area
- 🎯 **Filter** - By status and product area
- ↕️ **Sort** - Click any column header
- 📥 **Export** - Download as CSV
- 🔄 **Refresh** - Get latest data
- 📊 **Statistics** - Real-time KPIs

## 🔧 Configuration

### Python Script Options
```bash
python fetch_ediprod_data.py \
  --product SYS           # Product code (required)
  --change-type FIX       # Change type (FIX, PRD, ISS, etc.)
  --limit 20              # Max items (1-50)
  --output data.json      # Output file
```

### Environment Variables (Optional)
```bash
set EDI_PROD_BASE_URL=https://ediprod.mcp.wtg.zone
set EDI_PROD_TIMEOUT=30
```

### Dashboard Auto-Refresh
Edit in `defect_dashboard.html`:
```javascript
// Currently: 300000ms (5 minutes)
setInterval(() => loadFromEdiprod(), 300000);
```

## 📈 Typical Usage Workflow

### 1. Initial Setup
```bash
# Run once to fetch data
python fetch_ediprod_data.py --limit 20
```

### 2. Daily Usage
```bash
# Open dashboard
start defect_dashboard.html

# Use filters as needed
# Export for reports
```

### 3. Refresh Data
```bash
# When you need latest data
python fetch_ediprod_data.py

# Or in dashboard: click "Refresh from ediprod"
```

### 4. Generate Reports
```bash
# In dashboard:
# 1. Apply filters
# 2. Click "Export CSV"
# 3. Open in Excel
# 4. Create pivot tables
```

## 🔐 Security Notes

- ✅ All data stays local in `dashboard_data.json`
- ✅ No credentials stored in files
- ✅ MCP server handles authentication
- ✅ Browser-based, no server uploads
- ✅ CORS enabled only for localhost (if backend used)

## 🐛 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python 3.7+ from python.org |
| "No data available" | Run `python fetch_ediprod_data.py` |
| "Backend not available" | It's optional, dashboard works without it |
| "Slow dashboard" | Browser cache issue, press Ctrl+F5 |
| "Missing columns" | All columns mapped from ediprod data |
| "Data outdated" | Click "Refresh from ediprod" button |

See **README.md** for detailed troubleshooting.

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | 5-minute setup guide (start here!) |
| **README.md** | Complete documentation & API reference |
| **fetch_ediprod_data.py** | Inline comments explaining Python code |
| **defect_dashboard.html** | JavaScript comments in `<script>` section |

## 🎯 Next Steps

### Immediate
1. ✅ Run `run_dashboard.bat`
2. ✅ Select option A (fetch data)
3. ✅ Select option C (open dashboard)
4. ✅ Explore and test filters

### This Week
1. Review all dashboard columns
2. Export sample CSV
3. Share with team
4. Gather feedback

### Future Enhancements
- [ ] Real-time sync with websockets
- [ ] Scheduled email reports
- [ ] Custom defect categories
- [ ] Integration with other tools
- [ ] Advanced analytics & ML
- [ ] Mobile app version

## 📞 Support Resources

**Documentation:**
- QUICKSTART.md - For immediate help
- README.md - For comprehensive documentation

**Tools:**
- F12 key - Open browser developer tools
- Python debugger - `python -m pdb fetch_ediprod_data.py`

**Testing:**
- Test URL: `http://localhost:8000/defect_dashboard.html`
- Sample data: Loads automatically if no JSON found
- Backend: Optional, works without it

## ✨ Key Features Highlight

### Real-Time Data Fetching ⭐
- Direct connection to ediprod MCP server
- No manual data entry required
- Automatic data enrichment with defect details

### Powerful Filtering ⭐
- Multi-column filtering
- Full-text search across data
- Dynamic pivot table generation (via CSV export)

### Professional UI ⭐
- Modern responsive design
- Interactive charts and statistics
- Mobile-friendly layout

### Export Capabilities ⭐
- One-click CSV export
- Excel/Google Sheets compatible
- Filtered data exports

### Zero Setup for Viewing ⭐
- Works without backend (uses JSON file)
- Works without Node.js
- Just Python + browser needed

## 🎓 Learning Resources

### Understanding the Data
- **WI** = Work Item (e.g., WI0015391)
- **Check-in** = Code commit (e.g., Checkin #12345)
- **Defect Introduced** = Where did the bug come from?
- **Product Area** = Which module/team owns this?

### Common Queries
1. "What defects were introduced by WI0015391?"
   → Search for "WI0015391" in Defect Introduced column

2. "How many defects were introduced recently?"
   → Sort by "Created Time", count rows with defect values

3. "Which product area has most defects?"
   → Filter by product area, check "Total Defects" stat

4. "How long to close defects?"
   → Export CSV, calculate date differences in Excel

## 🚀 You're All Set!

Everything is configured and ready to use:
- ✅ Dashboard UI (HTML)
- ✅ Data fetcher (Python)
- ✅ Backend API (Node.js - optional)
- ✅ Documentation (README, QUICKSTART)
- ✅ Setup automation (Batch script)

**Start here:** Open QUICKSTART.md or run `run_dashboard.bat`

Happy dashboarding! 📊✨
