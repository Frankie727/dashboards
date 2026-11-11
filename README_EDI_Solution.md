# EDI Prod Work Items Query - Complete Solution Package

**Created:** 2026-11-05T13:07:05Z  
**Status:** 🟡 READY FOR EXECUTION (Awaiting MCP Tool Access)

---

## 📋 Executive Summary

This package provides a complete solution for querying the EDI Prod MCP Server to retrieve work items for ENT and GLW products with FIX changeType from the last 30 days (2026-10-06 to 2026-11-05), excluding closed and cancelled items.

**Current Situation:**
- ✅ Query specifications defined and validated
- ✅ Data extraction templates created
- ✅ Multiple execution options provided
- 🟡 Awaiting access to EDI Prod MCP Server tools
- ⏳ Ready to execute in VS Code Copilot Chat (recommended)

---

## 📦 Package Contents

### 1. **Documentation Files**

| File | Purpose | Format |
|------|---------|--------|
| `EDI_WorkItems_Query_Guide.md` | Detailed specifications for both queries | Markdown |
| `EDI_Query_Execution_Guide.md` | Step-by-step execution instructions | Markdown |
| `README_EDI_Solution.md` | This file - package overview | Markdown |

### 2. **Configuration & Templates**

| File | Purpose | Format |
|------|---------|--------|
| `EDI_WorkItems_Result_Template.json` | Expected JSON output structure | JSON |
| Query specifications (inline) | Tool parameters and filters | JSON Schema |

### 3. **Executable Scripts**

| File | Purpose | Language |
|------|---------|----------|
| `Query-EDIWorkItems.ps1` | Automated query script with pagination | PowerShell |
| `process_edi_results.py` | Results processor and report generator | Python 3 |

---

## 🚀 Quick Start

### **FASTEST METHOD: VS Code Copilot Chat** ⭐

1. Open VS Code
2. Open Copilot Chat (Ctrl+Shift+V or Cmd+Shift+V)
3. Use this command:

```
@edi Execute both of these queries with EDI-Prod-filter-workitems:

QUERY 1: product="ENT", changeType=["FIX"], createdAfter="2026-10-06", createdBefore="2026-11-05", top=50, skip=0 (paginate as needed)

QUERY 2: product="GLW", changeType=["FIX"], createdAfter="2026-10-06", createdBefore="2026-11-05", top=50, skip=0 (paginate as needed)

Filter OUT: status="CLS" or "CAN" or empty

Extract per item: workItemId, summary, status, changeType, productArea, product, createdTime, module, priority, defectIntroducedWI, defectIntroducedCI, relatedIncidents

Return JSON with meta (timestamp, queryParams, totalCount) and data array containing all valid items.
```

4. Wait for results
5. Export JSON: "Save as edi_workitems_result.json"

**Estimated Time:** 2-5 minutes

---

## 📊 Query Parameters

### ENT Product Query
```json
{
  "product": "ENT",
  "changeType": ["FIX"],
  "createdAfter": "2026-10-06",
  "createdBefore": "2026-11-05",
  "top": 50,
  "skip": 0
}
```

### GLW Product Query
```json
{
  "product": "GLW",
  "changeType": ["FIX"],
  "createdAfter": "2026-10-06",
  "createdBefore": "2026-11-05",
  "top": 50,
  "skip": 0
}
```

### Status Filter
**INCLUDE:** OPN, ASN, WRK, SUS, and any other status EXCEPT:  
**EXCLUDE:** CLS (Closed), CAN (Cancelled), empty/null

---

## 📈 Expected Data Structure

### Per Work Item
```json
{
  "workItemId": "WI00123456",
  "summary": "Fix database connection timeout",
  "status": "OPN",
  "changeType": "FIX",
  "productArea": "DEL",
  "product": "ENT",
  "createdTime": "2026-10-15T10:30:00Z",
  "module": "ATR",
  "priority": "P1",
  "defectIntroducedWI": "WI00123450",
  "defectIntroducedCI": "CI#45678",
  "relatedIncidents": 2
}
```

### Complete Result Structure
```json
{
  "meta": {
    "timestamp": "2026-11-05T13:07:00Z",
    "queryParams": {
      "products": ["ENT", "GLW"],
      "changeType": "FIX",
      "statusFilter": "NCM (NOT CLS, NOT CAN, NOT empty)",
      "createdLastDays": 30
    },
    "totalCount": 0,
    "itemsWithDefectIntroduced": 0,
    "itemsWithoutDefectIntroduced": 0
  },
  "data": [/* work items array */]
}
```

---

## 🔧 Execution Options

### Option 1: VS Code Copilot Chat ⭐ RECOMMENDED
- **Pros:** Fastest, most direct, fully integrated
- **Cons:** Requires VS Code with MCP enabled
- **Time:** 2-5 minutes
- **See:** `EDI_Query_Execution_Guide.md` → "OPTION 1"

