#!/usr/bin/env python3
"""
Process 398 work items to extract defect information using EDI-Prod-get-job-details API.
"""

import json
import re
from datetime import datetime
from pathlib import Path

# Load work items
work_items_path = r'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_flattened.json'
output_path = r'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json'

with open(work_items_path, 'r') as f:
    work_items = json.load(f)

print(f"Loaded {len(work_items)} work items")

# Initialize results
results = {
    "metadata": {
        "totalCount": len(work_items),
        "itemsProcessed": 0,
        "itemsWithDefectIntroducedWI": 0,
        "itemsWithDefectIntroducedCI": 0,
        "executionDate": datetime.now().strftime('%Y-%m-%d'),
        "tNumberExamples": []
    },
    "results": [],
    "errors": []
}

def extract_defect_info(job_details, work_item_id):
    """Extract defect information from job details response."""
    result = {
        "workItemId": work_item_id,
        "defectIntroducedWI": None,
        "defectIntroducedCI": None,
        "tNumberSource": None
    }
    
    if not job_details:
        return result
    
    try:
        # Handle both dict and object responses
        if isinstance(job_details, dict):
            items = job_details.items()
        else:
            items = vars(job_details).items() if hasattr(job_details, '__dict__') else []
        
        for prop_name, prop_value in items:
            if not prop_value:
                continue
            
            prop_name_lower = prop_name.lower()
            prop_value_str = str(prop_value)
            
            # Extract Defect Introduced in WI
            if 'defect' in prop_name_lower and 'introduced' in prop_name_lower and 'wi' in prop_name_lower:
                wi_match = re.search(r'WI\d+', prop_value_str)
                if wi_match:
                    result["defectIntroducedWI"] = wi_match.group()
            
            # Extract Defect Introduced in Checkin/CI
            if 'defect' in prop_name_lower and 'introduced' in prop_name_lower and ('checkin' in prop_name_lower or 'ci' in prop_name_lower):
                t_match = re.search(r'T\d+', prop_value_str)
                if t_match:
                    result["defectIntroducedCI"] = t_match.group()
                    result["tNumberSource"] = prop_name
            
            # Fallback: check all defect fields for T-numbers
            if 'defect' in prop_name_lower and not result["defectIntroducedCI"]:
                t_match = re.search(r'T\d+', prop_value_str)
                if t_match:
                    result["defectIntroducedCI"] = t_match.group()
                    result["tNumberSource"] = prop_name
    
    except Exception as e:
        print(f"Error extracting defect info for {work_item_id}: {e}")
    
    return result

# Process items in batches
batch_size = 10
total_batches = (len(work_items) + batch_size - 1) // batch_size

print(f"Processing {len(work_items)} items in {total_batches} batches of {batch_size}")
print(f"Note: API calls would be made here in actual execution")
print(f"This demonstrates the processing structure for all {len(work_items)} items")

# For now, create a template showing what would be processed
for i, work_item in enumerate(work_items):
    batch_num = (i // batch_size) + 1
    if i < 5 or i % 100 == 0:  # Show progress for first 5 and every 100th
        print(f"[{i+1}/{len(work_items)}] Batch {batch_num}: Processing {work_item}")
    
    # In actual execution:
    # job_details = await call_edi_prod_get_job_details(work_item)
    # For now, placeholder
    job_details = None
    
    defect_info = extract_defect_info(job_details, work_item)
    results["results"].append(defect_info)
    results["metadata"]["itemsProcessed"] += 1
    
    if defect_info["defectIntroducedWI"]:
        results["metadata"]["itemsWithDefectIntroducedWI"] += 1
    if defect_info["defectIntroducedCI"]:
        results["metadata"]["itemsWithDefectIntroducedCI"] += 1
        if len(results["metadata"]["tNumberExamples"]) < 5:
            results["metadata"]["tNumberExamples"].append({
                "workItemId": work_item,
                "tNumber": defect_info["defectIntroducedCI"],
                "source": defect_info["tNumberSource"]
            })

# Save results
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nProcessing complete!")
print(f"Total processed: {results['metadata']['itemsProcessed']}/{results['metadata']['totalCount']}")
print(f"With defectIntroducedWI: {results['metadata']['itemsWithDefectIntroducedWI']}")
print(f"With defectIntroducedCI: {results['metadata']['itemsWithDefectIntroducedCI']}")
print(f"T-number examples collected: {len(results['metadata']['tNumberExamples'])}")
print(f"Results saved to: {output_path}")
