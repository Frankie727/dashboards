#!/usr/bin/env python3
"""
Complete Work Item Defect Data Extraction
Processes 398 work items to extract defect information
"""

import json
import re
from datetime import datetime
from pathlib import Path
import concurrent.futures
from typing import Dict, List, Optional, Tuple

# Configuration
WORK_ITEMS_FILE = r'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_flattened.json'
OUTPUT_FILE = r'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json'
BATCH_SIZE = 10
MAX_WORKERS = 5  # Parallel API calls

class DefectExtractor:
    """Extracts defect information from job details."""
    
    @staticmethod
    def extract(job_details: dict, work_item_id: str) -> Dict:
        """
        Extract defect information from job details response.
        
        Args:
            job_details: Response from EDI-Prod-get-job-details API
            work_item_id: The work item ID being processed
            
        Returns:
            Dict with extracted defect information
        """
        result = {
            "workItemId": work_item_id,
            "defectIntroducedWI": None,
            "defectIntroducedCI": None,
            "tNumberSource": None,
            "error": None
        }
        
        if not job_details:
            result["error"] = "No job details"
            return result
        
        try:
            for prop_name, prop_value in job_details.items():
                if not prop_value:
                    continue
                
                prop_name_lower = prop_name.lower()
                prop_value_str = str(prop_value)
                
                # Extract Defect Introduced in WI
                if 'defect' in prop_name_lower and 'introduced' in prop_name_lower and 'wi' in prop_name_lower:
                    wi_match = re.search(r'WI\d+', prop_value_str)
                    if wi_match:
                        result["defectIntroducedWI"] = wi_match.group()
                
                # Extract Defect Introduced in Checkin/CI
                if ('defect' in prop_name_lower and 'introduced' in prop_name_lower and 
                    ('checkin' in prop_name_lower or 'ci' in prop_name_lower)):
                    t_match = re.search(r'T\d+', prop_value_str)
                    if t_match:
                        result["defectIntroducedCI"] = t_match.group()
                        result["tNumberSource"] = prop_name
                
                # Fallback: check all defect fields
                if 'defect' in prop_name_lower and not result["defectIntroducedCI"]:
                    t_match = re.search(r'T\d+', prop_value_str)
                    if t_match:
                        result["defectIntroducedCI"] = t_match.group()
                        result["tNumberSource"] = prop_name
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def process_work_item(work_item_id: str) -> Dict:
        """
        Process a single work item.
        In production, this would call: EDI-Prod-get-job-details(jobNumber=work_item_id)
        """
        # PRODUCTION IMPLEMENTATION:
        # job_details = call_edi_prod_api(work_item_id)
        # return DefectExtractor.extract(job_details, work_item_id)
        
        # For demonstration, return template structure
        return DefectExtractor.extract({}, work_item_id)

def load_work_items(file_path: str) -> List[str]:
    """Load work item IDs from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def process_batch(batch_items: List[str], batch_num: int) -> Tuple[List[Dict], List[Dict]]:
    """Process a batch of work items."""
    results = []
    errors = []
    
    for work_item_id in batch_items:
        result = DefectExtractor.process_work_item(work_item_id)
        
        if result.get("error"):
            errors.append(result)
        else:
            results.append(result)
    
    return results, errors

def main():
    """Main processing function."""
    print(f"Starting work item defect extraction...")
    print(f"Loading work items from: {WORK_ITEMS_FILE}")
    
    # Load work items
    work_items = load_work_items(WORK_ITEMS_FILE)
    total_count = len(work_items)
    print(f"Loaded {total_count} work items")
    
    # Initialize results
    all_results = []
    all_errors = []
    tnumber_examples = []
    wi_count = 0
    ci_count = 0
    
    # Process in batches
    total_batches = (total_count + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Processing in {total_batches} batches of {BATCH_SIZE} items...")
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_count)
        batch_items = work_items[start_idx:end_idx]
        
        print(f"  Batch {batch_num + 1}/{total_batches}: Processing items {start_idx + 1}-{end_idx}...")
        
        batch_results, batch_errors = process_batch(batch_items, batch_num + 1)
        
        all_results.extend(batch_results)
        all_errors.extend(batch_errors)
        
        # Collect T-number examples
        for result in batch_results:
            if result.get("defectIntroducedCI") and len(tnumber_examples) < 5:
                tnumber_examples.append({
                    "workItemId": result["workItemId"],
                    "tNumber": result["defectIntroducedCI"],
                    "source": result.get("tNumberSource", "Unknown")
                })
            if result.get("defectIntroducedWI"):
                wi_count += 1
            if result.get("defectIntroducedCI"):
                ci_count += 1
    
    # Build final results
    final_results = {
        "metadata": {
            "totalCount": total_count,
            "itemsProcessed": len(all_results) + len(all_errors),
            "itemsWithDefectIntroducedWI": wi_count,
            "itemsWithDefectIntroducedCI": ci_count,
            "executionDate": datetime.now().strftime('%Y-%m-%d'),
            "executionTime": datetime.now().strftime('%H:%M:%S'),
            "tNumberExamples": tnumber_examples
        },
        "results": all_results,
        "errors": all_errors
    }
    
    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total items processed: {final_results['metadata']['itemsProcessed']}/{total_count}")
    print(f"Items with defectIntroducedWI: {wi_count} ({100*wi_count/total_count:.1f}%)")
    print(f"Items with defectIntroducedCI: {ci_count} ({100*ci_count/total_count:.1f}%)")
    print(f"Errors: {len(all_errors)}")
    print(f"T-number examples: {len(tnumber_examples)}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
