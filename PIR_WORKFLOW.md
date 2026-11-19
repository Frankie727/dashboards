# PIR Generation Workflow - Internal Major Incidents

This document describes the complete workflow for generating Internal Post Incident Review (PIR) documents for Major Incidents using the automated Teams chat parsing and PIR generation system.

## Overview

The PIR generation system consists of three components:

1. **Teams Chat Parser** (`teams-pir-parser.py`) - Extracts and consolidates incident data from Teams chat exports
2. **Internal PIR Prompt** (`internal-pir-generator.prompt.md`) - AI-assisted prompt for generating comprehensive internal PIRs
3. **Workflow Guide** (this document) - Step-by-step instructions for using the system

## Quick Start

### Step 1: Gather Incident Data from Teams Chat

**Option A: Export Teams Chat as JSON**
1. In Teams, open the incident response channel
2. Use Teams' export feature to download chat history (usually available via channel settings or message export)
3. Save as `incident_<ID>.json` in the `data/incidents/` folder

**Option B: Manual Export - Copy/Paste Relevant Messages**
1. Manually select and copy key incident messages from Teams
2. Create a JSON file with this structure:
```json
{
  "messages": [
    {
      "timestamp": "2024-11-19T10:30:00Z",
      "from": "Support Team",
      "body": "Incident declared - Customs messages not sending"
    },
    {
      "timestamp": "2024-11-19T10:45:00Z",
      "from": "Engineer A",
      "body": "Investigating database performance issues"
    }
  ]
}
```

### Step 2: Parse Timeline Events (Automatic Consolidation)

Run the parser to extract and consolidate timeline events:

```bash
# Using Python
python scripts/teams-pir-parser.py --input data/incidents/incident_ING00000526.json --output data/incidents/incident_ING00000526_parsed.json

# Or interactively in Python:
from scripts.teams_pir_parser import TeamsChatsToTimelineParser
parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
events = parser.parse_teams_json_export('data/incidents/incident_ING00000526.json')
```

The parser will:
- Extract all messages from Teams chat
- Classify events by type (incident_start, investigation, mitigation, resolution, etc.)
- Assign severity levels (critical, important, info)
- Consolidate to max 15 events, keeping critical milestones
- Remove redundant or low-value updates

### Step 3: Gather Remaining Incident Details

While the timeline is being prepared, gather the following information:

**Incident Metadata:**
- Incident ID (e.g., ING00000526)
- Incident Title
- Start Date (date only, no time)
- End Date (date only, or "Ongoing")

**Impact Details:**
- Business impact statement (what customers/business experienced)
- Affected services (list)
- Affected customers/regions
- Estimated customer impact (number of customers, transactions, etc.)

**Root Cause:**
- Clear explanation of root cause
- Category: Configuration / Deployment / Resource / Bug / External

**Resolution:**
- Immediate actions taken to restore service
- Permanent fix (if different from immediate mitigation)
- Teams involved

**Prevention:**
- List of preventative measures being implemented
- For each: what it does, who owns it, expected completion date

### Step 4: Create Structured Incident Data

Create a JSON file with all incident details:

```json
{
  "incident_id": "ING00000526",
  "incident_title": "xT Customs messages not sending/receiving",
  "start_time": "2024-11-19",
  "end_time": "2024-11-19",
  "business_impact": "Customs-related messages unable to send or receive in IT, IE, CH, ES regions",
  "affected_services": ["Customs Integration Service", "Message Queue Service"],
  "affected_customers": "Multiple customers in EMEA region",
  "root_cause": "Database routine running with settings optimized for only one of multiple calling processes",
  "root_cause_category": "Configuration",
  "timeline_events": [
    {
      "timestamp": "2024-11-19 10:30",
      "description": "Incident declared - Customs message delivery failures reported"
    },
    {
      "timestamp": "2024-11-19 10:50",
      "description": "Root cause identified - database configuration issue"
    },
    {
      "timestamp": "2024-11-19 11:05",
      "description": "Temporary mitigation applied - processes restarted"
    },
    {
      "timestamp": "2024-11-19 11:30",
      "description": "Service restored - all messages clearing normally"
    }
  ],
  "immediate_fix": "Restarted affected processes and cleared message backlog",
  "permanent_fix": "Update database routine to use process-specific configuration profiles with validation",
  "teams_involved": ["Database Performance Team", "Customs Integration Team", "Support"],
  "prevention_measures": [
    "Implement pre-deployment configuration validation checks",
    "Add automated alerts for unusual process performance patterns"
  ],
  "customer_communication_sent": true,
  "notes": "Highlighted importance of process-specific database tuning"
}
```

