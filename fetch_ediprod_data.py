#!/usr/bin/env python3
"""
EDI-Prod Dashboard Data Fetcher
Fetches work items and defect information from ediprod and exports to JSON
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

class EDIProdClient:
    """Client to interact with EDI-Prod MCP server via CLI"""
    
    def __init__(self):
        self.cache = {}
        self.timestamp = datetime.now().isoformat()
    
    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an EDI-Prod MCP tool via CLI.
        Note: This requires the MCP server to be set up and accessible.
        """
        try:
            # Build the command - this would depend on your MCP server setup
            cmd = [
                "npx", "mcp", "call",
                tool_name,
                json.dumps(params)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Error calling {tool_name}: {result.stderr}", file=sys.stderr)
                return {"error": result.stderr}
        except Exception as e:
            print(f"Exception calling {tool_name}: {str(e)}", file=sys.stderr)
            return {"error": str(e)}
    
    def get_workitems(self, product: str = "SYS", change_type: str = "FIX", 
                     top: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch work items from EDI-Prod
        """
        print(f"Fetching work items... (product={product}, changeType={change_type})", file=sys.stderr)
        
        params = {
            "product": product,
            "changeType": [change_type],
            "top": top,
            "skip": skip,
            "sortBy": "createdAt",
            "sortOrder": "desc"
        }
        
        result = self.call_mcp_tool("EDI-Prod-filter-workitems", params)
        
        if "error" in result:
            print(f"Error fetching work items: {result['error']}", file=sys.stderr)
            return []
        
        # Parse CSV response and convert to structured data
        workitems = self._parse_workitems_response(result)
        print(f"Fetched {len(workitems)} work items", file=sys.stderr)
        
        return workitems
    
    def get_workitem_details(self, workitem_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific work item including defect details
        """
        print(f"Fetching details for {workitem_id}...", file=sys.stderr)
        
        params = {
            "number": workitem_id
        }
        
        result = self.call_mcp_tool("EDI-Prod-get-issue-details", params)
        return result
    
    def get_workflow_tasks(self, workitem_id: str) -> List[Dict[str, Any]]:
        """
        Get workflow and task information to identify defect introduced and first missed review
        """
        # First get workflows
        workflows_result = self.call_mcp_tool("EDI-Prod-get-job-workflows", 
                                             {"jobNumber": workitem_id})
        
        if "error" in workflows_result:
            return []
        
        all_tasks = []
        workflows = workflows_result.get("workflows", [])
        
        # For each workflow, get its tasks
        for workflow in workflows:
            tasks_result = self.call_mcp_tool("EDI-Prod-get-workflow-tasks",
                                             {"workflowId": workflow.get("id")})
            if "tasks" in tasks_result:
                all_tasks.extend(tasks_result["tasks"])
        
        return all_tasks
    
    def extract_defect_introduced(self, workitem_id: str, tasks: List[Dict]) -> Dict[str, Optional[str]]:
        """
        Extract defect introduced information from tasks
        """
        result = {
            "defectIntroducedWI": None,
            "defectIntroducedCI": None,
            "introducedInCheckinTaskId": None,
            "firstMissedReviewTaskId": None
        }
        
        if not tasks:
            return result
        
        # Look for checkin task (defect introduced point)
        for task in tasks:
            task_type = task.get("type", "").upper()
            task_desc = task.get("description", "").upper()
            
            # Check for checkin/check-in tasks
            if "CHECK" in task_type or "CHECK" in task_desc or "CDF" in task_type:
                result["introducedInCheckinTaskId"] = task.get("id")
                result["defectIntroducedCI"] = task.get("description", "Checkin")
                break
        
        # Look for review/barrier tasks (first missed)
        for task in tasks:
            task_type = task.get("type", "").upper()
            task_desc = task.get("description", "").upper()
            
            if "REVIEW" in task_type or "REVIEW" in task_desc or "CBC" in task_type:
                result["firstMissedReviewTaskId"] = task.get("id")
                break
        
        return result
    
    def _parse_workitems_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse work items response (typically CSV format from MCP)
        """
        # This parsing depends on the actual response format from EDI-Prod
        # Adjust based on the actual MCP server response structure
        
        workitems = []
        if isinstance(response, list):
            workitems = response
        elif "data" in response:
            workitems = response["data"]
        elif "workitems" in response:
            workitems = response["workitems"]
        
        # Normalize the response format
        normalized = []
        for item in workitems:
            if isinstance(item, dict):
                normalized.append({
                    "workItemId": item.get("number") or item.get("workItemId") or item.get("id"),
                    "summary": item.get("title") or item.get("summary") or item.get("description"),
                    "status": item.get("status"),
                    "changeType": item.get("changeType") or item.get("change_type"),
                    "productArea": item.get("area") or item.get("productArea"),
                    "createdTime": item.get("createdAt") or item.get("created_time"),
                    "module": item.get("module"),
                    "product": item.get("product"),
                    "priority": item.get("priority"),
                    "createdBy": item.get("createdBy") or item.get("created_by"),
                    "relatedIncidents": item.get("relatedIncidents") or 0,
                })
        
        return normalized
    
    def enrich_workitems_with_defects(self, workitems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich work items with defect introduced information
        """
        enriched = []
        
        for item in workitems:
            workitem_id = item.get("workItemId")
            print(f"Enriching {workitem_id}...", file=sys.stderr)
            
            # Get workflow tasks for this item
            tasks = self.get_workflow_tasks(workitem_id)
            
            # Extract defect information
            defect_info = self.extract_defect_introduced(workitem_id, tasks)
            
            # Merge with original item
            enriched_item = {**item, **defect_info}
            enriched.append(enriched_item)
        
        return enriched


def fetch_and_export_dashboard_data(output_file: str = "dashboard_data.json",
                                   product: str = "SYS",
                                   change_type: str = "FIX",
                                   limit: int = 20):
    """
    Main function to fetch data and export to JSON
    """
    client = EDIProdClient()
    
    print(f"Starting EDI-Prod Dashboard Data Fetch...", file=sys.stderr)
    print(f"Target file: {output_file}", file=sys.stderr)
    
    # Step 1: Get work items
    workitems = client.get_workitems(
        product=product,
        change_type=change_type,
        top=limit
    )
    
    if not workitems:
        print("Warning: No work items fetched", file=sys.stderr)
    
    # Step 2: Enrich with defect information
    enriched_workitems = client.enrich_workitems_with_defects(workitems)
    
    # Step 3: Prepare final data structure
    dashboard_data = {
        "meta": {
            "timestamp": client.timestamp,
            "product": product,
            "changeType": change_type,
            "totalCount": len(enriched_workitems),
            "introducedCount": sum(1 for item in enriched_workitems if item.get("defectIntroducedWI")),
            "resolutionRate": sum(1 for item in enriched_workitems if item.get("status") == "Closed") / len(enriched_workitems) * 100 if enriched_workitems else 0
        },
        "data": enriched_workitems
    }
    
    # Step 4: Export to JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Data exported to {output_file}", file=sys.stderr)
        print(f"✓ Total items: {len(enriched_workitems)}", file=sys.stderr)
        print(f"✓ Items with defects introduced: {dashboard_data['meta']['introducedCount']}", file=sys.stderr)
    except Exception as e:
        print(f"Error exporting data: {str(e)}", file=sys.stderr)
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch EDI-Prod work items and generate dashboard data")
    parser.add_argument("--output", default="dashboard_data.json", help="Output JSON file")
    parser.add_argument("--product", default="SYS", help="Product code to filter by")
    parser.add_argument("--change-type", default="FIX", help="Change type to filter by")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of items to fetch")
    
    args = parser.parse_args()
    
    success = fetch_and_export_dashboard_data(
        output_file=args.output,
        product=args.product,
        change_type=args.change_type,
        limit=args.limit
    )
    
    sys.exit(0 if success else 1)
