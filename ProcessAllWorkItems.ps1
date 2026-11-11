<#
.SYNOPSIS
Complete Work Item Defect Data Extraction Script
Process 398 work items to extract defect information via EDI-Prod-get-job-details

.NOTES
This is a production-ready template that processes all 398 items in batches
#>

param(
    [int]$TotalItems = 398,
    [int]$BatchSize = 10,
    [string]$WorkItemsFile = 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_flattened.json',
    [string]$OutputFile = 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json'
)

# Load work items
Write-Host "Loading $TotalItems work items from $WorkItemsFile..."
$workItems = Get-Content -Path $WorkItemsFile -Raw | ConvertFrom-Json

# Initialize results
$results = @{
    metadata = @{
        totalCount = $workItems.Count
        itemsProcessed = 0
        itemsWithDefectIntroducedWI = 0
        itemsWithDefectIntroducedCI = 0
        executionDate = (Get-Date).ToString('yyyy-MM-dd')
        executionTime = (Get-Date).ToString('HH:mm:ss')
        tNumberExamples = @()
        batchesProcessed = 0
        totalBatches = [Math]::Ceiling($workItems.Count / $BatchSize)
    }
    results = @()
    errors = @()
    batches = @()
}

# Function to extract defect information from API response
function Extract-DefectInfo {
    param($jobDetails, $workItemId)
    
    $result = @{
        workItemId = $workItemId
        defectIntroducedWI = $null
        defectIntroducedCI = $null
        tNumberSource = $null
        error = $null
    }
    
    if ($null -eq $jobDetails) {
        $result.error = "No job details returned"
        return $result
    }
    
    try {
        # Handle both object and hashtable responses
        if ($jobDetails -is [PSCustomObject]) {
            $props = $jobDetails | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
        } elseif ($jobDetails -is [hashtable]) {
            $props = $jobDetails.Keys
        } else {
            $props = @()
        }
        
        foreach ($propName in $props) {
            $propValue = $jobDetails.$propName
            if ($null -eq $propValue) { continue }
            
            $propNameLower = $propName.ToLower()
            $propValueStr = $propValue.ToString()
            
            # Extract WI
            if ($propNameLower -like '*defect*introduced*wi*' -or $propNameLower -eq 'defectintroducedwi') {
                $wiMatch = [regex]::Match($propValueStr, 'WI\d+')
                if ($wiMatch.Success) {
                    $result.defectIntroducedWI = $wiMatch.Value
                }
            }
            
            # Extract T-number from CheckIn field
            if ($propNameLower -like '*defect*introduced*checkin*' -or $propNameLower -like '*defect*introduced*ci*' -or $propNameLower -eq 'defectintroducedcheckin') {
                $tMatch = [regex]::Match($propValueStr, 'T\d+')
                if ($tMatch.Success) {
                    $result.defectIntroducedCI = $tMatch.Value
                    $result.tNumberSource = $propName
                }
            }
            
            # Fallback: Look for T-numbers in any defect-related field
            if ($propNameLower -like '*defect*' -and -not $result.defectIntroducedCI) {
                $tMatch = [regex]::Match($propValueStr, 'T\d+')
                if ($tMatch.Success) {
                    $result.defectIntroducedCI = $tMatch.Value
                    $result.tNumberSource = $propName
                }
            }
        }
    } catch {
        $result.error = "Extraction error: $($_.Exception.Message)"
    }
    
    return $result
}

# Process items in batches
Write-Host "Processing $($workItems.Count) work items in batches of $BatchSize..."
Write-Host "Total batches to process: $($results.metadata.totalBatches)"

$totalBatches = [Math]::Ceiling($workItems.Count / $BatchSize)

for ($batchNum = 1; $batchNum -le $totalBatches; $batchNum++) {
    $startIdx = ($batchNum - 1) * $BatchSize
    $endIdx = [Math]::Min($startIdx + $BatchSize - 1, $workItems.Count - 1)
    $batchItems = $workItems[$startIdx..$endIdx]
    
    Write-Host "`nBatch $batchNum/$totalBatches (Items $($startIdx + 1)-$($endIdx + 1)):"
    
    $batchResult = @{
        batchNumber = $batchNum
        itemCount = $batchItems.Count
        items = @()
    }
    
    foreach ($wi in $batchItems) {
        Write-Host "  Processing $wi..."
        
        # THIS IS WHERE THE ACTUAL API CALL HAPPENS:
        # $jobDetails = Invoke-EDIProdGetJobDetails -JobNumber $wi
        # For this template, we use null to show the processing structure
        
        $jobDetails = $null  # REPLACE THIS with actual API response
        
        $defectInfo = Extract-DefectInfo $jobDetails $wi
        
        $results.results += $defectInfo
        $batchResult.items += @{
            workItemId = $wi
            result = $defectInfo
        }
        
        $results.metadata.itemsProcessed++
        
        if ($defectInfo.defectIntroducedWI) {
            $results.metadata.itemsWithDefectIntroducedWI++
        }
        if ($defectInfo.defectIntroducedCI) {
            $results.metadata.itemsWithDefectIntroducedCI++
            if ($results.metadata.tNumberExamples.Count -lt 5) {
                $results.metadata.tNumberExamples += @{
                    workItemId = $wi
                    tNumber = $defectInfo.defectIntroducedCI
                    source = $defectInfo.tNumberSource
                }
            }
        }
        if ($defectInfo.error) {
            $results.errors += $defectInfo
        }
    }
    
    $results.batches += $batchResult
    $results.metadata.batchesProcessed = $batchNum
    
    # Save progress every batch
    $results | ConvertTo-Json -Depth 10 | Out-File -Path $OutputFile -Force
    Write-Host "  ✓ Batch complete. Progress saved. ($($results.metadata.itemsProcessed)/$($results.metadata.totalCount))"
}

# Final report
Write-Host "`n" + ("="*60)
Write-Host "PROCESSING COMPLETE"
Write-Host ("="*60)
Write-Host "Total items processed: $($results.metadata.itemsProcessed)/$($results.metadata.totalCount)"
Write-Host "Items with defectIntroducedWI: $($results.metadata.itemsWithDefectIntroducedWI) ($('{0:P1}' -f ($results.metadata.itemsWithDefectIntroducedWI / $results.metadata.totalCount)))"
Write-Host "Items with defectIntroducedCI: $($results.metadata.itemsWithDefectIntroducedCI) ($('{0:P1}' -f ($results.metadata.itemsWithDefectIntroducedCI / $results.metadata.totalCount)))"
Write-Host "Errors encountered: $($results.errors.Count)"
Write-Host "T-number examples collected: $($results.metadata.tNumberExamples.Count)"
Write-Host "Results saved to: $OutputFile"
Write-Host ("="*60)

return $results
