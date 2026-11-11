$ErrorActionPreference='Stop'
# Isolated dependency fixture: exercise the real drivers action without changing Windows.
function Get-CimInstance([string]$ClassName) {
  if($ClassName -eq 'Win32_PnPEntity') {
    [pscustomobject]@{PNPDeviceID='unknown';ConfigManagerErrorCode=$null}
    [pscustomobject]@{PNPDeviceID='zero';ConfigManagerErrorCode=0}
    [pscustomobject]@{PNPDeviceID='issue';ConfigManagerErrorCode=28}
  } elseif($ClassName -eq 'Win32_PnPSignedDriver') {
    foreach($id in @('unknown','zero','issue','missing')) {
      [pscustomobject]@{DeviceID=$id;DeviceName=$id;DriverProviderName='Test fixture';DriverVersion='1.0';DriverDate=$null;IsSigned=$true;InfName=($id+'.inf');DeviceClass='Net'}
    }
  } else {throw 'Unexpected fixture class'}
}
$result=Join-Path $env:TEMP ('aion-driver-null-'+[guid]::NewGuid().ToString('N')+'.json')
try {
  & (Join-Path $PSScriptRoot '..\backend\Windows.ps1') -Action drivers -ResultFile $result
  $reply=Get-Content -LiteralPath $result -Raw|ConvertFrom-Json
  if(-not $reply.ok -or @($reply.data).Count -ne 4){throw 'Driver fixture failed'}
  foreach($id in @('unknown','missing')) {if($null -ne ($reply.data|Where-Object {$_.id -eq $id}).problem){throw 'Unknown driver code was converted to a healthy code'}}
  if(($reply.data|Where-Object {$_.id -eq 'zero'}).problem -ne 0){throw 'Real zero driver code changed'}
  if(($reply.data|Where-Object {$_.id -eq 'issue'}).problem -ne 28){throw 'Problem driver code changed'}
  Write-Host 'PASS: driver problem codes preserve null, missing, zero and actual issues'
} finally {Remove-Item -LiteralPath $result -Force -ErrorAction SilentlyContinue}
