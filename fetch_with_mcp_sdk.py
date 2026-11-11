#!/usr/bin/env python3
"""
EDI-Prod Work Items Fetcher using MCP Python SDK
Fetches work items using EDI-Prod-filter-workitems tool and filters by status
"""

import json
import csv
from io import StringIO
from typing import List, Dict, Any, Tuple

# Note: This script assumes MCP server is available and properly configured
# It will attempt to connect to EDI-Prod MCP server

def parse_and_filter_csv(csv_content: str) -> Tuple[int, List[str]]:
    """Parse CSV and filter by status"""
    if not csv_content.strip():
        return 0, []
    
    try:
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)
        
        before_count = len(rows)
        filtered_ids = []
        
        for row in rows:
            status = row.get('status', '').strip()
            
            # FILTER RULE: Exclude CLS, CAN, or empty status
            if status not in ['CLS', 'CAN', '']:
                # Extract work item ID
                wi_id = None
                for col_name in ['number', 'Number', 'id', 'ID']:
                    if col_name in row:
                        wi_id = row[col_name].strip()
                        if wi_id:
                            break
                
                if wi_id:
                    filtered_ids.append(wi_id)
        
        return before_count, filtered_ids
    
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return 0, []

async def fetch_workitems_async():
    """
    Asynchronously fetch work items using MCP client
    """
    from mcp import ClientSession, StdioServerParameters, stdio_client
    
    # Configuration for EDI-Prod MCP server
    # You may need to adjust these based on your setup
    server_params = StdioServerParameters(
        command="edi-prod-server",  # or the actual command to start the EDI-Prod MCP server
        args=[]
    )
    
    result = {
        "ent": {"beforeFilter": 0, "afterFilter": 0, "items": []},
        "glw": {"beforeFilter": 0, "afterFilter": 0, "items": []},
        "totals": {"beforeFilter": 0, "afterFilter": 0}
    }
    
    try:
        # Connect to MCP server
        async with stdio_client(server_params) as client:
            # Fetch ENT items
            ent_before = 0
            ent_items = []
            
            for skip in [0, 50, 100, 150, 200, 250, 300, 350, 400]:
                params = {
                    "product": "ENT",
                    "changeType": ["FIX"],
                    "createdAfter": "2026-10-06",
                    "createdBefore": "2026-11-05",
                    "skip": skip,
                    "top": 50
                }
                
                # Call the tool
                response = await client.call_tool(
                    name="EDI-Prod-filter-workitems",
                    arguments=params
                )
                
                if response.error:
                    print(f"Error fetching ENT skip={skip}: {response.error}")
                    break
                
                # Process response
                if isinstance(response.content, list) and len(response.content) > 0:
                    csv_data = response.content[0].text
                    before, items = parse_and_filter_csv(csv_data)
                    
                    if before == 0:
                        print(f"No more ENT results at skip={skip}")
                        break
                    
                    ent_before += before
                    ent_items.extend(items)
                    print(f"ENT skip={skip}: before={before}, after={len(items)}")
            
            # Remove duplicates
            ent_unique = list(dict.fromkeys(ent_items))
            result["ent"]["beforeFilter"] = ent_before
            result["ent"]["afterFilter"] = len(ent_unique)
            result["ent"]["items"] = ent_unique
            
            # Fetch GLW items (similar process)
            glw_before = 0
            glw_items = []
            
            for skip in [0, 50, 100, 150, 200, 250, 300, 350, 400]:
                params = {
                    "product": "GLW",
                    "changeType": ["FIX"],
                    "createdAfter": "2026-10-06",
                    "createdBefore": "2026-11-05",
                    "skip": skip,
                    "top": 50
                }
                
                response = await client.call_tool(
                    name="EDI-Prod-filter-workitems",
                    arguments=params
                )
                
                if response.error:
                    print(f"Error fetching GLW skip={skip}: {response.error}")
                    break
                
                if isinstance(response.content, list) and len(response.content) > 0:
                    csv_data = response.content[0].text
                    before, items = parse_and_filter_csv(csv_data)
                    
                    if before == 0:
                        print(f"No more GLW results at skip={skip}")
                        break
                    
                    glw_before += before
                    glw_items.extend(items)
                    print(f"GLW skip={skip}: before={before}, after={len(items)}")
            
            # Remove duplicates
            glw_unique = list(dict.fromkeys(glw_items))
            result["glw"]["beforeFilter"] = glw_before
            result["glw"]["afterFilter"] = len(glw_unique)
            result["glw"]["items"] = glw_unique
            
            # Calculate totals
            result["totals"]["beforeFilter"] = ent_before + glw_before
            result["totals"]["afterFilter"] = len(ent_unique) + len(glw_unique)
            
            return result
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure EDI-Prod MCP server is configured and running")
        return result

def main():
    """Main execution"""
    import asyncio
    
    print("="*80)
    print("EDI-PROD WORK ITEMS FETCHER (MCP SDK Version)")
    print("="*80)
    print()
    
    # Try to run async version
    try:
        result = asyncio.run(fetch_workitems_async())
        
        # Save result
        with open('workitems_mcp_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print()
        print("Result Summary:")
        print(f"  ENT: {result['ent']['afterFilter']} items (from {result['ent']['beforeFilter']})")
        print(f"  GLW: {result['glw']['afterFilter']} items (from {result['glw']['beforeFilter']})")
        print(f"  TOTAL: {result['totals']['afterFilter']} items (expected 221)")
        print()
        print("Output file: workitems_mcp_result.json")
        print()
        print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Failed to use async method: {e}")
        print("\nNote: EDI-Prod MCP server must be properly configured")
        print("Expected server configuration needed for tool calls to work")

if __name__ == "__main__":
    main()
