#!/usr/bin/env python3
"""
Fetch and process all 292 work items from EDI-Prod.
This script creates batches of tool calls to efficiently retrieve all job details.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

def load_work_items() -> Tuple[Dict[str, str], int]:
    """Load all work item IDs from the filtered result file."""
    with open("workitems_filtered_final_result.json", "r") as f:
        data = json.load(f)
    
    ent_items = data["ent"]["items"]
    glw_items = data["glw"]["items"]
    
    # Create a mapping of work item ID to product
    items = {}
    for wi_id in ent_items:
        items[wi_id] = "ENT"
    for wi_id in glw_items:
        items[wi_id] = "GLW"
    
    total_expected = data["totals"]["afterFilter"]
    
    print(f"[INFO] Loaded work item IDs:")
    print(f"       ENT: {len(ent_items)} items")
    print(f"       GLW: {len(glw_items)} items")
    print(f"       Total loaded: {len(items)}")
    print(f"       Expected total: {total_expected}")
    
    return items, total_expected


def create_job_detail_stub(wi_id: str, product: str) -> Dict[str, Any]:
    """Create a stub item that represents one work item."""
    item = {
        "workItemId": wi_id,
        "summary": None,  # Will be populated from EDI-Prod-get-job-details
        "status": None,   # Will be populated from EDI-Prod-get-job-details
        "changeType": "FIX",
        "product": product,
        "area": None,     # Will be populated from EDI-Prod-get-job-details
        "module": None,   # Will be populated from EDI-Prod-get-job-details
        "createdTime": None,  # Will be populated from EDI-Prod-get-job-details
        "defectIntroducedWI": None,  # Extracted from job details response
        "defectIntroducedCI": None   # Extracted from job details response (T-number)
    }
    return item


def build_complete_dashboard(work_items: Dict[str, str]) -> Dict:
    """Build the complete dashboard JSON with placeholder data."""
    
    # Get current timestamp
    now = datetime.now(timezone.utc)
    iso_timestamp = now.isoformat()
    
    # Build meta information
    meta = {
        "timestamp": iso_timestamp,
        "totalCount": len(work_items),
        "itemsWithDefectIntroduced": 0,  # Will be calculated after fetching real data
        "itemsWithoutDefectIntroduced": len(work_items),  # Start with all items
        "queryParams": {
            "changeType": "FIX",
            "products": ["ENT", "GLW"],
            "statusFilter": "NOT CLS AND NOT CAN AND NOT empty",
            "createdDateRange": "2026-10-06 to 2026-11-05"
        }
    }
    
    # Build data array - sorted by product then by ID
    data_items = []
    for wi_id, product in sorted(work_items.items(), key=lambda x: (x[1], x[0])):
        item = create_job_detail_stub(wi_id, product)
        data_items.append(item)
    
    # Create the dashboard
    dashboard = {
        "meta": meta,
        "data": data_items
    }
    
    return dashboard


def save_dashboard_json(dashboard: Dict, output_file: str = "dashboard_data.json") -> None:
    """Save the dashboard JSON to file."""
    path = Path(output_file)
    
    # Write with proper formatting
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2)
    
    # Verify the file was created
    if path.exists():
        size_bytes = path.stat().st_size
        size_kb = size_bytes / 1024
        print(f"[OK] Dashboard saved to: {path}")
        print(f"     File size: {size_kb:.1f} KB")
        print(f"     Total items in data array: {len(dashboard['data'])}")
    else:
        raise Exception(f"Failed to save dashboard to {path}")


def print_dashboard_info(dashboard: Dict) -> None:
    """Print information about the dashboard."""
    meta = dashboard["meta"]
    data = dashboard["data"]
    
    print("\n" + "="*70)
    print("DASHBOARD INFORMATION")
    print("="*70)
    print(f"Timestamp: {meta['timestamp']}")
    print(f"Total Count: {meta['totalCount']}")
    print(f"Items With Defect Introduced: {meta['itemsWithDefectIntroduced']}")
    print(f"Items Without Defect Introduced: {meta['itemsWithoutDefectIntroduced']}")
    
    print("\nQuery Parameters:")
    for param_name, param_value in meta['queryParams'].items():
        if isinstance(param_value, list):
            print(f"  {param_name}: {', '.join(param_value)}")
        else:
            print(f"  {param_name}: {param_value}")
    
    # Count breakdown
    ent_items = [item for item in data if item['product'] == 'ENT']
    glw_items = [item for item in data if item['product'] == 'GLW']
    
    print(f"\nProduct Breakdown:")
    print(f"  ENT: {len(ent_items)} items")
    print(f"  GLW: {len(glw_items)} items")
    print(f"  TOTAL: {len(data)} items")
    
    # Show first and last items
    if data:
        print(f"\nFirst item: {data[0]['workItemId']} ({data[0]['product']})")
        print(f"Last item: {data[-1]['workItemId']} ({data[-1]['product']})")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("To populate this dashboard with real data from EDI-Prod:")
    print("  1. For each work item in the 'data' array")
    print("  2. Call EDI-Prod-get-job-details with the workItemId")
    print("  3. Extract the following fields from the response:")
    print("     - summary (or title)")
    print("     - status")
    print("     - area (3-character code)")
    print("     - module (3-character code)")
    print("     - createdTime")
    print("     - defectIntroducedWI (look for 'Defect Introduced in WI')")
    print("     - defectIntroducedCI (look for 'Defect Introduced in Checkin' T-number)")
    print("  4. Update each item in the data array with the fetched values")
    print("  5. Update meta counts:")
    print("     - itemsWithDefectIntroduced")
    print("     - itemsWithoutDefectIntroduced")
    print("="*70)


def main() -> int:
    """Main function."""
    print("\nBuilding Dashboard JSON for Filtered Work Items")
    print("="*70)
    
    try:
        # Step 1: Load work items
        work_items, expected_total = load_work_items()
        
        if len(work_items) == 0:
            print("[ERROR] No work items loaded!")
            return 1
        
        # Step 2: Build dashboard structure
        print(f"\n[INFO] Building dashboard JSON structure...")
        dashboard = build_complete_dashboard(work_items)
        
        # Step 3: Save dashboard
        print(f"[INFO] Saving dashboard JSON...")
        save_dashboard_json(dashboard)
        
        # Step 4: Print information
        print_dashboard_info(dashboard)
        
        print("\n[SUCCESS] Dashboard template created successfully!")
        print(f"          Ready to fetch details for {len(work_items)} work items")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
