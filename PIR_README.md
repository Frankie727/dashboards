# Internal PIR Generation System for Major Incidents

This system automates the generation of Internal Post Incident Review (PIR) documents for Major Incidents (CR1/CR2 classification). It includes automated Teams chat parsing, timeline consolidation, and comprehensive PIR generation.

## Overview

The system consists of three main components:

### 1. **Teams Chat Parser** (`scripts/teams-pir-parser.py`)
Automatically extracts incident data from Teams chat exports and consolidates timeline events.

**Features:**
- Parses Teams chat JSON exports
- Classifies events by type (incident_start, investigation, mitigation, resolution, etc.)
- Assigns severity levels (critical, important, info)
- Consolidates timeline to max 10-15 critical milestone events
- Removes redundant or low-value updates automatically
- Outputs structured incident data

**Key Classes:**
- `TimelineEvent` - Represents a single timeline event
- `IncidentData` - Complete incident data structure
- `TeamsChatsToTimelineParser` - Parses and consolidates Teams exports
- `IncidentDataExtractor` - Extracts and formats incident data

### 2. **Internal PIR Generator Prompt** (`.github/prompts/internal-pir-generator.prompt.md`)
AI-assisted prompt template for generating comprehensive internal PIR documents.

**Includes:**
- Detailed instructions for comprehensive internal PIR
- Format guidelines for 10+ sections
- Tone and language guidelines (professional, technical, internal audience)
- Example input data structure
- Output formatting requirements

**Key Sections:**
- Executive Summary
- Incident Details (ID, services, timing, impact)
- Business Impact Statement
- Root Cause Analysis
- Timeline History (max 10-15 events)
- Resolution Details
- Prevention Measures (with ownership/tracking)
- Teams Involved
- Lessons Learned (optional)

### 3. **Workflow Guide** (`PIR_WORKFLOW.md`)
Step-by-step instructions for using the system end-to-end.

**Covers:**
- Extracting incident data from Teams
- Parsing timeline events
- Gathering remaining incident details
- Generating PIR documents
- Review and finalization
- File structure and best practices

## Quick Start

### Setup

```bash
# No dependencies required - pure Python standard library
# Supports Python 3.8+
python --version  # Verify Python 3.8+
```

### Basic Usage

#### Step 1: Export Teams Chat
1. In Teams, open your incident response channel
2. Export or copy chat messages to JSON file
3. Save as `data/incidents/incident_<ID>.json`

Expected format:
```json
{
  "messages": [
    {
      "timestamp": "2024-11-19T10:30:00Z",
      "from": "Person Name",
      "body": "Message text"
    }
  ]
}
```

#### Step 2: Parse and Consolidate Timeline
```python
from scripts.teams_pir_parser import TeamsChatsToTimelineParser

parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
events = parser.parse_teams_json_export('data/incidents/incident_ING00000526.json')
consolidated = parser.consolidate_timeline(events)

for event in consolidated:
    print(f"[{event.timestamp}] {event.event_type}: {event.description}")
```

#### Step 3: Gather Incident Data
Create a JSON file with complete incident information:
```json
{
  "incident_id": "ING00000526",
  "incident_title": "xT Customs messages not sending/receiving",
  "start_time": "2024-11-19",
  "end_time": "2024-11-19",
  "business_impact": "...",
  "affected_services": [...],
  "root_cause": "...",
  "root_cause_category": "Configuration",
  "timeline_events": [...],
  "immediate_fix": "...",
  "permanent_fix": "...",
  "teams_involved": [...],
  "prevention_measures": [...],
  "customer_communication_sent": true
}
```

See `data/incidents/incident_ING00000526_example.json` for a complete example.

#### Step 4: Generate PIR Document
Use the Internal PIR Generator prompt with your incident data:

**Option A - In VS Code with Copilot:**
1. Open `.github/prompts/internal-pir-generator.prompt.md`
2. Use Copilot chat
3. Provide your incident JSON data
4. Copilot generates comprehensive internal PIR

**Option B - Any AI Tool:**
1. Copy the prompt from `.github/prompts/internal-pir-generator.prompt.md`
2. Add your incident JSON data
3. Paste into Claude, ChatGPT, or other AI tool
4. AI generates the PIR

