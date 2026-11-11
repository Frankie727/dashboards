param(
    [int]$BatchSize = 5,
    [int]$StartIndex = 0
)

# Load work items
$workItems = Get-Content 'C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\all_work_item_ids_complete.json' | ConvertFrom-Json
$totalItems = $workItems.Count

Write-Output @"
===============================================
Defect Details Extraction Script
===============================================
Total Work Items: $totalItems
Batch Size: $BatchSize
Starting Index: $StartIndex
===============================================
"@

# Initialize tracking
$results = @()
$stats = @{
    totalProcessed = 0
    defectWIFound = 0
    defectCIFound = 0
    tNumberExamples = @()
    errors = @()
}

# Helper function to extract T-number from text
function Extract-TNumber {
    param([string]$text)
    if ([string]::IsNullOrEmpty($text)) { return $null }
    
    # Look for pattern T followed by digits (e.g., T43227671)
    $match = [regex]::Match($text, 'T(\d{5,})')
    if ($match.Success) {
        return $match.Value
    }
    return $null
}

# Helper function to extract T-number from UUID field if present
function Extract-TNumberFromField {
    param([string]$fieldValue)
    if ([string]::IsNullOrEmpty($fieldValue)) { return $null }
    
    # Check if it's a UUID format
    if ($fieldValue -match '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$') {
        Write-Output "Found UUID: $fieldValue"
        return $null  # Return null for UUID; we'll handle this separately
    }
    
    # Try to extract T-number
    return Extract-TNumber $fieldValue
}

# Process work items in batches
$batchCount = [Math]::Ceiling($totalItems / $BatchSize)
Write-Output "`nProcessing $totalItems items in $batchCount batches...`n"

for ($batchIndex = 0; $batchIndex -lt $batchCount; $batchIndex++) {
    $batchStart = $batchIndex * $BatchSize
    $batchEnd = [Math]::Min($batchStart + $BatchSize - 1, $totalItems - 1)
    
    Write-Output "Batch $($batchIndex + 1)/$batchCount (items $($batchStart + 1)-$($batchEnd + 1))"
    
    $batchItems = $workItems[$batchStart..$batchEnd]
    
    # Create batch request data
    $batchData = @{
        batchIndex = $batchIndex
        batchNumber = $batchIndex + 1
        items = @()
    }
    
    foreach ($workItemId in $batchItems) {
        $batchData.items += @{
            workItemId = $workItemId
            status = "pending"
        }
    }
    
    # Output batch info for external processing
    $batchJsonFile = "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards\batch_$($batchIndex).json"
    $batchData | ConvertTo-Json | Set-Content $batchJsonFile
    Write-Output "  Created batch file: batch_$($batchIndex).json"
    Write-Output "  Waiting for external processing...`n"
}

Write-Output @"

===============================================
Batch files created successfully.
Waiting for EDI-Prod-get-job-details calls...
===============================================
"@
