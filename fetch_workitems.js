#!/usr/bin/env node

/**
 * Work Items Fetcher
 * Fetches work items from EDI-Prod MCP server and exports to JSON
 */

const fs = require('fs');
const path = require('path');

// Since we're in a constrained environment without direct MCP client,
// we'll create a manifest of what needs to be fetched
// and provide instructions for collecting this data

const config = {
  products: [
    {
      code: 'ENT',
      changeType: ['FIX'],
      createdAfter: '2026-10-06',
      batchSize: 50
    },
    {
      code: 'GLW',
      changeType: ['FIX'],
      createdAfter: '2026-10-06',
      batchSize: 50
    }
  ],
  outputFile: path.join(__dirname, 'workitems_data.json'),
  fields: [
    'workItemId',
    'summary',
    'status',
    'changeType',
    'product',
    'productArea',
    'createdTime',
    'module',
    'priority',
    'defectIntroducedWI',
    'defectIntroducedCI',
    'relatedIncidents'
  ]
};

console.log('='.repeat(60));
console.log('EDI-Prod Work Items Fetcher Configuration');
console.log('='.repeat(60));
console.log(JSON.stringify(config, null, 2));
console.log('='.repeat(60));

// Export config for potential use
module.exports = config;
