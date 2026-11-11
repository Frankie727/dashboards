#!/usr/bin/env python3
"""
Batch processor for fetching 300 work item details.
This creates the commands needed to fetch all items and then builds the final dashboard.
"""

import json
from pathlib import Path

def create_batch_commands():
    """Create list of all work items that need to be fetched"""
    
    # Load work item IDs
    with open("workitems_filtered_final_result.json") as f:
        data = json.load(f)
    
    all_items = []
    
    # Add ENT items
    for wi in data["ent"]["items"]:
        all_items.append({"id": wi, "product": "ENT"})
    
    # Add GLW items  
    for wi in data["glw"]["items"]:
        all_items.append({"id": wi, "product": "GLW"})
    
    print(f"Total items: {len(all_items)}")
    print(f"ENT: {len(data['ent']['items'])}")
    print(f"GLW: {len(data['glw']['items'])}")
    
    # Create batch lists (50 items per batch)
    batch_size = 50
    batches = []
    for i in range(0, len(all_items), batch_size):
        batch = all_items[i:i+batch_size]
        batches.append(batch)
    
    print(f"\nCreated {len(batches)} batches of {batch_size} items each")
    print(f"Batch 1: {len(batches[0])} items")
    print(f"Batch 2: {len(batches[1])} items")
    print(f"Last batch: {len(batches[-1])} items")
    
    # Save batches
    with open("work_items_batches.json", "w") as f:
        json.dump(batches, f, indent=2)
    
    return batches

if __name__ == "__main__":
    batches = create_batch_commands()
    print("\nBatches created and saved to work_items_batches.json")
