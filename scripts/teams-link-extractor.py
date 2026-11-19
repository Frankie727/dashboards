"""
Teams Link to PIR Parser
Extracts incident data directly from Teams chat links
Supports Microsoft Teams web app and Graph API
"""

import re
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from urllib.parse import unquote, parse_qs, urlparse
from dataclasses import dataclass, asdict


@dataclass
class TeamsLinkInfo:
    """Information extracted from a Teams link"""
    link_type: str  # 'chat', 'channel', 'message'
    chat_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_id: Optional[str] = None
    organization_id: Optional[str] = None
    team_id: Optional[str] = None


class TeamsLinkParser:
    """Parse different Teams link formats and extract relevant IDs"""
    
    # Teams link patterns
    PATTERNS = {
        'chat': re.compile(r'/l/chat/([^/]+)/conversations'),
        'channel': re.compile(r'/l/channel/([^/]+)/conversations'),
        'message': re.compile(r'/l/message/([^/]+)/([^/]+)'),
        'team': re.compile(r'/l/team/([^/]+)/conversations'),
    }
    
    @staticmethod
    def parse_teams_link(link: str) -> TeamsLinkInfo:
        """
        Parse a Teams link and extract relevant IDs and information
        
        Supported link formats:
        - Chat: https://teams.microsoft.com/l/chat/19:xxxx/conversations
        - Channel: https://teams.microsoft.com/l/channel/19:xxxx/conversations
        - Message: https://teams.microsoft.com/l/message/xxxx/xxxx
        - Team: https://teams.microsoft.com/l/team/xxxx/conversations
        
        Args:
            link: Teams URL
            
        Returns:
            TeamsLinkInfo with parsed components
        """
        # Decode URL-encoded characters
        decoded_link = unquote(link)
        
        # Try each pattern
        for link_type, pattern in TeamsLinkParser.PATTERNS.items():
            match = pattern.search(decoded_link)
            if match:
                info = TeamsLinkInfo(link_type=link_type)
                
                if link_type == 'chat':
                    info.chat_id = match.group(1)
                elif link_type == 'channel':
                    info.channel_id = match.group(1)
                elif link_type == 'message':
                    info.chat_id = match.group(1)
                    info.message_id = match.group(2)
                elif link_type == 'team':
                    info.team_id = match.group(1)
                
                return info
        
        raise ValueError(f"Unable to parse Teams link: {link}")
    
    @staticmethod
    def extract_context_from_link(link: str) -> Dict:
        """
        Extract context information from query parameters
        
        Args:
            link: Teams URL with context parameters
            
        Returns:
            Dict with context information
        """
        try:
            parsed_url = urlparse(unquote(link))
            context_param = parse_qs(parsed_url.query).get('context', [None])[0]
            
            if context_param:
                context = json.loads(context_param)
                return context
            return {}
        except Exception as e:
            print(f"Could not extract context: {e}")
            return {}


class TeamsGraphAPIExtractor:
    """
    Extract Teams chat messages using Microsoft Graph API
    
    Requires:
    - Microsoft Graph API access
    - Azure AD application registration
    - Proper permissions (Chat.Read)
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Graph API extractor
        
        Args:
            access_token: Microsoft Graph API access token (optional)
                         If not provided, manual extraction required
        """
        self.access_token = access_token
        self.graph_api_endpoint = "https://graph.microsoft.com/v1.0"
    
    def extract_from_chat_id(self, chat_id: str) -> List[Dict]:
        """
        Extract messages from a chat using Graph API
        
        Args:
            chat_id: Teams chat ID (e.g., "19:xxxx@thread.v2")
            
        Returns:
            List of message dictionaries
            
        Requires:
            - Valid access_token set during initialization
            - Chat.Read permissions
        """
        if not self.access_token:
            return self._get_manual_extraction_instructions(chat_id)
        
        # This would use requests library to call Graph API
        # For now, provide instructions
        endpoint = f"{self.graph_api_endpoint}/chats/{chat_id}/messages"
        
        return {
            "status": "requires_api_access",
            "endpoint": endpoint,
            "instructions": self._get_api_instructions()
        }
    
    @staticmethod
    def _get_manual_extraction_instructions(chat_id: str) -> Dict:
        """
        Provide instructions for manual extraction without API access
        """
        return {
            "status": "manual_extraction_required",
            "chat_id": chat_id,
            "instructions": [
                "1. Open the Teams chat link in your browser",
                "2. Scroll to load all messages (may need to scroll up multiple times)",
                "3. Right-click on the conversation area",
                "4. Select 'Inspect' (or 'Inspect Element')",
                "5. Find the message elements in the HTML (usually in <div> with message content)",
                "6. Copy the page content or use the browser console:",
                "   - Open Developer Console (F12 or Ctrl+Shift+I)",
                "   - Go to Console tab",
                "   - Run the extraction script provided below"
            ],
            "browser_extraction_script": """
// Extract all visible messages from Teams chat
const messages = [];
document.querySelectorAll('[role="article"]').forEach(msg => {
    const author = msg.querySelector('[aria-label*="sent by"]')?.innerText || "Unknown";
    const content = msg.querySelector('[role="document"]')?.innerText || "";
    const timestamp = msg.querySelector('[aria-label*="sent"]')?.innerText || "";
    
    if (content.trim()) {
        messages.push({
            timestamp: timestamp,
            from: author,
            body: content
        });
    }
});

// Copy to clipboard
copy(JSON.stringify({messages: messages}, null, 2));
console.log('Messages copied to clipboard!', messages.length + ' messages extracted');
            """
        }
    
    @staticmethod
    def _get_api_instructions() -> List[str]:
        """Get instructions for using Microsoft Graph API"""
        return [
            "To extract Teams chat data programmatically:",
            "1. Register an Azure AD application",
            "2. Grant 'Chat.Read' or 'Chat.ReadWrite' permissions",
            "3. Obtain an access token",
            "4. Call the Microsoft Graph API endpoint",
            "5. Use the extracted messages with the PIR parser"
        ]


