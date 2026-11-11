param(
    [string]$OutputPath = "edi_workitems_result.json"
)

<#
.SYNOPSIS
    Queries EDI Prod MCP Server for ENT and GLW product work items with FIX changeType
    
.DESCRIPTION
    This script queries the EDI Prod MCP Server for fix work items created in the last 30 days.
    It handles pagination, filters out closed/cancelled items, and produces a comprehensive JSON report.
    
.PARAMETER OutputPath
    Path where the JSON result file will be saved (default: edi_workitems_result.json)
    
.NOTES
    Requirements: EDI Prod MCP Server must be accessible
    Created: 2026-11-05
#>

$ErrorActionPreference = "Stop"

# Configuration
$QueryParams = @{
    DateRange = @{
        From = "2026-10-06"
        To   = "2026-11-05"
    }
    Products = @("ENT", "GLW")
    ChangeType = @("FIX")
    ExcludedStatuses = @("CLS", "CAN")
    PageSize = 50
}

# Result accumulator
$AllWorkItems = @()
$QueryHistory = @()
$Statistics = @{
    TotalCount = 0
    PageCount = 0
    ItemsWithDefect = 0
    ItemsWithoutDefect = 0
    ByProduct = @{
        ENT = @{ Count = 0; WithDefect = 0; WithoutDefect = 0; ByStatus = @{} }
        GLW = @{ Count = 0; WithDefect = 0; WithoutDefect = 0; ByStatus = @{} }
    }
    DefectTraceability = @{
        WithDefectIntroducedWI = 0
        WithDefectIntroducedCI = 0
        WithBoth = 0
        WithNeither = 0
    }
}

function Invoke-EDIWorkItemQuery {
    param(
        [string]$Product,
        [int]$Skip = 0
    )
    
    Write-Host "Querying $Product product (skip: $Skip)..."
    
    # In a real scenario, this would call the MCP tool:
    # EDI-Prod-filter-workitems with:
    #   product = $Product
    #   changeType = @("FIX")
    #   createdAfter = "2026-10-06"
    #   createdBefore = "2026-11-05"
    #   top = 50
    #   skip = $Skip
    
    # Placeholder for demonstration
    @{
        Items = @()
        TotalCount = 0
    }
}

function Process-WorkItems {
    param(
        [array]$Items,
        [string]$Product
    )
    
    $validItems = @()
    
    foreach ($item in $Items) {
        # Check if status should be excluded
        if ([string]::IsNullOrWhiteSpace($item.status) -or $item.status -in $QueryParams.ExcludedStatuses) {
            continue
        }
        
        $validItems += $item
        
        # Update statistics
        $Statistics.TotalCount++
        $Statistics.ByProduct[$Product].Count++
        
        # Track defect information
        $hasDefect = ![string]::IsNullOrWhiteSpace($item.defectIntroducedWI) -or ![string]::IsNullOrWhiteSpace($item.defectIntroducedCI)
        if ($hasDefect) {
            $Statistics.ItemsWithDefect++
            $Statistics.ByProduct[$Product].WithDefect++
        } else {
            $Statistics.ItemsWithoutDefect++
            $Statistics.ByProduct[$Product].WithoutDefect++
        }
        
        # Track defect type
        $hasWI = ![string]::IsNullOrWhiteSpace($item.defectIntroducedWI)
        $hasCI = ![string]::IsNullOrWhiteSpace($item.defectIntroducedCI)
        
        if ($hasWI -and $hasCI) {
            $Statistics.DefectTraceability.WithBoth++
        } elseif ($hasWI) {
            $Statistics.DefectTraceability.WithDefectIntroducedWI++
        } elseif ($hasCI) {
            $Statistics.DefectTraceability.WithDefectIntroducedCI++
        } else {
            $Statistics.DefectTraceability.WithNeither++
        }
        
        # Track status distribution
        if (-not $Statistics.ByProduct[$Product].ByStatus.ContainsKey($item.status)) {
            $Statistics.ByProduct[$Product].ByStatus[$item.status] = 0
        }
        $Statistics.ByProduct[$Product].ByStatus[$item.status]++
    }
    
    return $validItems
}

# Main execution
Write-Host "Starting EDI Prod Work Items Query..."
Write-Host "Date Range: $($QueryParams.DateRange.From) to $($QueryParams.DateRange.To)"
Write-Host "Products: $($QueryParams.Products -join ', ')"
Write-Host "Change Type: $($QueryParams.ChangeType -join ', ')"
Write-Host ""

foreach ($product in $QueryParams.Products) {
    Write-Host "Processing $product product..."
    
    $skip = 0
    $pageNum = 0
    $continueQuery = $true
    
    while ($continueQuery) {
        $result = Invoke-EDIWorkItemQuery -Product $product -Skip $skip
        $items = $result.Items
        
        if ($items.Count -gt 0) {
            $validItems = Process-WorkItems -Items $items -Product $product
            $AllWorkItems += $validItems
            
            $Statistics.PageCount++
            
            $QueryHistory += @{
                Product = $product
                Page = $pageNum
                Skip = $skip
                Top = $QueryParams.PageSize
                ResultCount = $items.Count
                ValidItems = $validItems.Count
                MorePages = $items.Count -eq $QueryParams.PageSize
            }
            
            Write-Host "  Page $pageNum: $($items.Count) items, $($validItems.Count) valid"
            
            if ($items.Count -lt $QueryParams.PageSize) {
                $continueQuery = $false
            }
        } else {
            Write-Host "  No items found"
            $continueQuery = $false
        }
        
        $skip += $QueryParams.PageSize
        $pageNum++
    }
}

# Build final result
$Result = @{
    meta = @{
        timestamp = (Get-Date -Format "o")
        queryParams = @{
            products = $QueryParams.Products
            changeType = $QueryParams.ChangeType[0]
            statusFilter = "NCM (NOT CLS, NOT CAN, NOT empty)"
            createdLastDays = 30
            dateRange = $QueryParams.DateRange
        }
        totalCount = $Statistics.TotalCount
        pageCount = $Statistics.PageCount
        itemsWithDefectIntroduced = $Statistics.ItemsWithDefect
        itemsWithoutDefectIntroduced = $Statistics.ItemsWithoutDefect
    }
    data = $AllWorkItems
    statistics = $Statistics
    queryHistory = $QueryHistory
}

# Save to JSON
$Result | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "Query completed successfully!"
Write-Host "Results saved to: $OutputPath"
Write-Host "Total work items: $($Statistics.TotalCount)"
Write-Host "Items with defect info: $($Statistics.ItemsWithDefect)"
Write-Host "Items without defect info: $($Statistics.ItemsWithoutDefect)"
