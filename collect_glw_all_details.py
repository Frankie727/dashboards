#!/usr/bin/env python3
"""
Comprehensive GLW Work Item Data Collector

This script orchestrates fetching ALL GLW work items and their complete details.
It uses a multi-phase approach:
1. Fetch work item IDs via pagination (7 batches)
2. Fetch complete details for each work item  
3. Aggregate and save to JSON

Since MCP tool invocation may have call limits, this script prepares
all necessary parameters and coordinates the collection.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class GLWDataCollector:
    """Orchestrates GLW work item data collection"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent
        self.output_file = self.output_dir / 'glw_complete_details_all.json'
        self.params_file = self.output_dir / 'glw_tool_params.json'
        self.tool_calls_file = self.output_dir / 'glw_tool_calls.json'
        
        self.all_work_items = {}
        self.batch_work_items = {}
        self.failed_items = []
        self.collection_metadata = {
            'started_at': datetime.utcnow().isoformat() + 'Z',
            'phase': 'INITIALIZATION'
        }
    
    def create_batch_parameters(self) -> List[Dict[str, Any]]:
        """Create parameters for all batch collection calls"""
        batches = []
        
        for batch_num in range(7):
            skip = batch_num * 50
            batches.append({
                'batch_id': f'batch_{batch_num}',
                'batch_number': batch_num,
                'skip': skip,
                'top': 50,
                'tool': 'EDI-Prod-filter-workitems',
                'parameters': {
                    'product': 'GLW',
                    'changeType': ['FIX'],
                    'status': ['NCM'],
                    'createdAfter': '2026-10-06',
                    'createdBefore': '2026-11-05',
                    'skip': skip,
                    'top': 50
                }
            })
        
        return batches
    
    def create_detail_parameters_template(self) -> Dict[str, Any]:
        """Create template for detail collection calls"""
        return {
            'tool': 'EDI-Prod-get-job-details',
            'parameter_template': {
                'jobNumber': 'WI00000000'  # to be replaced with actual ID
            },
            'expected_calls': 'Will be ~165 calls based on batch results'
        }
    
    def create_tool_call_manifest(self) -> Dict[str, Any]:
        """Create complete manifest of all tool calls needed"""
        
        batch_params = self.create_batch_parameters()
        detail_template = self.create_detail_parameters_template()
        
        manifest = {
            'metadata': {
                'product': 'GLW',
                'description': 'Complete GLW work item data collection',
                'filters': {
                    'changeType': 'FIX',
                    'status': 'NCM',
                    'dateRange': '2026-10-06 to 2026-11-05'
                },
                'creation_time': datetime.utcnow().isoformat() + 'Z',
                'total_batch_calls': len(batch_params),
                'total_detail_calls': 'TBD (after batch collection)',
                'total_estimated_calls': '~172'
            },
            'phase_1_batch_collection': {
                'description': 'Fetch all work item IDs using pagination',
                'tool': 'EDI-Prod-filter-workitems',
                'calls': batch_params,
                'expected_result': 'CSV format with WI numbers, total count'
            },
            'phase_2_detail_collection': {
                'description': 'Fetch complete details for each work item',
                'tool': 'EDI-Prod-get-job-details',
                'template': detail_template,
                'note': 'Will iterate over all work item IDs from phase 1'
            }
        }
        
        return manifest
    
    def save_manifest(self):
        """Save tool call manifest to file"""
        manifest = self.create_tool_call_manifest()
        
        with open(self.tool_calls_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Tool call manifest saved to: {self.tool_calls_file}")
        return manifest
    
    def create_collection_plan(self) -> Dict[str, Any]:
        """Create detailed collection plan"""
        
        plan = {
            'overview': {
                'product': 'GLW',
                'objective': 'Fetch complete details for ALL GLW work items',
                'filters': {
                    'changeType': 'FIX (defect fixes)',
                    'status': 'NCM',
                    'createdAfter': '2026-10-06',
                    'createdBefore': '2026-11-05'
                }
            },
            'collection_phases': [
                {
                    'phase': 1,
                    'name': 'Batch Collection',
                    'duration': 'Sequential',
                    'steps': [
                        'Call EDI-Prod-filter-workitems with skip=0',
                        'Call EDI-Prod-filter-workitems with skip=50',
                        'Call EDI-Prod-filter-workitems with skip=100',
                        'Continue until batch has < 50 items',
                        'Extract all WI numbers from CSV results'
                    ],
                    'expected_results': '~165 work item IDs'
                },
                {
                    'phase': 2,
                    'name': 'Detail Collection',
                    'duration': 'Parallel (if possible) or sequential',
                    'steps': [
                        'For each work item ID from phase 1',
                        'Call EDI-Prod-get-job-details',
                        'Collect complete details including:',
                        '  - Description and notes',
                        '  - Status and metadata',
                        '  - Related items',
                        '  - Workflows and tasks',
                        '  - Attached files'
                    ],
                    'expected_results': '~165 complete work item records'
                },
                {
                    'phase': 3,
                    'name': 'Data Aggregation',
                    'steps': [
                        'Combine all work item details',
                        'Create unified JSON structure',
                        'Add summary statistics',
                        'Save to glw_complete_details_all.json'
                    ]
                }
            ],
            'output_specification': {
                'file': 'glw_complete_details_all.json',
                'format': 'JSON',
                'structure': {
                    'metadata': {
                        'product': 'GLW',
                        'totalItems': 'number',
                        'collectionDate': 'ISO timestamp',
                        'filters': 'object'
                    },
                    'workItems': 'array of work item objects',
                    'summary': {
                        'totalCollected': 'number',
                        'byStatus': 'counts by status',
                        'byArea': 'counts by area',
                        'byModule': 'counts by module'
                    }
                }
            },
            'execution_readiness': {
                'batch_params_prepared': True,
                'detail_template_prepared': True,
                'tool_manifest_created': True,
                'ready_for_execution': True,
                'next_action': 'Execute phase 1 batch collection calls'
            }
        }
        
        return plan
    
    def prepare_execution(self):
        """Prepare everything for execution"""
        
        print("=" * 80)
        print("GLW COMPLETE DETAILS COLLECTOR - PREPARATION PHASE")
        print("=" * 80)
        print()
        
        # Save tool call manifest
        manifest = self.save_manifest()
        print()
        
        # Create and save collection plan
        plan = self.create_collection_plan()
        plan_file = self.output_dir / 'glw_collection_plan.json'
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"Collection plan saved to: {plan_file}")
        print()
        
        # Show summary
        print("=" * 80)
        print("PREPARATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Total batch calls needed: {manifest['metadata']['total_batch_calls']}")
        print(f"Total detail calls needed: {manifest['metadata']['total_detail_calls']}")
        print(f"Total estimated calls: {manifest['metadata']['total_estimated_calls']}")
        print()
        print("Files created:")
        print(f"  - {self.tool_calls_file}")
        print(f"  - {plan_file}")
        print()
        print("Ready to execute tool calls in sequence")
        print()

def main():
    collector = GLWDataCollector()
    collector.prepare_execution()

if __name__ == "__main__":
    main()
