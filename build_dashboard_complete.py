#!/usr/bin/env python3
"""
Build complete dashboard JSON with job details for all 300 work items.
This script will be run step-by-step by calling EDI-Prod-get-job-details for each work item.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def extract_defect_introduced_wi(text: str) -> Optional[str]:
    """Extract defect introduced work item reference from text"""
    if not text:
        return None
    
    # Multiple patterns to check
    patterns = [
        r'Defect\s+Introduced\s+in\s+WI\s*[:=]?\s*(WI\d{8})',
        r'Defect Introduced WI[:\s]*\s*(WI\d{8})',
        r'defectIntroducedWI[:\s]*\s*(WI\d{8})',
        r'Related\s+[Ww]ork[Ii]tem[s]?\s*[:=]?\s*(WI\d{8})',
        r'related\s+wi\s*[:=]?\s*(WI\d{8})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_defect_introduced_ci(text: str) -> Optional[str]:
    """Extract defect introduced checkin reference from text"""
    if not text:
        return None
    
    patterns = [
        r'Defect\s+Introduced\s+in\s+Checkin\s*[:=]?\s*(T\d{8})',
        r'Defect Introduced Checkin[:\s]*\s*(T\d{8})',
        r'defectIntroducedCI[:\s]*\s*(T\d{8})',
        r'checkin\s*[:=]?\s*(T\d{8})',
        r'\b(T\d{8})\b',  # Generic T-number
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)
    
    return None

def extract_from_response(response: Dict) -> Dict:
    """Extract relevant fields from EDI-Prod job details response"""
    extracted = {
        'summary': None,
        'status': None,
        'area': None,
        'module': None,
        'createdTime': None,
        'defectIntroducedWI': None,
        'defectIntroducedCI': None,
    }
    
    try:
        # Extract basic fields
        if 'summary' in response:
            extracted['summary'] = response['summary']
        elif 'title' in response:
            extracted['summary'] = response['title']
        
        if 'status' in response:
            extracted['status'] = response['status']
        elif 'statusCode' in response:
            extracted['status'] = response['statusCode']
        
        if 'area' in response:
            extracted['area'] = response['area']
        elif 'areaCode' in response:
            extracted['area'] = response['areaCode']
        
        if 'module' in response:
            extracted['module'] = response['module']
        elif 'moduleCode' in response:
            extracted['module'] = response['moduleCode']
        
        # Extract date
        if 'createdTime' in response:
            extracted['createdTime'] = response['createdTime']
        elif 'createdAt' in response:
            extracted['createdTime'] = response['createdAt']
        elif 'created' in response:
            extracted['createdTime'] = response['created']
        
        # Extract defect information from all text fields
        all_text = []
        
        if 'description' in response:
            all_text.append(str(response['description']))
        if 'notes' in response:
            all_text.append(str(response['notes']))
        if 'defectDetails' in response:
            if isinstance(response['defectDetails'], dict):
                all_text.append(json.dumps(response['defectDetails']))
            else:
                all_text.append(str(response['defectDetails']))
        
        # Check custom fields
        if 'customFields' in response and isinstance(response['customFields'], dict):
            for key, value in response['customFields'].items():
                if value:
                    all_text.append(f"{key}: {value}")
        
        # Check related items
        if 'relatedItems' in response:
            if isinstance(response['relatedItems'], list):
                all_text.append(json.dumps(response['relatedItems']))
            elif isinstance(response['relatedItems'], dict):
                all_text.append(json.dumps(response['relatedItems']))
            else:
                all_text.append(str(response['relatedItems']))
        
        combined_text = '\n'.join(all_text)
        
        # Extract defect introduced WI
        defect_wi = extract_defect_introduced_wi(combined_text)
        if defect_wi:
            extracted['defectIntroducedWI'] = defect_wi
        
        # Extract defect introduced CI
        defect_ci = extract_defect_introduced_ci(combined_text)
        if defect_ci:
            extracted['defectIntroducedCI'] = defect_ci
    
    except Exception as e:
        print(f"Error extracting from response: {e}")
    
    return extracted

def create_dashboard_structure() -> Dict:
    """Create empty dashboard structure"""
    return {
        "meta": {
            "timestamp": datetime.now().isoformat(timespec='milliseconds') + '+11:00',
            "totalCount": 300,
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

def build_work_item_entry(wi_id: str, product: str, response: Dict) -> Dict:
    """Build a single work item entry for the dashboard"""
    extracted = extract_from_response(response)
    
    entry = {
        "workItemId": wi_id,
        "summary": extracted['summary'],
        "status": extracted['status'],
        "changeType": "FIX",
        "product": product,
        "area": extracted['area'],
        "module": extracted['module'],
        "createdTime": extracted['createdTime'],
        "defectIntroducedWI": extracted['defectIntroducedWI'],
        "defectIntroducedCI": extracted['defectIntroducedCI']
    }
    
    return entry

if __name__ == "__main__":
    # Create template dashboard
    dashboard = create_dashboard_structure()
    
    # Load work items
    mapping_file = Path('work_items_mapping.json')
    if mapping_file.exists():
        with open(mapping_file) as f:
            work_items = json.load(f)
        print(f"Loaded {len(work_items)} work items")
        print("Sample:", work_items[0:3])
    else:
        print("Error: work_items_mapping.json not found")
    
    print("\nDashboard template created and ready for population")
    print(f"Total items to process: {dashboard['meta']['totalCount']}")
    
    # Save template
    with open('dashboard_template.json', 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print("Template saved to dashboard_template.json")
