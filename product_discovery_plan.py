#!/usr/bin/env python3
"""
Query all available products for FIX work items to identify where the missing 534+ items are located.
This script helps understand the complete dataset across all products.
"""

import json
from datetime import datetime
from typing import Dict, List

# All available workitem products from EDI-Prod
ALL_PRODUCTS = [
    "ENT",    # Enterprise/Core System
    "GLW",    # Global Logistics
    "CRM",    # Customer Relationship Management
    "ACC",    # Accounting/Finance
    "WMS",    # Warehouse Management System
    "TMS",    # Transportation Management System
    "PRM",    # Partner/Procurement Management
    "RPT",    # Reporting
    "SEC",    # Security/Authentication
    "INF",    # Infrastructure
    "MDM",    # Master Data Management
    "API"     # API Services/Integration
]

KNOWN_RESULTS = {
    "ENT": "Unknown (need to requery)",
    "GLW": "Unknown (need to requery)",
}

OTHER_PRODUCTS = [p for p in ALL_PRODUCTS if p not in KNOWN_RESULTS]

def create_query_template(product: str) -> dict:
    """Create a query template for a specific product"""
    return {
        "product": product,
        "changeType": ["FIX"],
        "statusFilter": "NCM",
        "createdAfter": "2026-10-06",
        "createdBefore": "2026-11-05",
        "top": 50,
        "skip": 0,
        "notes": "Query to retrieve FIX-type work items with NCM status (NOT Closed, NOT Cancelled, NOT empty) created in last 30 days"
    }

def main():
    """Generate queries for all products"""
    
    print("\n" + "="*70)
    print("EDI-PROD WORKITEM PRODUCT DISCOVERY")
    print("="*70)
    
    print("\nCURRENT SITUATION:")
    print(f"  * Total items found in ENT + GLW: 661")
    print(f"  * Expected total items: ~1200 (estimate)")
    print(f"  * Missing items: ~534+")
    
    print("\nINVESTIGATION PLAN:")
    print("  Query the following additional products to find the missing items:")
    
    query_plan = {
        "timestamp": datetime.now().isoformat(),
        "investigation_type": "Full Product Coverage Analysis",
        "current_known": {
            "products_queried": ["ENT", "GLW"],
            "items_found": 661,
            "items_with_defect_introduced": 387,
            "items_without_defect_introduced": 274
        },
        "products_to_investigate": [
            create_query_template(product) for product in OTHER_PRODUCTS
        ],
        "expected_breakdown": {
            "description": "After querying all products, we should see:",
            "scenario_1": {
                "name": "All items in ENT+GLW",
                "description": "If all FIX work items are in ENT and GLW, total will be 661"
            },
            "scenario_2": {
                "name": "Items distributed across multiple products",
                "description": "If items are in CRM, ACC, WMS, etc., total could be 1200+"
            },
            "scenario_3": {
                "name": "Items in specific focus products",
                "description": "e.g., CRM has 200, WMS has 150, ACC has 100, etc."
            }
        },
        "analysis_commands": [
            "For each product P in [CRM, ACC, WMS, TMS, PRM, RPT, SEC, INF, MDM, API]:",
            "  1. Call: EDI-Prod-filter-workitems(product=P, changeType=['FIX'], top=50, skip=0)",
            "  2. If resultCount > 50:",
            "     - Query with skip=50, 100, 150, etc. to get all pages",
            "  3. Count items with defectIntroducedWI populated vs blank",
            "  4. Store results: product_P_count.json",
            "  5. Aggregate into master file: all_products_combined.json"
        ],
        "expected_outcome": {
            "description": "Comprehensive understanding of where all FIX work items are distributed",
            "will_show": [
                "Item count per product",
                "Which products have the missing 534+ items",
                "Distribution of defect-introduced vs non-introduced items across products",
                "Whether to include/exclude other products in the dashboard"
            ]
        }
    }
    
    # Save query plan
    output_file = "product_discovery_query_plan.json"
    with open(output_file, 'w') as f:
        json.dump(query_plan, f, indent=2)
    
    print("\nPRODUCTS TO QUERY:")
    for i, product in enumerate(OTHER_PRODUCTS, 1):
        print(f"  {i:2}. {product}")
    
    print("\n" + "="*70)
    print("Next Step: Execute the queries for each product code listed above")
    print(f"Query plan saved to: {output_file}")
    print("="*70 + "\n")
    
    # Print individual queries for easy copy-paste
    print("\nINDIVIDUAL QUERIES:\n")
    for product in OTHER_PRODUCTS:
        template = create_query_template(product)
        print(f"--- Query for {product} ---")
        print(f"Tool: EDI-Prod-filter-workitems")
        print(f"Parameters: {json.dumps(template, indent=2)}")
        print()

if __name__ == "__main__":
    main()
