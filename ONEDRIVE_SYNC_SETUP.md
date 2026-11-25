# OneDrive Sync Setup - Quick Guide

## 🎯 Goal
Sync the SharePoint Stats folder to your PC so data can automatically sync to Frankie's machine.

---

## ✅ Manual Setup Steps

### **Step 1: Navigate to SharePoint Stats Folder**
1. Go to: https://wisetechglobal.sharepoint.com/sites/t-ProdDevGlobalProductSupport
2. Click: **Shared Documents** → **Global Product Support** → **Buddy Training Material** → **Stats**
3. You should see the **Stats** folder (currently shows as empty or with 94raunak subfolder)

### **Step 2: Click the "Sync" Button** 
1. Look at the top menu bar in SharePoint
2. Find and click **"Sync"** button (typically in the toolbar)
3. A dialog will appear: **"Open with OneDrive"**
4. Click **"Yes"** when prompted

### **Step 3: Choose Local Sync Folder**
1. OneDrive will ask where to sync the folder
2. **Recommended location**: `C:\SharePoint\GPS-Stats`
3. Click **"Select Folder"** or **"Next"**
4. OneDrive will start syncing files

### **Step 4: Wait for Sync to Complete**
- OneDrive will sync the folder in the background
- You'll see a folder icon in your taskbar (bottom right) showing sync status
- Once complete, the **Stats** folder will appear on your PC

---

## 📂 After Sync is Complete

Your folder structure will be:
```
C:\SharePoint\GPS-Stats\          ← This is what syncs from SharePoint
├── gps_team.csv                  ← Will appear after you export from app
├── group_incidents.csv           ← Will appear after you export from app
└── data_metadata.json            ← Timestamps
```

---

## 🔗 Link App to Synced Folder (Optional)

If you want the app to use the synced folder directly:

### **Option A: Create a Symlink (Recommended)**
```powershell
# Run PowerShell as Administrator
cd C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards
mklink /d .data_cache "C:\SharePoint\GPS-Stats"
```

### **Option B: Manual Copy**
- Copy files from synced folder to `.data_cache/` manually
- OR Just rely on OneDrive to sync after export

---

## 📊 Testing the Setup

### **1. Export Data from Dashboard**
```
http://localhost:8507
Click: 🔄 "Update Data from SQL"
Wait for: ✅ "Data updated successfully!"
```

### **2. Check Local Files**
```powershell
Get-ChildItem "C:\Users\raunak.singh\OneDrive - WiseTech Global Pty Ltd\REPO\dashboards\.data_cache\"
# Should show: gps_team.csv, group_incidents.csv, data_metadata.json
```

### **3. Check SharePoint (should auto-sync)**
```
https://wisetechglobal.sharepoint.com/sites/t-ProdDevGlobalProductSupport/Shared Documents/Global Product Support/Buddy Training Material/Stats
# Should show the same files
```

### **4. Verify Frankie's Access**
- Frankie clones the repo
- Syncs the same SharePoint Stats folder
- Runs: `python -m streamlit run app.py`
- Clicks: 📥 "Load from SharePoint"
- ✅ Dashboard shows data from synced folder!

---

## ⏱️ Timing

| Step | Time |
|------|------|
| Navigate to SharePoint | 1 min |
| Click Sync | 1 min |
| Initial OneDrive Sync | 2-5 mins |
| **Total Setup** | **5-10 mins** |

---

## ❓ Troubleshooting

### "Sync" button not visible?
- Try refreshing the page (F5)
- Use new Edge/Chrome browser
- Try different device

### "OneDrive folder not syncing"?
- Check OneDrive taskbar icon → Activity
- Ensure OneDrive is running
- Check: Settings → Accounts → Sync settings

### "Files not appearing in .data_cache"?
- Wait 2-5 minutes for OneDrive to sync
- Check OneDrive taskbar for sync progress
- Manually copy files from C:\SharePoint\GPS-Stats to .data_cache\

---

## ✨ Next Steps

1. ✅ Set up OneDrive sync (this guide)
2. 🔄 Click "Update Data from SQL" in dashboard
3. ⏳ Wait for OneDrive to sync files to SharePoint
4. 📥 Click "Load from SharePoint" to test
5. 🎉 Share dashboard URL with Frankie!

