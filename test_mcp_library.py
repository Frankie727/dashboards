#!/usr/bin/env python3
"""
EDI-Prod Work Items Fetcher using MCP library
Fetches work items and filters by status
"""

import json
import asyncio
from typing import List, Dict, Any, Tuple

async def main():
    """Main execution"""
    
    try:
        # Try to import and use MCP
        import mcp
        print(f"MCP library found: {mcp.__version__ if hasattr(mcp, '__version__') else 'version unknown'}")
    except Exception as e:
        print(f"Error importing MCP: {e}")
        return
    
    # Test the MCP library
    print("\nTesting MCP library capabilities...")
    print(f"Available attributes: {[attr for attr in dir(mcp) if not attr.startswith('_')]}")

if __name__ == "__main__":
    asyncio.run(main())
