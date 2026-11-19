"""
Teams Chat to PIR Parser
Extracts incident data from Teams chat exports and structures it for PIR document generation.
Automatically consolidates timeline events to max 10-15 critical milestones.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TimelineEvent:
    """Represents a single timeline event"""
    timestamp: str  # ISO format
    event_type: str  # 'incident_start', 'investigation', 'mitigation', 'resolution', 'update', 'communication'
    description: str
    actor: str  # Who made this entry (optional)
    severity: int = 2  # 1=critical (keep), 2=important (consider), 3=info (consolidate)


@dataclass
class IncidentData:
    """Complete incident data structure for PIR"""
    incident_id: str
    incident_title: str
    start_time: str  # ISO format
    end_time: str  # ISO format or "ongoing"
    
    # Impact
    business_impact: str
    affected_services: List[str]
    affected_customers: Optional[List[str]]
    estimated_customer_impact: Optional[str]  # e.g., "5000 customers", "EMEA region"
    
    # Root Cause
    root_cause: str
    root_cause_category: str  # e.g., 'Configuration', 'Deployment', 'Resource', 'Bug', 'External'
    
    # Timeline Events (consolidated)
    timeline_events: List[TimelineEvent]
    
    # Resolution
    immediate_fix: str
    permanent_fix: Optional[str]
    
    # Teams involved
    teams_involved: List[str]
    
    # Preventative measures
    prevention_measures: List[str]  # List of actions to prevent recurrence
    
    # Communication
    customer_communication_sent: bool
    
    # Additional notes
    notes: Optional[str]


class TeamsChatsToTimelineParser:
    """Parse Teams chat export and extract incident timeline"""
    
    CRITICAL_KEYWORDS = {
        'incident_start': [
            'incident declared', 'major incident', 'critical issue', 'service down', 
            'outage', 'investigation started', 'issue identified', 'problem reported'
        ],
        'investigation': [
            'investigating', 'checking logs', 'analyzing', 'reviewing',
            'identified', 'found', 'discovered', 'root cause'
        ],
        'mitigation': [
            'mitigating', 'mitigated', 'workaround', 'temporary fix',
            'applied fix', 'rolled back', 'restarted', 'redeployed'
        ],
        'resolution': [
            'resolved', 'fixed', 'restored', 'back to normal', 'incident closed',
            'service restored', 'issue resolved', 'back online'
        ],
        'update': [
            'update', 'status', 'ongoing', 'continuing', 'working on',
            'teams engaged', 'coordinating'
        ]
    }
    
    def __init__(self, max_timeline_entries: int = 15):
        """
        Initialize parser
        
        Args:
            max_timeline_entries: Maximum number of timeline events to keep (default 15)
        """
        self.max_timeline_entries = max_timeline_entries
        self.timeline_events: List[TimelineEvent] = []
    
    def classify_message(self, text: str) -> str:
        """Classify a message to determine event type"""
        text_lower = text.lower()
        
        for event_type, keywords in self.CRITICAL_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return event_type
        
        return 'update'
    
    def parse_teams_export(self, chat_data: Dict) -> List[TimelineEvent]:
        """
        Parse Teams chat export format
        
        Expected format:
        {
            "messages": [
                {
                    "timestamp": "2024-11-19T10:30:00Z",
                    "from": "Engineer Name",
                    "body": "Message content"
                },
                ...
            ]
        }
        """
        events = []
        
        if isinstance(chat_data, dict) and 'messages' in chat_data:
            messages = chat_data['messages']
        elif isinstance(chat_data, list):
            messages = chat_data
        else:
            raise ValueError("Expected dict with 'messages' key or list of messages")
        
        for msg in messages:
            if not isinstance(msg, dict) or 'body' not in msg:
                continue
            
            timestamp = msg.get('timestamp', datetime.now().isoformat())
            actor = msg.get('from', 'Unknown')
            body = msg.get('body', '').strip()
            
            if not body:
                continue
            
            event_type = self.classify_message(body)
            severity = self._calculate_severity(event_type)
            
            event = TimelineEvent(
                timestamp=timestamp,
                event_type=event_type,
                description=body,
                actor=actor,
                severity=severity
            )
            events.append(event)
        
        return events
    
    def _calculate_severity(self, event_type: str) -> int:
        """
        Calculate severity (1=critical, 2=important, 3=info)
        Lower numbers = more likely to be kept
        """
        severity_map = {
            'incident_start': 1,
            'investigation': 2,
            'mitigation': 1,
            'resolution': 1,
            'update': 3,
            'communication': 2
        }
        return severity_map.get(event_type, 2)
    
    def consolidate_timeline(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        """
        Consolidate timeline events to max N entries, keeping critical milestones.
        Strategy:
        1. Keep all severity 1 events (critical)
        2. Keep important severity 2 events at key transitions
        3. Remove redundant severity 3 (info) events
        4. If still over limit, keep first event, last event, and evenly space the rest
        """
        if len(events) <= self.max_timeline_entries:
            return events
        
        # Separate by severity
        critical_events = [e for e in events if e.severity == 1]
        important_events = [e for e in events if e.severity == 2]
        info_events = [e for e in events if e.severity == 3]
        
        # Build result starting with critical
        consolidated = critical_events.copy()
        
        # Add important events if space available
        for event in important_events:
            if len(consolidated) < self.max_timeline_entries:
                consolidated.append(event)
        
        # Add info events if still under limit
        for event in info_events:
            if len(consolidated) < self.max_timeline_entries:
                consolidated.append(event)
        
        # If STILL over limit, prune strategically
        if len(consolidated) > self.max_timeline_entries:
            # Keep first and last
            result = [consolidated[0]]
            
            # Evenly space the rest
            remaining = consolidated[1:-1]
            step = len(remaining) // (self.max_timeline_entries - 2)
            if step > 0:
                result.extend(remaining[::step])
            
            result.append(consolidated[-1])
            consolidated = result[:self.max_timeline_entries]
        
        # Sort by timestamp
        consolidated.sort(key=lambda x: x.timestamp)
        return consolidated
    
    def parse_teams_json_export(self, json_file_path: str) -> List[TimelineEvent]:
        """
        Load and parse Teams export from JSON file
        
        Args:
            json_file_path: Path to Teams chat export JSON file
            
        Returns:
            List of consolidated timeline events
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        events = self.parse_teams_export(chat_data)
        consolidated = self.consolidate_timeline(events)
        
        return consolidated


