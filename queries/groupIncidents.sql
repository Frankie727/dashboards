-- Dataset "groupIncidents": closed incidents where every closed, staff-assigned task was closed by a team member.
-- Team = members of @Capabilities (e.g. GPS, INS) plus any extra @StaffCodes.
-- Tasks considered: P9_Status CLS, assigned staff present, type not EXC/MIL/TRG (cancelled and unassigned tasks are ignored).
-- TotalHours = sum of P9_ActualDuration on those tasks (offset from 1900-01-01; values beyond 999:59 are not durations and count as 0).
-- OpenToCloseHours = elapsed time from IM_SystemCreateTimeUtc to IM_CloseTimeUtc (NULL when no close time).
-- One row per qualifying incident; the dashboard applies product, created-date window and other filters.
-- Runs unchanged on EDIUAT or EDISYD. For a manual Excel export, run as-is and save the result as groupIncidents.csv.
-- <params> (Refresh-GpsData.ps1 removes this block and supplies the values)
DECLARE @From datetime = '2024-05-01';
DECLARE @Capabilities varchar(100) = 'GPS,INS';
-- Extra staff added to the capability members; set to NULL on EDISYD to use the capabilities alone.
DECLARE @StaffCodes varchar(max) = 'LS,EK,NDM,FOX,SMS,MA3,KAJ,M.D,MMA,FCM,RCL,IR,MLM,SNT,RGB,RYL,CPS,JM8,KKR,PGK,JED';
-- </params>
SET NOCOUNT ON;

DROP TABLE IF EXISTS #team;
DROP TABLE IF EXISTS #tasks;

SELECT s.GS_Code, s.GS_FullName
INTO #team
FROM dbo.GlbStaff s
WHERE s.GS_Code IN (SELECT LTRIM(RTRIM(value)) FROM STRING_SPLIT(COALESCE(@StaffCodes, ''), ','))
   OR s.GS_PK IN (
        SELECT p.G5_GS_Resource
        FROM dbo.GlbResourceCapabilityPivot p
        JOIN dbo.GlbCapability c ON c.G4_PK = p.G5_G4_Capability
        WHERE c.G4_Code IN (SELECT LTRIM(RTRIM(value)) FROM STRING_SPLIT(@Capabilities, ',')));

SELECT im.IM_PK,
       t.P9_GS_NKAssignedStaffMember AS StaffCode,
       COALESCE(tm.GS_FullName, t.P9_GS_NKAssignedStaffMember) AS StaffName,
       ISNULL(t.P9_Description, '') AS TaskDescription,
       c.G4_Code AS Capability,
       COALESCE(t.P9_CompletedTimeUtc, t.P9_SystemLastEditTimeUtc) AS ClosedUtc,
       CASE WHEN t.P9_ActualDuration > '19000101' AND t.P9_ActualDuration <= '19000211 15:59'
            THEN DATEDIFF_BIG(second, '19000101', t.P9_ActualDuration) ELSE 0 END AS Seconds,
       CASE WHEN tm.GS_Code IS NULL THEN 0 ELSE 1 END AS IsTeam
INTO #tasks
FROM dbo.IncidentMain im
JOIN dbo.ProcessTasks t ON t.P9_ParentTableCode = 'IM' AND t.P9_ParentID = im.IM_PK
LEFT JOIN #team tm ON tm.GS_Code = t.P9_GS_NKAssignedStaffMember
LEFT JOIN dbo.GlbCapability c ON c.G4_PK = t.P9_G4_RequiredCapability
WHERE im.IM_Status = 'CLS'
  AND im.IM_SystemCreateTimeUtc >= @From
  AND t.P9_Status = 'CLS'
  AND ISNULL(t.P9_GS_NKAssignedStaffMember, '') <> ''
  AND t.P9_Type NOT IN ('EXC', 'MIL', 'TRG');

WITH qualifying AS (
    SELECT IM_PK, COUNT(*) AS TotalTasks, COUNT(DISTINCT StaffCode) AS StaffCount, SUM(Seconds) AS Seconds
    FROM #tasks
    GROUP BY IM_PK
    HAVING MIN(IsTeam) = 1
)
SELECT im.IM_IncidentNumber AS IncidentNumber,
       im.IM_Product AS Product,
       im.IM_Module AS ProductArea,
       CONVERT(char(10), im.IM_SystemCreateTimeUtc, 120) AS CreatedDate,
       CONVERT(char(10), im.IM_CloseTimeUtc, 120) AS ClosedDate,
       lastTask.StaffCode AS LastClosedByCode,
       lastTask.StaffName AS LastClosedBy,
       q.StaffCount,
       staff.StaffCodes,
       staff.StaffNames,
       flow.StaffWorkflow,
       caps.Capabilities,
       q.TotalTasks,
       CAST(q.Seconds / 3600.0 AS decimal(12, 4)) AS TotalHours,
       CAST(DATEDIFF_BIG(minute, im.IM_SystemCreateTimeUtc, im.IM_CloseTimeUtc) / 60.0 AS decimal(12, 2)) AS OpenToCloseHours
FROM qualifying q
JOIN dbo.IncidentMain im ON im.IM_PK = q.IM_PK
CROSS APPLY (SELECT TOP 1 x.StaffCode, x.StaffName FROM #tasks x WHERE x.IM_PK = q.IM_PK ORDER BY x.ClosedUtc DESC) lastTask
CROSS APPLY (
    SELECT STRING_AGG(d.StaffCode, ',') WITHIN GROUP (ORDER BY d.StaffName) AS StaffCodes,
           STRING_AGG(d.StaffName, ', ') WITHIN GROUP (ORDER BY d.StaffName) AS StaffNames
    FROM (SELECT DISTINCT x.StaffCode, x.StaffName FROM #tasks x WHERE x.IM_PK = q.IM_PK) d) staff
CROSS APPLY (
    SELECT STRING_AGG(CAST(x.StaffName + ' closed ' + x.TaskDescription AS nvarchar(max)), '; ') WITHIN GROUP (ORDER BY x.ClosedUtc) AS StaffWorkflow
    FROM #tasks x WHERE x.IM_PK = q.IM_PK) flow
CROSS APPLY (
    SELECT STRING_AGG(d.Capability, ',') WITHIN GROUP (ORDER BY d.Capability) AS Capabilities
    FROM (SELECT DISTINCT x.Capability FROM #tasks x WHERE x.IM_PK = q.IM_PK AND x.Capability IS NOT NULL) d) caps
ORDER BY im.IM_SystemCreateTimeUtc DESC;

DROP TABLE #tasks;
DROP TABLE #team;
