#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

# Initialize the complete dashboard structure
dashboard = {
    "meta": {
        "timestamp": datetime.now().isoformat(timespec="milliseconds") + "+11:00",
        "totalCount": 300,
        "itemsWithDefectIntroduced": 0,
        "itemsWithoutDefectIntroduced": 0,
        "queryParams": {
            "changeType": "FIX",
            "products": ["ENT", "GLW"],
            "statusFilter": "NOT CLS AND NOT CAN AND NOT empty",
            "createdDateRange": "2026-10-06 to 2026-11-05"
        }
    },
    "data": []
}

# Load work item mapping
with open("batch_config.json") as f:
    batch_config = json.load(f)

work_items = batch_config["workItems"]
id_to_product = batch_config["idToProduct"]

print(f"Total work items to process: {len(work_items)}")
print(f"Dashboard structure prepared")

# Save template
with open("dashboard_structure.json", "w") as f:
    json.dump(dashboard, f, indent=2)

print("Template saved to dashboard_structure.json")

# Create a list file for tracking
work_item_list = []
for wi in work_items:
    work_item_list.append({
        "id": wi,
        "product": id_to_product[wi],
        "status": "pending",
        "data": None
    })

with open("work_item_tracking.json", "w") as f:
    json.dump(work_item_list, f, indent=2)

print(f"Created tracking file with {len(work_item_list)} items")
