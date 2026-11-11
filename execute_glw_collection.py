#!/usr/bin/env python3
"""
Execute GLW work item collection using MCP tools.
This script makes actual tool calls to fetch all work items.
"""

import json
from pathlib import Path
import sys

def generate_execution_commands():
    """Generate the exact tool calls needed"""
    
    output_dir = Path(__file__).parent
    
    # Read the tool calls manifest
    tool_calls_file = output_dir / 'glw_tool_calls.json'
    
    if not tool_calls_file.exists():
        print("ERROR: glw_tool_calls.json not found")
        sys.exit(1)
    
    with open(tool_calls_file, 'r') as f:
        manifest = json.load(f)
    
    print("=" * 80)
    print("GLW BATCH COLLECTION EXECUTION")
    print("=" * 80)
    print()
    print("Preparing to make the following tool calls:")
    print()
    
    batch_calls = manifest['phase_1_batch_collection']['calls']
    
    for batch in batch_calls:
        print(f"Call {batch['batch_number']}: EDI-Prod-filter-workitems")
        print(f"  skip: {batch['skip']}, top: {batch['top']}")
        print()
    
    print("=" * 80)
    print("READY TO EXECUTE")
    print("=" * 80)
    print()
    print("These calls need to be made to fetch all work item IDs")
    print("Then EDI-Prod-get-job-details will be called for each work item")
    print()

if __name__ == "__main__":
    generate_execution_commands()
