# EDI-Prod Job Details Collection Plan

## Work Items to Retrieve (10 total)
1. WI01152234
2. WI01152163
3. WI01152157
4. WI01152123
5. WI01152119
6. WI01152084
7. WI01152037
8. WI01151930
9. WI01151929
10. WI01151864

## Target Fields to Extract
1. **priority** - Work item priority level
2. **defectIntroducedWI** - Defect introduced by workitem ID
3. **defectIntroducedCI** - Defect introduced by CI/build identifier
4. **relatedIncidents** - List of related incident numbers

## Additional Information to Note
- Complete JSON structure returned by the tool
- Presence of "Related Workitems" or "Related Issues" sections
- Overall response structure and schema

## Tool Details
- **Tool Name**: EDI-Prod-get-job-details
- **Parameter**: jobNumber (string, format: WI\d{5,})
- **Response Type**: Comprehensive details including metadata, description, related items, conversation history, attachments

## Analysis Required
1. Which of the 4 target fields appear in the responses
2. How to extract each field (path/location in JSON)
3. Whether this tool provides all required information
4. Any alternative tools needed for missing data

## Expected Output Format
```json
{
  "fieldAvailability": {
    "priority": {
      "found": true/false,
      "locations": ["path.to.field"],
      "example": "value"
    },
    "defectIntroducedWI": { ... },
    "defectIntroducedCI": { ... },
    "relatedIncidents": { ... }
  },
  "workItemResults": {
    "WI01152234": { ...full response... },
    ...
  },
  "extractionGuide": { ... },
  "conclusionAndRecommendations": "..."
}
```

## Status
- Awaiting tool invocation through proper MCP interface
