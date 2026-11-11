const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// This backend would connect to your EDI Prod MCP server
// For now, we'll create a proxy endpoint that your dashboard can call

// Configuration
const EDI_PROD_BASE_URL = 'https://ediprod.mcp.wtg.zone';

// Sample endpoint - in production, this would call EDI-Prod-filter-workitems
app.get('/api/workitems', async (req, res) => {
  try {
    const { product = 'SYS', changeType = 'FIX', top = 20, skip = 0 } = req.query;
    
    // This is where you would call your EDI Prod MCP server
    // For example:
    // const response = await callEDIProdMCP('EDI-Prod-filter-workitems', {
    //   product,
    //   changeType: [changeType],
    //   top: parseInt(top),
    //   skip: parseInt(skip)
    // });
    
    // For now returning mock data
    const mockData = [
      {
        workItemId: 'WD151292',
        summary: 'PRO: SCIM missing users leads to potential Audit failures (CSI)',
        status: 'Open',
        changeType: 'Defect Fix',
        productArea: 'Identity & Security',
        createdTime: '04-Nov-26 10:53',
        defectIntroducedWI: 'WI0015391',
        defectIntroducedCI: 'Checkin #12345',
        module: 'SCIM Service',
        relatedIncidents: 3
      }
    ];
    
    res.json({
      success: true,
      data: mockData,
      total: mockData.length
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Get single work item details
app.get('/api/workitems/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Call EDI-Prod-get-issue-details for the work item
    // const response = await callEDIProdMCP('EDI-Prod-get-issue-details', { workitemId: id });
    
    res.json({
      success: true,
      data: {
        workItemId: id,
        // ... details
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Get defect introduced information
app.get('/api/workitems/:id/defect-details', async (req, res) => {
  try {
    const { id } = req.params;
    
    // Call EDI-Prod-set-workitem-defect-details or similar
    res.json({
      success: true,
      data: {
        workItemId: id,
        introducedInCheckinTaskId: null,
        firstMissedReviewTaskId: null
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Defect Dashboard Backend running on http://localhost:${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  GET /api/workitems - List work items`);
  console.log(`  GET /api/workitems/:id - Get work item details`);
  console.log(`  GET /api/workitems/:id/defect-details - Get defect information`);
});
