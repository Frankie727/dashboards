# Defect Dashboard - EDI Prod Integration

A comprehensive web-based dashboard for tracking defect work items from ediprod with real-time data fetching and advanced filtering capabilities.

## Features

✅ **Real-time Data Sync** - Fetch defect data directly from ediprod  
✅ **Rich Dashboard** - Interactive charts, statistics, and filters  
✅ **Defect Tracking** - View "Defect Introduced in WI" and "Defect Introduced in Check-in"  
✅ **Advanced Filtering** - Filter by status, product area, and search terms  
✅ **Export Capabilities** - Download data as CSV for further analysis  
✅ **Sortable Columns** - Click any column header to sort ascending/descending  
✅ **Responsive Design** - Works on desktop and mobile devices  

## Components

### 1. `defect_dashboard.html`
The main interactive web dashboard. Features:
- Real-time statistics cards
- Filterable data grid with 10 columns
- Search functionality
- Column sorting
- CSV export
- Multiple data source support

### 2. `fetch_ediprod_data.py`
Python script to fetch work items and defect data from ediprod MCP server:
- Connects to ediprod via EDI-Prod-filter-workitems
- Enriches data with defect details
- Exports to JSON format
- Supports filtering by product and change type

### 3. `backend.js`
Optional Node.js/Express backend server:
- RESTful API for work items
- Proxies to ediprod MCP server
- Enables real-time dashboard refresh
- Supports pagination

### 4. `run_dashboard.bat`
Windows batch script for easy setup and execution:
- Verifies Python and Node.js installation
- Fetches data from ediprod
- Starts backend server
- Opens dashboard in browser

## Installation & Setup

### Prerequisites

1. **Python 3.7+** (Required)
   ```
   Download from https://www.python.org/
   Add to PATH during installation
   ```

2. **Node.js 14+** (Optional - for backend API)
   ```
   Download from https://nodejs.org/
   ```

3. **Web Browser** (Chrome, Firefox, Safari, Edge)

4. **EDI-Prod MCP Server** (Required)
   - Must be configured and accessible
   - File location: `.../vscode/.../file_mcp.json`
   - Endpoint: `https://ediprod.mcp.wtg.zone/`

### Setup Steps

#### Option 1: Quick Start with Batch Script (Windows)

```batch
cd "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
run_dashboard.bat
```

Then select options:
- **A**: Fetch fresh data from ediprod
- **B**: Start backend API (optional)
- **C**: Open dashboard in browser

#### Option 2: Manual Setup

1. **Fetch Data**
   ```bash
   python fetch_ediprod_data.py --product SYS --change-type FIX --limit 20
   ```

2. **Start Backend Server** (Optional)
   ```bash
   npm install express cors
   node backend.js
   ```

3. **Open Dashboard**
   - Double-click `defect_dashboard.html`, or
   - Use Python's built-in server:
     ```bash
     python -m http.server 8000
     ```
   - Visit: `http://localhost:8000/defect_dashboard.html`

#### Option 3: Direct in VS Code

1. Open this folder in VS Code
2. Use Copilot with EDI-Prod MCP tools available
3. Ask Copilot to query ediprod data
4. Copy JSON response and save as `dashboard_data.json`
5. Open `defect_dashboard.html`

## Data Flow

```
┌─────────────────┐
│   ediprod       │
│   MCP Server    │
└────────┬────────┘
         │
         │ EDI-Prod-filter-workitems
         │
    ┌────▼──────────┐
    │  Python Script │
    │ fetch_ediprod_ │
    │    data.py     │
    └────┬───────────┘
         │
         │ JSON Export
         │
    ┌────▼──────────────────┐
    │ dashboard_data.json    │
    │ (or backend.js proxy)  │
    └────┬───────────────────┘
         │
         │ HTTP Request
         │
    ┌────▼─────────────────┐
    │  defect_dashboard    │
    │  .html (Browser)     │
    └──────────────────────┘
```

## Usage

### 1. View Dashboard
- Open `defect_dashboard.html` in your browser
- Dashboard loads sample data by default
- If `dashboard_data.json` exists, it's loaded automatically
- If backend is running, live data is fetched from ediprod

### 2. Fetch Fresh Data
```bash
python fetch_ediprod_data.py
```

Options:
```bash
--output <file>        Output JSON file (default: dashboard_data.json)
--product <code>       Product code (default: SYS)
--change-type <code>   Change type (default: FIX)
--limit <number>       Max items to fetch (default: 20, max: 50)
```

Examples:
```bash
# Fetch all defect fixes
python fetch_ediprod_data.py --change-type FIX --limit 50

# Fetch from specific product
python fetch_ediprod_data.py --product RAT --limit 30

# Export to different file
python fetch_ediprod_data.py --output my_defects.json
```

### 3. Use Dashboard Features

