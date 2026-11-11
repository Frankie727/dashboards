#!/usr/bin/env python3
"""
Fetch detailed job information for all 300 filtered work items and build dashboard JSON.
Processes in parallel batches to handle large volume efficiently.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import re

# For calling the EDI-Prod MCP tools, we'll need to use them via the API
# Since we're in a Python environment without direct MCP access, we'll use the tool interface

def extract_defect_details(text):
    """Extract defect-related information from text"""
    if not text:
        return None, None
    
    # Look for "Defect Introduced in WI" patterns
    wi_match = re.search(r'Defect\s+Introduced\s+in\s+WI\s*[:=]?\s*(WI\d+)', text, re.IGNORECASE)
    if wi_match:
        defect_wi = wi_match.group(1)
    else:
        # Look for related workitem references
        wi_match = re.search(r'Related\s+(?:Work)?[Ii]tem\s*[:=]?\s*(WI\d+)', text, re.IGNORECASE)
        defect_wi = wi_match.group(1) if wi_match else None
    
    # Look for T-number patterns (checkin references)
    ci_match = re.search(r'(T\d{8})', text)
    defect_ci = ci_match.group(1) if ci_match else None
    
    return defect_wi, defect_ci

def main():
    """Main processing function"""
    
    # Load work item IDs
    ids_file = Path("workitems_filtered_final_result.json")
    with open(ids_file) as f:
        data = json.load(f)
    
    all_ids = data['ent']['items'] + data['glw']['items']
    
    print(f"Total work items to process: {len(all_ids)}")
    print(f"ENT: {len(data['ent']['items'])}")
    print(f"GLW: {len(data['glw']['items'])}")
    
    # Create a mapping of ID to product
    id_to_product = {}
    for wi in data['ent']['items']:
        id_to_product[wi] = 'ENT'
    for wi in data['glw']['items']:
        id_to_product[wi] = 'GLW'
    
    # Store results and metadata
    dashboard = {
        "meta": {
            "timestamp": datetime.now().isoformat() + "+11:00",
            "totalCount": len(all_ids),
            "itemsWithDefectIntroduced": 0,
            "itemsWithoutDefectIntroduced": 0,
            "queryParams": {
                "changeType": "FIX",
                "products": ["ENT", "GLW"],
                "statusFilter": "NOT CLS AND NOT CAN AND NOT empty",
                "createdDateRange": "2026-10-06 to 2026-11-05"
            }
        },
        "data": []
    }
    
    # Write the work IDs to a file for batch processing with MCP
    batch_file = Path("work_items_batch_for_mcp.json")
    with open(batch_file, 'w') as f:
        json.dump({
            "workItems": all_ids,
            "idToProduct": id_to_product
        }, f, indent=2)
    
    print(f"\nWork item batch file created: {batch_file}")
    print(f"Now you need to use the MCP tool to fetch details for each work item.")
    print(f"This script requires interactive MCP tool calls to EDI-Prod-get-job-details")
    
    return all_ids, id_to_product, dashboard

if __name__ == "__main__":
    main()
