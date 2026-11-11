# EDI Prod Work Items Query - Execution Guide

**Date Created:** 2026-11-05  
**Query Period:** 2026-10-06 to 2026-11-05 (Last 30 days)  
**Status:** Ready for Execution

## ⚠️ Current Limitation

This session is non-interactive and does **NOT** have direct access to invoke deferred MCP tools (EDI-Prod-filter-workitems). The MCP infrastructure is detected but not accessible via the available interface.

## ✅ Solution Options

### **OPTION 1: Execute in VS Code Copilot Chat (Recommended)**

The EDI Prod MCP Server tools are fully integrated with VS Code. Follow these steps:

#### Step 1: Copy the Query Prompt
Use this exact prompt in VS Code Copilot Chat:

```
@edi Use the EDI-Prod-filter-workitems tool to query work items with these EXACT parameters:

QUERY 1 - ENT Product:
- product: "ENT"
- changeType: ["FIX"]
- createdAfter: "2026-10-06"
- createdBefore: "2026-11-05"
- top: 50
- skip: 0

Then paginate: skip=50, 100, 150, etc. until result count < 50

QUERY 2 - GLW Product:
- product: "GLW"
- changeType: ["FIX"]
- createdAfter: "2026-10-06"
- createdBefore: "2026-11-05"
- top: 50
- skip: 0

Then paginate: skip=50, 100, 150, etc. until result count < 50

DATA EXTRACTION:
For each work item in all pages, extract:
- workItemId
- summary
- status (filter OUT: "CLS", "CAN", null/empty)
- changeType
- productArea
- product
- createdTime
- module
- priority
- defectIntroducedWI
- defectIntroducedCI
- relatedIncidents

RETURN FORMAT:
Compile all results into JSON with this structure:
{
  "meta": {
    "timestamp": "ISO 8601 timestamp",
    "queryParams": {
      "products": ["ENT", "GLW"],
      "changeType": "FIX",
      "statusFilter": "NCM (NOT CLS, NOT CAN, NOT empty)",
      "createdLastDays": 30
    },
    "totalCount": NUMBER,
    "itemsWithDefectIntroduced": NUMBER,
    "itemsWithoutDefectIntroduced": NUMBER
  },
  "data": [EXTRACTED WORK ITEMS]
}

INCLUDE: Pagination details, status distribution, defect traceability stats.
```

#### Step 2: Run Query
Click "Run" or press Enter to execute the queries.

#### Step 3: Export Results
Once complete, ask Copilot to:
- "Export this as a JSON file"
- Save to: `edi_workitems_result.json`

---

### **OPTION 2: Execute PowerShell Script (If MCP Server is Accessible Locally)**

The script `Query-EDIWorkItems.ps1` is provided with full pagination and filtering logic.

#### Requirements:
- EDI Prod MCP Server accessible on localhost or networked
- PowerShell 5.1+ with MCP client capabilities

#### Execution:
```powershell
cd "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
.\Query-EDIWorkItems.ps1 -OutputPath "edi_workitems_result.json"
```

#### Output:
- JSON file with all work items
- Statistics and query history
- Status: ✅ Complete when script exits without errors

---

### **OPTION 3: Use EDI Prod Web Interface**

If programmatic access isn't available, you can manually:

1. Log into EDI Prod Application
2. Navigate to **Work Items** → **Advanced Search**
3. Set filters:
   - Product: ENT or GLW
   - Change Type: FIX
   - Created Date: 2026-10-06 to 2026-11-05
   - Status: NOT IN (Closed, Cancelled)
4. Export results as CSV
5. Use the provided Python script to convert to JSON

---

### **OPTION 4: REST API Call (If EDI Prod Exposes REST)**

If EDI Prod has a REST API endpoint:

```bash
# ENT Query
curl -X POST "https://ediprod.company.com/api/workitems/filter" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "ENT",
    "changeType": ["FIX"],
    "createdAfter": "2026-10-06",
    "createdBefore": "2026-11-05",
    "top": 50,
    "skip": 0
  }' > ent_results.json

# GLW Query
curl -X POST "https://ediprod.company.com/api/workitems/filter" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "GLW",
    "changeType": ["FIX"],
    "createdAfter": "2026-10-06",
    "createdBefore": "2026-11-05",
    "top": 50,
    "skip": 0
  }' > glw_results.json
```

---

## 📋 Query Specifications Summary

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Products** | ENT, GLW | Both queried separately |
| **Change Type** | FIX | Defect fixes only |
| **Date Range** | 2026-10-06 to 2026-11-05 | Last 30 days |
| **Status Filter** | NOT CLS, NOT CAN, NOT empty | Include: OPN, ASN, WRK, SUS |
| **Page Size** | 50 items max | Use pagination for >50 results |
| **Pagination** | skip/top | Continue until count < 50 |

---

## 📊 Expected Data Fields

```
workItemId          - Work item identifier (e.g., WI00123456)
summary             - Title/description of the work item
status              - Current status code (OPN, ASN, WRK, SUS, etc.)
changeType          - Type of change (FIX, PRD, ENH, etc.)
productArea         - Product area code (RAT, DEL, FIN, etc.)
product             - Product code (ENT or GLW)
createdTime         - ISO 8601 timestamp when created
module              - Module code (ATR, PPI, etc.)
priority            - Priority level (P1, P2, P3, etc.)
defectIntroducedWI  - Work item that introduced the defect (if known)
defectIntroducedCI  - Commit/integration that introduced defect (if known)
relatedIncidents    - Count of related customer incidents
```

---

## 🎯 Success Criteria

**Query is successful when:**
1. ✅ Both ENT and GLW products queried
2. ✅ All pages retrieved (pagination complete)
3. ✅ Closed and Cancelled items excluded
4. ✅ All required fields extracted
5. ✅ JSON output generated with meta information
6. ✅ Statistics calculated (defect traceability, status distribution)

---

## 📁 Files Provided

| File | Purpose |
|------|---------|
| `EDI_WorkItems_Query_Guide.md` | Detailed query specifications |
| `EDI_WorkItems_Result_Template.json` | Expected JSON output structure |
| `Query-EDIWorkItems.ps1` | PowerShell script for local execution |
| `EDI_Query_Execution_Guide.md` | This file - execution instructions |

---

## 🔗 Related Commands

Once you have the results, you can:

```powershell
# View results
Get-Content edi_workitems_result.json | ConvertFrom-Json | Format-Table

# Count by product
(Get-Content edi_workitems_result.json | ConvertFrom-Json).data | 
  Group-Object product | 
  Select-Object Name, @{N="Count";E={$_.Group.Count}}

# Count by status
(Get-Content edi_workitems_result.json | ConvertFrom-Json).data | 
  Group-Object status | 
  Select-Object Name, @{N="Count";E={$_.Group.Count}}

# Find items with defects
(Get-Content edi_workitems_result.json | ConvertFrom-Json).data | 
  Where-Object { $_.defectIntroducedWI -or $_.defectIntroducedCI } | 
  Select-Object workItemId, summary, defectIntroducedWI, defectIntroducedCI
```

---

## 📞 Support

If you encounter issues:

1. **MCP Tool Not Found:** Ensure VS Code's EDI Prod MCP extension is installed and enabled
2. **Authentication Error:** Verify your EDI Prod credentials are valid
3. **Timeout:** If query takes > 5 minutes, paginate manually with higher skip values
4. **Empty Results:** Verify the date range (2026-10-06 to 2026-11-05) contains actual work items

---

**Last Updated:** 2026-11-05T13:07:05Z  
**Status:** Ready for Execution
