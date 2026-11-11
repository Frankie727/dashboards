#!/usr/bin/env python3
"""
Work Items Fetcher from EDI-Prod MCP Server
This script fetches work items and saves them to JSON
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import csv
from io import StringIO


class WorkItemsFetcher:
    """
    Fetches work items from EDI-Prod MCP Server
    Handles pagination and CSV parsing
    """

    def __init__(self):
        self.all_workitems: List[Dict[str, Any]] = []
        self.fetch_summary = {
            'ENT': {'total': 0, 'batches': 0},
            'GLW': {'total': 0, 'batches': 0}
        }

    def parse_csv_response(self, csv_data: str, product: str) -> List[Dict[str, Any]]:
        """
        Parse CSV response from EDI-Prod-filter-workitems tool
        Maps CSV columns to expected JSON fields
        """
        workitems = []
        
        try:
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            if csv_reader is None:
                print(f"Warning: No CSV data to parse for product {product}", file=sys.stderr)
                return workitems
            
            for row in csv_reader:
                # Extract and map fields from CSV
                workitem = {
                    'workItemId': row.get('Number', '').strip(),
                    'summary': row.get('Summary', '').strip(),
                    'status': row.get('Status', '').strip(),
                    'changeType': row.get('ChangeType', '').strip(),
                    'product': row.get('Product', '').strip(),
                    'productArea': row.get('Area', '').strip(),
                    'createdTime': self._extract_date(row.get('Created', '')),
                    'module': row.get('Module', '').strip(),
                    'priority': row.get('Priority', '').strip() or '',
                    'defectIntroducedWI': row.get('DefectIntroducedWI') or None,
                    'defectIntroducedCI': row.get('DefectIntroducedCI') or None,
                    'relatedIncidents': int(row.get('RelatedIncidents', 0)) if row.get('RelatedIncidents', '').isdigit() else 0
                }
                
                if workitem['workItemId']:  # Only add if we have a valid ID
                    workitems.append(workitem)
        
        except Exception as e:
            print(f"Error parsing CSV for product {product}: {str(e)}", file=sys.stderr)
        
        return workitems

    def _extract_date(self, created_field: str) -> str:
        """
        Extract YYYY-MM-DD date from ISO datetime string
        """
        if not created_field:
            return ''
        
        # Handle ISO format: 2026-10-06T12:30:45.123Z or similar
        if 'T' in created_field:
            return created_field.split('T')[0]
        
        # If it's already just a date, return as-is
        return created_field[:10] if len(created_field) >= 10 else created_field

    def save_to_json(self, output_path: str) -> None:
        """
        Save collected work items to JSON file
        """
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        output = {
            'metadata': {
                'fetchedAt': datetime.now().isoformat(),
                'totalItems': len(self.all_workitems),
                'productSummary': self.fetch_summary
            },
            'workitems': self.all_workitems
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(self.all_workitems)} work items to {output_path}")
        print(f"\nFetch Summary:")
        for product, stats in self.fetch_summary.items():
            print(f"  {product}: {stats['total']} items ({stats['batches']} batches)")

    def add_workitems(self, workitems: List[Dict[str, Any]], product: str) -> None:
        """
        Add work items to the collection and update stats
        """
        self.all_workitems.extend(workitems)
        self.fetch_summary[product]['total'] += len(workitems)
        self.fetch_summary[product]['batches'] += 1


def main():
    """
    Main entry point
    Coordinates fetching work items for ENT and GLW products
    """
    print("Work Items Fetcher Configuration")
    print("=" * 70)
    print(f"Target file: C:\\Users\\Francesco.Mangione\\GitHub Repo - Francesco\\Dashboards\\workitems_data.json")
    print(f"Products: ENT, GLW")
    print(f"Filters: changeType=['FIX'], createdAfter='2026-10-06'")
    print(f"Pagination: top=50 per batch")
    print("=" * 70)
    print()
    print("NOTE: This script requires EDI-Prod-filter-workitems tool to be called")
    print("The actual data fetching will be done by the calling agent")
    print()


if __name__ == '__main__':
    main()
