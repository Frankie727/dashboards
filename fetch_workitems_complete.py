#!/usr/bin/env python3
"""
EDI-Prod Work Items Data Fetcher
Fetches work items from EDI-Prod MCP Server and saves to JSON

Usage:
    python fetch_workitems_complete.py

This script:
1. Calls EDI-Prod-filter-workitems for ENT and GLW products
2. Paginates through all results (50 per batch)
3. Parses CSV responses
4. Saves combined data to workitems_data.json
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import csv
from io import StringIO
from pathlib import Path


class EDIProdWorkItemsFetcher:
    """Fetches work items from EDI-Prod MCP Server"""
    
    BATCH_SIZE = 50
    PRODUCTS = ['ENT', 'GLW']
    CHANGE_TYPE = ['FIX']
    CREATED_AFTER = '2026-10-06'
    CHANGE_TYPE_FILTER = 'FIX'
    
    def __init__(self):
        self.all_workitems: List[Dict[str, Any]] = []
        self.fetch_summary = {'ENT': {'total': 0, 'batches': 0}, 'GLW': {'total': 0, 'batches': 0}}
        self.errors: List[str] = []
        
    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Call an EDI-Prod MCP tool
        
        Attempts multiple approaches:
        1. Direct MCP CLI call (if available)
        2. Environment-based lookup
        """
        try:
            # Try using the MCP CLI if available
            # This assumes 'mcp' command is in PATH
            
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
                error_msg = f"MCP tool error: {result.stderr}"
                self.errors.append(f"{tool_name}: {error_msg}")
                return None
                
        except FileNotFoundError:
            error_msg = "MCP CLI not found in PATH"
            self.errors.append(error_msg)
            return None
        except subprocess.TimeoutExpired:
            error_msg = f"MCP tool call timed out"
            self.errors.append(f"{tool_name}: {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Error calling MCP tool: {str(e)}"
            self.errors.append(f"{tool_name}: {error_msg}")
            return None
    
    def fetch_product_workitems(self, product: str) -> List[Dict[str, Any]]:
        """
        Fetch all work items for a product, paginating through results
        """
        all_items = []
        skip = 0
        batch_num = 0
        
        print(f"\n{'='*70}")
        print(f"Fetching {product} work items (FIX, created after {self.CREATED_AFTER})")
        print(f"{'='*70}")
        
        while True:
            batch_num += 1
            print(f"\nBatch {batch_num}: Fetching {self.BATCH_SIZE} items (skip={skip})...")
            
            params = {
                'product': product,
                'changeType': [self.CHANGE_TYPE_FILTER],
                'createdAfter': self.CREATED_AFTER,
                'top': self.BATCH_SIZE,
                'skip': skip
            }
            
            csv_data = self.call_mcp_tool('EDI-Prod-filter-workitems', params)
            
            if csv_data is None:
                print(f"  [!] Failed to fetch batch for {product}")
                break
            
            items = self.parse_csv_response(csv_data, product)
            
            if not items:
                print(f"  [OK] No more items (received {len(items)} items)")
                break
            
            print(f"  [OK] Fetched {len(items)} items")
            all_items.extend(items)
            
            # Update summary
            self.fetch_summary[product]['total'] += len(items)
            self.fetch_summary[product]['batches'] += 1
            
            # Check if we got fewer than the batch size (means we're done)
            if len(items) < self.BATCH_SIZE:
                print(f"  → Pagination complete ({len(items)} < {self.BATCH_SIZE})")
                break
            
            skip += self.BATCH_SIZE
        
        print(f"\n{product} Summary: {self.fetch_summary[product]['total']} items in {self.fetch_summary[product]['batches']} batch(es)")
        return all_items
    
    def parse_csv_response(self, csv_data: str, product: str) -> List[Dict[str, Any]]:
        """
        Parse CSV response from EDI-Prod-filter-workitems
        
        Expected CSV columns:
        Number, Summary, Status, ChangeType, Product, Area, Created, Module, 
        Priority, DefectIntroducedWI, DefectIntroducedCI, RelatedIncidents
        """
        workitems = []
        
        try:
            lines = csv_data.strip().split('\n')
            if len(lines) < 2:
                return workitems
            
            reader = csv.DictReader(StringIO(csv_data))
            
            for row in reader:
                if not row or not row.get('Number'):
                    continue
                
                # Extract date from ISO format (YYYY-MM-DDTHH:MM:SS...)
                created = row.get('Created', '').split('T')[0] if row.get('Created') else ''
                
                workitem = {
                    'workItemId': row.get('Number', '').strip(),
                    'summary': row.get('Summary', '').strip(),
                    'status': row.get('Status', '').strip(),
                    'changeType': row.get('ChangeType', '').strip(),
                    'product': row.get('Product', '').strip(),
                    'productArea': row.get('Area', '').strip(),
                    'createdTime': created,
                    'module': row.get('Module', '').strip(),
                    'priority': row.get('Priority', '').strip() or '',
                    'defectIntroducedWI': row.get('DefectIntroducedWI') or None,
                    'defectIntroducedCI': row.get('DefectIntroducedCI') or None,
                    'relatedIncidents': int(row.get('RelatedIncidents', 0)) if row.get('RelatedIncidents', '').isdigit() else 0
                }
                
                workitems.append(workitem)
        
        except Exception as e:
            self.errors.append(f"Error parsing CSV for {product}: {str(e)}")
        
        return workitems
    
    def save_to_json(self, output_path: str) -> bool:
        """
        Save work items to JSON file
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            total_items = len(self.all_workitems)
            
            data = {
                'metadata': {
                    'fetchedAt': datetime.now().isoformat(),
                    'totalItems': total_items,
                    'productSummary': self.fetch_summary,
                    'filters': {
                        'changeType': [self.CHANGE_TYPE_FILTER],
                        'createdAfter': self.CREATED_AFTER
                    }
                },
                'workitems': self.all_workitems
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            self.errors.append(f"Error saving JSON: {str(e)}")
            return False
    
    def run(self, output_path: str) -> bool:
        """
        Main execution method
        """
        print(f"EDI-Prod Work Items Fetcher")
        print(f"{'='*70}")
        print(f"Output: {output_path}")
        print(f"Products: {', '.join(self.PRODUCTS)}")
        print(f"Filters: changeType={self.CHANGE_TYPE_FILTER}, createdAfter={self.CREATED_AFTER}")
        
        # Fetch work items for each product
        for product in self.PRODUCTS:
            items = self.fetch_product_workitems(product)
            self.all_workitems.extend(items)
        
        # Save to JSON
        print(f"\n{'='*70}")
        print(f"Saving {len(self.all_workitems)} work items to JSON...")
        
        if self.save_to_json(output_path):
            print(f"[OK] Successfully saved to {output_path}")
            self.print_summary()
            return True
        else:
            print(f"[ERROR] Failed to save JSON")
            return False
    
    def print_summary(self):
        """Print summary of fetch operation"""
        print(f"\n{'='*70}")
        print(f"FETCH SUMMARY")
        print(f"{'='*70}")
        print(f"Total work items: {len(self.all_workitems)}")
        for product, stats in self.fetch_summary.items():
            print(f"  {product}: {stats['total']} items ({stats['batches']} batch/batches)")
        
        if self.errors:
            print(f"\nWarnings/Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  [!] {error}")
        
        print(f"{'='*70}\n")


def main():
    output_file = r"C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\workitems_data.json"
    
    fetcher = EDIProdWorkItemsFetcher()
    success = fetcher.run(output_file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
