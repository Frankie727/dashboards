#!/usr/bin/env python3
"""
Fetch all available workitem product codes from EDI-Prod
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def call_ediprod_tool(tool_name: str, params: dict) -> dict:
    """
    Call an EDI-Prod MCP tool.
    Attempts to use the mcp client if available.
    """
    try:
        # Try using Copilot's MCP client
        cmd = [
            sys.executable, "-m", "mcp",
            "call",
            tool_name,
            json.dumps(params)
        ]
        
        print(f"Calling tool: {tool_name} with params: {json.dumps(params)}", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # Response might be CSV, convert it
                return {"raw_output": result.stdout}
        else:
            print(f"Tool call failed: {result.stderr}", file=sys.stderr)
            return {"error": result.stderr, "return_code": result.returncode}
    except Exception as e:
        print(f"Exception: {str(e)}", file=sys.stderr)
        return {"error": str(e)}

def fetch_workitem_products():
    """Fetch all workitem product codes"""
    
    print("Fetching all available workitem products from EDI-Prod...", file=sys.stderr)
    
    # Call the lookup-products tool
    result = call_ediprod_tool("EDI-Prod-lookup-products", {"jobType": "workitem"})
    
    if "error" in result and "raw_output" not in result:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        return None
    
    # Parse CSV response if present
    output = result.get("raw_output", json.dumps(result))
    
    # Try to parse as CSV
    products = []
    lines = output.strip().split('\n')
    
    for i, line in enumerate(lines):
        if i == 0:
            # Skip header
            continue
        if line.strip():
            parts = line.split(',', 1)
            if len(parts) >= 2:
                code = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else ""
                products.append({
                    "code": code,
                    "description": description
                })
            elif parts:
                products.append({
                    "code": parts[0].strip(),
                    "description": ""
                })
    
    return products

def main():
    """Main function"""
    
    print("Starting product lookup...", file=sys.stderr)
    
    products = fetch_workitem_products()
    
    if products is None:
        print("Failed to fetch products", file=sys.stderr)
        sys.exit(1)
    
    # Create output structure
    output = {
        "timestamp": datetime.now().isoformat(),
        "jobType": "workitem",
        "total_products": len(products),
        "products": products
    }
    
    # Print to stdout
    print(json.dumps(output, indent=2))
    
    # Save to file
    output_path = Path(__file__).parent / "all_products.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_path}", file=sys.stderr)
    print(f"Total products found: {len(products)}", file=sys.stderr)
    
    if products:
        print("\nProduct codes found:", file=sys.stderr)
        for prod in products:
            print(f"  - {prod['code']}: {prod['description']}", file=sys.stderr)

if __name__ == "__main__":
    main()
