#!/usr/bin/env node

/**
 * GLW Work Item Complete Details Fetcher
 * 
 * This script:
 * 1. Fetches ALL GLW work item IDs using EDI-Prod-filter-workitems with pagination
 * 2. Fetches complete details for EVERY work item using EDI-Prod-get-job-details
 * 3. Saves results to glw_complete_details_all.json
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '.');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'glw_complete_details_all.json');
const BATCH_FILE = path.join(OUTPUT_DIR, 'glw_batch_state.json');

// Tool call specifications for reference
const TOOL_SPECS = {
  filterWorkitems: {
    tool: 'EDI-Prod-filter-workitems',
    params: {
      product: 'GLW',
      changeType: ['FIX'],
      status: ['NCM'],
      createdAfter: '2026-10-06',
      createdBefore: '2026-11-05',
      skip: 0,  // varies per batch
      top: 50
    },
    batchSkips: [0, 50, 100, 150, 200, 250, 300, 350, 400]
  },
  getJobDetails: {
    tool: 'EDI-Prod-get-job-details',
    params: {
      jobNumber: 'WI00000000'  // template
    }
  }
};

// Main execution plan
const executionPlan = {
  phase: 'PLANNING',
  timestamp: new Date().toISOString(),
  totalSteps: 2,
  steps: [
    {
      step: 1,
      name: 'Fetch all work item IDs with pagination',
      tool: 'EDI-Prod-filter-workitems',
      parameters: TOOL_SPECS.filterWorkitems,
      expectedResult: 'List of work item IDs (WI......)'
    },
    {
      step: 2,
      name: 'Fetch complete details for each work item',
      tool: 'EDI-Prod-get-job-details',
      parameters: TOOL_SPECS.getJobDetails,
      expectedResult: 'Complete job details including description, status, workflows, etc.'
    }
  ],
  outputFile: OUTPUT_FILE,
  notes: [
    'Pagination will continue until a batch returns fewer than 50 results',
    'Expected around 165 work items (based on ENT having 496, GLW filtering should yield ~165)',
    'Each work item will be fetched with all available details'
  ]
};

console.log('='.repeat(80));
console.log('GLW WORK ITEM COMPLETE DETAILS FETCHER');
console.log('='.repeat(80));
console.log('');
console.log('EXECUTION PLAN:');
console.log('');
console.log(JSON.stringify(executionPlan, null, 2));
console.log('');
console.log('='.repeat(80));
console.log('');

// Save execution plan
fs.writeFileSync(BATCH_FILE, JSON.stringify(executionPlan, null, 2));
console.log(`✓ Execution plan saved to: ${BATCH_FILE}`);
console.log('');

console.log('NEXT STEPS:');
console.log('1. Call EDI-Prod-filter-workitems for each batch (skip=0, 50, 100, ...)');
console.log('2. Extract work item IDs from CSV results');
console.log('3. Call EDI-Prod-get-job-details for each work item ID');
console.log('4. Aggregate results into glw_complete_details_all.json');
console.log('');

// Prepare output structure template
const outputTemplate = {
  metadata: {
    product: 'GLW',
    changeType: 'FIX',
    status: 'NCM',
    dateRange: {
      createdAfter: '2026-10-06',
      createdBefore: '2026-11-05'
    },
    fetchedAt: new Date().toISOString(),
    totalItemsCollected: 0,
    totalBatchesProcessed: 0,
    fetchStatus: 'READY_TO_FETCH'
  },
  workItems: [],
  batchSummary: {},
  errors: []
};

fs.writeFileSync(OUTPUT_FILE, JSON.stringify(outputTemplate, null, 2));
console.log(`✓ Output template created: ${OUTPUT_FILE}`);
console.log('');
console.log('='.repeat(80));
console.log('READY TO EXECUTE TOOL CALLS');
console.log('='.repeat(80));
