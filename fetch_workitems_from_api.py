#!/usr/bin/env python3
"""
Fetch work items from EDI-Prod API and filter by status.
This script attempts to call EDI-Prod-filter-workitems tool via multiple methods.
"""

import json
import sys
import os
from typing import List, Dict, Any, Tuple
import subprocess
from datetime import datetime

def fetch_workitems_batch(product: str, skip: int, top: int = 50) -> Tuple[int, int, List[str]]:
    """
    Fetch a batch of work items using EDI-Prod-filter-workitems tool
    Returns: (before_count, after_count, filtered_ids)
    """
    params = {
        "product": product,
        "changeType": ["FIX"],
        "createdAfter": "2026-10-06",
        "createdBefore": "2026-11-05",
        "skip": skip,
        "top": top
    }
    
    print(f"Fetching {product} items (skip={skip}, top={top})...", file=sys.stderr)
    
    # Method 1: Try using invoke-mcp command (if such exists)
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            f"""
$VerbosePreference = 'SilentlyContinue'
# This would call the EDI-Prod-filter-workitems tool
# For now, returning empty to indicate the method needs implementation
Write-Output ""
"""
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            # Parse CSV response
            csv_data = result.stdout.strip()
            before_count, after_count, ids = parse_and_filter_csv(csv_data)
            return before_count, after_count, ids
    except Exception as e:
        print(f"  Method 1 failed: {e}", file=sys.stderr)
    
    # Method 2: Try direct HTTP call if API is exposed
    try:
        import requests
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            "http://localhost:8000/api/EDI-Prod-filter-workitems",
            json=params,
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result.get('data'), str):
                # CSV response
                before_count, after_count, ids = parse_and_filter_csv(result['data'])
                return before_count, after_count, ids
    except ImportError:
        pass
    except Exception as e:
        print(f"  Method 2 failed: {e}", file=sys.stderr)
    
    # If we get here, we couldn't fetch data
    print(f"  Warning: Unable to fetch data for {product} skip={skip}", file=sys.stderr)
    return 0, 0, []

def parse_and_filter_csv(csv_data: str) -> Tuple[int, int, List[str]]:
    """
    Parse CSV data and filter by status
    Excludes: CLS, CAN, empty string
    Returns: (before_count, after_count, filtered_ids)
    """
    import csv
    from io import StringIO
    
    lines = csv_data.strip().split('\n')
    if not lines or len(lines) < 2:
        return 0, 0, []
    
    try:
        reader = csv.DictReader(StringIO(csv_data))
        rows = list(reader)
        
        before_count = len(rows)
        filtered_ids = []
        
        for row in rows:
            status = row.get('status', '').strip()
            
            # Exclude CLS, CAN, or empty
            if status not in ['CLS', 'CAN', '']:
                # Get work item ID (try common column names)
                wi_id = (row.get('number') or row.get('Number') or 
                        row.get('id') or row.get('ID') or 
                        row.get('workitem') or row.get('Workitem'))
                if wi_id:
                    filtered_ids.append(wi_id.strip())
        
        return before_count, len(filtered_ids), filtered_ids
    except Exception as e:
        print(f"  Error parsing CSV: {e}", file=sys.stderr)
        return 0, 0, []

def main():
    """Main execution"""
    print("EDI-Prod Work Items Fetcher", file=sys.stderr)
    print("Fetching work items with exact parameters...", file=sys.stderr)
    print("")
    
    result = {
        "ent": {
            "beforeFilter": 0,
            "afterFilter": 0,
            "items": []
        },
        "glw": {
            "beforeFilter": 0,
            "afterFilter": 0,
            "items": []
        },
        "totals": {
            "beforeFilter": 0,
            "afterFilter": 0
        }
    }
    
    ent_all_ids = []
    glw_all_ids = []
    ent_total_before = 0
    ent_total_after = 0
    glw_total_before = 0
    glw_total_after = 0
    
    # Fetch ENT items
    skip_values = [0, 50, 100, 150, 200, 250, 300, 350, 400]
    for skip in skip_values:
        before, after, ids = fetch_workitems_batch("ENT", skip)
        ent_total_before += before
        ent_total_after += after
        ent_all_ids.extend(ids)
        
        if before == 0 and after == 0:
            print(f"  No more ENT results at skip={skip}, stopping", file=sys.stderr)
            break
    
    # Fetch GLW items
    for skip in skip_values:
        before, after, ids = fetch_workitems_batch("GLW", skip)
        glw_total_before += before
        glw_total_after += after
        glw_all_ids.extend(ids)
        
        if before == 0 and after == 0:
            print(f"  No more GLW results at skip={skip}, stopping", file=sys.stderr)
            break
    
    # Remove duplicates while preserving order
    ent_unique = []
    seen = set()
    for id in ent_all_ids:
        if id not in seen:
            ent_unique.append(id)
            seen.add(id)
    
    glw_unique = []
    seen = set()
    for id in glw_all_ids:
        if id not in seen:
            glw_unique.append(id)
            seen.add(id)
    
    # Fill result
    result["ent"]["beforeFilter"] = ent_total_before
    result["ent"]["afterFilter"] = ent_total_after
    result["ent"]["items"] = ent_unique
    
    result["glw"]["beforeFilter"] = glw_total_before
    result["glw"]["afterFilter"] = glw_total_after
    result["glw"]["items"] = glw_unique
    
    result["totals"]["beforeFilter"] = ent_total_before + glw_total_before
    result["totals"]["afterFilter"] = ent_total_after + glw_total_after
    
    # Output result
    print(json.dumps(result, indent=2))
    
    # Save to file
    output_file = "workitems_fetch_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"INFO: Results saved to {output_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
