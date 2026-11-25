# 🔄 Cache System - Quick Summary

## The Issue You Asked About
**"Why does data refresh even when I don't update SharePoint?"**

**Answer:** The app has a **5-minute automatic cache refresh**. Every 5 minutes, the app automatically clears its cache and reloads data:
- Loads from CSV if files exist in SharePoint folder
- Falls back to SQL Server if CSV doesn't exist

---

## What Changed

### 1. ✅ Added "Clear Cache & Refresh" Buttons
- **Main Dashboard:** `🗑️ Clear Cache & Refresh Now` button
- **GPS Team page:** `🗑️ Clear Cache & Refresh` + `🔄 Soft Refresh` buttons
- **GPS Incidents page:** `🗑️ Clear Cache & Refresh` + `🔄 Soft Refresh` buttons

**Use these to:**
- Force immediate data reload (don't wait 5 minutes)
- Confirm new CSV files are loaded
- Refresh after SQL Server changes

### 2. ✅ Better Data Source Indicators
Each page now clearly shows:
- 📂 **Green info box** = Data from CSV file (with timestamp)
- ⚠️ **Yellow warning box** = Data from SQL Server (CSV not found)
- ⏱️ Cache expiry information and auto-refresh note

### 3. ✅ Documentation
Created comprehensive guide: `CACHE_AND_DATA_REFRESH_GUIDE.md`
- Explains how cache works
- Shows data flow diagram
- Answers common questions
- Troubleshooting steps

---

## How the Cache Works Now

```
CSV File exists?
  ├─ YES → Load CSV → Cache for 5 min → Display
  └─ NO  → Query SQL → Cache for 5 min → Display

After 5 minutes → Cache expires → Repeat above
```

---

## Three Ways to Get Fresh Data

### 1. Click "Clear Cache & Refresh" (Recommended)
- Gets fresh data **immediately**
- Best when you just uploaded CSV files
- Found on all dashboard pages

### 2. Wait 5 Minutes
- Cache expires automatically
- App refreshes on next interaction
- No action needed

### 3. Click "Soft Refresh"
- Reruns page (may still use cached data if valid)
- Use for visual glitches
- Lighter than Clear Cache

---

## Key Files Modified

1. **app.py** - Added cache info and clear button to main dashboard
2. **pages/1_GPS_Team.py** - Added cache info and refresh buttons
3. **pages/2_GPS_Group_Incidents.py** - Added cache info and refresh buttons
4. **CACHE_AND_DATA_REFRESH_GUIDE.md** - New comprehensive guide

---

## Testing the Cache

Try this workflow:

1. **Go to GPS Dashboard** → See cache info box
2. **Click "Clear Cache & Refresh Now"** → Page refreshes immediately
3. **Go to GPS Team page** → See data source (CSV or SQL)
4. **Change date filters** → Data updates instantly
5. **Wait 5 minutes** → Cache auto-expires
6. **Interact with app** → Data reloads automatically

---

## Important Notes

- **CSV Priority:** App always tries CSV first, falls back to SQL
- **Cache Key:** Each unique date range/product creates separate cache entry
- **Date Logic:** "Last 14 days" = today back 14 days (not future dates)
- **No 90-day Limit:** "Total Data Window" can be 365+ days now

---

## Next Steps for You

1. **Read:** `CACHE_AND_DATA_REFRESH_GUIDE.md` for detailed explanation
2. **Test:** Click cache buttons and verify data sources
3. **Upload CSV:** Place files in `C:\Users\raunak.singh\WiseTech Global\Team - ProdDev Global Product Support - Stats`
4. **Confirm:** Use "Clear Cache & Refresh" after uploading

---

**The cache system is now transparent and fully controllable! 🎉**
