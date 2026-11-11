#!/usr/bin/env python3
"""
Comprehensive dashboard builder - processes API responses and builds final JSON.
This script aggregates job detail responses and builds the complete dashboard.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

def extract_defect_info(response: Dict) -> tuple:
    """Extract defect introduced info from job details response"""
    defect_wi = None
    defect_ci = None
    
    try:
        # Convert entire response to string for searching
        response_str = json.dumps(response, indent=2)
        
        # Search for defect introduced WI patterns
        wi_patterns = [
            r'Defect Introduced[^:]*WI\s*[:\s]+\s*(WI\d{8})',
            r'Defect Introduced in WI\s*[:\s]*\s*(WI\d{8})',
            r'defectIntroducedWI["\s:]*\s*(WI\d{8})',
            r'Related\s+[Ww]ork[Ii]tem\s*[:\s]+\s*(WI\d{8})',
        ]
        
        for pattern in wi_patterns:
            match = re.search(pattern, response_str, re.IGNORECASE)
            if match:
                defect_wi = match.group(1)
                break
        
        # Search for defect introduced CI (T-number) patterns
        ci_patterns = [
            r'Defect Introduced[^:]*Checkin\s*[:\s]+\s*(T\d{8})',
            r'Defect Introduced in Checkin\s*[:\s]*\s*(T\d{8})',
            r'defectIntroducedCI["\s:]*\s*(T\d{8})',
            r'checkin\s*[:\s]+\s*(T\d{8})',
            r'\b(T\d{8})\b',  # Generic T-number
        ]
        
        for pattern in ci_patterns:
            match = re.search(pattern, response_str, re.IGNORECASE)
            if match:
                defect_ci = match.group(1)
                break
    
    except Exception as e:
        pass
    
    return defect_wi, defect_ci

def process_job_details_response(wi_id: str, product: str, response: Dict) -> Dict:
    """Process a job details response into dashboard entry"""
    
    defect_wi, defect_ci = extract_defect_info(response)
    
    # Extract basic fields with fallbacks
    summary = response.get('summary') or response.get('title') or ""
    status = response.get('status') or response.get('statusCode') or ""
    area = response.get('area') or response.get('areaCode') or ""
    module = response.get('module') or response.get('moduleCode') or ""
    created_time = response.get('createdTime') or response.get('createdAt') or response.get('created') or ""
    
    entry = {
        "workItemId": wi_id,
        "summary": summary if summary else None,
        "status": status if status else None,
        "changeType": "FIX",
        "product": product,
        "area": area if area else None,
        "module": module if module else None,
        "createdTime": created_time[:10] if created_time and len(created_time) >= 10 else created_time,
        "defectIntroducedWI": defect_wi,
        "defectIntroducedCI": defect_ci
    }
    
    return entry

def build_final_dashboard(job_responses: Dict) -> Dict:
    """Build final dashboard from all job responses"""
    
    # Load batches for reference
    with open("work_items_batches.json") as f:
        batches = json.load(f)
    
    # Create all work item list
    all_work_items = []
    for batch in batches:
        all_work_items.extend(batch)
    
    # Initialize dashboard
    dashboard = {
        "meta": {
            "timestamp": datetime.now().isoformat(timespec="milliseconds") + "+11:00",
            "totalCount": len(all_work_items),
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
    
    # Process each work item
    with_defect_samples = []
    
    for item in all_work_items:
        wi_id = item["id"]
        product = item["product"]
        
        if wi_id in job_responses:
            response = job_responses[wi_id]
            entry = process_job_details_response(wi_id, product, response)
        else:
            # Handle missing response with default
            entry = {
                "workItemId": wi_id,
                "summary": None,
                "status": None,
                "changeType": "FIX",
                "product": product,
                "area": None,
                "module": None,
                "createdTime": None,
                "defectIntroducedWI": None,
                "defectIntroducedCI": None
            }
        
        # Count defect introduced items
        if entry["defectIntroducedWI"] or entry["defectIntroducedCI"]:
            dashboard["meta"]["itemsWithDefectIntroduced"] += 1
            if entry["defectIntroducedCI"] and len(with_defect_samples) < 5:
                with_defect_samples.append(entry["defectIntroducedCI"])
        else:
            dashboard["meta"]["itemsWithoutDefectIntroduced"] += 1
        
        dashboard["data"].append(entry)
    
    return dashboard, with_defect_samples

if __name__ == "__main__":
    print("Dashboard builder ready")
    print("This script will process job detail responses and build the final dashboard")
    print("\nKey functions:")
    print("- extract_defect_info(): Parses responses for defect references")
    print("- process_job_details_response(): Converts API response to dashboard entry")
    print("- build_final_dashboard(): Aggregates all responses into final JSON")
    
    # Load batch config
    with open("work_items_batches.json") as f:
        batches = json.load(f)
    
    total = sum(len(b) for b in batches)
    print(f"\nReady to process {total} work items across {len(batches)} batches")
