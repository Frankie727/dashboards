# EDI Work Items Query - Quick Reference

## 🎯 What to Query
- **Products:** ENT, GLW
- **Type:** FIX (defect fixes only)
- **Date Range:** 2026-10-06 to 2026-11-05 (last 30 days)
- **Status:** Exclude CLS, CAN, empty (Include: OPN, ASN, WRK, SUS)

## 🚀 Fastest Execution: VS Code Copilot Chat

**Copy & Paste This:**
```
@edi Execute both work item queries with EDI-Prod-filter-workitems:
QUERY 1: product=ENT, changeType=[FIX], createdAfter=2026-10-06, createdBefore=2026-11-05, top=50, skip=0
QUERY 2: product=GLW, changeType=[FIX], createdAfter=2026-10-06, createdBefore=2026-11-05, top=50, skip=0
Paginate until count<50. Exclude status CLS,CAN,empty. Extract: workItemId, summary, status, changeType, productArea, product, createdTime, module, priority, defectIntroducedWI, defectIntroducedCI, relatedIncidents. Return JSON with meta and data array.
```

**Done in:** 2-5 minutes ✅

## 📊 Data Fields to Extract
| Field | Example |
|-------|---------|
| workItemId | WI00123456 |
| summary | "Fix database connection" |
| status | OPN, ASN, WRK, SUS |
| changeType | FIX |
| productArea | DEL, FIN, RAT |
| product | ENT or GLW |
| createdTime | 2026-10-15T10:30:00Z |
| module | ATR, PPI |
| priority | P1, P2, P3 |
| defectIntroducedWI | WI00123450 |
| defectIntroducedCI | CI#12345 |
| relatedIncidents | 0, 1, 2, ... |

## 📁 Files in This Package
1. `README_EDI_Solution.md` - Complete overview
2. `EDI_Query_Execution_Guide.md` - Detailed instructions
3. `EDI_WorkItems_Query_Guide.md` - Technical specs
4. `EDI_WorkItems_Result_Template.json` - Expected output
5. `Query-EDIWorkItems.ps1` - PowerShell automation
6. `process_edi_results.py` - Results processor
7. `EDI_WorkItems_Quick_Reference.md` - This file

## ✅ Success Criteria
- [ ] Both ENT and GLW queried
- [ ] All pages retrieved (pagination)
- [ ] Closed/cancelled items excluded
- [ ] All fields extracted
- [ ] Valid JSON output
- [ ] Meta info included
- [ ] Statistics calculated

## 🔗 Tool Used
**EDI-Prod-filter-workitems**
- Input: product, changeType, createdAfter, createdBefore, top, skip
- Output: CSV with workitem details + total count
- Max 50 items per page (use skip for pagination)

## 📈 Expected Results
```
Total: ~50-200 work items (estimated)
By Product:
  - ENT: variable count
  - GLW: variable count
Defect Traceability:
  - With introduced defect info: ~30-50%
  - Without defect info: ~50-70%
```

## 🛠️ Post-Execution
```bash
# Process results with Python
python process_edi_results.py --input result.json --report

# View in PowerShell
$data = Get-Content result.json | ConvertFrom-Json
$data.data | Format-Table workItemId, summary, status
```

## ❌ Common Issues & Fixes
| Issue | Solution |
|-------|----------|
| "Tool not found" | Enable EDI Prod MCP in VS Code |
| Empty results | Verify date range has work items |
| Timeout | Try manual pagination with skip |
| Missing fields | Ensure all items returned complete |

## 📞 Quick Help
- **Questions?** See `EDI_Query_Execution_Guide.md`
- **Technical details?** See `EDI_WorkItems_Query_Guide.md`
- **Need processing?** Use `process_edi_results.py`

---
**Status:** Ready ✅ | **Time:** 2-5 min | **Method:** VS Code Copilot Chat