### Option 2: PowerShell Script (Local MCP Access)
- **Pros:** Automated, handles pagination, generates full report
- **Cons:** Requires local MCP server access
- **Time:** 5-10 minutes
- **See:** `EDI_Query_Execution_Guide.md` → "OPTION 2"
- **Run:** `.\Query-EDIWorkItems.ps1 -OutputPath "result.json"`

### Option 3: Manual EDI Prod UI
- **Pros:** No technical setup required
- **Cons:** Manual process, slower
- **Time:** 15-30 minutes
- **See:** `EDI_Query_Execution_Guide.md` → "OPTION 3"

### Option 4: REST API Call
- **Pros:** Scriptable, programmatic
- **Cons:** Requires API documentation and credentials
- **Time:** 10-20 minutes
- **See:** `EDI_Query_Execution_Guide.md` → "OPTION 4"

---

## 🛠️ Post-Processing

Once you have the results, use the Python processor:

```bash
# Generate report and save as JSON
python process_edi_results.py --input edi_workitems_result.json --output-json processed_results.json --report

# Convert CSV to JSON with statistics
python process_edi_results.py --input results.csv --format csv --output-json results.json

# Just print the report
python process_edi_results.py --input results.json --report
```

**Report includes:**
- Total items by product
- Status distribution
- Module distribution  
- Priority breakdown
- Defect traceability analysis
- Quality metrics

---

## 📊 Key Statistics to Extract

```
Total Work Items: [number]
By Product:
  ENT: [count] items
  GLW: [count] items

Defect Traceability:
  With WI reference: [count]
  With CI reference: [count]
  With both: [count]
  With neither: [count]

Status Distribution:
  OPN (Open): [count]
  ASN (Assigned): [count]
  WRK (Working): [count]
  SUS (Suspended): [count]
  [Other]: [count]

Top Modules: [list by count]
Priority Distribution: P1, P2, P3, etc.
```

---

## ✅ Validation Checklist

After execution, verify:

- [ ] Both ENT and GLW products queried
- [ ] All pagination pages retrieved (if > 50 items)
- [ ] Closed (CLS) items excluded
- [ ] Cancelled (CAN) items excluded
- [ ] Empty status items excluded
- [ ] All required fields present in output
- [ ] Timestamps in ISO 8601 format
- [ ] JSON is valid and well-formed
- [ ] Meta information populated correctly
- [ ] Statistics calculated accurately

---

## 🐛 Troubleshooting

### **"Tool not found" error**
→ EDI Prod MCP extension not installed in VS Code  
→ Enable in VS Code: Settings > MCP > Enable EDI Prod

### **"Authentication failed"**
→ Verify EDI Prod credentials  
→ Check if session token has expired  
→ Re-authenticate in EDI Prod UI first

### **Empty results**
→ Verify date range (2026-10-06 to 2026-11-05)  
→ Check if query period contains actual work items  
→ Try different status filter

### **Timeout**
→ Query is taking too long  
→ Try paginating manually with skip values  
→ Reduce date range if possible

### **Pagination incomplete**
→ Verify script continues until count < 50  
→ Check network connectivity  
→ Review query history in output

---

## 📝 File Locations

All files created in:
```
C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\
```

Specific files:
- Query Guide: `EDI_WorkItems_Query_Guide.md`
- Execution Guide: `EDI_Query_Execution_Guide.md`
- Template: `EDI_WorkItems_Result_Template.json`
- PowerShell Script: `Query-EDIWorkItems.ps1`
- Python Processor: `process_edi_results.py`

---

## 🎯 Next Steps

1. **Choose execution method** (Option 1 recommended)
2. **Execute query** using appropriate tool
3. **Collect results** and save as JSON
4. **Process results** using Python script if needed
5. **Validate output** using checklist above
6. **Generate report** and archive results

---

## 📞 Support & References

**Tool Documentation:** EDI-Prod-filter-workitems  
- Supports: product, changeType, createdAfter, createdBefore, top, skip
- Max results per page: 50
- Returns: CSV format with metadata

**Related Tools:**
- `EDI-Prod-get-job-workflows` - Get workflow details per work item
- `EDI-Prod-get-issue-details` - Get detailed work item information
- `EDI-Prod-lookup-products` - List valid product codes

---

## 📅 Timeline

| Phase | Status | Timeline |
|-------|--------|----------|
| Query Design | ✅ Complete | 2026-11-05 |
| Template Creation | ✅ Complete | 2026-11-05 |
| Script Development | ✅ Complete | 2026-11-05 |
| Execution | ⏳ Pending | 2026-11-05 |
| Post-Processing | ⏳ Pending | 2026-11-05 |
| Report Generation | ⏳ Pending | 2026-11-05 |

---

**Package Status:** 🟡 Ready for Execution  
**Last Updated:** 2026-11-05T13:07:05Z  
**Next Action:** Execute using Option 1 (VS Code Copilot Chat)

