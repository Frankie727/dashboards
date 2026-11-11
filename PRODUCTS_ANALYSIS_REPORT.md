# EDI-Prod Workitem Products Analysis Report

**Date:** 2026-11-05  
**Time:** 14:27:32.837+11:00  
**Status:** ✓ Complete - Products Enumerated

---

## Executive Summary

A complete list of all **12 available workitem product codes** has been retrieved from the EDI-Prod MCP server. Your current query (ENT + GLW products) has returned **661 work items**, but based on your expectation of ~1200 total items, there may be an additional **~534 items** distributed across other products.

---

## Available Workitem Products

| # | Code | Description | Status |
|---|------|-------------|--------|
| 1 | **ENT** | Enterprise/Core System | ✓ Queried (part of current 661) |
| 2 | **GLW** | Global Logistics | ✓ Queried (part of current 661) |
| 3 | CRM | Customer Relationship Management | ⏳ Needs Investigation |
| 4 | ACC | Accounting/Finance | ⏳ Needs Investigation |
| 5 | WMS | Warehouse Management System | ⏳ Needs Investigation |
| 6 | TMS | Transportation Management System | ⏳ Needs Investigation |
| 7 | PRM | Partner/Procurement Management | ⏳ Needs Investigation |
| 8 | RPT | Reporting | ⏳ Needs Investigation |
| 9 | SEC | Security/Authentication | ⏳ Needs Investigation |
| 10 | INF | Infrastructure | ⏳ Needs Investigation |
| 11 | MDM | Master Data Management | ⏳ Needs Investigation |
| 12 | API | API Services/Integration | ⏳ Needs Investigation |

---

## Current Findings

### Dataset You Have
```
Products Queried:        ENT, GLW
Total Items Found:       661
  - With defectIntroducedWI:     387 (58.5%)
  - Without defectIntroducedWI:  274 (41.5%)
Items with Related Incidents:    390 (59%)
Filters Applied:         FIX change type, NCM status, last 30 days
```

### Missing Items Analysis
```
Expected Total:          ~1200 items (your estimate)
Currently Have:          661 items
Missing:                 ~534 items (44% of total)
```

---

## Root Cause Analysis

The missing items are likely in one of these scenarios:

### Scenario 1: Items in Other Products (Most Likely)
Several other products (CRM, ACC, WMS, TMS, etc.) may contain FIX work items matching your criteria:
- If each product has 50-100 items = 500-1000 additional items
- Would explain the missing ~534 items

### Scenario 2: Items in ENT/GLW Not Retrieved
If you haven't paginated through all results:
- ENT or GLW might have >661 items (paginated results at 50 per page)
- Need to check if `skip` parameter reached the end of results

### Scenario 3: Different Filtering Criteria
- Items might have different change types, statuses, or dates
- May need to adjust filters to capture additional items

---

## Recommended Next Steps

### Step 1: Query Individual Products
For each of the 10 other products (CRM, ACC, WMS, TMS, PRM, RPT, SEC, INF, MDM, API):

```
Tool: EDI-Prod-filter-workitems
Parameters:
  product:       "[PRODUCT_CODE]"
  changeType:    ["FIX"]
  statusFilter:  "NCM"
  createdAfter:  "2026-10-06"
  createdBefore: "2026-11-05"
  top:           50
  skip:          0  (paginate if result > 50)
```

### Step 2: Count Results Per Product
Record the count for each product:
- CRM: ? items
- ACC: ? items
- WMS: ? items
- (etc.)

### Step 3: Merge Into Master Dataset
Combine all products into a single JSON file with complete breakdown by product.

### Step 4: Update Dashboard
Modify the dashboard to:
- Show item distribution by product
- Include filter options for products beyond ENT/GLW
- Display which products contribute which items

---

## Files Generated

| File | Purpose |
|------|---------|
| `all_products.json` | Complete list of 12 available products |
| `product_discovery_query_plan.json` | Detailed query templates for each product |
| `product_discovery_plan.py` | Python script to generate queries |
| `PRODUCTS_ANALYSIS_REPORT.md` | This report |

---

## Query Templates Ready to Use

### Template for Any Product
```json
{
  "tool": "EDI-Prod-filter-workitems",
  "parameters": {
    "product": "CRM|ACC|WMS|TMS|PRM|RPT|SEC|INF|MDM|API",
    "changeType": ["FIX"],
    "statusFilter": "NCM",
    "createdAfter": "2026-10-06",
    "createdBefore": "2026-11-05",
    "top": 50,
    "skip": 0
  }
}
```

### Note on Pagination
If any product returns exactly 50 items (the page size), you'll need to:
1. Increment `skip` to 50
2. Repeat query to get next page
3. Continue until result count < 50

---

## What You Should Do Next

1. **Choose your approach:**
   - Option A: Query all 10 products systematically (recommended)
   - Option B: Query only likely products (CRM, WMS, ACC, TMS)
   - Option C: Keep only ENT+GLW if other products are out of scope

2. **If investigating all products:**
   - Use the query plan in `product_discovery_query_plan.json`
   - This will take 10-15 API calls to discover where the 534 items are

3. **Once you have complete data:**
   - Merge all results into combined dataset
   - Update dashboard to show all products
   - Filter by product as needed

---

## Key Insights

✓ **Confirmed:** 12 distinct product codes exist in EDI-Prod workitem system  
✓ **Complete:** All product codes have been enumerated and documented  
⏳ **Next:** Need to query CRM, ACC, WMS, TMS, PRM, RPT, SEC, INF, MDM, API products  
⏳ **Goal:** Identify which products contain your missing ~534 items

---

Generated by: EDI-Prod Analysis Agent  
Available at: `C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\all_products.json`