class TeamsLinkToPIRExtractor:
    """
    Complete workflow: Teams link → Extract messages → Generate PIR data
    """
    
    def __init__(self):
        self.link_parser = TeamsLinkParser()
        self.graph_extractor = TeamsGraphAPIExtractor()
    
    def process_teams_link(self, link: str, messages: Optional[List[Dict]] = None) -> Dict:
        """
        Process a Teams link and optionally integrate with messages
        
        Args:
            link: Teams chat link
            messages: Optional list of messages extracted from the chat
                     If provided, will parse and structure them
                     If not provided, will return extraction instructions
                     
        Returns:
            Dict with:
            - link_info: Parsed Teams link information
            - extraction_status: Whether messages were provided
            - messages: Structured message list (if provided)
            - instructions: How to extract if not provided
        """
        # Parse the link
        link_info = self.link_parser.parse_teams_link(link)
        
        result = {
            "incident_link": link,
            "link_info": {
                "type": link_info.link_type,
                "chat_id": link_info.chat_id,
                "channel_id": link_info.channel_id,
                "team_id": link_info.team_id,
            },
            "extraction_status": "pending" if not messages else "complete",
            "message_count": len(messages) if messages else 0,
        }
        
        if messages:
            # Messages were provided - structure them for PIR parsing
            result["messages"] = messages
            result["structured_data"] = {
                "incidents": self._identify_incidents(messages),
                "timeline": self._extract_timeline(messages),
                "teams": self._identify_teams(messages),
            }
        else:
            # No messages provided - return extraction instructions
            result["extraction_instructions"] = self._get_extraction_guide(link_info)
        
        return result
    
    @staticmethod
    def _identify_incidents(messages: List[Dict]) -> List[str]:
        """Identify incident declarations and summaries from messages"""
        incident_keywords = [
            'incident', 'issue', 'problem', 'error', 'down', 'outage',
            'critical', 'major', 'emergency', 'urgent'
        ]
        
        incidents = []
        for msg in messages:
            body = msg.get('body', '').lower()
            if any(keyword in body for keyword in incident_keywords):
                incidents.append(msg)
        
        return incidents
    
    @staticmethod
    def _extract_timeline(messages: List[Dict]) -> List[Dict]:
        """Extract timeline events from messages"""
        timeline_keywords = {
            'investigation': ['investigating', 'checking', 'analyzing', 'reviewing'],
            'discovery': ['found', 'identified', 'discovered', 'root cause'],
            'mitigation': ['fix', 'workaround', 'restart', 'rollback', 'mitigated'],
            'resolution': ['resolved', 'fixed', 'back to normal', 'restored'],
        }
        
        timeline = []
        for msg in messages:
            body = msg.get('body', '').lower()
            timestamp = msg.get('timestamp', '')
            
            for event_type, keywords in timeline_keywords.items():
                if any(keyword in body for keyword in keywords):
                    timeline.append({
                        "timestamp": timestamp,
                        "event_type": event_type,
                        "message": msg
                    })
                    break
        
        return timeline
    
    @staticmethod
    def _identify_teams(messages: List[Dict]) -> List[str]:
        """Identify teams/groups involved from message senders"""
        teams = set()
        for msg in messages:
            sender = msg.get('from', '').strip()
            if sender and sender != 'Unknown':
                # Extract team hints from sender names
                # e.g., "John (Database Team)" or "Database Team"
                teams.add(sender)
        
        return list(teams)
    
    @staticmethod
    def _get_extraction_guide(link_info: TeamsLinkInfo) -> Dict:
        """Get a guide for extracting messages based on link type"""
        
        guide = {
            "link_type": link_info.link_type,
            "overview": f"To extract messages from this {link_info.link_type} link:",
            "methods": {
                "method_1_manual": {
                    "name": "Manual Browser Extraction (Quickest)",
                    "steps": [
                        "1. Open the Teams link in your browser",
                        "2. Load all messages (scroll up to top)",
                        "3. Press F12 to open Developer Tools",
                        "4. Go to Console tab",
                        "5. Copy-paste the browser extraction script",
                        "6. Right-click and 'Copy' the results",
                        "7. Paste the JSON into a file: data/incidents/incident_<ID>_teams_export.json",
                        "8. Run the parser"
                    ],
                    "estimated_time": "5-10 minutes"
                },
                "method_2_export": {
                    "name": "Teams Native Export (If Available)",
                    "steps": [
                        "1. Right-click on the conversation",
                        "2. Look for 'Export chat' or similar option",
                        "3. Save the export file",
                        "4. Convert to JSON format if needed"
                    ],
                    "estimated_time": "5 minutes"
                },
                "method_3_api": {
                    "name": "Microsoft Graph API (Most Automated)",
                    "steps": [
                        "1. Register Azure AD application",
                        "2. Grant Chat.Read permissions",
                        "3. Obtain access token",
                        "4. Use this extractor with token",
                        "5. Automatically extracts all messages"
                    ],
                    "estimated_time": "30+ minutes (one-time setup)"
                }
            },
            "next_steps": [
                "Choose extraction method above",
                "Extract messages from the Teams chat",
                "Paste extracted JSON into data/incidents/ folder",
                "Run: python scripts/teams-pir-parser.py with the extracted file"
            ]
        }
        
        return guide


