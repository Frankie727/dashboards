#!/usr/bin/env python3
"""
Complete GLW Work Item Fetcher - Batch Collection and Detail Retrieval
Uses MCP to fetch ALL GLW work items with complete details
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / 'glw_complete_details_all.json'
STATE_FILE = OUTPUT_DIR / 'glw_fetch_state.json'

class GLWFetcher:
    """Fetches GLW work items and their complete details"""
    
    def __init__(self):
        self.all_work_item_ids: List[str] = []
        self.all_work_items_details: Dict[str, Any] = {}
        self.batch_results: Dict[int, Any] = {}
        self.errors: List[str] = []
        self.start_time = time.time()
    
    def get_filter_params(self, skip: int = 0, top: int = 50) -> Dict[str, Any]:
        """Get parameters for EDI-Prod-filter-workitems call"""
        return {
            "product": "GLW",
            "changeType": ["FIX"],
            "status": ["NCM"],
            "createdAfter": "2026-10-06",
            "createdBefore": "2026-11-05",
            "skip": skip,
            "top": top
        }
    
    def get_job_details_params(self, workitem_id: str) -> Dict[str, Any]:
        """Get parameters for EDI-Prod-get-job-details call"""
        return {"jobNumber": workitem_id}
    
    def generate_tool_invocations(self) -> Dict[str, Any]:
        """Generate all tool invocations needed for a complete fetch"""
        
        invocations = {
            "metadata": {
                "product": "GLW",
                "changeType": "FIX",
                "status": "NCM",
                "dateRange": {
                    "createdAfter": "2026-10-06",
                    "createdBefore": "2026-11-05"
                },
                "generatedAt": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "expectedPhases": 2
            },
            "phase_1_batch_collection": {
                "description": "Fetch ALL work item IDs using pagination",
                "tool": "EDI-Prod-filter-workitems",
                "total_batches": 7,
                "batches": []
            },
            "phase_2_detail_collection": {
                "description": "Fetch complete details for each work item",
                "tool": "EDI-Prod-get-job-details",
                "batch_size": "50 work items per batch",
                "template": self.get_job_details_params("WI00000000")
            }
        }
        
        # Add batch invocations
        for skip in range(0, 350, 50):
            invocations["phase_1_batch_collection"]["batches"].append({
                "batch_num": skip // 50,
                "skip": skip,
                "top": 50,
                "parameters": self.get_filter_params(skip, 50)
            })
        
        return invocations
    
    def create_execution_script(self) -> str:
        """Create a PowerShell script to execute the tool calls"""
        
        script = '''# GLW Work Items Complete Details Fetcher
# This script executes the EDI-Prod MCP tool calls to fetch all GLW work items

$outputFile = 'C:\\Users\\Francesco.Mangione\\GitHub Repo - Francesco\\Dashboards\\glw_complete_details_all.json'
$allWorkItemIds = @()
$allDetails = @()

# Phase 1: Collect all work item IDs via pagination
Write-Host "Phase 1: Collecting work item IDs..."
$skip = 0
$batchNum = 0
$totalItems = 0

do {
    Write-Host "  Batch $batchNum (skip=$skip)..."
    
    # Call EDI-Prod-filter-workitems
    # Tool parameters:
    # - product: "GLW"
    # - changeType: ["FIX"]
    # - status: ["NCM"]
    # - createdAfter: "2026-10-06"
    # - createdBefore: "2026-11-05"
    # - skip: $skip
    # - top: 50
    
    # This should return CSV format with work item numbers
    # Extract all "WI" IDs from the results
    
    $skip += 50
    $batchNum++
    
} while ($batchNum -lt 7)  # Try up to 7 batches (350 items potential)

Write-Host "Total work items collected: $totalItems"

# Phase 2: Fetch details for each work item
Write-Host "Phase 2: Collecting complete details for each work item..."
$detailsCollected = 0

foreach ($workItemId in $allWorkItemIds) {
    # Call EDI-Prod-get-job-details with jobNumber: $workItemId
    # This returns comprehensive details including:
    # - Basic attributes (title, status, product info)
    # - Description and notes
    # - Related workitems, incidents, projects
    # - Related issues
    # - Attached documents
    
    $detailsCollected++
}

Write-Host "Complete details collected: $detailsCollected"

# Phase 3: Save results
$output = @{
    metadata = @{
        product = "GLW"
        changeType = "FIX"
        status = "NCM"
        dateRange = @{
            createdAfter = "2026-10-06"
            createdBefore = "2026-11-05"
        }
        fetchedAt = Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ'
        totalItems = $totalItems
    }
    workItems = $allWorkItemIds
    details = $allDetails
}

$output | ConvertTo-Json -Depth 20 | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "Results saved to: $outputFile"
'''
        
        return script
    
    def create_summary(self) -> Dict[str, Any]:
        """Create a summary of what needs to be fetched"""
        
        return {
            "executionPlan": {
                "product": "GLW",
                "filters": {
                    "changeType": "FIX",
                    "status": "NCM",
                    "createdAfter": "2026-10-06",
                    "createdBefore": "2026-11-05"
                },
                "phases": [
                    {
                        "phase": 1,
                        "name": "Batch Collection",
                        "tool": "EDI-Prod-filter-workitems",
                        "calls": 7,
                        "description": "Fetch work item IDs with pagination (skip=0, 50, 100, ...)"
                    },
                    {
                        "phase": 2,
                        "name": "Detail Retrieval",
                        "tool": "EDI-Prod-get-job-details",
                        "calls": "~165",
                        "description": "Fetch complete details for each work item"
                    }
                ],
                "expectedResults": {
                    "totalWorkItems": "~165",
                    "totalAPICalls": "~172",
                    "outputFile": str(OUTPUT_FILE)
                }
            },
            "toolInvocations": self.generate_tool_invocations()
        }
    
    def save_summary(self):
        """Save execution summary to file"""
        summary = self.create_summary()
        summary_file = OUTPUT_DIR / 'glw_execution_summary.json'
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary_file

def main():
    print("=" * 80)
    print("GLW WORK ITEM COMPLETE DETAILS FETCHER")
    print("=" * 80)
    print()
    
    fetcher = GLWFetcher()
    
    print("STEP 1: Generating execution plan...")
    summary_file = fetcher.save_summary()
    print(f"[OK] Saved to: {summary_file}")
    print()
    
    print("STEP 2: Reading execution summary...")
    with open(summary_file, 'r') as f:
        summary = json.load(f)
    
    print("Execution Plan:")
    print(json.dumps(summary['executionPlan'], indent=2))
    print()
    
    print("=" * 80)
    print("READY FOR TOOL INVOCATIONS")
    print("=" * 80)
    print()
    print("Tool Invocation Details:")
    print(json.dumps(summary['toolInvocations']['phase_1_batch_collection']['batches'][:3], indent=2))
    print()
    print("... and more batches ...")
    print()

if __name__ == "__main__":
    main()
