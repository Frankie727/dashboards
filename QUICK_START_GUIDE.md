# PIR Generation System - Quick Start Guide

## 🚀 Your Complete Workflow (5 Steps)

You now have a **complete, production-ready system** for generating Internal Post-Incident Review (PIR) documents from Teams chat. Here's how to use it:

---

## Step 1: Extract Your Teams Chat (5-10 minutes)

You have three methods to extract messages from your Teams incident chat. Choose the easiest for your situation:

### **Option A: Browser Console (Fastest - Recommended)** ⭐
*Best for: Anyone who can access the Teams chat in a browser*

1. **Open your Teams chat in a browser:**
   - Use the link: [ING00000532 - ICS2 Authorization Rejection Errors](https://teams.microsoft.com/l/chat/19%3A98b932ab943b40809fc75633d7fb1c78%40thread.v2/conversations?context=%7B%22contextType%22%3A%22chat%22%7D)
   - Scroll through the entire conversation to load all messages

2. **Open browser Developer Tools:**
   - Press `F12` (Windows) or `Cmd+Option+I` (Mac)
   - Go to the **Console** tab

3. **Paste and run this extraction script:**
```javascript
// Extract all Teams messages from the current page
const messages = [];
const articles = document.querySelectorAll('[role="article"]');

articles.forEach(article => {
  try {
    // Extract author
    let author = "Unknown";
    const authorEl = article.querySelector('[data-tid="messageAuthor"]') || 
                     article.querySelector('.author-name');
    if (authorEl) author = authorEl.textContent.trim();
    
    // Extract timestamp
    let timestamp = new Date().toISOString();
    const timeEl = article.querySelector('time') || 
                   article.querySelector('[data-tid="messageTime"]');
    if (timeEl) {
      const ariaLabel = timeEl.getAttribute('aria-label');
      timestamp = ariaLabel || timeEl.textContent.trim();
    }
    
    // Extract message body
    let body = "";
    const bodyEl = article.querySelector('[role="document"]') || 
                   article.querySelector('.message-body');
    if (bodyEl) {
      body = bodyEl.textContent.trim();
    } else {
      body = article.textContent.trim();
    }
    
    if (body && body.length > 0 && !body.includes("Sign in") && body.length < 2000) {
      messages.push({
        timestamp: timestamp,
        from: author,
        body: body
      });
    }
  } catch (e) {
    console.error('Error processing message:', e);
  }
});

// Save to JSON
const json = JSON.stringify(messages, null, 2);
console.log(`Extracted ${messages.length} messages`);
console.log(json);

// Copy to clipboard
navigator.clipboard.writeText(json).then(() => {
  console.log("✅ Copied to clipboard! Paste into a text editor and save as incident.json");
});
```

4. **Save the extracted data:**
   - Paste the copied JSON into a text editor
   - Save as `incident_ING00000532_teams_export.json` in your `data/incidents/` folder

### **Option B: Teams Native Export** (5-10 minutes)
*If your Teams workspace has export functionality:*
1. Right-click on the chat → **Export conversation**
2. Save the exported file as JSON

### **Option C: Manual Export** (10-15 minutes)
*If neither of the above works:*
1. Manually copy each important message from Teams
2. Create a JSON file following this format:
```json
[
  {
    "timestamp": "2024-01-10T14:35:00Z",
    "from": "Sarah Chen",
    "body": "Alert: Authorization service error rate spiking. Currently 15% failures."
  },
  {
    "timestamp": "2024-01-10T14:42:00Z",
    "from": "James Martinez",
    "body": "Acknowledged. Starting investigation on authorization service logs."
  }
]
```

---

## Step 2: Prepare Your Incident Data (5 minutes)

Once you have the Teams messages extracted, transform them into structured incident data:

1. **Create incident JSON file** with metadata:
```json
{
  "incident_id": "ING00000532",
  "incident_title": "ICS2 Authorization Rejection Errors",
  "incident_date": "2024-01-10",
  "severity": "Critical",
  "duration_minutes": 107,
  "teams_messages": [
    // Paste your extracted messages here
  ],
  "incident_summary": "Brief description of what happened",
  "root_cause": "What caused the incident",
  "impact": "Who/what was affected"
}
```

2. **Save as:** `data/incidents/incident_ING00000532.json`

---

## Step 3: Run the Teams Parser (< 1 minute)

The parser automatically consolidates 50+ Teams messages into 10-15 key timeline events:

```bash
# From the repository root
python scripts/teams-pir-parser.py --input data/incidents/incident_ING00000532.json --output data/incidents/incident_ING00000532_parsed.json
```

**Output:** A structured incident file with:
- ✅ Consolidated timeline (10-15 critical events)
- ✅ Event classification (incident_start, investigation, mitigation, resolution, update)
- ✅ Severity scoring
- ✅ Ready-to-use format for PIR generation

---

## Step 4: Generate Your PIR (3-5 minutes)

Use the AI prompt template with your incident data to generate the final PIR:

### **Using Copilot in VS Code:**
1. Open `.github/prompts/internal-pir-generator.prompt.md`
2. This is the complete prompt template for your AI
3. Copy the prompt and add your incident data
4. Send to Claude/ChatGPT with your incident JSON
5. AI generates the complete Internal PIR document

### **Example Prompt:**
```
# Internal PIR Generator Prompt

[Copy the full content from: .github/prompts/internal-pir-generator.prompt.md]

## Your Incident Data:
{
  "incident_id": "ING00000532",
  "incident_title": "ICS2 Authorization Rejection Errors",
  "severity": "Critical",
  "duration_minutes": 107,
  "timeline": [
    // Your parsed timeline events here
  ],
  "root_cause": "...",
  "impact": "...",
  "prevention_measures": [...]
}
```

---

## Step 5: Review & Publish (5 minutes)

1. **Review the generated PIR** for accuracy and completeness
2. **Save to reports folder:** `reports/Internal_PIR_ING00000532.md`
3. **Add sign-off section** with your team's names and dates
4. **Commit to git:**
   ```bash
   git add reports/Internal_PIR_ING00000532.md
   git commit -m "docs: Internal PIR for incident ING00000532 - ICS2 Authorization Rejection Errors"
   git push
   ```

---

## 📚 Reference & Examples

### Complete Example PIR
**File:** `reports/Example_Internal_PIR_ING00000532.md`

This is a **full, real-world example** showing:
- Executive summary and impact analysis
- Complete timeline with 15 key events
- Detailed root cause analysis (5 contributing factors)
- Prevention measures (10 actions across immediate/medium/long-term)
- Appendices with logs, checklists, and verification details

👉 **Use this as your template** - it shows exactly what your final PIR should look like.

### Core Scripts
- **`scripts/teams-pir-parser.py`** (365 lines)
  - Consolidates Teams messages to timeline
  - Classifies events into 5 types
  - Scores severity (critical/important/info)
  - Ready to run

- **`scripts/teams-link-extractor.py`** (450+ lines)
  - Parses Teams URLs
  - Provides extraction framework
  - Includes Graph API integration guide

### AI Prompt Template
- **`.github/prompts/internal-pir-generator.prompt.md`**
  - 10,500 characters of detailed instructions
  - 10+ comprehensive sections
  - Language guidelines and examples
  - Use with Claude/ChatGPT/Copilot

### Documentation
| File | Purpose |
|------|---------|
| `PIR_INDEX.md` | Navigation hub - start here |
| `PIR_WORKFLOW.md` | Complete step-by-step guide |
| `PIR_README.md` | System documentation |
| `PIR_QUICK_REFERENCE.md` | 1-page quick reference |
| `EXTRACT_FROM_TEAMS_LINK.md` | Teams extraction guide |

---

## 🎯 Key Features

✅ **Automatic Timeline Consolidation**
- Reduces 50+ messages to 10-15 critical events
- Maintains chronological order
- Scores events by severity
- Removes redundant information

✅ **Professional PIR Structure**
- Executive summary
- Impact analysis
- Root cause analysis with contributing factors
- Prevention measures (immediate, medium-term, long-term)
- Appendices with detailed logs

✅ **Language Standards**
- Professional technical tone
- Consistent terminology
- Clear action items
- Proper severity classifications

✅ **Easy Customization**
- Templates for each section
- Example language and phrasing
- Flexible format for your organization
- Ready-to-use AI prompt

---

## ⏱️ Time Estimates

| Step | Time | Effort |
|------|------|--------|
| Step 1: Extract Teams chat | 5-10 min | Easy |
| Step 2: Prepare incident JSON | 5 min | Easy |
| Step 3: Run parser | <1 min | Automatic |
| Step 4: Generate PIR | 3-5 min | With AI |
| Step 5: Review & publish | 5 min | Easy |
| **Total** | **~20-30 min** | **Mostly Automated** |

---

## 🔧 Troubleshooting

### "I can't access the Teams page"
→ Use **Option B (Teams Export)** or **Option C (Manual Export)**

### "The browser console script didn't work"
→ Teams page structure may have changed
→ Use the **EXTRACT_FROM_TEAMS_LINK.md** guide for updated selectors
→ Or use Teams native export feature

### "The parser isn't finding messages"
→ Check your JSON format matches the template
→ Run with `--debug` flag for detailed output
→ See `data/incidents/incident_ING00000526_teams_export.json` for format example

### "I want to customize the PIR structure"
→ Edit `.github/prompts/internal-pir-generator.prompt.md`
→ Add/remove sections as needed
→ See `PIR_QUICK_REFERENCE.md` for section guidelines

---

## 📞 Get Help

| Need | Resource |
|------|----------|
| **Overview of system** | `PIR_INDEX.md` |
| **Step-by-step guide** | `PIR_WORKFLOW.md` |
| **Full documentation** | `PIR_README.md` |
| **1-page reference** | `PIR_QUICK_REFERENCE.md` |
| **Example PIR** | `reports/Example_Internal_PIR_ING00000532.md` |
| **Teams extraction help** | `EXTRACT_FROM_TEAMS_LINK.md` |

---

## ✅ You're All Set!

Your PIR system is **complete and ready to use**. Everything you need is in this repository:

1. ✅ Python parser for Teams messages
2. ✅ AI prompt template for PIR generation
3. ✅ Complete example PIR document
4. ✅ Teams extraction guides
5. ✅ Documentation and templates

**Next step:** Follow the 5 steps above to generate your first PIR for incident ING00000532!

Questions? See the **Reference & Examples** section above.

---

**Last Updated:** 2024-01-15  
**System Status:** ✅ Production Ready