#### Search
- Type in "Search Work Items" field
- Searches: Work Item ID, Summary, Product Area
- Click "Apply Filters" or press Enter

#### Filter by Status
1. Select status from "Filter by Status" dropdown
2. Click "Apply Filters"
3. Grid updates in real-time

#### Filter by Product Area
1. Select area from "Filter by Product Area" dropdown
2. Click "Apply Filters"

#### Sort Columns
- Click any column header to sort
- Click again to reverse sort direction
- Works on all columns

#### Export Data
1. Apply filters as needed (optional)
2. Click "📥 Export CSV"
3. Saves filtered data as CSV file
4. Open in Excel/Google Sheets

#### Reset
- Click "🔄 Reset" to clear all filters
- Restores full dataset view

### 4. Refresh Data
1. Click "🔄 Refresh from ediprod"
2. Fetches latest data from ediprod
3. Updates dashboard automatically

## Data Columns Explained

| Column | Description |
|--------|-------------|
| **Work Item #** | Unique identifier (e.g., WD151292) |
| **Summary** | Brief description of the defect/change |
| **Status** | Current state: Open, In Progress, Closed |
| **Change Type** | FIX, PRD, PRJ, etc. |
| **Product Area** | High-level category (e.g., Identity & Security) |
| **Created Time** | When the work item was created |
| **Defect Introduced in WI** | Work item that introduced the defect |
| **Defect Introduced in Check-in** | Check-in/commit that introduced the defect |
| **Module** | Specific module/component affected |
| **Related Incidents** | Count of related customer incidents |

## Key Metrics

### Total Defects
- Count of all work items matching filters
- Updated when filters change

### Defects Introduced
- Count of work items with "Defect Introduced in WI" value
- Shows impact of previous changes

### Resolution Rate
- Percentage of closed items vs. total
- Indicates team efficiency

## Troubleshooting

### Dashboard shows "No data available"
**Solution:**
1. Run `python fetch_ediprod_data.py` to fetch data
2. Verify `dashboard_data.json` was created
3. Refresh browser (Ctrl+F5)

### "Error connecting to backend API" message
**Solution:**
1. Backend API is optional - dashboard works without it
2. To enable: Run `node backend.js` in separate terminal
3. Ensure Node.js and Express are installed

### Python script fails with "No module named mcp"
**Solution:**
1. Make sure EDI-Prod MCP server is configured
2. Check file: `.../vscode/.../file_mcp.json`
3. Verify ediprod endpoint is accessible

### Data looks outdated
**Solution:**
1. Click "🔄 Refresh from ediprod"
2. Or manually run: `python fetch_ediprod_data.py`
3. Dashboard auto-refreshes every 5 minutes

### Browser can't find defect_dashboard.html
**Solution:**
1. Right-click the file and "Open with" your browser
2. Or use Python server:
   ```bash
   python -m http.server 8000
   ```
   Then visit: `http://localhost:8000/defect_dashboard.html`

## API Endpoints (Backend Only)

If backend.js is running, available endpoints:

```
GET /api/workitems
  Query parameters:
    ?product=SYS
    ?changeType=FIX
    ?top=20
    ?skip=0

GET /api/workitems/:id
  Returns detailed info for work item

GET /api/workitems/:id/defect-details
  Returns defect introduced information

POST /api/refresh
  Triggers data refresh from ediprod
```

## Performance Notes

- Dashboard handles 50-100 items smoothly
- For larger datasets (1000+ items), consider pagination
- CSV export works best with <10,000 rows
- Python script fetch time: ~1-2 seconds per 20 items

## Configuration Files

### dashboard_data.json
Generated by `fetch_ediprod_data.py`. Format:
```json
{
  "meta": {
    "timestamp": "2026-11-05T12:40:11Z",
    "product": "SYS",
    "changeType": "FIX",
    "totalCount": 20,
    "introducedCount": 15,
    "resolutionRate": 35.5
  },
  "data": [
    {
      "workItemId": "WD151292",
      "summary": "...",
      "status": "Open",
      ...
    }
  ]
}
```

## Customization

### Change Refresh Interval
In `defect_dashboard.html`, find:
```javascript
// Auto-refresh every 5 minutes
setInterval(() => {
    loadFromEdiprod();
}, 300000);
```
Change `300000` to milliseconds (e.g., `600000` for 10 minutes)

### Add Custom Columns
1. Edit the table structure in HTML
2. Add column to `renderTable()` function
3. Update data structure in Python script

### Change Color Scheme
Search for gradient definitions and update colors:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Python script output for error messages
3. Check browser console (F12) for JavaScript errors
4. Verify ediprod MCP server is running and accessible

## License

Internal use only - CargoWise Defect Tracking Dashboard

## Version History

- **v1.0** (2026-11-05)
  - Initial release with ediprod MCP integration
  - Real-time data fetching
  - Advanced filtering and export
  - Responsive dashboard UI
