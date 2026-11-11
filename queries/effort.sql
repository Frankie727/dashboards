-- Dataset "effort": GPS staff time per staff member, job and activity date (all record types), from ProcessTasks.P9_ActualDuration.
-- ActivityDate = task completion date (UTC), or creation date when not completed.
-- P9_ActualDuration is a datetime offset from 1900-01-01 (displayed as HHH:MM, e.g. 1900-01-01 01:07 = 001:07).
-- Values beyond 999:59 (1900-02-11 15:59) are real dates, not durations, and are excluded.
-- RecordType: IM incident, ING incident group, WKI work item, WKP project, IMT incident triage, OQ CRM communication (OrgSalesCall).
-- Runs unchanged on EDIUAT or EDISYD. For a manual Excel export, run as-is and save the result as effort.csv.
-- <params> (Refresh-GpsData.ps1 removes this block and supplies the values)
DECLARE @From datetime = '2024-05-01';
DECLARE @Capability varchar(3) = 'GPS';
-- Staff = live capability members plus any extra @StaffCodes; set @StaffCodes to NULL on EDISYD to use the capability alone.
DECLARE @StaffCodes varchar(max) = 'LS,EK,NDM,FOX,SMS,MA3,KAJ,M.D,MMA,FCM,RCL,IR,MLM,SNT,RGB,RYL,CPS,JM8,KKR,PGK,JED';
-- </params>

WITH gps AS (
    SELECT s.GS_Code, s.GS_FullName
    FROM dbo.GlbStaff s
    WHERE s.GS_Code IN (SELECT LTRIM(RTRIM(value)) FROM STRING_SPLIT(COALESCE(@StaffCodes, ''), ','))
       OR s.GS_PK IN (
            SELECT p.G5_GS_Resource
            FROM dbo.GlbResourceCapabilityPivot p
            JOIN dbo.GlbCapability c ON c.G4_PK = p.G5_G4_Capability
            WHERE c.G4_Code = @Capability)
), tasks AS (
    SELECT t.P9_GS_NKAssignedStaffMember AS StaffCode, t.P9_ParentTableCode AS RecordType, t.P9_ParentID AS ParentId,
           CAST(COALESCE(t.P9_CompletedTimeUtc, t.P9_SystemCreateTimeUtc) AS date) AS ActivityDate,
           COUNT(*) AS Tasks,
           SUM(CASE WHEN t.P9_Status = 'SUS' THEN 1 ELSE 0 END) AS SuspendedTasks,
           SUM(DATEDIFF_BIG(second, '19000101', t.P9_ActualDuration)) AS Seconds
    FROM dbo.ProcessTasks t
    WHERE t.P9_GS_NKAssignedStaffMember IN (SELECT GS_Code FROM gps)
      AND t.P9_ActualDuration > '19000101'
      AND t.P9_ActualDuration <= '19000211 15:59'
      AND COALESCE(t.P9_CompletedTimeUtc, t.P9_SystemCreateTimeUtc) >= @From
    GROUP BY t.P9_GS_NKAssignedStaffMember, t.P9_ParentTableCode, t.P9_ParentID,
             CAST(COALESCE(t.P9_CompletedTimeUtc, t.P9_SystemCreateTimeUtc) AS date)
)
SELECT x.StaffCode,
       g.GS_FullName AS StaffName,
       x.RecordType,
       COALESCE(im.IM_IncidentNumber, wki.WKI_WorkItemNumber, ing.ING_IncidentGroupNumber, imt.IMT_TriageNumber, wkp.WKP_ProjectNumber, '') AS JobNumber,
       COALESCE(im.IM_Description, wki.WKI_Summary, ing.ING_Description, imt.IMT_SupportDescription, wkp.WKP_Summary, oq.OQ_CallSummary, '') AS JobTitle,
       CONVERT(char(10), x.ActivityDate, 120) AS ActivityDate,
       x.Tasks,
       x.SuspendedTasks,
       CAST(x.Seconds / 3600.0 AS decimal(12, 4)) AS ActualHours
FROM tasks x
JOIN gps g ON g.GS_Code = x.StaffCode
LEFT JOIN dbo.IncidentMain im            ON x.RecordType = 'IM'  AND im.IM_PK   = x.ParentId
LEFT JOIN dbo.WorkItem wki               ON x.RecordType = 'WKI' AND wki.WKI_PK = x.ParentId
LEFT JOIN dbo.IncidentManagementGroup ing ON x.RecordType = 'ING' AND ing.ING_PK = x.ParentId
LEFT JOIN dbo.IncidentTriage imt         ON x.RecordType = 'IMT' AND imt.IMT_PK = x.ParentId
LEFT JOIN dbo.WorkProject wkp            ON x.RecordType = 'WKP' AND wkp.WKP_PK = x.ParentId
LEFT JOIN dbo.OrgSalesCall oq            ON x.RecordType = 'OQ'  AND oq.OQ_PK   = x.ParentId
ORDER BY ActivityDate DESC, ActualHours DESC;

