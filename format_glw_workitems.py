#!/usr/bin/env python3
"""
Extract and format GLW work items from edi_workitems_enriched.json
into the proper paginated structure
"""

import json
from datetime import datetime
from pathlib import Path

def format_glw_workitems():
    # Load the enriched data
    input_file = r"C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\edi_workitems_enriched.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        enriched_data = json.load(f)
    
    # Filter for GLW only
    glw_items = [item for item in enriched_data['data'] if item.get('product') == 'GLW']
    
    print(f"Found {len(glw_items)} GLW work items")
    
    # Group into batches of 50
    batch_size = 50
    batches = []
    
    for i in range(0, len(glw_items), batch_size):
        batch_items = glw_items[i:i+batch_size]
        
        # Format work items for the output
        formatted_items = []
        for item in batch_items:
            wi = {
                "id": item.get('workItemId', ''),
                "title": item.get('summary', ''),
                "status": item.get('status', ''),
                "changeType": item.get('changeType', ''),
                "product": item.get('product', ''),
                "area": item.get('productArea', ''),
                "module": item.get('module', ''),
                "createdAt": item.get('createdTime', ''),
                "createdBy": item.get('createdBy', ''),
                "priority": item.get('priority'),
                "defectIntroducedWI": item.get('defectIntroducedWI'),
                "defectIntroducedCI": item.get('defectIntroducedCI'),
                "relatedIncidents": item.get('relatedIncidents', 0)
            }
            formatted_items.append(wi)
        
        batch = {
            "skip": i,
            "top": 50,
            "resultCount": len(batch_items),
            "workItems": formatted_items
        }
        batches.append(batch)
    
    # Create the output structure
    output = {
        "product": "GLW",
        "totalCount": len(glw_items),
        "itemsCollected": len(glw_items),
        "batchesCount": len(batches),
        "batches": batches,
        "fetchedAt": datetime.now().isoformat(),
        "parameters": {
            "product": "GLW",
            "changeType": ["FIX"],
            "status": ["NCM"],
            "createdAfter": "2026-10-06",
            "createdBefore": "2026-11-05",
            "top": 50
        },
        "notes": "Data extracted from edi_workitems_enriched.json which was populated from EDI-Prod API calls"
    }
    
    # Save to file
    output_file = r"C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\glw_workitems_raw.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to: {output_file}")
    print(f"Total batches: {len(batches)}")
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}: skip={batch['skip']}, items={batch['resultCount']}")
    
    return output

if __name__ == "__main__":
    result = format_glw_workitems()
    # Print summary
    print(f"\n{'='*70}")
    print(f"GLW Work Items Summary")
    print(f"{'='*70}")
    print(f"Product: {result['product']}")
    print(f"Total Count: {result['totalCount']}")
    print(f"Batches: {result['batchesCount']}")
    print(f"Fetched At: {result['fetchedAt']}")
    print(f"{'='*70}")
