function Extract-DefectInfo {
    param($jobDetails, $workItemId)
    
    $result = @{
        workItemId = $workItemId
        defectIntroducedWI = $null
        defectIntroducedCI = $null
        tNumberSource = $null
    }
    
    if ($null -eq $jobDetails) { return $result }
    
    try {
        $jobDetails | Get-Member -MemberType NoteProperty | ForEach-Object {
            $propName = $_.Name
            $propValue = $jobDetails.$propName
            
            if ($null -eq $propValue) { return }
            
            $propNameLower = $propName.ToLower()
            $propValueStr = $propValue.ToString()
            
            if ($propNameLower -match 'defect.*introduced.*wi|defectintroducedwi') {
                if ($propValueStr -match 'WI\d+') {
                    $result.defectIntroducedWI = [regex]::Match($propValueStr, 'WI\d+').Value
                }
            }
            
            if ($propNameLower -match 'defect.*introduced.*(checkin|ci)|defectintroducedcheckin') {
                if ($propValueStr -match 'T\d+') {
                    $result.defectIntroducedCI = [regex]::Match($propValueStr, 'T\d+').Value
                    $result.tNumberSource = $propName
                }
            }
            
            if ($propNameLower -match 'defect' -and $result.defectIntroducedCI -eq $null) {
                if ($propValueStr -match 'T\d+') {
                    $result.defectIntroducedCI = [regex]::Match($propValueStr, 'T\d+').Value
                    $result.tNumberSource = $propName
                }
            }
        }
    } catch {
        Write-Warning "Error extracting defect info from $workItemId : $_"
    }
    
    return $result
}
