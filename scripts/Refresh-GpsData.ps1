<#
.SYNOPSIS
Rebuilds data/gps-data.<Source>.js for the GPS Dashboard from EDIUAT, EDISYD or exported CSV files.
The dashboard header's Data source switch picks which file to load.

.EXAMPLE
./scripts/Refresh-GpsData.ps1 -Source EDIUAT
./scripts/Refresh-GpsData.ps1 -Source EDISYD -Server <host> -Database <database> -WindowsAuth -UseCapability
./scripts/Refresh-GpsData.ps1 -Source Csv -CsvFolder C:\Exports\GPS
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('EDIUAT', 'EDISYD', 'Csv')][string]$Source,
    [string]$Server,
    [string]$Database,
    [switch]$WindowsAuth,
    [switch]$TrustServerCertificate,
    [string]$CsvFolder,
    [datetime]$From = '2024-05-01',
    [string]$Capability = 'GPS',
    # Capabilities whose members count as the team for the groupIncidents dataset.
    [string]$Capabilities = 'GPS,INS',
    [string]$StaffCodes = 'LS,EK,NDM,FOX,SMS,MA3,KAJ,M.D,MMA,FCM,RCL,IR,MLM,SNT,RGB,RYL,CPS,JM8,KKR,PGK,JED',
    # Use only live capability membership, without the extra -StaffCodes (EDIUAT capability membership is incomplete).
    [switch]$UseCapability,
    [string]$OutFile
)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
if (-not $OutFile) { $OutFile = Join-Path $root "data\gps-data.$Source.js" }

# Each dataset becomes window.GPS_DATA.<name>; the CSV import expects <name>.csv with the same columns.
$datasets = [ordered]@{ effort = 'effort.sql'; groupIncidents = 'groupIncidents.sql' }
$numericColumns = 'Tasks', 'SuspendedTasks', 'ActualHours', 'StaffCount', 'TotalTasks', 'TotalHours', 'OpenToCloseHours'

function Invoke-Dataset {
    param([System.Data.SqlClient.SqlConnection]$Connection, [string]$QueryFile)

    $sql = Get-Content -Raw -Path (Join-Path $root "queries\$QueryFile")
    $sql = [regex]::Replace($sql, '(?s)-- <params>.*?-- </params>', '')

    $command = $Connection.CreateCommand()
    $command.CommandText = $sql
    $command.CommandTimeout = 300
    $command.Parameters.Add('@From', [System.Data.SqlDbType]::DateTime).Value = $From
    $command.Parameters.Add('@Capability', [System.Data.SqlDbType]::VarChar, 3).Value = $Capability
    $command.Parameters.Add('@Capabilities', [System.Data.SqlDbType]::VarChar, 100).Value = $Capabilities
    $command.Parameters.Add('@StaffCodes', [System.Data.SqlDbType]::VarChar, -1).Value = if ($UseCapability) { [DBNull]::Value } else { $StaffCodes }

    $table = [System.Data.DataTable]::new()
    $reader = $command.ExecuteReader()
    try { $table.Load($reader) } finally { $reader.Dispose() }

    foreach ($row in $table.Rows) {
        $item = [ordered]@{}
        foreach ($column in $table.Columns) {
            $value = $row[$column]
            $item[$column.ColumnName] = if ($value -is [DBNull]) { $null }
                elseif ($value -is [string]) { $value.Trim() }
                elseif ($value -is [decimal]) { [double]$value }
                else { $value }
        }
        [pscustomobject]$item
    }
}

$data = [ordered]@{
    meta = [ordered]@{
        source       = $Source
        location     = $null
        refreshedUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        from         = $From.ToString('yyyy-MM-dd')
        capabilities = $Capabilities
    }
}

if ($Source -eq 'Csv') {
    if (-not $CsvFolder) { throw '-CsvFolder is required when -Source is Csv.' }
    $data.meta.location = $CsvFolder
    foreach ($name in $datasets.Keys) {
        $path = Join-Path $CsvFolder "$name.csv"
        if (-not (Test-Path $path)) { throw "Missing $path. Export the result of queries\$($datasets[$name]) to this file." }
        $data[$name] = @(Import-Csv -Path $path | ForEach-Object {
            foreach ($column in $numericColumns) {
                if ($_.PSObject.Properties[$column]) { $_.$column = if ([string]::IsNullOrWhiteSpace($_.$column)) { $null } else { [double]$_.$column } }
            }
            $_
        })
    }
}
else {
    if ($Source -eq 'EDIUAT') {
        if (-not $Server) { $Server = 'ediuat.db.sand.wtg.zone' }
        if (-not $Database) { $Database = 'Odysseyediuat' }
    }
    if (-not $Server -or -not $Database) { throw "-Server and -Database are required when -Source is $Source." }
    $data.meta.location = "$Server/$Database"

    $builder = [System.Data.SqlClient.SqlConnectionStringBuilder]::new()
    $builder['Data Source'] = $Server
    $builder['Initial Catalog'] = $Database
    $builder['Encrypt'] = $true
    $builder['TrustServerCertificate'] = [bool]$TrustServerCertificate
    $builder['ApplicationIntent'] = 'ReadOnly'
    $builder['Application Name'] = 'GPS Dashboard refresh'

    $connection = [System.Data.SqlClient.SqlConnection]::new()
    if ($WindowsAuth) {
        $builder['Integrated Security'] = $true
        $connection.ConnectionString = $builder.ConnectionString
    }
    else {
        $credential = Get-Credential -Message "SQL login for $Server/$Database"
        $password = $credential.Password.Copy()
        $password.MakeReadOnly()
        $connection.ConnectionString = $builder.ConnectionString
        $connection.Credential = [System.Data.SqlClient.SqlCredential]::new($credential.UserName, $password)
    }

    try {
        $connection.Open()
        foreach ($name in $datasets.Keys) {
            $data[$name] = @(Invoke-Dataset -Connection $connection -QueryFile $datasets[$name])
        }
    }
    finally {
        $connection.Dispose()
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path $OutFile -Parent) | Out-Null
$json = $data | ConvertTo-Json -Depth 6 -Compress
Set-Content -Path $OutFile -Value "window.GPS_DATA = $json;" -Encoding utf8

foreach ($name in $datasets.Keys) {
    Write-Host ("{0}: {1} rows" -f $name, $data[$name].Count)
}
Write-Host "Wrote $OutFile from $Source ($($data.meta.location))"
