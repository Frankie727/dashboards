# Quick Reference: Query Each Product for Missing Items

This document provides ready-to-use queries to investigate the 10 additional products and find your missing ~534 items.

## Current Status
- **Already Have:** 661 items from ENT + GLW
- **Missing:** ~534 items (expecting ~1200 total)
- **To Investigate:** CRM, ACC, WMS, TMS, PRM, RPT, SEC, INF, MDM, API

---

## Product-by-Product Query Guide

### Standard Query Parameters (Same for All Products)
```
Tool:          EDI-Prod-filter-workitems
changeType:    ["FIX"]
statusFilter:  "NCM"  (Status NOT Closed, NOT Cancelled, NOT empty)
createdAfter:  "2026-10-06"
createdBefore: "2026-11-05"
top:           50
skip:          0 (increment to 50, 100, etc. if results >= 50)
```

---

## Individual Product Queries

### 1. CRM (Customer Relationship Management)
```
Product:  CRM
Purpose:  Customer-facing system changes
Expected: Possibly high volume (customer-affecting defects)
Query:    product="CRM", changeType=["FIX"], top=50, skip=0
```

### 2. ACC (Accounting/Finance)  
```
Product:  ACC
Purpose:  Financial system, invoicing, GL
Expected: Medium volume (financial reconciliation fixes)
Query:    product="ACC", changeType=["FIX"], top=50, skip=0
```

### 3. WMS (Warehouse Management System)
```
Product:  WMS
Purpose:  Warehouse operations, inventory
Expected: High volume (operational defects)
Query:    product="WMS", changeType=["FIX"], top=50, skip=0
```

### 4. TMS (Transportation Management System)
```
Product:  TMS
Purpose:  Shipping, freight, logistics tracking
Expected: Medium-high volume (transportation-related fixes)
Query:    product="TMS", changeType=["FIX"], top=50, skip=0
```

### 5. PRM (Partner/Procurement Management)
```
Product:  PRM
Purpose:  Supplier management, purchase orders
Expected: Medium volume (supplier-related fixes)
Query:    product="PRM", changeType=["FIX"], top=50, skip=0
```

### 6. RPT (Reporting)
```
Product:  RPT
Purpose:  Reporting engine, dashboards, analytics
Expected: Low-medium volume (report generation fixes)
Query:    product="RPT", changeType=["FIX"], top=50, skip=0
```

### 7. SEC (Security/Authentication)
```
Product:  SEC
Purpose:  User authentication, authorization, security
Expected: Low-medium volume (security-related fixes)
Query:    product="SEC", changeType=["FIX"], top=50, skip=0
```

### 8. INF (Infrastructure)
```
Product:  INF
Purpose:  System infrastructure, deployment, monitoring
Expected: Low volume (infrastructure-related fixes)
Query:    product="INF", changeType=["FIX"], top=50, skip=0
```

### 9. MDM (Master Data Management)
```
Product:  MDM
Purpose:  Data quality, master records, data synchronization
Expected: Low-medium volume (data consistency fixes)
Query:    product="MDM", changeType=["FIX"], top=50, skip=0
```

### 10. API (API Services/Integration)
```
Product:  API
Purpose:  Integration points, API endpoints, third-party systems
Expected: Medium volume (integration-related fixes)
Query:    product="API", changeType=["FIX"], top=50, skip=0
```

---

## Execution Checklist

- [ ] Query CRM → Record count: _____ items
- [ ] Query ACC → Record count: _____ items
- [ ] Query WMS → Record count: _____ items
- [ ] Query TMS → Record count: _____ items
- [ ] Query PRM → Record count: _____ items
- [ ] Query RPT → Record count: _____ items
- [ ] Query SEC → Record count: _____ items
- [ ] Query INF → Record count: _____ items
- [ ] Query MDM → Record count: _____ items
- [ ] Query API → Record count: _____ items

**Total from other products: _____ items**

---

## Expected Outcome

### Scenario A: Items Found in Other Products
If totals sum to ~534 additional items, your complete dataset structure will be:
```
ENT:  X items
GLW:  Y items
CRM:  Z items
...
Total: ~1200 items
```

### Scenario B: Items Concentrated in 1-2 Products
If 500+ items are in one product (e.g., WMS or CRM):
- Focus dashboard on that product
- May want to use separate filters per product

### Scenario C: No Additional Items Found
If totals remain 661:
- ENT + GLW contain all available FIX items
- Your "missing" 534 items may not exist or use different criteria
- Review filter assumptions (dates, change types, status values)

---

## Pagination Handling

If any product returns **exactly 50 items**:
1. The result is truncated (more items available)
2. Query again with `skip=50`
3. Continue until result < 50 items
4. Sum all pages for that product

**Example:**
```
CRM, skip=0  → 50 items
CRM, skip=50 → 50 items  
CRM, skip=100 → 25 items  ← Stop (< 50)
CRM Total: 125 items
```

---

## Files to Support Investigation

1. **all_products.json** - Complete product list with descriptions
2. **product_discovery_query_plan.json** - Detailed query parameters
3. **product_discovery_plan.py** - Python script to generate queries
4. **PRODUCTS_ANALYSIS_REPORT.md** - Analysis and recommendations

---

## Notes

- All queries use the same time window (last 30 days: 2026-10-06 to 2026-11-05)
- All queries filter for FIX change type and NCM status
- Products are mutually exclusive (one WI belongs to one product)
- Complete your investigation to get full picture of available items

---

**Date:** 2026-11-05  
**Status:** Ready for Investigation  
**Expected Duration:** 15-30 minutes to query all products
