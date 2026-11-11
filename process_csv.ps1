# CSV Processing Script for Work Items Filtering

function Parse-WorkItemsCSV {
    param(
        [string]$CsvContent,
        [string]$Product,
        [int]$Skip
    )
    
    # Handle empty content
    if ([string]::IsNullOrWhiteSpace($CsvContent)) {
        return @{
            product = $Product
            skip = $Skip
            beforeFilterCount = 0
            afterFilterCount = 0
            items = @()
            error = "Empty response"
        }
    }
    
    # Split into lines
    $lines = $CsvContent -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    
    if ($lines.Count -eq 0) {
        return @{
            product = $Product
            skip = $Skip
            beforeFilterCount = 0
            afterFilterCount = 0
            items = @()
        }
    }
    
    # Parse CSV - first line is header
    $header = $null
    $dataLines = @()
    $statusColumnIndex = -1
    $idColumnIndex = -1
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($i -eq 0) {
            $header = $lines[$i] -split ","
            # Find status and id/number columns (case-insensitive)
            for ($j = 0; $j -lt $header.Count; $j++) {
                $colName = $header[$j].Trim().ToLower()
                if ($colName -eq "status") { $statusColumnIndex = $j }
                if ($colName -in @("number", "id", "workitem", "workitemnumber")) { $idColumnIndex = $j }
            }
        }
        else {
            $dataLines += $lines[$i]
        }
    }
    
    $beforeCount = $dataLines.Count
    $filteredItems = @()
    
    # Parse each data line
    foreach ($line in $dataLines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        
        $fields = $line -split ","
        $status = if ($statusColumnIndex -ge 0 -and $statusColumnIndex -lt $fields.Count) {
            $fields[$statusColumnIndex].Trim()
        }
        else {
            ""
        }
        
        $id = if ($idColumnIndex -ge 0 -and $idColumnIndex -lt $fields.Count) {
            $fields[$idColumnIndex].Trim()
        }
        else {
            ""
        }
        
        # Filter: EXCLUDE CLS, CAN, or empty status
        if ($status -notin @("CLS", "CAN", "")) {
            $filteredItems += $id
        }
    }
    
    return @{
        product = $Product
        skip = $Skip
        beforeFilterCount = $beforeCount
        afterFilterCount = $filteredItems.Count
        items = $filteredItems
    }
}

Write-Host "Processing script loaded and ready."
