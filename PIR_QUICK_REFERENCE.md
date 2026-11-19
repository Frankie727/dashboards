# PIR Generation - Quick Reference Card

## 🚀 Quick Start (3 Steps)

### Step 1: Export Teams Chat
```json
Save Teams messages as JSON in: data/incidents/incident_<ID>.json
{
  "messages": [
    {"timestamp": "2024-11-19T10:30:00Z", "from": "Support", "body": "Incident declared"},
    ...
  ]
}
```

### Step 2: Parse Timeline
```python
from scripts.teams_pir_parser import TeamsChatsToTimelineParser
parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
events = parser.parse_teams_json_export('data/incidents/incident_ING00000526.json')
```

### Step 3: Generate PIR
1. Gather incident data (business impact, root cause, prevention measures)
2. Use `.github/prompts/internal-pir-generator.prompt.md` with Copilot/Claude
3. AI generates comprehensive internal PIR document
4. Save to `reports/Internal_PIR_<IncidentID>.md`

---

## 📋 Incident Data Template

```json
{
  "incident_id": "ING00000526",
  "incident_title": "Service incident description",
  "start_time": "2024-11-19",
  "end_time": "2024-11-19",
  "business_impact": "What customers/business experienced",
  "affected_services": ["Service 1", "Service 2"],
  "affected_customers": "Description of affected customers",
  "root_cause": "Clear explanation of root cause",
  "root_cause_category": "Configuration|Deployment|Resource|Bug|External",
  "timeline_events": [/* parsed from Teams chat */],
  "immediate_fix": "Actions taken to restore service",
  "permanent_fix": "Long-term solution being implemented",
  "teams_involved": ["Team 1", "Team 2"],
  "prevention_measures": [
    "Specific action to prevent recurrence",
    "With owner and completion date"
  ],
  "customer_communication_sent": true,
  "notes": "Additional context"
}
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `scripts/teams-pir-parser.py` | Teams chat parser - extracts & consolidates timeline |
| `.github/prompts/internal-pir-generator.prompt.md` | AI prompt for PIR generation |
| `PIR_WORKFLOW.md` | Detailed step-by-step guide |
| `PIR_README.md` | Complete system documentation |
| `data/incidents/incident_ING00000526_teams_export.json` | Example Teams chat |
| `data/incidents/incident_ING00000526_example.json` | Example incident data |

---

## 📊 Timeline Consolidation

**Automatic Filtering:**
- Keeps: Incident declaration, root cause discovery, major actions, service restoration
- Removes: Routine updates, minor checks, duplicate reports
- Max Events: 10-15 (configurable)
- Result: Clean, focused timeline

**Example:**
```
❌ 21 Messages from Teams chat
  ↓ Parser
✅ 15 Critical milestone events
  - Incident declared
  - Investigation milestone
  - Root cause found
  - Mitigation applied
  - Service restored
  ... etc
```

---

## 🎯 Language Guidelines

| ✅ Preferred | ❌ Avoid |
|-------------|---------|
| "experienced performance degradation" | "got slow" |
| "experienced issues" | "struggled" |
| "increased processing time" | "was sluggish" |
| "multiple" or "several" | Exact numbers (e.g., "14") |
| Dates only: "19 November" | Dates + times: "10:30 SAST" |

---

## 🛡️ Prevention Measures Format

Each prevention measure needs:

```json
{
  "action": "Specific, measurable action to implement",
  "target": "What aspect this prevents",
  "owner": "Team responsible",
  "expected_completion": "2024-11-30",
  "status": "Planned | In Progress | Completed"
}
```

**Example:**
```json
{
  "action": "Implement configuration validation checks before database routine deployment",
  "target": "Prevents misconfiguration from reaching production",
  "owner": "Database Performance Team",
  "expected_completion": "2024-11-30",
  "status": "In Progress"
}
```

---

## 🔄 Complete Workflow

```
Teams Chat → Parser → Consolidated Timeline (10-15 events)
                           ↓
                    + Gather Incident Details
                           ↓
                    Create Incident JSON
                           ↓
                    Internal PIR Prompt + AI
                           ↓
                    Internal PIR Document
                           ↓
                    Review & Publish
                           ↓
                    Track Prevention Measures
```

---

## 🧪 Testing

Run the validation script:
```bash
python test_parser.py
```

Expected output:
- ✅ Parsed timeline events
- ✅ Classified by event type
- ✅ Severity-scored
- ✅ Consolidated to 15 events
- ✅ Structured PIR summary data

---

## 📂 Directory Structure

```
Dashboards/
├── scripts/
│   └── teams-pir-parser.py              # Parser implementation
├── .github/prompts/
│   ├── internal-pir-generator.prompt.md # Internal PIR prompt
│   └── pir-generator.prompt.md           # Customer-facing prompt
├── data/incidents/
│   ├── incident_ING00000526_teams_export.json  # Sample Teams chat
│   └── incident_ING00000526_example.json       # Sample incident data
├── reports/
│   └── Internal_PIR_*.md                       # Generated PIRs
├── PIR_README.md          # Complete documentation
├── PIR_WORKFLOW.md        # Step-by-step guide
└── PIR_PROJECT_SUMMARY.md # Project overview
```

---

## ⚡ Common Tasks

### Parse a Teams export
```python
from scripts.teams_pir_parser import TeamsChatsToTimelineParser
parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
events = parser.parse_teams_json_export('path/to/export.json')
```

### Adjust timeline length
```python
# For shorter timelines (10 events)
parser = TeamsChatsToTimelineParser(max_timeline_entries=10)

# For longer timelines (20 events)
parser = TeamsChatsToTimelineParser(max_timeline_entries=20)
```

### Extract PIR summary
```python
from scripts.teams_pir_parser import IncidentDataExtractor, IncidentData
summary = IncidentDataExtractor.extract_summary_for_pir(incident)
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Too many timeline events | Use `max_timeline_entries=10` or manually remove low-value events |
| Generated PIR incomplete | Verify all JSON fields populated, review prompt template |
| Timeline events out of order | Ensure timestamps in ISO format: `YYYY-MM-DDTHH:MM:SSZ` |
| Event classification wrong | Review/adjust keywords in `CRITICAL_KEYWORDS` dict |

---

## 📞 Support Resources

- **Detailed Guide**: See `PIR_WORKFLOW.md`
- **Full Documentation**: See `PIR_README.md`
- **Example Data**: See `data/incidents/`
- **Sample Output**: See `PIR_PROJECT_SUMMARY.md`

---

**Last Updated**: November 2024 | **Status**: Production Ready