#### Step 5: Review and Publish
1. Review generated PIR against quality checklist
2. Save as `reports/Internal_PIR_<IncidentID>.md`
3. Add to incident tracking system
4. Create follow-up tasks for prevention measures

## File Structure

```
dashboards/
├── .github/
│   └── prompts/
│       ├── internal-pir-generator.prompt.md   # Internal PIR prompt
│       └── pir-generator.prompt.md             # Customer-facing PIR prompt
├── scripts/
│   └── teams-pir-parser.py                    # Teams chat parser & utilities
├── data/
│   └── incidents/
│       ├── incident_ING00000526_teams_export.json      # Teams chat export (example)
│       ├── incident_ING00000526_example.json           # Complete incident data (example)
│       └── [other incident files]
├── reports/
│   └── [Internal PIR documents generated]
├── PIR_WORKFLOW.md                            # Detailed workflow guide
└── README.md                                  # This file
```

## Examples

### Example Files Included

1. **Teams Chat Export**: `data/incidents/incident_ING00000526_teams_export.json`
   - Shows expected Teams chat format
   - 21 messages from incident response discussion

2. **Incident Data**: `data/incidents/incident_ING00000526_example.json`
   - Complete incident information
   - Structured timeline with 10 key events
   - Prevention measures with ownership
   - Outstanding action items

### Example Workflow

```
Teams Chat Export
     ↓
Teams Chat Parser
     ↓
Consolidated Timeline (10-15 events)
     ↓
Gather Additional Details
     ↓
Create Incident Data JSON
     ↓
Internal PIR Generator Prompt
     ↓
AI Tool (Claude/ChatGPT)
     ↓
Internal PIR Document
     ↓
Review & Publish
```

## Key Features

### Automatic Timeline Consolidation

The parser automatically reduces timelines to maximum 10-15 critical events:

**Strategy:**
1. Classify all messages by event type
2. Assign severity levels (1=critical, 2=important, 3=info)
3. Keep all critical severity events
4. Add important events if space available
5. Remove low-value informational events
6. If still over limit, evenly space remaining events

**Result:** Clean, readable timeline focusing on decision points and major milestones

### Smart Event Classification

Automatic classification of Teams messages:

| Event Type | Keywords | Severity |
|-----------|----------|----------|
| incident_start | "incident declared", "critical issue", "outage" | 1 (Critical) |
| investigation | "investigating", "found", "identified root cause" | 2 (Important) |
| mitigation | "workaround", "applied fix", "restarted" | 1 (Critical) |
| resolution | "resolved", "fixed", "restored", "back to normal" | 1 (Critical) |
| communication | "customer communication", "notification sent" | 2 (Important) |
| update | "status", "ongoing", "working on" | 3 (Info) |

### Language & Tone Guidelines

The system enforces professional language suitable for internal technical audience:

**Preferred Terms:**
- "experienced performance degradation" (not "got slow")
- "experienced issues" (not "struggled")
- "increased processing time" (not "was sluggish")
- "multiple" or "several" (not specific numbers like "14")

**Formatting:**
- Dates only, no specific times (e.g., "19 November" not "10:30 SAST")
- Professional, accountable tone
- Technical depth appropriate for engineering audience
- Clear, actionable prevention measures

## Prevention Measures Format

Each prevention measure should include:

```json
{
  "action": "Specific, measurable action to implement",
  "target": "What aspect of incident this prevents",
  "owner": "Team responsible for implementation",
  "expected_completion": "YYYY-MM-DD",
  "status": "Planned | In Progress | Completed"
}
```

**Good Example:**
```json
{
  "action": "Implement pre-deployment configuration validation checks for database routines",
  "target": "Prevents misconfiguration from being deployed to production",
  "owner": "Database Performance Team",
  "expected_completion": "2024-11-30",
  "status": "In Progress"
}
```

**Avoid:**
- Vague actions: "Improve monitoring" ❌ → "Add performance degradation alerts" ✓
- Missing ownership
- No target/completion dates
- Too broad scope