class IncidentDataExtractor:
    """Extract structured incident data from various sources"""
    
    @staticmethod
    def extract_from_manual_input(prompt_data: Dict) -> IncidentData:
        """
        Extract incident data from manual input (structured dict/JSON)
        
        Required fields in prompt_data:
        - incident_id
        - incident_title
        - start_time
        - end_time
        - business_impact
        - affected_services (list)
        - root_cause
        - root_cause_category
        - immediate_fix
        - teams_involved (list)
        """
        return IncidentData(
            incident_id=prompt_data['incident_id'],
            incident_title=prompt_data['incident_title'],
            start_time=prompt_data['start_time'],
            end_time=prompt_data['end_time'],
            business_impact=prompt_data['business_impact'],
            affected_services=prompt_data.get('affected_services', []),
            affected_customers=prompt_data.get('affected_customers'),
            estimated_customer_impact=prompt_data.get('estimated_customer_impact'),
            root_cause=prompt_data['root_cause'],
            root_cause_category=prompt_data['root_cause_category'],
            timeline_events=prompt_data.get('timeline_events', []),
            immediate_fix=prompt_data['immediate_fix'],
            permanent_fix=prompt_data.get('permanent_fix'),
            teams_involved=prompt_data.get('teams_involved', []),
            prevention_measures=prompt_data.get('prevention_measures', []),
            customer_communication_sent=prompt_data.get('customer_communication_sent', False),
            notes=prompt_data.get('notes')
        )
    
    @staticmethod
    def extract_summary_for_pir(incident: IncidentData) -> Dict:
        """
        Extract key data for PIR document generation
        
        Returns simplified dict suitable for prompt input
        """
        return {
            'incident_id': incident.incident_id,
            'incident_title': incident.incident_title,
            'duration': f"From {incident.start_time} to {incident.end_time}",
            'business_impact': incident.business_impact,
            'affected_services': ', '.join(incident.affected_services),
            'root_cause': incident.root_cause,
            'root_cause_category': incident.root_cause_category,
            'immediate_fix': incident.immediate_fix,
            'permanent_fix': incident.permanent_fix,
            'teams_involved': ', '.join(incident.teams_involved),
            'timeline_summary': IncidentDataExtractor._format_timeline_summary(
                incident.timeline_events
            ),
            'prevention_measures': incident.prevention_measures,
            'customer_communication_sent': incident.customer_communication_sent,
            'notes': incident.notes
        }
    
    @staticmethod
    def _format_timeline_summary(events: List[TimelineEvent]) -> str:
        """Format timeline events into readable summary"""
        if not events:
            return "No timeline events available"
        
        summary_lines = []
        for event in sorted(events, key=lambda x: x.timestamp):
            summary_lines.append(
                f"[{event.timestamp}] {event.event_type.upper()}: {event.description}"
            )
        
        return '\n'.join(summary_lines)


