#!/usr/bin/env python3
"""
Efficient batch processor for 292 work items.
Builds complete dashboard JSON with proper structure.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def load_work_items() -> Dict[str, str]:
    """Load all 292 work item IDs from the filtered result file."""
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
    
    print(f"[OK] Loaded {len(items)} work item IDs")
    print(f"  - ENT: {len(ent_items)} items")
    print(f"  - GLW: {len(glw_items)} items")
    
    return items


def extract_area_module_from_id(wi_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract area and module codes from work item ID.
    Format: WI01XXXXXX where XXXX might contain encoded area/module info.
    This is a simplified extraction - real data comes from EDI-Prod.
    """
    return None, None


def build_dashboard_json(work_items: Dict[str, str]) -> Dict:
    """
    Build the complete dashboard JSON structure.
    This creates the container that will be populated with EDI-Prod data.
    """
    
    # Build meta data with current timestamp
    now = datetime.now(timezone.utc)
    iso_timestamp = now.isoformat()
    
    meta = {
        "timestamp": iso_timestamp,
        "totalCount": len(work_items),
        "itemsWithDefectIntroduced": 0,  # Will be updated after fetching
        "itemsWithoutDefectIntroduced": len(work_items),  # All items start here
        "queryParams": {
            "changeType": "FIX",
            "products": ["ENT", "GLW"],
            "statusFilter": "NOT CLS AND NOT CAN AND NOT empty",
            "createdDateRange": "2026-10-06 to 2026-11-05"
        }
    }
    
    # Build data array with placeholder items
    # Each item will be populated with real data from EDI-Prod calls
    data_items = []
    
    for wi_id, product in sorted(work_items.items(), key=lambda x: (x[1], x[0])):
        item = {
            "workItemId": wi_id,
            "summary": None,  # Populated from EDI-Prod response
            "status": None,   # Populated from EDI-Prod response (WRK, ASN, OPN, SUS, etc.)
            "changeType": "FIX",
            "product": product,
            "area": None,     # Populated from EDI-Prod response (3-char code)
            "module": None,   # Populated from EDI-Prod response (3-char code)
            "createdTime": None,  # Populated from EDI-Prod response
            "defectIntroducedWI": None,  # Extracted from "Defect Introduced in WI" field
            "defectIntroducedCI": None   # Extracted from "Defect Introduced in Checkin" (T-number)
        }
        data_items.append(item)
    
    dashboard = {
        "meta": meta,
        "data": data_items
    }
    
    return dashboard


def save_dashboard(dashboard: Dict, output_path: str = "dashboard_data.json") -> Path:
    """Save the dashboard JSON to file."""
    path = Path(output_path)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    
    size_kb = path.stat().st_size / 1024
    print(f"[OK] Dashboard JSON saved to {path}")
    print(f"  - Size: {size_kb:.1f} KB")
    print(f"  - Total items: {len(dashboard['data'])}")
    
    return path


def print_summary(dashboard: Dict):
    """Print a summary of the dashboard."""
    meta = dashboard["meta"]
    data = dashboard["data"]
    
    print("\n" + "="*60)
    print("DASHBOARD STRUCTURE SUMMARY")
    print("="*60)
    print(f"Timestamp: {meta['timestamp']}")
    print(f"Total work items: {meta['totalCount']}")
    print(f"Items WITH defect introduced: {meta['itemsWithDefectIntroduced']}")
    print(f"Items WITHOUT defect introduced: {meta['itemsWithoutDefectIntroduced']}")
    print(f"\nQuery Parameters:")
    for key, value in meta['queryParams'].items():
        print(f"  - {key}: {value}")
    print(f"\nData items in dashboard: {len(data)}")
    
    # Count by product
    ent_count = sum(1 for item in data if item['product'] == 'ENT')
    glw_count = sum(1 for item in data if item['product'] == 'GLW')
    print(f"\nBreakdown by product:")
    print(f"  - ENT: {ent_count} items")
    print(f"  - GLW: {glw_count} items")
    
    print("\n" + "="*60)
    print("NOTE: This dashboard structure has been created.")
    print("To populate with actual data from EDI-Prod:")
    print("  1. For each work item ID in the data array")
    print("  2. Call EDI-Prod-get-job-details with the jobNumber")
    print("  3. Extract: summary, status, area, module, createdTime")
    print("  4. Extract defect fields: defectIntroducedWI, defectIntroducedCI")
    print("  5. Update the corresponding item in the data array")
    print("="*60)


def main():
    """Main function."""
    print("\nBuilding Dashboard JSON for 292 Work Items")
    print("=" * 60)
    
    try:
        # Load work items
        work_items = load_work_items()
        
        # Build dashboard structure
        print("\n[OK] Building dashboard JSON structure...")
        dashboard = build_dashboard_json(work_items)
        
        # Save dashboard
        print("\n[OK] Saving dashboard...")
        save_dashboard(dashboard)
        
        # Print summary
        print_summary(dashboard)
        
        print("\nDashboard template created successfully!")
        print("Next steps:")
        print("  1. Use EDI-Prod-get-job-details tool to fetch each work item's details")
        print("  2. Populate the 'data' array with actual information")
        print("  3. Update meta counts for items with/without defect introduced")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
