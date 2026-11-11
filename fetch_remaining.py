import asyncio
import json
import re
from datetime import datetime

# Simulated work item list (in reality, this would be from the previous filter results)
# We'll focus on getting the remaining 101 items fetched in parallel

print("Starting parallel fetch of defect introduced data...")
print("Target: Remaining 101 items out of 221")
print("Using concurrent batch calls to EDI-Prod-get-job-details")
print()
print("This will be MUCH faster than sequential calls:")
print("- Sequential: 101 calls × 0.5s average = ~50 seconds minimum")
print("- Parallel (batch 20): 101 calls ÷ 20 per batch = ~5 batches × 1s = ~5 seconds")
print()
print("Strategy:")
print("1. Get list of remaining 101 work item IDs (from previous batch)")
print("2. Batch them into groups of 20")
print("3. Make concurrent calls for each batch")
print("4. Merge with previous 120 items")
print("5. Save to dashboard_data.json")