### Step 5: Generate Internal PIR Document

Use the Internal PIR Generator prompt with your incident data:

**Option A: Using Copilot in VS Code**
1. Open `.github/prompts/internal-pir-generator.prompt.md`
2. Use the prompt with Copilot, providing your incident JSON data
3. Copilot will generate a comprehensive internal PIR

**Option B: Command Line (Python + Claude API)**
```bash
python scripts/generate_pir.py \
  --data data/incidents/incident_ING00000526.json \
  --prompt .github/prompts/internal-pir-generator.prompt.md \
  --output reports/Internal_PIR_ING00000526.md
```

**Option C: Manual Process**
1. Copy the incident JSON data
2. Paste into the PIR generator prompt
3. Provide to AI tool (Claude, ChatGPT, etc.)
4. Review and refine the output

### Step 6: Review and Finalize

The generated PIR will include:
- Executive Summary
- Incident Details
- Consolidated Timeline (10-15 critical events)
- Root Cause Analysis
- Resolution Details
- Prevention Measures
- Teams Involved

**Review checklist:**
- [ ] All dates are correct (date only, no times)
- [ ] Timeline includes only 10-15 critical events
- [ ] Root cause explanation is clear and accurate
- [ ] Prevention measures are specific and actionable
- [ ] No sensitive internal details exposed
- [ ] Language is professional and appropriate for internal audience
- [ ] All team names and roles are correct
- [ ] Business impact statement is accurate

### Step 7: Publish and Track

1. Save final PIR as `Internal_PIR_<IncidentID>.md` in `reports/` folder
2. Add to incident tracking system/SharePoint
3. Create follow-up tasks for prevention measures
4. Set reminders for completion tracking

## Example: Full Workflow

Here's a complete example for incident ING00000526:

### Input from Teams Chat (Partial Export)
```
Support (10:30): @channel Incident declared - Customs message delivery failures reported in xT for IT region
Engineer A (10:35): Investigating... checking database logs
Engineer B (10:45): Found it - database routine is running with wrong configuration
Engineer A (10:50): Root cause confirmed - settings optimized for only one of the calling processes
Engineer A (11:00): Applying temporary fix - restarting the affected processes
Engineer B (11:10): Message queue backlog detected - 50K messages queued
Support (11:20): Queue clearing now that processes are restarted
Engineer A (11:30): ✓ All messages clearing normally - incident resolved
Support (11:35): Customer communication being sent to affected accounts
```

### Structured Data Created
```json
{
  "incident_id": "ING00000526",
  "incident_title": "xT Customs messages not sending/receiving",
  "start_time": "2024-11-19",
  "end_time": "2024-11-19",
  "business_impact": "Customs-related messages unable to send or receive in IT, IE, CH, ES regions, affecting cross-border operations",
  "affected_services": ["Customs Integration Service", "Message Queue Service"],
  "affected_customers": "Multiple customers in EMEA region",
  "root_cause": "A database routine shared by several integration processes had been configured with database settings optimized for only one process, causing other processes to experience performance degradation",
  "root_cause_category": "Configuration",
  "timeline_events": [
    {"timestamp": "2024-11-19 10:30", "description": "Incident declared - Customs message delivery failures reported in IT region"},
    {"timestamp": "2024-11-19 10:45", "description": "Database issue identified - routine configuration not matching all calling processes"},
    {"timestamp": "2024-11-19 11:05", "description": "Temporary mitigation applied - affected processes restarted"},
    {"timestamp": "2024-11-19 11:20", "description": "Message backlog detected - 50K messages in queue"},
    {"timestamp": "2024-11-19 11:30", "description": "Service restored - message queue clearing normally"},
    {"timestamp": "2024-11-19 11:35", "description": "Customer communication sent to affected accounts"}
  ],
  "immediate_fix": "Restarted the database routine and affected integration processes. This immediately restored normal throughput and allowed the queued messages to process.",
  "permanent_fix": "Implement process-specific configuration profiles for the database routine, with pre-deployment validation to prevent misconfiguration",
  "teams_involved": ["Database Performance Team", "Customs Integration Team", "Support Operations"],
  "prevention_measures": [
    "Implement pre-deployment configuration validation checks for all database routines",
    "Add automated monitoring to detect similar performance degradation patterns",
    "Create configuration documentation with process-specific requirements"
  ],
  "customer_communication_sent": true,
  "notes": "Incident highlighted the need for more granular configuration management. All affected customers in IT, IE, CH, ES regions were notified with resolution details."
}
```

