#!/usr/bin/env python3
"""
Fetch complete details for ALL GLW work items using EDI-Prod MCP tools.

Process:
1. Call EDI-Prod-filter-workitems with pagination (skip=0, 50, 100, ...)
2. Collect ALL work item IDs
3. Call EDI-Prod-get-job-details for each work item ID
4. Save complete JSON file
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Configuration
OUTPUT_FILE = Path(__file__).parent / "glw_complete_details_all.json"

def create_filter_params(skip: int, top: int = 50) -> Dict[str, Any]:
    """Create parameters for EDI-Prod-filter-workitems"""
    return {
        "product": "GLW",
        "changeType": ["FIX"],
        "status": ["NCM"],
        "createdAfter": "2026-10-06",
        "createdBefore": "2026-11-05",
        "skip": skip,
        "top": top
    }

def create_job_details_params(workitem_id: str) -> Dict[str, Any]:
    """Create parameters for EDI-Prod-get-job-details"""
    return {
        "jobNumber": workitem_id
    }

def main():
    print("=" * 70)
    print("GLW Work Item Complete Details Fetcher")
    print("=" * 70)
    print()
    
    print("STEP 1: Fetch ALL work item IDs via pagination")
    print("-" * 70)
    print("Using EDI-Prod-filter-workitems with:")
    print("  product: GLW")
    print("  changeType: FIX")
    print("  status: NCM")
    print("  createdAfter: 2026-10-06")
    print("  createdBefore: 2026-11-05")
    print("  pagination: skip=0, 50, 100, 150, ... until < 50 results")
    print()
    
    print("STEP 2: Fetch complete details for EVERY work item")
    print("-" * 70)
    print("For each work item ID, call EDI-Prod-get-job-details")
    print()
    
    print("STEP 3: Build and save JSON with all items")
    print("-" * 70)
    print(f"Output file: {OUTPUT_FILE}")
    print()
    
    print("=" * 70)
    print("Tool Invocation Template:")
    print("=" * 70)
    print()
    print("Batch 0 (skip=0):")
    print(json.dumps(create_filter_params(0), indent=2))
    print()
    print("Batch 1 (skip=50):")
    print(json.dumps(create_filter_params(50), indent=2))
    print()
    print("Batch 2 (skip=100):")
    print(json.dumps(create_filter_params(100), indent=2))
    print()
    print("Batch 3 (skip=150):")
    print(json.dumps(create_filter_params(150), indent=2))
    print()
    print("Example job details fetch (for WI01152234):")
    print(json.dumps(create_job_details_params("WI01152234"), indent=2))
    print()
    
    print("=" * 70)
    print("NEXT: Use these parameters with the MCP tools")
    print("=" * 70)

if __name__ == "__main__":
    main()
