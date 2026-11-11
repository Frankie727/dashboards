# Dashboard Builder for 300 Work Items
# This script orchestrates fetching all work item details and building the dashboard

# Initialize dashboard structure
$dashboard = @{
    meta = @{
        timestamp = (Get-Date -AsUTC -Format "o").Replace("Z", "+11:00")
        totalCount = 300
        itemsWithDefectIntroduced = 0
        itemsWithoutDefectIntroduced = 0
        queryParams = @{
            changeType = "FIX"
            products = @("ENT", "GLW")
            statusFilter = "NOT CLS AND NOT CAN AND NOT empty"
            createdDateRange = "2026-10-06 to 2026-11-05"
        }
    }
    data = @()
}

# Load work items
$mapping = Get-Content "work_items_mapping.json" | ConvertFrom-Json
$totalItems = $mapping.Count

Write-Host "Loaded $totalItems work items"
Write-Host "Starting to fetch job details..."
Write-Host ""

# Process counter
$processed = 0
$withDefect = 0
$withoutDefect = 0

# Store successful items for building dashboard
$items = @()

# Note: The actual MCP calls will be made by the system
# This structure prepares the data for when responses are received

Write-Host "Preparation complete. Ready to process $totalItems work items"
Write-Host "Dashboard structure initialized"

# Save template
$dashboard | ConvertTo-Json -Depth 10 | Set-Content "dashboard_template_final.json"
Write-Host "Template saved"
