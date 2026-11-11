# 🎯 EXECUTION METHOD DECISION TREE

**Goal:** Query ENT and GLW work items from EDI Prod MCP Server

---

## Quick Decision Guide

```
                          START HERE
                              ↓
                    Do you have VS Code?
                         /          \
                       YES           NO
                        ↓             ↓
              Want fastest          Use Option 3
              results? (5 min)      or Option 4
                    ↓                 ↓
              METHOD 1: ⭐        (See below)
              Copilot Chat           ↓
                                  Takes 20 min?
                                     ↓
                            Choose your time
```

---

## 📊 Comparison Table

| Factor | Method 1 | Method 2 | Method 3 | Method 4 |
|--------|----------|----------|----------|----------|
| **Name** | VS Code Copilot | PowerShell | Manual UI | REST API |
| **Speed** | ⭐ 5 min | 10 min | 20 min | 15 min |
| **Setup** | None | Local access | Browser | Terminal |
| **Skill** | Beginner | Intermediate | Beginner | Advanced |
| **Auto** | Yes | Yes | No | Yes |
| **Best For** | Quick queries | Automation | Audits | Integration |

---

## 🎯 Method Selection by Use Case

### **I need results NOW** → **METHOD 1** ⭐
- Fastest execution (5 minutes)
- No setup required
- Copy/paste command
- See: `EDI_WorkItems_Quick_Reference.md`

### **I want to automate this** → **METHOD 2**
- Handles pagination automatically
- Can schedule as task
- Full error handling
- See: `Query-EDIWorkItems.ps1`

### **I need audit trail** → **METHOD 3**
- Manual process = clear audit trail
- Screenshots possible
- Approval-friendly
- See: `EDI_Query_Execution_Guide.md` → Option 3

### **I'm integrating with API** → **METHOD 4**
- Programmatic access
- CI/CD pipeline friendly
- Scriptable
- See: `EDI_Query_Execution_Guide.md` → Option 4

---

## 📋 Step-by-Step: Method 1 (Fastest) ⭐

```
STEP 1: Prepare (1 minute)
├─ Open VS Code
├─ Open Copilot Chat (Ctrl+Shift+V)
└─ Open: EDI_WorkItems_Quick_Reference.md

STEP 2: Copy (1 minute)
└─ Copy the command from Quick_Reference.md

STEP 3: Execute (2 minutes)
├─ Paste command into Copilot Chat
├─ Press Enter
└─ Wait for results

STEP 4: Export (1 minute)
├─ Select "Export as JSON"
├─ Save as: edi_workitems_result.json
└─ DONE! ✅

TOTAL TIME: 5 minutes
```

---

## 📋 Step-by-Step: Method 2 (Automated)

```
STEP 1: Setup (2 minutes)
├─ Open PowerShell
├─ cd "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
└─ Verify EDI Prod MCP server access

STEP 2: Execute Query (5 minutes)
├─ Run: .\Query-EDIWorkItems.ps1 -OutputPath "result.json"
└─ Wait for completion

STEP 3: Process Results (2 minutes)
├─ Run: python process_edi_results.py --input result.json --report
└─ Review console output

STEP 4: Verify (1 minute)
├─ Check result.json exists
├─ Validate JSON format
└─ DONE! ✅

TOTAL TIME: 10 minutes
```

---

## 📋 Step-by-Step: Method 3 (Manual UI)

```
STEP 1: Login (2 minutes)
├─ Open EDI Prod Application
├─ Login with your credentials
└─ Navigate to Work Items section

STEP 2: Set Filters (5 minutes)
├─ Product: ENT (run first)
├─ Change Type: FIX
├─ Created Date: 2026-10-06 to 2026-11-05
├─ Status: Exclude Closed, Cancelled
└─ Click Search

STEP 3: Export Results (5 minutes)
├─ Select all results
├─ Click Export
├─ Choose CSV format
└─ Save as: ent_results.csv

STEP 4: Repeat for GLW (5 minutes)
├─ Change Product filter to GLW
├─ Repeat steps 2-3
└─ Save as: glw_results.csv

STEP 5: Convert to JSON (3 minutes)
├─ Run: python process_edi_results.py --input ent_results.csv --format csv --output-json results.json
└─ DONE! ✅

TOTAL TIME: 20 minutes
```