# Example usage
if __name__ == "__main__":
    # Example Teams chat data
    example_chat = {
        "messages": [
            {
                "timestamp": "2024-11-19T10:30:00Z",
                "from": "Support",
                "body": "Incident declared - Customs messages not sending in IT region"
            },
            {
                "timestamp": "2024-11-19T10:35:00Z",
                "from": "Engineer A",
                "body": "Investigating database performance issues"
            },
            {
                "timestamp": "2024-11-19T10:50:00Z",
                "from": "Engineer B",
                "body": "Found root cause - database routine misconfiguration"
            },
            {
                "timestamp": "2024-11-19T11:05:00Z",
                "from": "Engineer A",
                "body": "Applied temporary workaround - restarted affected processes"
            },
            {
                "timestamp": "2024-11-19T11:30:00Z",
                "from": "Support",
                "body": "Service restored - message backlog cleared"
            }
        ]
    }
    
    # Parse timeline
    parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
    events = parser.parse_teams_export(example_chat)
    consolidated = parser.consolidate_timeline(events)
    
    print("=== Consolidated Timeline ===")
    for event in consolidated:
        print(f"[{event.timestamp}] {event.event_type}: {event.description}")
    
    # Create incident data
    incident = IncidentData(
        incident_id="ING00000526",
        incident_title="xT Customs messages not sending/receiving",
        start_time="2024-11-19T10:30:00Z",
        end_time="2024-11-19T11:30:00Z",
        business_impact="Customs-related messages unable to send/receive in IT, IE, CH, ES regions",
        affected_services=["Customs Integration Service", "Message Queue"],
        affected_customers=None,
        estimated_customer_impact="Multiple customers in affected regions",
        root_cause="Database routine running with misconfigured settings affecting multiple processes",
        root_cause_category="Configuration",
        timeline_events=consolidated,
        immediate_fix="Restarted affected processes and cleared message backlog",
        permanent_fix="Updated database routine configuration and added monitoring",
        teams_involved=["Database Team", "Integration Team", "Support"],
        prevention_measures=[
            "Implement configuration validation before deployment",
            "Add automated monitoring for database routine performance"
        ],
        customer_communication_sent=True,
        notes="Incident impacted cross-border customs operations"
    )
    
    # Extract summary
    summary = IncidentDataExtractor.extract_summary_for_pir(incident)
    print("\n=== PIR Summary ===")
    print(json.dumps(summary, indent=2))
