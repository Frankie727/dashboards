param([int]$StartIndex = 0, [int]$BatchSize = 10)

$workItems = Get-Content -Path 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_flattened.json' -Raw | ConvertFrom-Json

# Load or initialize results
$resultsPath = 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\work_items_with_defects.json'
if (Test-Path $resultsPath) {
    $allResults = Get-Content $resultsPath -Raw | ConvertFrom-Json
} else {
    $allResults = @{
        metadata = @{
            totalCount = $workItems.Count
            itemsProcessed = 0
            itemsWithDefectIntroducedWI = 0
            itemsWithDefectIntroducedCI = 0
            executionDate = (Get-Date).ToString('yyyy-MM-dd')
            tNumberExamples = @()
        }
        results = @()
        errors = @()
    }
}

# Function to extract defect info
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
        $props = if ($jobDetails -is [hashtable]) { $jobDetails.Keys } else { ($jobDetails | Get-Member -MemberType NoteProperty).Name }
        
        foreach ($propName in $props) {
            $propValue = $jobDetails.$propName
            if ($null -eq $propValue) { continue }
            
            $propNameLower = $propName.ToLower()
            $propValueStr = $propValue.ToString()
            
            # Extract WI
            if ($propNameLower -like '*defect*introduced*wi*') {
                if ($propValueStr -match 'WI\d+') {
                    $result.defectIntroducedWI = [regex]::Match($propValueStr, 'WI\d+').Value
                }
            }
            
            # Extract T-number
            if ($propNameLower -like '*defect*introduced*checkin*' -or $propNameLower -like '*defect*introduced*ci*') {
                if ($propValueStr -match 'T\d+') {
                    $result.defectIntroducedCI = [regex]::Match($propValueStr, 'T\d+').Value
                    $result.tNumberSource = $propName
                }
            }
            
            # Fallback: any defect field with T-number
            if ($propNameLower -like '*defect*' -and -not $result.defectIntroducedCI) {
                if ($propValueStr -match 'T\d+') {
                    $result.defectIntroducedCI = [regex]::Match($propValueStr, 'T\d+').Value
                    $result.tNumberSource = $propName
                }
            }
        }
    } catch {
        $result.error = $_.Exception.Message
    }
    
    return $result
}

Write-Host "Processing work items $StartIndex through $([Math]::Min($StartIndex + $BatchSize - 1, $workItems.Count - 1))"

# Process batch
for ($i = $StartIndex; $i -lt [Math]::Min($StartIndex + $BatchSize, $workItems.Count); $i++) {
    $wi = $workItems[$i]
    Write-Host "[$i/$($workItems.Count)] Processing $wi..."
    
    # This is where the API call would happen
    # For now, we'll placeholder it
    # In actual execution, replace this with: $jobDetails = Invoke-EDI-Prod-get-job-details -jobNumber $wi
    
    $jobDetails = $null # Placeholder
    $defectInfo = Extract-DefectInfo $jobDetails $wi
    
    $allResults.results += $defectInfo
    $allResults.metadata.itemsProcessed++
    
    if ($defectInfo.defectIntroducedWI) { $allResults.metadata.itemsWithDefectIntroducedWI++ }
    if ($defectInfo.defectIntroducedCI) { 
        $allResults.metadata.itemsWithDefectIntroducedCI++
        if ($allResults.metadata.tNumberExamples.Count -lt 5) {
            $allResults.metadata.tNumberExamples += @{ 
                workItemId = $wi
                tNumber = $defectInfo.defectIntroducedCI
                source = $defectInfo.tNumberSource
            }
        }
    }
    if ($defectInfo.error) { $allResults.errors += $defectInfo }
}

# Save results
$allResults | ConvertTo-Json -Depth 10 | Out-File -Path $resultsPath -Force
Write-Host "Saved results. Total processed: $($allResults.metadata.itemsProcessed)/$($allResults.metadata.totalCount)"
