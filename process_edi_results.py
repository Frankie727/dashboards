#!/usr/bin/env python3
"""
EDI Prod Work Items Result Processor

This script processes work item results from EDI Prod MCP Server queries.
Handles CSV/JSON conversion, filtering, and report generation.

Usage:
    python process_edi_results.py --input edi_workitems.json --output edi_report.json
    python process_edi_results.py --input edi_workitems.csv --format csv
"""

import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional


class EDIWorkItemProcessor:
    """Process EDI work item results and generate reports."""
    
    EXCLUDED_STATUSES = {"CLS", "CAN"}
    
    def __init__(self):
        self.work_items = []
        self.statistics = {
            "totalCount": 0,
            "byProduct": {},
            "byStatus": defaultdict(int),
            "byModule": defaultdict(int),
            "byPriority": defaultdict(int),
            "defectTraceability": {
                "withDefectIntroducedWI": 0,
                "withDefectIntroducedCI": 0,
                "withBoth": 0,
                "withNeither": 0
            }
        }
    
    def load_json(self, filepath: str) -> None:
        """Load work items from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle both direct array and object with 'data' key
        if isinstance(data, dict) and 'data' in data:
            self.work_items = data['data']
        else:
            self.work_items = data if isinstance(data, list) else []
    
    def load_csv(self, filepath: str) -> None:
        """Load work items from CSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.work_items.append(row)
    
    def filter_work_items(self) -> None:
        """Filter out closed, cancelled, and empty status items."""
        original_count = len(self.work_items)
        
        self.work_items = [
            item for item in self.work_items
            if item.get('status') and item.get('status') not in self.EXCLUDED_STATUSES
        ]
        
        excluded_count = original_count - len(self.work_items)
        print(f"Filtered: Excluded {excluded_count} items (closed/cancelled/empty status)")
    
    def calculate_statistics(self) -> None:
        """Calculate statistics from work items."""
        self.statistics["totalCount"] = len(self.work_items)
        
        for item in self.work_items:
            # Product distribution
            product = item.get('product', 'UNKNOWN')
            if product not in self.statistics['byProduct']:
                self.statistics['byProduct'][product] = {'count': 0, 'withDefect': 0}
            self.statistics['byProduct'][product]['count'] += 1
            
            # Status distribution
            status = item.get('status', 'UNKNOWN')
            self.statistics['byStatus'][status] += 1
            
            # Module distribution
            module = item.get('module', 'UNKNOWN')
            self.statistics['byModule'][module] += 1
            
            # Priority distribution
            priority = item.get('priority', 'UNKNOWN')
            self.statistics['byPriority'][priority] += 1
            
            # Defect traceability
            has_wi = bool(item.get('defectIntroducedWI'))
            has_ci = bool(item.get('defectIntroducedCI'))
            
            if has_wi and has_ci:
                self.statistics['defectTraceability']['withBoth'] += 1
                self.statistics['byProduct'][product]['withDefect'] += 1
            elif has_wi:
                self.statistics['defectTraceability']['withDefectIntroducedWI'] += 1
                self.statistics['byProduct'][product]['withDefect'] += 1
            elif has_ci:
                self.statistics['defectTraceability']['withDefectIntroducedCI'] += 1
                self.statistics['byProduct'][product]['withDefect'] += 1
            else:
                self.statistics['defectTraceability']['withNeither'] += 1
        
        # Convert defaultdicts to regular dicts for JSON serialization
        self.statistics['byStatus'] = dict(self.statistics['byStatus'])
        self.statistics['byModule'] = dict(self.statistics['byModule'])
        self.statistics['byPriority'] = dict(self.statistics['byPriority'])
    
    def save_json(self, filepath: str) -> None:
        """Save work items and statistics to JSON file."""
        output = {
            "meta": {
                "timestamp": datetime.now().isoformat() + "Z",
                "totalItems": len(self.work_items),
                "processedAt": datetime.now().isoformat()
            },
            "statistics": self.statistics,
            "data": self.work_items
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def save_csv(self, filepath: str) -> None:
        """Save work items to CSV file."""
        if not self.work_items:
            print("No items to save")
            return
        
        # Get all unique keys
        fieldnames = set()
        for item in self.work_items:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.work_items)
    
    def generate_report(self) -> str:
        """Generate a text report of statistics."""
        report = []
        report.append("=" * 80)
        report.append("EDI WORK ITEMS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        report.append(f"Total Work Items: {self.statistics['totalCount']}")
        report.append("")
        
        report.append("Distribution by Product:")
        for product, data in self.statistics['byProduct'].items():
            defect_count = data.get('withDefect', 0)
            pct = (defect_count / data['count'] * 100) if data['count'] > 0 else 0
            report.append(f"  {product:5} - {data['count']:4} items, {defect_count:3} with defect info ({pct:.1f}%)")
        report.append("")
        
        report.append("Distribution by Status:")
        for status, count in sorted(self.statistics['byStatus'].items()):
            report.append(f"  {status:5} - {count:4} items")
        report.append("")
        
        report.append("Distribution by Module (Top 10):")
        sorted_modules = sorted(
            self.statistics['byModule'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for module, count in sorted_modules:
            report.append(f"  {module:5} - {count:4} items")
        report.append("")
        
        report.append("Distribution by Priority:")
        for priority in ["P1", "P2", "P3", "P4", "P5"]:
            count = self.statistics['byPriority'].get(priority, 0)
            if count > 0:
                report.append(f"  {priority:5} - {count:4} items")
        report.append("")
        
        report.append("Defect Traceability:")
        total_defect = sum([
            self.statistics['defectTraceability']['withDefectIntroducedWI'],
            self.statistics['defectTraceability']['withDefectIntroducedCI'],
            self.statistics['defectTraceability']['withBoth'],
            self.statistics['defectTraceability']['withNeither']
        ])
        
        for key, count in self.statistics['defectTraceability'].items():
            pct = (count / total_defect * 100) if total_defect > 0 else 0
            report.append(f"  {key:30} - {count:4} items ({pct:.1f}%)")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def process(self, input_file: str, input_format: str = "json") -> None:
        """Process the input file."""
        print(f"Loading {input_format.upper()} file: {input_file}")
        
        if input_format == "json":
            self.load_json(input_file)
        elif input_format == "csv":
            self.load_csv(input_file)
        else:
            raise ValueError(f"Unsupported format: {input_format}")
        
        print(f"Loaded {len(self.work_items)} items")
        
        print("Filtering work items...")
        self.filter_work_items()
        
        print("Calculating statistics...")
        self.calculate_statistics()
        
        print("Processing complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Process EDI Prod work item results"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file (JSON or CSV)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Input file format (default: json)"
    )
    parser.add_argument(
        "--output-json", "-oj",
        help="Output JSON file"
    )
    parser.add_argument(
        "--output-csv", "-oc",
        help="Output CSV file"
    )
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Print text report to console"
    )
    
    args = parser.parse_args()
    
    # Create processor
    processor = EDIWorkItemProcessor()
    processor.process(args.input, args.format)
    
    # Save outputs
    if args.output_json:
        print(f"Saving JSON: {args.output_json}")
        processor.save_json(args.output_json)
    
    if args.output_csv:
        print(f"Saving CSV: {args.output_csv}")
        processor.save_csv(args.output_csv)
    
    # Print report
    if args.report or (not args.output_json and not args.output_csv):
        print("\n" + processor.generate_report())


if __name__ == "__main__":
    main()