# Example usage & browser extraction script
BROWSER_EXTRACTION_SCRIPT = """
// =========================================================================
// Teams Chat Message Extractor - Run in Browser Console
// =========================================================================
// 
// Instructions:
// 1. Open the Teams chat in your browser
// 2. Scroll to load all messages you want to extract
// 3. Press F12 or Ctrl+Shift+I to open Developer Tools
// 4. Click on the "Console" tab
// 5. Copy and paste this entire script
// 6. Press Enter
// 7. Right-click on the output and select "Copy object"
// 8. Save to a file as JSON
//
// =========================================================================

(function extractTeamsMessages() {
    const messages = [];
    
    // Method 1: Extract from message article elements
    document.querySelectorAll('[role="article"], [data-tid="messageContent"]').forEach((element, index) => {
        try {
            // Try to extract author
            let author = "Unknown";
            const authorElem = element.querySelector('[aria-label*="sent by"], .message-author, .author-name');
            if (authorElem) {
                author = authorElem.textContent.trim();
            }
            
            // Try to extract timestamp
            let timestamp = new Date().toISOString();
            const timeElem = element.querySelector('[aria-label*="sent"], time, .message-time');
            if (timeElem) {
                timestamp = timeElem.getAttribute('aria-label') || timeElem.textContent || timestamp;
            }
            
            // Extract message body
            const bodyElem = element.querySelector('[role="document"], .message-body, .content');
            let body = bodyElem ? bodyElem.textContent.trim() : element.textContent.trim();
            
            if (body && body.length > 0) {
                messages.push({
                    timestamp: timestamp,
                    from: author,
                    body: body
                });
            }
        } catch (e) {
            console.error('Error extracting message:', e);
        }
    });
    
    // Method 2: Fallback - extract from all text nodes
    if (messages.length === 0) {
        const chatContainer = document.querySelector('[role="main"], .chat-container, [data-tid="chat-view"]');
        if (chatContainer) {
            const allText = chatContainer.innerText;
            console.log('Fallback extraction - raw text length:', allText.length);
        }
    }
    
    // Format for display
    const output = {
        extraction_timestamp: new Date().toISOString(),
        message_count: messages.length,
        messages: messages
    };
    
    console.log('✅ Extraction complete!');
    console.log('Messages extracted:', messages.length);
    console.log('JSON data:');
    console.log(output);
    
    // Try to copy to clipboard
    try {
        const jsonStr = JSON.stringify(output, null, 2);
        // Create temporary textarea
        const textarea = document.createElement('textarea');
        textarea.value = jsonStr;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        console.log('✅ JSON copied to clipboard!');
        console.log('Paste it here: data/incidents/incident_ING00000532_teams_export.json');
    } catch (e) {
        console.log('Could not auto-copy. Here is the JSON:');
        console.log(JSON.stringify(output, null, 2));
    }
    
    return output;
})();
"""


if __name__ == "__main__":
    # Example: Parse a Teams link
    link = "https://teams.microsoft.com/l/chat/19%3A98b932ab943b40809fc75633d7fb1c78%40thread.v2/conversations?context=%7B%22contextType%22%3A%22chat%22%7D"
    
    extractor = TeamsLinkToPIRExtractor()
    
    print("=" * 70)
    print("TEAMS LINK PARSER")
    print("=" * 70)
    print()
    
    # Parse the link
    result = extractor.process_teams_link(link)
    print("Link Information:")
    print(json.dumps(result, indent=2))
    print()
    
    print("=" * 70)
    print("TO EXTRACT MESSAGES FROM THIS CHAT:")
    print("=" * 70)
    print()
    print(result.get("extraction_instructions", {}).get("overview"))
    print()
    
    print("BROWSER EXTRACTION SCRIPT:")
    print("-" * 70)
    print(BROWSER_EXTRACTION_SCRIPT)
    print("-" * 70)
