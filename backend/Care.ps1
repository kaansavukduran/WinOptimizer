# Windows care evidence adapted from SysMender (MIT), Copyright (c) 2026 Oguzhan DUYAR.
# Pending-restart checks also derive from WinUtil (MIT), Copyright (c) 2022 CT Tech Group LLC.
# Pinned sources and full notices: docs/SYSMENDER-DONOR.md and native/licenses/.
# Local inspection only. No repair, service configuration, event deletion or dump-content reads.
function Read-CareSection([string]$Name,[string]$Source,[scriptblock]$Read) {
  Write-OperationStatus ('care-'+$Name) 'running'
  try {
    $rows=@(& $Read);$limited=$rows.Count -gt 100;$items=@($rows|Select-Object -First 100)
    Write-OperationStatus ('care-'+$Name) 'complete' $items.Count
    if($limited){Write-OperationStatus ('care-'+$Name) 'skipped' -1 '' 'limit'}
    return @{id=$Name;source=$Source;status=if($items.Count){'available'}else{'empty'};items=$items;shown=$items.Count;limited=$limited}
  }catch {
    Write-OperationStatus ('care-'+$Name) 'failed' -1 '' 'provider-unavailable'
    return @{id=$Name;source=$Source;status='unavailable';items=@();shown=0;limited=$false}
  }
}
function Convert-CareEvent($Event) {
  $message=$null;try{$message=[string]$Event.Message;if($message.Length -gt 2000){$message=$message.Substring(0,2000)}}catch{}
  [pscustomobject]@{at=if($Event.TimeCreated){$Event.TimeCreated.ToUniversalTime().ToString('o')}else{$null};provider=$Event.ProviderName;eventId=$Event.Id;level=$Event.Level;recordId=$Event.RecordId;message=$message}
}
function Read-CareEvents([string]$Name) {
  try {$events=@(Get-WinEvent -FilterHashtable @{LogName=$Name;Level=1,2;StartTime=(Get-Date).AddDays(-7)} -MaxEvents 101 -ErrorAction Stop)}
  catch {if($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*'){$events=@()}else{throw}}
  foreach($event in $events){Convert-CareEvent $event}
}
function Get-CareReadiness {
  $os=Get-CimInstance Win32_OperatingSystem -OperationTimeoutSec 10 -ErrorAction Stop
  # Preserve unreadable indicators as unknown, never as "no restart needed".
  $signals=@();$unknown=$false
  $paths=[ordered]@{CBS='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending';WindowsUpdate='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'}
  foreach($entry in $paths.GetEnumerator()){try{if(Test-Path -LiteralPath $entry.Value -ErrorAction Stop){$signals+=$entry.Key}}catch{$unknown=$true}}
  try {
    $manager=Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -ErrorAction Stop
    if(@($manager.PendingFileRenameOperations|Where-Object {-not [string]::IsNullOrWhiteSpace([string]$_)}).Count){$signals+='PendingFileRenameOperations'}
  }catch{$unknown=$true}
  [pscustomobject]@{name=$os.Caption;version=$os.Version;build=$os.BuildNumber;bootAt=$os.LastBootUpTime.ToUniversalTime().ToString('o');uptimeSeconds=[math]::Max(0,[math]::Floor(((Get-Date)-$os.LastBootUpTime).TotalSeconds));restartSignals=$signals;restartUnknown=$unknown}
}
function Get-CareUpdateHistory {
  $session=New-Object -ComObject Microsoft.Update.Session
  $searcher=$null
  try {
    $searcher=$session.CreateUpdateSearcher();$count=[math]::Min(101,$searcher.GetTotalHistoryCount())
    if($count -gt 0){foreach($item in $searcher.QueryHistory(0,$count)){
      [pscustomobject]@{at=$item.Date.ToUniversalTime().ToString('o');name=$item.Title;operation=[int]$item.Operation;resultCode=[int]$item.ResultCode;hresult=('0x{0:X8}' -f ([int64]$item.HResult -band 4294967295))}
    }}
  }finally{if($searcher){[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($searcher)};[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($session)}
}
function Get-LocalCare {
  $sections=@()
  $sections+=Read-CareSection 'readiness' 'CIM + local pending-restart indicators' {Get-CareReadiness}
  $sections+=Read-CareSection 'defender' 'Get-MpComputerStatus' {
    $d=Get-MpComputerStatus -ErrorAction Stop
    [pscustomobject]@{name='Microsoft Defender';mode=$d.AMRunningMode;serviceEnabled=$d.AMServiceEnabled;antivirusEnabled=$d.AntivirusEnabled;realtimeEnabled=$d.RealTimeProtectionEnabled;signatureVersion=$d.AntivirusSignatureVersion;signatureAgeDays=$d.AntivirusSignatureAge;signatureAt=if($d.AntivirusSignatureLastUpdated){$d.AntivirusSignatureLastUpdated.ToUniversalTime().ToString('o')}else{$null};rebootRequired=$d.RebootRequired}
  }
  $sections+=Read-CareSection 'firewall' 'Get-NetFirewallProfile / ActiveStore' {
    Get-NetFirewallProfile -PolicyStore ActiveStore -ErrorAction Stop|ForEach-Object {[pscustomobject]@{name=$_.Name;enabled=switch([string]$_.Enabled){'True'{$true}'False'{$false}default{$null}};inbound=$_.DefaultInboundAction.ToString();outbound=$_.DefaultOutboundAction.ToString()}}
  }
  $sections+=Read-CareSection 'systemEvents' 'System / newest 100 critical-error events / 7 days' {Read-CareEvents 'System'}
  $sections+=Read-CareSection 'appEvents' 'Application / newest 100 critical-error events / 7 days' {Read-CareEvents 'Application'}
  $sections+=Read-CareSection 'crashes' 'System / bug-check and unexpected-shutdown events / 14 days' {
    $query="*[System[TimeCreated[timediff(@SystemTime) <= 1209600000] and ((EventID=41 and Provider[@Name='Microsoft-Windows-Kernel-Power']) or (EventID=6008 and Provider[@Name='EventLog']) or (EventID=1001 and (Provider[@Name='Microsoft-Windows-WER-SystemErrorReporting'] or Provider[@Name='BugCheck'])))]]"
    try{$events=@(Get-WinEvent -LogName System -FilterXPath $query -MaxEvents 101 -ErrorAction Stop)}catch{if($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*'){$events=@()}else{throw}}
    foreach($event in $events){Convert-CareEvent $event}
  }
  $sections+=Read-CareSection 'dumps' 'Minidump + MEMORY.DMP metadata only' {
    $folder=Join-Path $env:SystemRoot 'Minidump';$files=@()
    if(Test-Path -LiteralPath $folder -ErrorAction Stop){$files+=@(Get-ChildItem -LiteralPath $folder -File -Filter '*.dmp' -ErrorAction Stop|Sort-Object LastWriteTimeUtc -Descending|Select-Object -First 101)}
    $large=Join-Path $env:SystemRoot 'MEMORY.DMP';if(Test-Path -LiteralPath $large -ErrorAction Stop){$files+=Get-Item -LiteralPath $large -ErrorAction Stop}
    $files|Sort-Object LastWriteTimeUtc -Descending|ForEach-Object {[pscustomobject]@{name=$_.Name;at=$_.LastWriteTimeUtc.ToString('o');sizeBytes=$_.Length}}
  }
  $sections+=Read-CareSection 'updateHistory' 'Windows Update local history / no online search' {Get-CareUpdateHistory}
  $sections+=Read-CareSection 'services' 'CIM / selected Windows services' {
    Get-CimInstance Win32_Service -Filter "Name='wuauserv' OR Name='BITS' OR Name='EventLog' OR Name='WinDefend' OR Name='MpsSvc' OR Name='TrustedInstaller'" -OperationTimeoutSec 10 -ErrorAction Stop|ForEach-Object {[pscustomobject]@{name=$_.Name;displayName=$_.DisplayName;state=$_.State;startMode=$_.StartMode}}
  }
  $unavailable=@($sections|Where-Object {$_.status -eq 'unavailable'}).Count
  $attention=($unavailable -gt 0) -or @($sections|Where-Object {$_.id -eq 'crashes' -and $_.items.Count -gt 0}).Count -gt 0
  $ready=$sections|Where-Object {$_.id -eq 'readiness'}
  if($ready.items.Count -and ($ready.items[0].restartUnknown -or $ready.items[0].restartSignals.Count)){$attention=$true}
  return @{schema=1;at=(Get-Date).ToUniversalTime().ToString('o');readOnly=$true;online=$false;success=($unavailable -eq 0);needsAttention=[bool]$attention;sections=$sections}
}
function Get-CareComponentState {
  Assert-Admin
  Write-OperationStatus 'care-component' 'running'
  $result=Repair-WindowsImage -Online -CheckHealth -ErrorAction Stop
  $state=switch([string]$result.ImageHealthState){'Healthy'{'healthy'}'Repairable'{'repairable'}'NonRepairable'{'nonRepairable'}default{'unknown'}}
  Write-OperationStatus 'care-component' 'complete'
  return @{at=(Get-Date).ToUniversalTime().ToString('o');state=$state;restartNeeded=[bool]$result.RestartNeeded;mode='recorded-only';readOnly=$true;online=$false;success=($state -ne 'unknown');needsAttention=($state -ne 'healthy' -or $result.RestartNeeded)}
}
