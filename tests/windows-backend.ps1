$ErrorActionPreference='Stop'
$file=Join-Path $PSScriptRoot '..\backend\Windows.ps1'
$tokens=$null;$errors=$null;$null=[Management.Automation.Language.Parser]::ParseFile($file,[ref]$tokens,[ref]$errors)
if($errors.Count){$errors|Format-List;throw 'PowerShell parser errors'}
function Call-Backend($Action,$Data=@{}){
  $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($Data|ConvertTo-Json -Compress)))
  $raw=& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $file -Action $Action -PayloadBase64 $encoded
  $r=$raw|ConvertFrom-Json;if(-not $r.ok){throw $r.error};return $r.data
}
$health=Call-Backend 'health';if(-not $health.os -or $health.ramTotal -le 0){throw 'Invalid health output'}
$drivers=@(Call-Backend 'drivers');if($drivers.Count -lt 1){throw 'No drivers enumerated'}
$network=Call-Backend 'network';if($null -eq $network.adapters){throw 'Missing network output'}
$plans=@(Call-Backend 'power-profiles');if($plans.Count -lt 1){throw 'No power plans'}
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
Write-Host 'PASS: PS 5.1 parser, real health/drivers/network/power and reversible HKCU startup entry'
