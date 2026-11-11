#!/usr/bin/env python3
"""
Fetch ALL GLW work items using MCP CLI
Systematically retrieves all pages until fewer than 50 results are returned
Saves to: glw_workitems_raw.json
"""

import json
import subprocess
import sys
import os
import csv
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any, Optional

class GLWWorkItemsCollector:
    """Fetches and collects all GLW work items using MCP CLI"""
    
    BATCH_SIZE = 50
    TOOL_NAME = "EDI-Prod-filter-workitems"
    BASE_PARAMS = {
        "product": "GLW",
        "changeType": ["FIX"],
        "status": ["NCM"],
        "createdAfter": "2026-10-06",
        "createdBefore": "2026-11-05"
    }
    
    def __init__(self):
        self.batches: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.total_count: Optional[int] = None
    
    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[str]:
        """Call an MCP tool via CLI and return raw response"""
        try:
            cmd = ['mcp', 'call', tool_name, json.dumps(params)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ}
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                error_msg = f"MCP call failed with code {result.returncode}: {result.stderr}"
                self.errors.append(f"{tool_name}: {error_msg}")
                print(f"ERROR: {error_msg}", file=sys.stderr)
                return None
                
        except FileNotFoundError:
            error_msg = "MCP CLI not found in PATH"
            self.errors.append(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return None
        except subprocess.TimeoutExpired:
            error_msg = f"MCP tool call timed out (60s)"
            self.errors.append(f"{tool_name}: {error_msg}")
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return None
        except Exception as e:
            error_msg = f"Exception calling MCP tool: {str(e)}"
            self.errors.append(f"{tool_name}: {error_msg}")
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return None
    
    def parse_csv_response(self, csv_data: str) -> tuple[List[Dict[str, Any]], Optional[int]]:
        """
        Parse CSV response from MCP tool
        CSV format includes headers and may include total count info
        """
        items = []
        total_count = None
        
        try:
            reader = csv.DictReader(StringIO(csv_data))
            if reader is None or reader.fieldnames is None:
                print(f"Warning: No CSV headers found in response", file=sys.stderr)
                return items, total_count
            
            for row in reader:
                if row:  # Skip empty rows
                    items.append(row)
            
            print(f"  Parsed {len(items)} items from CSV response", file=sys.stderr)
            
        except Exception as e:
            error_msg = f"Error parsing CSV response: {str(e)}"
            self.errors.append(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            print(f"  CSV data first 500 chars: {csv_data[:500]}", file=sys.stderr)
        
        return items, total_count
    
    def fetch_page(self, skip: int, page_num: int) -> tuple[List[Dict[str, Any]], int]:
        """Fetch a single page of results"""
        params = {**self.BASE_PARAMS, "skip": skip, "top": self.BATCH_SIZE}
        
        print(f"\n[Page {page_num}] Fetching with skip={skip}, top={self.BATCH_SIZE}...", 
              file=sys.stderr)
        
        csv_response = self.call_mcp_tool(self.TOOL_NAME, params)
        if csv_response is None:
            return [], 0
        
        items, total_count = self.parse_csv_response(csv_response)
        if total_count is not None and self.total_count is None:
            self.total_count = total_count
        
        result_count = len(items)
        print(f"  Got {result_count} items from this page", file=sys.stderr)
        
        # Extract key fields for each work item
        work_items = []
        for item in items:
            wi = {
                "id": item.get("number", ""),
                "title": item.get("title", ""),
                "status": item.get("status", ""),
                "changeType": item.get("changeType", ""),
                "area": item.get("area", ""),
                "module": item.get("module", ""),
                "createdAt": item.get("createdAt", ""),
                "createdBy": item.get("createdBy", "")
            }
            # Include any other fields that were returned
            for key, value in item.items():
                if key not in wi:
                    wi[key] = value
            work_items.append(wi)
        
        return work_items, result_count
    
    def fetch_all_pages(self) -> None:
        """Paginate through all work items"""
        skip = 0
        page_num = 1
        
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"Fetching ALL GLW work items with FIX/NCM status", file=sys.stderr)
        print(f"{'='*70}", file=sys.stderr)
        print(f"Base Parameters:", file=sys.stderr)
        print(f"  Product: GLW", file=sys.stderr)
        print(f"  ChangeType: FIX", file=sys.stderr)
        print(f"  Status: NCM", file=sys.stderr)
        print(f"  Created: 2026-10-06 to 2026-11-05", file=sys.stderr)
        print(f"  Batch size: {self.BATCH_SIZE}", file=sys.stderr)
        
        while True:
            work_items, result_count = self.fetch_page(skip, page_num)
            
            batch_data = {
                "skip": skip,
                "top": self.BATCH_SIZE,
                "resultCount": result_count,
                "workItems": work_items
            }
            self.batches.append(batch_data)
            
            if result_count < self.BATCH_SIZE:
                print(f"\n[Page {page_num}] Got {result_count} results (< {self.BATCH_SIZE}), stopping", 
                      file=sys.stderr)
                break
            
            skip += self.BATCH_SIZE
            page_num += 1
            
            # Safety limit
            if page_num > 100:
                print(f"WARNING: Reached safety limit of 100 pages", file=sys.stderr)
                break
        
        total_items = sum(b["resultCount"] for b in self.batches)
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"Fetch complete: {len(self.batches)} pages fetched", file=sys.stderr)
        print(f"Total items collected: {total_items}", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)
    
    def generate_output(self) -> Dict[str, Any]:
        """Generate the final output structure"""
        total_items = sum(b["resultCount"] for b in self.batches)
        
        return {
            "product": "GLW",
            "totalCount": self.total_count or total_items,
            "itemsCollected": total_items,
            "batchesCount": len(self.batches),
            "batches": self.batches,
            "fetchedAt": datetime.now().isoformat(),
            "parameters": self.BASE_PARAMS,
            "errors": self.errors if self.errors else None
        }

def main():
    # Create collector
    collector = GLWWorkItemsCollector()
    
    # Fetch all pages
    collector.fetch_all_pages()
    
    # Generate output
    output = collector.generate_output()
    
    # Save to file
    output_file = r"C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\glw_workitems_raw.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Successfully saved to: {output_file}", file=sys.stderr)
    except Exception as e:
        print(f"\n✗ Error saving to file: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Also print to stdout
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
