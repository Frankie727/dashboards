#!/usr/bin/env python3
"""
Fetch job details for all work items using EDI-Prod-get-job-details.

This script will systematically fetch details for all work items and update
the dashboard_data.json file with the actual information.

Since we can't directly call MCP tools from Python, this script generates
the tool calls and documents them. The actual execution will be done through
Copilot's tool interface.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def load_work_items_from_filtered() -> Dict[str, str]:
    """Load work items from the filtered results file."""
    with open("workitems_filtered_final_result.json", "r") as f:
        data = json.load(f)
    
    items = {}
    for wi_id in data["ent"]["items"]:
        items[wi_id] = "ENT"
    for wi_id in data["glw"]["items"]:
        items[wi_id] = "GLW"
    
    return items


def load_dashboard() -> Dict[str, Any]:
    """Load the current dashboard JSON."""
    with open("dashboard_data.json", "r") as f:
        return json.load(f)


def generate_batch_tool_calls(work_items: Dict[str, str], batch_size: int = 5) -> List[List[str]]:
    """
    Generate batches of work item IDs for tool calls.
    Each batch will be passed to EDI-Prod-get-job-details.
    """
    wi_list = list(work_items.keys())
    batches = []
    
    for i in range(0, len(wi_list), batch_size):
        batch = wi_list[i:i + batch_size]
        batches.append(batch)
    
    return batches


def create_tool_call_script(batches: List[List[str]]) -> str:
    """
    Create a script that documents all the tool calls needed.
    """
    script = """#!/usr/bin/env python3
# Auto-generated tool call documentation
# This file documents all the EDI-Prod-get-job-details calls needed

TOOL_CALLS_REQUIRED = [
"""
    
    for batch_idx, batch in enumerate(batches, 1):
        script += f"    # Batch {batch_idx}\n"
        for wi_id in batch:
            script += f'    {{ "tool": "EDI-Prod-get-job-details", "jobNumber": "{wi_id}" }},\n'
    
    script += """]\n\nTOTAL_CALLS = len(TOOL_CALLS_REQUIRED)
BATCHES = """ + str(len(batches)) + """
ITEMS_PER_BATCH = 5
"""
    
    return script


def create_powershell_batch_template() -> str:
    """Create a PowerShell template for processing batches."""
    return """# PowerShell template for fetching work item details
# This demonstrates how to process batches of work items

# Example: Process first batch of work items
$workItems = @(
    "WI01152234",
    "WI01152163",
    "WI01152157",
    "WI01152123",
    "WI01152119"
)

# For each work item, call EDI-Prod-get-job-details
# In practice, this would be done through the Copilot interface

Write-Host "Processing $(workItems.Count) work items..."
Write-Host "Total batches needed: 60 (at 5 items per batch)"
"""


def main():
    """Main function to prepare the fetching process."""
    print("Preparing EDI-Prod Bulk Fetch")
    print("=" * 60)
    
    # Load work items
    work_items = load_work_items_from_filtered()
    print(f"Total work items to fetch: {len(work_items)}")
    
    # Load existing dashboard
    dashboard = load_dashboard()
    print(f"Dashboard data items: {len(dashboard['data'])}")
    
    # Generate batches
    batches = generate_batch_tool_calls(work_items, batch_size=5)
    print(f"\nBatch information:")
    print(f"  Total batches: {len(batches)}")
    print(f"  Items per batch: 5 (except possibly last batch)")
    
    # Create tool call documentation
    script = create_tool_call_script(batches)
    
    # Save batch documentation
    with open("batch_tool_calls.py", "w") as f:
        f.write(script)
    
    print(f"\nTool call documentation saved to: batch_tool_calls.py")
    
    # Print summary
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Use Copilot interface to call EDI-Prod-get-job-details")
    print("2. For each work item ID, extract:")
    print("   - summary")
    print("   - status")
    print("   - area (3-char)")
    print("   - module (3-char)")
    print("   - createdTime")
    print("   - defectIntroducedWI (or related field)")
    print("   - defectIntroducedCI (T-number)")
    print("3. Update dashboard_data.json with fetched values")
    print("=" * 60)
    
    # Create first batch example
    if batches:
        first_batch = batches[0]
        print(f"\nFIRST BATCH ({len(first_batch)} items):")
        for wi_id in first_batch:
            print(f"  - {wi_id}")


if __name__ == "__main__":
    main()
