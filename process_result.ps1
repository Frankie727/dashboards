param([string]$Product, [int]$Skip, [string]$CsvData)

$dataDir = "C:\Users\Francesco.Mangione\GitHub Repo - Francesco\Dashboards"
$resultFile = "$dataDir\api_results.json"

# Parse the JSON file
$results = Get-Content $resultFile -Raw | ConvertFrom-Json
$productKey = $Product.ToLower()

# Store the raw CSV for this batch
$results.$productKey += @{
    skip = $Skip
    csvData = $CsvData
}

# Save back
$results | ConvertTo-Json -Depth 10 | Out-File $resultFile -Encoding UTF8
Write-Host "Stored $Product results for skip=$Skip"