### Generated Internal PIR (Excerpt)

```markdown
---
incident_id: ING00000526
title: xT Customs messages not sending/receiving
date_range: 19 November 2024
status: Resolved
---

# Internal Post Incident Review

## Executive Summary

On 19 November, Customs-related message delivery failures affected multiple customers in EMEA regions (IT, IE, CH, ES). Investigation identified that a database routine used by several integration processes had been configured with settings optimized for only one of them, causing the others to experience performance degradation and creating a backlog of approximately 50,000 messages. The issue was resolved on the same day through process restart and configuration corrections. All affected customers were notified.

## Incident Details

#### Incident Information
- **Incident ID**: ING00000526
- **Title**: xT Customs messages not sending/receiving
- **Service(s) Affected**: Customs Integration Service, Message Queue Service
- **Start Time**: 19 November
- **End Time**: 19 November
- **Customer Impact**: Multiple customers in EMEA region (IT, IE, CH, ES)

[... continues with full PIR structure ...]
```

## Best Practices

### Timeline Consolidation
- Keep 10-15 critical events maximum
- Include: incident declaration, root cause discovery, major actions, resolution
- Remove: routine updates, minor checks that led nowhere, duplicate reports
- Use clear dates (19 November) without specific times

### Teams Chat Parsing
- Export full chat history for the incident response channel
- Parser will automatically classify and consolidate events
- Review consolidated timeline - may need manual adjustments for context
- Look for key decision points and transitions

### Incident Data Gathering
- Involve the incident commander/lead engineer in documenting root cause
- Get specific details about business impact (not just "some customers affected")
- Ensure prevention measures are specific, measurable, and owned
- Document estimated customer impact (number of customers, transactions, duration)

### Language Guidelines
- Use "experienced performance degradation" not "got slow"
- Use "multiple" or "several" for internal counts (don't expose exact numbers)
- Keep professional tone suitable for internal engineering/management audience
- Avoid blame language - focus on systems and processes
- Provide technical depth appropriate for internal audience (more than customer-facing PIR)

## Troubleshooting

### "Too many timeline events"
- Parser consolidates to max 15 by default
- Run parser again with `--max-events 10` for stricter consolidation
- Manually remove low-value updates from JSON

### "Missing timeline events"
- Ensure Teams chat export includes all messages
- Check message timestamps are in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- Manually add critical events if parsing missed them

### "Generated PIR looks incomplete"
- Verify all input JSON fields are populated
- Review prompt template to ensure all required sections are included
- Run generator again with more detailed input data

## File Structure

```
dashboards/
├── .github/prompts/
│   ├── internal-pir-generator.prompt.md    # This prompt template
│   └── pir-generator.prompt.md              # Customer-facing PIR prompt
├── scripts/
│   ├── teams-pir-parser.py                 # Teams chat parser
│   └── generate_pir.py                     # PIR generation script (optional)
├── data/
│   └── incidents/
│       ├── incident_ING00000526.json       # Teams chat export
│       └── incident_ING00000526_parsed.json # Parsed timeline output
└── reports/
    ├── Internal_PIR_ING00000526.md         # Generated internal PIR
    └── ...
```

## References

- Internal PIR Generator Prompt: `.github/prompts/internal-pir-generator.prompt.md`
- Teams Chat Parser: `scripts/teams-pir-parser.py`
- Example Incident: `data/incidents/incident_ING00000526_example.json`

## Support

For issues with:
- **Timeline consolidation**: Review `teams-pir-parser.py` - adjust severity rules or max event count
- **Generated content**: Check PIR prompt template for missing sections or guidance
- **Teams chat parsing**: Ensure export format matches expected schema
