# Extract Messages from Teams Chat Link - Quick Guide

## Your Incident Link

📌 **Incident**: ING00000532 - ICS2 Authorization Rejection Errors  
🔗 **Chat Link**: https://teams.microsoft.com/l/chat/19%3A98b932ab943b40809fc75633d7fb1c78%40thread.v2/conversations  
🆔 **Chat ID**: `19:98b932ab943b40809fc75633d7fb1c78@thread.v2`

---

## ⚡ Fastest Method: Browser Console Extraction (5-10 minutes)

### Step 1: Open the Teams Link
Click the link above or paste it in your browser. Load all messages (scroll up to see older messages).

### Step 2: Open Developer Tools
Press: **F12** or **Ctrl+Shift+I** (Windows) / **Cmd+Option+I** (Mac)

### Step 3: Go to Console Tab
Click the **Console** tab in Developer Tools.

### Step 4: Paste the Extraction Script
Copy this entire script and paste it into the console:

```javascript
(function extractTeamsMessages() {
    const messages = [];
    
    // Extract from message article elements
    document.querySelectorAll('[role="article"], [data-tid="messageContent"]').forEach((element) => {
        try {
            // Extract author
            let author = "Unknown";
            const authorElem = element.querySelector('[aria-label*="sent by"], .message-author, .author-name');
            if (authorElem) {
                author = authorElem.textContent.trim();
            }
            
            // Extract timestamp
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
    
    // Output results
    const output = {
        extraction_timestamp: new Date().toISOString(),
        message_count: messages.length,
        messages: messages
    };
    
    console.log('Extraction complete! Messages extracted:', messages.length);
    console.log(JSON.stringify(output, null, 2));
    
    // Copy to clipboard
    try {
        const jsonStr = JSON.stringify(output, null, 2);
        const textarea = document.createElement('textarea');
        textarea.value = jsonStr;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        console.log('JSON copied to clipboard! Save it to: data/incidents/incident_ING00000532_teams_export.json');
    } catch (e) {
        console.log('Could not auto-copy. See output above.');
    }
    
    return output;
})();
```

### Step 5: Press Enter & Copy Results
The script will:
1. Extract all messages from the chat
2. Count them
3. Try to copy to clipboard automatically
4. Show the JSON in the console

### Step 6: Save to File
1. Create a new file: `data/incidents/incident_ING00000532_teams_export.json`
2. Paste the extracted JSON
3. Save!

### Step 7: Parse with Your Tool
```python
from scripts.teams_pir_parser import TeamsChatsToTimelineParser
parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
events = parser.parse_teams_json_export('data/incidents/incident_ING00000532_teams_export.json')
```

---

## 📊 Expected Output Format

After running the script, you'll get JSON like this:

```json
{
  "extraction_timestamp": "2026-11-19T12:00:00.000Z",
  "message_count": 25,
  "messages": [
    {
      "timestamp": "sent at 2:30 PM",
      "from": "Support Team",
      "body": "Incident declared - ICS2 auth errors reported"
    },
    {
      "timestamp": "sent at 2:35 PM",
      "from": "Engineer A",
      "body": "Investigating authentication service logs"
    },
    ...
  ]
}
```

---

## ✨ Alternative Method 1: Teams Export Feature

**If Teams has a native export option:**
1. Right-click on the conversation
2. Look for "Export chat" or "Save chat"
3. Save the export
4. Convert to the JSON format above if needed

**Estimated time:** 5 minutes

---

## 🔧 Alternative Method 2: Microsoft Graph API

**For fully automated extraction (one-time setup):**

1. Register an Azure AD application
2. Grant `Chat.Read` permissions
3. Obtain an access token
4. Use the Graph API endpoint:
   ```
   https://graph.microsoft.com/v1.0/chats/19:98b932ab943b40809fc75633d7fb1c78@thread.v2/messages
   ```
5. Automatically extracts all messages

**Estimated time:** 30+ minutes (one-time setup), then < 1 minute per chat

**Benefits:**
- Fully automated
- No manual copying required
- Can be integrated into scripts
- Scales to multiple chats

---

## 🚀 Once You Have the JSON

1. **Parse the timeline:**
   ```python
   parser = TeamsChatsToTimelineParser(max_timeline_entries=15)
   events = parser.parse_teams_json_export('data/incidents/incident_ING00000532_teams_export.json')
   ```

2. **Gather incident details:**
   - Business impact
   - Root cause
   - Prevention measures
   - Teams involved

3. **Generate internal PIR:**
   - Use `.github/prompts/internal-pir-generator.prompt.md`
   - Provide incident JSON + parsed timeline
   - AI generates comprehensive PIR

4. **Publish and track:**
   - Save to `reports/Internal_PIR_ING00000532.md`
   - Track prevention measures

---

## ❓ Troubleshooting

**Q: Script doesn't extract any messages?**
A: Teams HTML structure may have changed. Try:
- Right-clicking on a message and inspecting it
- Adjusting the CSS selectors in the script
- Using the alternative Teams export method

**Q: "Cannot copy to clipboard" error?**
A: Manually copy the console output:
1. Click on the JSON output
2. Right-click → Copy
3. Paste into a text file

**Q: Some messages are missing?**
A: Teams loads messages dynamically. Scroll up to load older messages before running the script.

**Q: What if I can't access the Teams link?**
A: You may need:
- Authentication with your organization
- Proper permissions to view the chat
- VPN/network access if Teams is restricted

---

## 📞 Need Help?

**For extraction issues:** Try alternative methods above
**For parser questions:** See `PIR_README.md` or `PIR_QUICK_REFERENCE.md`
**For full workflow:** See `PIR_WORKFLOW.md`

---

## ⏱️ Time Estimates

| Method | Time | Difficulty | Automation |
|--------|------|-----------|-----------|
| Browser Console | 5-10 min | Easy | Manual |
| Teams Export | 5 min | Easy | Manual |
| Graph API | 30+ min setup | Medium | Automatic |

---

**Ready to extract? Start with Step 1 above!** 🚀
