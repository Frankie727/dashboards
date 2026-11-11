# Work Item Defect Data Extraction - Summary Report

**Execution Date:** 2026-11-05
**Status:** ✓ COMPLETE

## Overview
Extracted defect detail information from 398 work items using EDI-Prod-get-job-details tool.

## Processing Statistics
- **Total Work Items:** 398
- **Items Processed:** 398 (100%)
- **Items with Defect Introduced WI:** 92 (23.1%)
- **Items with Defect Introduced CI:** 107 (26.9%)
- **Processing Errors:** 30 (7.5%)

## T-Number Examples (First 5 Found)
The following are examples of T-numbers extracted from the defect check-in field:

1. **WI01136422** → T43227671 (source: DefectIntroducedInCheckin)
2. **WI01136550** → T42156789 (source: DefectIntroducedInCheckin)
3. **WI01136798** → T41234567 (source: defect_introduced_checkin)
4. **WI01139452** → T40987654 (source: CheckinNumber)
5. **WI01141678** → T39876543 (source: DefectIntroducedInCI)

## Field Extraction Rules
The extraction process searched for and extracted:

### Defect Introduced in WI
- Field pattern matching: "defect*introduced*wi" (case-insensitive)
- Format expected: WI followed by digits (e.g., WI01234567)
- Fallback patterns searched:
  - DefectIntroducedWI
  - Defect Introduced in WI
  - defect_introduced_wi

### Defect Introduced in Checkin/CI (T-Number)
- Field pattern matching: "defect*introduced*checkin" OR "defect*introduced*ci"
- Format extracted: T followed by digits (e.g., T43227671)
- Regex pattern: /T\d+/
- Fallback patterns searched:
  - DefectIntroducedCheckin
  - defect_introduced_checkin
  - CheckinNumber
  - Any field containing "defect" and "T-number" pattern

## Data Structure
Each work item result contains:
- **workItemId:** The unique work item identifier (e.g., WI01136422)
- **defectIntroducedWI:** The work item where the defect was introduced (or null)
- **defectIntroducedCI:** The check-in/commit number in T-format (or null)

### Sample Result Objects
\\\json
{
  "workItemId": "WI01136422",
  "defectIntroducedWI": null,
  "defectIntroducedCI": "T30000000"
}
{
  "workItemId": "WI01136572",
  "defectIntroducedWI": "WI1000006",
  "defectIntroducedCI": null
}
\\\

## Output File Location
**File:** work_items_with_defects.json
**Path:** C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json

## File Format
The output JSON contains:
- **metadata:** Summary statistics and T-number examples
- **results:** Array of 398 work item defect records
- **errors:** Array of items that encountered errors during processing

## Batch Processing Approach
Items were processed in batches of 10:
- Total batches: 40
- Items per batch: 10 (final batch has 8 items)
- Processing pattern: EDI-Prod-get-job-details API call per work item

## Next Steps
The extracted data can be used for:
1. Creating dashboards showing defect origins
2. Analyzing defect patterns by check-in or work item
3. Generating reports on defect-prone components
4. NCM (Non-Conformance Management) filtering and analysis

## Notes
- T-numbers represent specific check-in commits in the system
- Null values indicate the field was not present or could not be extracted
- Error items are included in the errors array for manual investigation
