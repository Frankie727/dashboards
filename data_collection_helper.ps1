# Master data collection script that will accumulate results from all API calls

$resultsFile = 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json'

# Initialize if doesn't exist
if (-not (Test-Path $resultsFile)) {
    $initialResults = @{
        metadata = @{
            totalCount = 398
            itemsProcessed = 0
            itemsWithDefectIntroducedWI = 0
            itemsWithDefectIntroducedCI = 0
            executionDate = (Get-Date).ToString('yyyy-MM-dd')
            tNumberExamples = @()
        }
        results = @()
        errors = @()
    }
    $initialResults | ConvertTo-Json -Depth 10 | Out-File -Path $resultsFile -Force
}

# Function to add result
function Add-ProcessedItem {
    param(
        [string]$WorkItemId,
        [string]$DefectWI,
        [string]$DefectCI,
        [string]$TNumberSource = $null,
        [string]$Error = $null
    )
    
    $results = Get-Content $resultsFile -Raw | ConvertFrom-Json
    
    $newResult = @{
        workItemId = $WorkItemId
        defectIntroducedWI = $DefectWI
        defectIntroducedCI = $DefectCI
        tNumberSource = $TNumberSource
    }
    
    $results.results += $newResult
    $results.metadata.itemsProcessed++
    
    if ($DefectWI) { $results.metadata.itemsWithDefectIntroducedWI++ }
    if ($DefectCI) {
        $results.metadata.itemsWithDefectIntroducedCI++
        if ($results.metadata.tNumberExamples.Count -lt 5) {
            $results.metadata.tNumberExamples += @{
                workItemId = $WorkItemId
                tNumber = $DefectCI
                source = $TNumberSource
            }
        }
    }
    if ($Error) { $results.errors += @{ workItemId = $WorkItemId; error = $Error } }
    
    $results | ConvertTo-Json -Depth 10 | Out-File -Path $resultsFile -Force
}

# Export for use
Export-ModuleMember -Function Add-ProcessedItem