## Best Practices

### Teams Chat Export
- Export full incident response channel history
- Include timestamps and author names
- Ensure messages are in chronological order
- Include all significant communications

### Timeline Consolidation
- Maximum 10-15 events keeps PIR focused
- Include: declaration, root cause discovery, major actions, resolution
- Remove: routine updates, dead-end investigations, minor status checks
- Use clear dates without excessive time precision

### Incident Data Gathering
- Involve incident commander and lead engineer
- Get specific, quantifiable impact (not just "some customers")
- Ensure root cause explanation is clear and accurate
- Make prevention measures specific and measurable
- Document estimated customer impact (count, regions, duration)

### Language & Communication
- Use professional technical terminology
- Generalize internal implementation details
- Provide sufficient depth for technical audience
- Avoid blame - focus on systems and processes
- Keep dates simple (date only, no specific times)

### Prevention Measures
- Each measure should be specific and actionable
- Include clear ownership and completion dates
- Track progress and status
- Create follow-up tasks for all outstanding items
- Schedule retrospective/lessons learned session

## Troubleshooting

### "Too many timeline events in generated PIR"
1. Run parser with stricter threshold: `--max-events 10`
2. Manually remove low-value events from JSON
3. Focus on critical milestones only

### "Generated PIR seems incomplete"
1. Verify all JSON input fields are populated
2. Check prompt template includes all required sections
3. Review input data for missing information
4. Run generator again with more detailed input

### "Timeline events out of order"
1. Ensure timestamps are in ISO format: `YYYY-MM-DDTHH:MM:SSZ`
2. Parser will sort events automatically
3. If manual timeline, sort by timestamp before input

### "Event classification seems wrong"
1. Review keyword lists in `teams-pir-parser.py`
2. Adjust severity levels in `_calculate_severity()`
3. For one-off issues, manually set event type in JSON

## Extending the System

### Adding Custom Event Types

Edit `TeamsChatsToTimelineParser.CRITICAL_KEYWORDS`:

```python
CRITICAL_KEYWORDS = {
    'incident_start': [...],
    'investigation': [...],
    'custom_event_type': [
        'keyword1', 'keyword2', 'keyword3'
    ],
    ...
}
```

### Adjusting Timeline Consolidation

Change `max_timeline_entries` parameter:

```python
parser = TeamsChatsToTimelineParser(max_timeline_entries=20)  # For longer timelines
```

### Customizing PIR Sections

Edit `.github/prompts/internal-pir-generator.prompt.md` to:
- Add new sections
- Adjust guidelines
- Modify tone/language
- Change format requirements

## References

- **PIR Workflow Guide**: See `PIR_WORKFLOW.md` for detailed step-by-step instructions
- **Example Files**: 
  - Teams export: `data/incidents/incident_ING00000526_teams_export.json`
  - Incident data: `data/incidents/incident_ING00000526_example.json`
- **Parser Source**: `scripts/teams-pir-parser.py`
- **PIR Prompt**: `.github/prompts/internal-pir-generator.prompt.md`

## Support

### For Issues With:

**Timeline Consolidation:**
- Review `TeamsChatsToTimelineParser` logic
- Adjust severity levels or keywords
- Change max event count
- Manually curate critical events

**Generated Content:**
- Review prompt template for missing sections
- Ensure input JSON has all required fields
- Check for specific guidance in prompt

**Teams Chat Parsing:**
- Verify export format matches expected schema
- Check timestamps are valid ISO format
- Ensure message bodies are non-empty

## Related Documents

- **Customer-facing PIR Prompt**: `.github/prompts/pir-generator.prompt.md`
- **Incident Workflow**: `PIR_WORKFLOW.md`
- **Example Incident Data**: `data/incidents/incident_ING00000526_example.json`

## License

Internal use only - CargoWise / Leonardo

## Version

- **Version**: 1.0
- **Last Updated**: November 2024
- **Status**: Active

---

**Next Steps:**
1. Review the example files in `data/incidents/`
2. Follow the workflow in `PIR_WORKFLOW.md`
3. Use the parser on your Teams chat export
4. Generate your first internal PIR document
