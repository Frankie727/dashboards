#!/usr/bin/env python3
"""
EDI-Prod-get-job-details Data Collection Script
This script would invoke the EDI-Prod-get-job-details tool for multiple work items
and analyze the responses for specific fields.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass

# These would be invoked through the MCP client in a real scenario
WORK_ITEMS = [
    "WI01152234",
    "WI01152163",
    "WI01152157",
    "WI01152123",
    "WI01152119",
    "WI01152084",
    "WI01152037",
    "WI01151930",
    "WI01151929",
    "WI01151864"
]

TARGET_FIELDS = [
    "priority",
    "defectIntroducedWI",
    "defectIntroducedCI",
    "relatedIncidents"
]

@dataclass
class FieldAnalysis:
    field_name: str
    found: bool
    locations: List[str]
    example_values: List[Any]
    data_type: str

def extract_field_from_response(response: Dict, field_path: str) -> Any:
    """
    Extract a field from a response using dot notation path.
    Example: "metadata.priority" -> response["metadata"]["priority"]
    """
    keys = field_path.split(".")
    value = response
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def analyze_responses(all_responses: Dict[str, Dict]) -> Dict[str, FieldAnalysis]:
    """
    Analyze all responses to determine field availability and extraction paths.
    """
    field_analysis = {}
    
    for field in TARGET_FIELDS:
        found_instances = []
        example_values = []
        all_locations = set()
        
        for work_item, response in all_responses.items():
            if response is None:
                continue
                
            # Recursive search for the field in the response
            def search_for_field(obj, current_path=""):
                nonlocal found_instances, all_locations, example_values
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{current_path}.{key}" if current_path else key
                        
                        if key.lower() == field.lower():
                            found_instances.append((work_item, new_path))
                            all_locations.add(new_path)
                            if value is not None and len(example_values) < 3:
                                example_values.append(value)
                        
                        search_for_field(value, new_path)
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        new_path = f"{current_path}[{idx}]"
                        search_for_field(item, new_path)
            
            search_for_field(response)
        
        field_analysis[field] = FieldAnalysis(
            field_name=field,
            found=len(found_instances) > 0,
            locations=list(all_locations),
            example_values=example_values,
            data_type=type(example_values[0]).__name__ if example_values else "unknown"
        )
    
    return field_analysis

def generate_extraction_guide(field_analysis: Dict[str, FieldAnalysis]) -> Dict:
    """
    Generate a guide for extracting fields from the responses.
    """
    guide = {}
    
    for field_name, analysis in field_analysis.items():
        if analysis.found:
            guide[field_name] = {
                "status": "AVAILABLE",
                "extractionPaths": analysis.locations,
                "recommendedPath": analysis.locations[0] if analysis.locations else None,
                "dataType": analysis.data_type,
                "exampleValues": analysis.example_values
            }
        else:
            guide[field_name] = {
                "status": "NOT_FOUND",
                "extractionPaths": [],
                "recommendedPath": None,
                "note": "This field was not found in any of the tested work item responses"
            }
    
    return guide

def main():
    print("EDI-Prod-get-job-details Data Collection and Analysis")
    print("=" * 60)
    print(f"Work Items to retrieve: {len(WORK_ITEMS)}")
    print(f"Target fields to analyze: {len(TARGET_FIELDS)}")
    print()
    
    print("Work Items:")
    for wi in WORK_ITEMS:
        print(f"  - {wi}")
    print()
    
    print("Target Fields:")
    for field in TARGET_FIELDS:
        print(f"  - {field}")
    print()
    
    # In a real scenario, this would invoke the actual MCP tool
    # For now, we're showing the structure
    print("Tool Details:")
    print("-" * 60)
    print("Tool: EDI-Prod-get-job-details")
    print("Provider: EDI Prod MCP server")
    print("Parameter: jobNumber (string)")
    print()
    print("This tool would return:")
    print("  - Basic attributes (title, status, product info, etc.)")
    print("  - Description and notes")
    print("  - Related workitems, incidents, and projects")
    print("  - Related issues (issueId, issueNumber, issueMessage)")
    print("  - Conversation history (for incidents)")
    print("  - Attached documents")
    print()
    
    print("Field Extraction Guide Template:")
    print("-" * 60)
    template_guide = {
        "priority": {
            "status": "PENDING_INVOCATION",
            "possibleLocations": [
                "priority",
                "metadata.priority",
                "workItem.priority",
                "attributes.priority"
            ],
            "note": "Priority field may be at root level or nested in metadata/workItem/attributes"
        },
        "defectIntroducedWI": {
            "status": "PENDING_INVOCATION",
            "possibleLocations": [
                "defectIntroducedWI",
                "defectDetails.introducedWI",
                "defectInfo.introducedWI",
                "relatedWorkitems.defectIntroduced"
            ],
            "note": "May be in defect details section or related workitems"
        },
        "defectIntroducedCI": {
            "status": "PENDING_INVOCATION",
            "possibleLocations": [
                "defectIntroducedCI",
                "defectDetails.introducedCI",
                "defectInfo.introducedCI",
                "buildInfo.introducedCI"
            ],
            "note": "May be in defect details section or build/CI section"
        },
        "relatedIncidents": {
            "status": "PENDING_INVOCATION",
            "possibleLocations": [
                "relatedIncidents",
                "incidents",
                "relatedItems.incidents",
                "metadata.relatedIncidents"
            ],
            "note": "Likely in a dedicated incidents section or related items"
        }
    }
    print(json.dumps(template_guide, indent=2))

if __name__ == "__main__":
    main()
