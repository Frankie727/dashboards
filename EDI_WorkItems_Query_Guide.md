# EDI Prod Work Items Query Guide

## Objective
Query ENT and GLW product work items for FIX changes created in the last 30 days (2026-10-06 to 2026-11-05), excluding Closed and Cancelled items.

## Query Specifications

### Query 1: ENT Product

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

### Query 2: GLW Product

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

## Pagination Strategy

1. Start with `skip: 0, top: 50`
2. If result count == 50, continue with:
   - `skip: 50, top: 50`
   - `skip: 100, top: 50`
   - Continue until count < 50
3. Aggregate all pages

## Data Extraction

For each work item returned, extract:

| Field | Description | Example |
|-------|-------------|---------|
| workItemId | Work item number | WI00123456 |
| summary | Work item title/summary | "Fix database connection issue" |
| status | Status code | OPN, ASN, WRK, etc. |
| changeType | Type of change | FIX, PRD, etc. |
| productArea | Product area code | RAT, DEL, FIN, etc. |
| product | Product code | ENT or GLW |
| createdTime | Creation timestamp | 2026-10-15T10:30:00Z |
| module | Module code | ATR, PPI, etc. |
| priority | Priority level | P1, P2, P3, etc. |
| defectIntroducedWI | Work item that introduced defect | WI00123450 (if available) |
| defectIntroducedCI | Commit/Integration that introduced defect | CI#12345 (if available) |
| relatedIncidents | Count of related incidents | 0, 1, 2, etc. |

## Status Filter Criteria

**EXCLUDE items with:**
- status = "CLS" (Closed)
- status = "CAN" (Cancelled)
- status = null or empty

**INCLUDE items with:**
- status = "OPN" (Open)
- status = "ASN" (Assigned)
- status = "WRK" (Working)
- status = "SUS" (Suspended)
- Any other valid status EXCEPT CLS, CAN, or empty

## Expected Output Format

```json
{
  "meta": {
    "timestamp": "2026-11-05T13:06:28Z",
    "queryParams": {
      "products": ["ENT", "GLW"],
      "changeType": "FIX",
      "statusFilter": "NCM (NOT CLS, NOT CAN, NOT empty)",
      "createdLastDays": 30,
      "dateRange": {
        "from": "2026-10-06",
        "to": "2026-11-05"
      }
    },
    "totalCount": 0,
    "pageCount": 0,
    "itemsWithDefectIntroduced": 0,
    "itemsWithoutDefectIntroduced": 0,
    "byProduct": {
      "ENT": {
        "count": 0,
        "withDefect": 0,
        "withoutDefect": 0
      },
      "GLW": {
        "count": 0,
        "withDefect": 0,
        "withoutDefect": 0
      }
    }
  },
  "data": [
    {
      "workItemId": "WI00123456",
      "summary": "Fix critical issue in payment processing",
      "status": "OPN",
      "changeType": "FIX",
      "productArea": "FIN",
      "product": "ENT",
      "createdTime": "2026-10-15T10:30:00Z",
      "module": "PPI",
      "priority": "P1",
      "defectIntroducedWI": "WI00123450",
      "defectIntroducedCI": null,
      "relatedIncidents": 2
    }
  ],
  "statistics": {
    "defectTraceability": {
      "withDefectIntroducedWI": 0,
      "withDefectIntroducedCI": 0,
      "withBoth": 0,
      "withNeither": 0
    },
    "byStatus": {},
    "byModule": {},
    "byPriority": {}
  }
}
```

## How to Execute in VS Code

1. Open VS Code with Copilot Chat enabled
2. Use the following prompt:

```
Query the EDI Prod MCP Server with:

**Query 1 - ENT Product:**
Use EDI-Prod-filter-workitems with:
- product: "ENT"
- changeType: ["FIX"]
- createdAfter: "2026-10-06"
- createdBefore: "2026-11-05"
- top: 50
- skip: 0 (then 50, 100, etc. for pagination)

**Query 2 - GLW Product:**
Use EDI-Prod-filter-workitems with:
- product: "GLW"
- changeType: ["FIX"]
- createdAfter: "2026-10-06"
- createdBefore: "2026-11-05"
- top: 50
- skip: 0 (then 50, 100, etc. for pagination)

For both queries:
1. Exclude items with status "CLS", "CAN", or empty
2. Extract all required fields for each work item
3. Continue pagination until result count < 50
4. Return JSON with meta information and all work items
```

## How to Execute via Python (if MCP server is local)

```python
import json
import requests

# Configure EDI Prod server endpoint
EDI_PROD_URL = "http://localhost:8000/api/workitems"  # Adjust to your server

def query_workitems(product, skip=0):
    payload = {
        "product": product,
        "changeType": ["FIX"],
        "createdAfter": "2026-10-06",
        "createdBefore": "2026-11-05",
        "top": 50,
        "skip": skip
    }
    response = requests.post(EDI_PROD_URL, json=payload)
    return response.json()

# Query both products
all_items = []
for product in ["ENT", "GLW"]:
    skip = 0
    while True:
        result = query_workitems(product, skip)
        items = result.get("data", [])
        
        # Filter out closed/cancelled items
        valid_items = [
            item for item in items 
            if item.get("status") not in ["CLS", "CAN", None]
        ]
        all_items.extend(valid_items)
        
        if len(items) < 50:
            break
        skip += 50

# Save results
with open("edi_workitems.json", "w") as f:
    json.dump({"data": all_items}, f, indent=2)
```

## Tool Reference

**Tool Name:** EDI-Prod-filter-workitems

**Tool Type:** MCP (Model Context Protocol) Server

**Parameters:**
- `product` (required): "ENT" or "GLW"
- `changeType` (array): ["FIX"]
- `createdAfter` (ISO date): "2026-10-06"
- `createdBefore` (ISO date): "2026-11-05"
- `top` (integer, max 50): 50
- `skip` (integer): 0, 50, 100, etc.

**Returns:** CSV format with workitem details plus total count

---

**Created:** 2026-11-05
**Last Updated:** 2026-11-05T13:07:05Z