---

## 📋 Step-by-Step: Method 4 (REST API)

```
STEP 1: Get Token (5 minutes)
├─ Authenticate to EDI Prod API
├─ Get access token
└─ Set in environment variable

STEP 2: Query ENT (5 minutes)
├─ curl -X POST "https://ediprod.../api/workitems/filter" \
│      -H "Authorization: Bearer TOKEN" \
│      -d '{"product":"ENT","changeType":["FIX"],...}' \
│      > ent_results.json
└─ Handle pagination (skip=50, 100, etc)

STEP 3: Query GLW (5 minutes)
├─ Repeat Step 2 with product=GLW
└─ > glw_results.json

STEP 4: Process (2 minutes)
├─ Combine results
├─ Apply filters
└─ Generate report

TOTAL TIME: 15 minutes
```

---

## ⚡ Quick Decision Matrix

**How much time do you have?**

| Time | Best Option | Why |
|------|------------|-----|
| 5 min | Method 1 | Fastest |
| 10 min | Method 1 or 2 | Automated |
| 15 min | Method 4 | API integration |
| 20+ min | Method 3 | Manual audit trail |

---

## 🛠️ Prerequisites by Method

### Method 1 Requirements
- ✅ VS Code installed
- ✅ Copilot enabled
- ✅ MCP tools available
- ✅ Internet connection

### Method 2 Requirements
- ✅ PowerShell (built-in)
- ✅ Python 3 (optional, for processing)
- ✅ EDI Prod MCP access
- ✅ Network connectivity

### Method 3 Requirements
- ✅ Browser
- ✅ EDI Prod login credentials
- ✅ Network access to EDI Prod
- ✅ Excel/CSV viewer

### Method 4 Requirements
- ✅ curl or similar tool
- ✅ EDI Prod API credentials
- ✅ API endpoint URL
- ✅ Network access

---

## 🎓 Recommended Path by Role

### **Developer** 👨‍💻
→ **Method 1** (fastest) or **Method 2** (automated)  
Why: Need quick results or automation

### **DevOps/SRE** 🔧
→ **Method 2** (PowerShell) or **Method 4** (API)  
Why: Automation and integration

### **QA/Tester** 🧪
→ **Method 3** (manual) or **Method 1** (quick)  
Why: Audit trail or speed

### **System Admin** 🔐
→ **Method 3** (manual) or **Method 4** (API)  
Why: Control and documentation

### **Analyst** 📊
→ **Method 1** (quick) or **Method 3** (manual)  
Why: Get data fast, then analyze

---

## 🚀 Get Started Now

### If you choose Method 1:
```
→ Open: EDI_WorkItems_Quick_Reference.md
→ Copy command
→ Run in VS Code Copilot Chat
→ Export results
→ Done in 5 minutes! ✅
```

### If you choose Method 2:
```
→ Open PowerShell
→ cd to Dashboards folder
→ Run: .\Query-EDIWorkItems.ps1 -OutputPath result.json
→ Done in 10 minutes! ✅
```

### If you choose Method 3:
```
→ Read: EDI_Query_Execution_Guide.md → Option 3
→ Follow steps in manual UI
→ Export results
→ Done in 20 minutes! ✅
```

### If you choose Method 4:
```
→ Read: EDI_Query_Execution_Guide.md → Option 4
→ Use provided curl commands
→ Parse JSON responses
→ Done in 15 minutes! ✅
```

---

## 📞 Still Not Sure?

**Answer these questions:**

1. Do you have VS Code? → YES = Use Method 1 ⭐
2. Need automation? → YES = Use Method 2
3. Need audit trail? → YES = Use Method 3
4. Building API integration? → YES = Use Method 4

**Still stuck?** → See `INDEX.md` for complete guidance

---

## ✅ Post-Execution

**All methods produce:**
- ✅ JSON with work items
- ✅ Metadata and statistics
- ✅ Excluded closed/cancelled items
- ✅ All required data fields

**Next steps are identical:**
1. Process results (if needed)
2. Generate report (if needed)
3. Validate results
4. Archive for audit trail

---

**Decision Ready?** → Choose your method above and start! 🚀
