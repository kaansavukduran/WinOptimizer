$ErrorActionPreference='Stop'
$uiScript=Join-Path $PSScriptRoot '..\scripts\windows-native-update.ps1'
$uiTokens=$null;$uiErrors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($uiScript,[ref]$uiTokens,[ref]$uiErrors)
if($uiErrors.Count){$uiErrors|Format-List;throw 'Native UI automation PS 5.1 parser errors'}
$recovery=Join-Path $PSScriptRoot '..\backend\Recovery.ps1'
$rt=$null;$re=$null;$null=[Management.Automation.Language.Parser]::ParseFile($recovery,[ref]$rt,[ref]$re)
if($re.Count){throw 'Recovery PS 5.1 parser errors'}
$extra=Join-Path $PSScriptRoot '..\backend\Diagnostics.ps1'
$extraTokens=$null;$extraErrors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($extra,[ref]$extraTokens,[ref]$extraErrors)
if($extraErrors.Count){throw 'Diagnostics PS 5.1 parser errors'}
$file=Join-Path $PSScriptRoot '..\backend\Windows.ps1'
$tokens=$null;$errors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($file,[ref]$tokens,[ref]$errors)
if($errors.Count){$errors|Format-List;throw 'PowerShell parser errors'}
function Call-Backend($Action,$Data=@{}){
  $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($Data|ConvertTo-Json -Compress)))
  $progress=Join-Path $env:TEMP ('aion-progress-'+[guid]::NewGuid().ToString('N')+'.jsonl')
  try {
    $raw=& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $file -Action $Action -PayloadBase64 $encoded -ProgressFile $progress
    $events=@(Get-Content -LiteralPath $progress|ForEach-Object {$_|ConvertFrom-Json})
    if(-not @($events|Where-Object {$_.status -eq 'running'}).Count){throw 'Native progress start missing'}
    if($Action -eq 'care' -and @($events|Where-Object {$_.step -like 'care-*' -and $_.status -in @('complete','failed')}).Count -ne 9){throw 'Care section completion receipts missing'}
    if($Action -eq 'hardware' -and @($events|Where-Object {$_.step -like 'hardware-*' -and $_.status -in @('complete','failed')}).Count -ne 14){throw 'Hardware section completion events missing'}
    if($Action -eq 'diagnostics' -and -not @($events|Where-Object {$_.step -eq 'devices' -and $_.status -in @('complete','failed')}).Count){throw 'Native provider progress missing'}
  } finally {Remove-Item -LiteralPath $progress -Force -ErrorAction SilentlyContinue}
  $r=$raw|ConvertFrom-Json;if(-not $r.ok){throw $r.error};return $r.data
}
$hwPath=Join-Path $PSScriptRoot '..\backend\Hardware.ps1'
$hwTokens=$null;$hwErrors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($hwPath,[ref]$hwTokens,[ref]$hwErrors)
if($hwErrors.Count){$hwErrors|Format-List;throw 'Hardware PS 5.1 parser errors'}
Add-Type -Path (Join-Path $PSScriptRoot '..\backend\HardwareDxgi.cs')
if([AionHardware.Gpu].GetField('DedicatedVideoBytes').FieldType -ne [uint64]){throw 'VRAM must use 64-bit counts'}
$hw=Call-Backend 'hardware'
if($hw.readOnly -ne $true -or $hw.online -ne $false -or @($hw.sections).Count -ne 14){throw 'Invalid local inventory envelope'}
foreach($id in @('system','cpu','storage')){
  $section=$hw.sections|Where-Object {$_.id -eq $id}
  if($section.status -ne 'available' -or @($section.items).Count -lt 1){throw ('Required Windows hardware provider failed: '+$id)}
}
foreach($section in $hw.sections){if($section.status -notin @('available','empty','unavailable')){throw 'Unknown hardware status'}}
foreach($gpu in ($hw.sections|Where-Object {$_.id -eq 'gpu'}).items){
  if($gpu.memorySource -ne 'DXGI' -and $null -ne $gpu.dedicatedVideoBytes){throw 'Unreliable CIM VRAM used'}
}
$hw|ConvertTo-Json -Depth 12|Set-Content (Join-Path $env:TEMP 'aion-hardware-inventory.json')
$carePath=Join-Path $PSScriptRoot '..\backend\Care.ps1'
$careTokens=$null;$careErrors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($carePath,[ref]$careTokens,[ref]$careErrors)
if($careErrors.Count){$careErrors|Format-List;throw 'Care PS 5.1 parser errors'}
$care=Call-Backend 'care'
if($care.readOnly -ne $true -or $care.online -ne $false -or @($care.sections).Count -ne 9){throw 'Invalid local care envelope'}
foreach($id in @('readiness','services')){if(($care.sections|Where-Object {$_.id -eq $id}).status -ne 'available'){throw ('Required care provider unavailable: '+$id)}}
foreach($section in $care.sections){if($section.status -notin @('available','empty','unavailable') -or @($section.items).Count -gt 100){throw 'Invalid bounded care provider output'}}
$component=Call-Backend 'component-check'
if($component.mode -ne 'recorded-only' -or $component.state -notin @('healthy','repairable','nonRepairable') -or $component.readOnly -ne $true){throw 'DISM recorded-health state not verified'}
$diag=Call-Backend 'diagnostics'
if($diag.devices.Count -lt 1 -or $null -eq $diag.network -or $diag.runtimes.Count -ne 3){throw 'Invalid diagnostic inventory'}
if(@($diag.unavailable).Count){throw ('Unavailable scan provider: '+($diag.unavailable -join ','))}
if($diag.network.dnsChecked -ne $false){throw 'Offline scan performed an online check'}
$diag|ConvertTo-Json -Depth 12|Set-Content (Join-Path $env:TEMP 'aion-native-diagnostics.json')
$health=Call-Backend 'health';if(-not $health.os -or $health.ramTotal -le 0){throw 'Invalid health output'}
$drivers=@(Call-Backend 'drivers');if($drivers.Count -lt 1){throw 'No drivers enumerated'}
$network=Call-Backend 'network';if($null -eq $network.adapters){throw 'Missing network output'}
$points=Call-Backend 'restore-points';if($null -eq $points.available){throw 'Missing restore-point availability'}
$ghosts=@(Call-Backend 'ghosts')
$apps=@(Call-Backend 'focus-apps')
$plans=@(Call-Backend 'power-profiles');if($plans.Count -lt 1){throw 'No power plans'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if((New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){
  # Real native rejection paths stop before any Windows Update search/download/install.
  $planFile=Join-Path $env:TEMP ('aion-driver-plan-'+[guid]::NewGuid().ToString('N')+'.json')
  try {
    $ids=@(1..31|ForEach-Object{[guid]::NewGuid().ToString()})+@('invalid-update-id')
    $bytes=[Text.Encoding]::UTF8.GetBytes((@{ids=$ids}|ConvertTo-Json -Compress));[IO.File]::WriteAllBytes($planFile,$bytes)
    $hash=(Get-FileHash -LiteralPath $planFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $rejected=$false;try{Call-Backend 'windows-install' @{idsFile=$planFile;idsSha256=('0'*64)}}catch{if($_.Exception.Message -ne 'UPDATE_CHANGED'){throw};$rejected=$true};if(-not $rejected){throw 'Changed driver plan accepted'}
    $rejected=$false;try{Call-Backend 'windows-install' @{idsFile=$planFile;idsSha256=$hash}}catch{if($_.Exception.Message -ne 'INVALID_UPDATE_ID'){throw};$rejected=$true};if(-not $rejected){throw 'Invalid final bulk update ID accepted'}
  }finally{Remove-Item -LiteralPath $planFile -Force -ErrorAction SilentlyContinue}
  $destination=Join-Path $env:LOCALAPPDATA ('WinOptimizer Aion\DriverBackups\integration-'+[guid]::NewGuid().ToString('N'))
  $backup=Call-Backend 'driver-backup' @{destination=$destination}
  if(-not (Test-Path (Join-Path $destination 'backup.json'))){throw 'Driver backup manifest missing'}
  $manifest=Get-Content (Join-Path $destination 'backup.json') -Raw|ConvertFrom-Json
  foreach($f in $manifest.files){if((Get-FileHash (Join-Path $destination $f.path) -Algorithm SHA256).Hash -ne $f.sha256){throw 'Driver backup hash mismatch'}}
  $candidates=@(Call-Backend 'package-inspect' @{directory=$destination})
  if($backup.packages -gt 0 -and $candidates.Count -lt 1){throw 'Backed-up packages could not be inspected'}
  Remove-Item $destination -Recurse -Force
}
$name='WinOptimizerIntegration-'+[guid]::NewGuid().ToString('N');$key='HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
try{
  if(-not(Test-Path $key)){New-Item $key -Force|Out-Null}
  New-ItemProperty $key -Name $name -Value 'C:\Windows\notepad.exe' -PropertyType String|Out-Null
  $entries=@(Call-Backend 'startup');$entry=$entries|Where-Object{$_.id -eq $name};if(-not $entry){throw 'Fixture not listed'}
  $disabled=Call-Backend 'startup-disable' @{id=$name;command=$entry.command};if(-not $disabled.disabled){throw 'Not disabled'}
  if((Get-Item $key).GetValueNames() -contains $name){throw 'Registry entry still exists'}
  $restored=Call-Backend 'startup-restore' @{id=$name;command=$entry.command;kind='String'};if(-not $restored.restored){throw 'Not restored'}
  if((Get-ItemProperty $key).$name -ne 'C:\Windows\notepad.exe'){throw 'Restored data differs'}
}finally{Remove-ItemProperty $key -Name $name -ErrorAction SilentlyContinue}
& (Join-Path $PSScriptRoot 'windows-driver-null.ps1')
Write-Host 'PASS: PS 5.1 parser, real health/drivers/network/power and reversible HKCU startup entry'
