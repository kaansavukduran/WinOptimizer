param(
  [Parameter(Mandatory=$true)][ValidateSet('focus-apps','focus-close','package-inspect','package-apply','runtime-verify','runtime-install','restore-points','restore-point-create','ghosts','ghost-remove','diagnostics','diagnostic-repair','health','drivers','driver-backup','startup','startup-disable','startup-restore','windows-updates','windows-install','network','dns-flush','power-profiles','power-set')][string]$Action,
  [string]$PayloadBase64 = 'e30=',
  [string]$ResultFile = '',
  [string]$ProgressFile = ''
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$payload = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($PayloadBase64)) | ConvertFrom-Json
function Write-OperationStatus([string]$Step,[string]$Status,[int]$Count=-1,[string]$Item='', [string]$Reason='') {
  if(-not $ProgressFile){return}
  try {
    $entry=@{at=(Get-Date).ToUniversalTime().ToString('o');action=$Action;step=$Step;status=$Status}
    if($Count -ge 0){$entry.count=$Count};if($Item){$entry.item=$Item};if($Reason){$entry.reason=$Reason}
    [IO.File]::AppendAllText($ProgressFile,(($entry|ConvertTo-Json -Compress)+[Environment]::NewLine),(New-Object Text.UTF8Encoding($false)))
  }catch{}
}
function Test-Admin {
  $identity=[Security.Principal.WindowsIdentity]::GetCurrent()
  return (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
function Assert-Admin { if (-not (Test-Admin)) { throw 'ADMIN_REQUIRED' } }
function Get-Startup {
  $key='HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
  if (Test-Path $key) {
    $values=Get-ItemProperty -LiteralPath $key
    foreach($p in $values.PSObject.Properties) {
      if($p.Name -in @('PSPath','PSParentPath','PSChildName','PSDrive','PSProvider')){continue}
      [pscustomobject]@{id=$p.Name;name=$p.Name;command=[string]$p.Value;scope='user';kind=(Get-Item -LiteralPath $key).GetValueKind($p.Name).ToString()}
    }
  }
}
. (Join-Path $PSScriptRoot 'Diagnostics.ps1')
function Get-DriverBackup([string]$Destination) {
      Assert-Admin
      $dir=[IO.Path]::GetFullPath($Destination)
      if($dir -notmatch '\\WinOptimizer Aion\\DriverBackups\\[a-zA-Z0-9-]+$'){throw 'INVALID_DESTINATION'}
      Assert-NoReparseParent $dir
      New-Item -ItemType Directory -Path $dir -Force|Out-Null
      Assert-NoReparseParent $dir
      Write-OperationStatus 'backup' 'running'
      $log=& "$env:windir\System32\pnputil.exe" /export-driver '*' $dir 2>&1|Out-String
      if($LASTEXITCODE -ne 0){throw 'DRIVER_BACKUP_FAILED'}
      $infs=@(Get-ChildItem -LiteralPath $dir -Recurse -Filter '*.inf' -File)
      $hashes=@(Get-ChildItem -LiteralPath $dir -Recurse -File|ForEach-Object{[pscustomobject]@{path=$_.FullName.Substring($dir.Length+1);sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
      $manifest=@{created=(Get-Date).ToUniversalTime().ToString('o');packages=$infs.Count;files=$hashes;scope='third-party-driver-store'}
      $manifest|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $dir 'backup.json') -Encoding UTF8
      Write-OperationStatus 'backup' 'complete' $infs.Count
      return @{destination=$dir;packages=$infs.Count;scope='third-party-driver-store'}
}
. (Join-Path $PSScriptRoot 'Recovery.ps1')
function Invoke-Action {
  switch($Action) {
    {$_ -in @('focus-apps','focus-close','package-inspect','package-apply','runtime-verify','runtime-install','restore-points','restore-point-create','ghosts','ghost-remove')} {return Invoke-Recovery}
    'diagnostics' {return Get-Diagnostics}
    'diagnostic-repair' {return Invoke-DiagnosticRepair}
    'health' {
      $os=Get-CimInstance Win32_OperatingSystem
      $cpu=Get-CimInstance Win32_Processor | Select-Object -First 1
      $disks=@(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { [pscustomobject]@{name=$_.DeviceID;free=[double]$_.FreeSpace;size=[double]$_.Size} })
      $security=@{defender=$null;firewall=$null;bitlocker=$null}
      try{$mp=Get-MpComputerStatus;$security.defender=[bool]$mp.RealTimeProtectionEnabled}catch{}
      try{$fw=@(Get-NetFirewallProfile);$security.firewall=(@($fw|Where-Object{-not $_.Enabled}).Count -eq 0)}catch{}
      try{$bl=Get-BitLockerVolume -MountPoint ($env:SystemDrive);$security.bitlocker=($bl.ProtectionStatus.ToString() -eq 'On')}catch{}
      $physical=@();try{$physical=@(Get-PhysicalDisk|ForEach-Object{[pscustomobject]@{name=$_.FriendlyName;media=$_.MediaType.ToString();health=$_.HealthStatus.ToString()}})}catch{}
      return @{os=$os.Caption;build=$os.BuildNumber;cpu=$cpu.Name;ramTotal=[double]$os.TotalVisibleMemorySize*1024;ramFree=[double]$os.FreePhysicalMemory*1024;boot=$os.LastBootUpTime.ToUniversalTime().ToString('o');disks=$disks;physical=$physical;security=$security;admin=(Test-Admin)}
    }
    'drivers' {
      $problems=@{};Get-CimInstance Win32_PnPEntity | ForEach-Object{if($_.PNPDeviceID){$problems[$_.PNPDeviceID]=[int]$_.ConfigManagerErrorCode}}
      return @((Get-CimInstance Win32_PnPSignedDriver)|Where-Object{$_.DeviceName}|ForEach-Object{[pscustomobject]@{id=$_.DeviceID;name=$_.DeviceName;provider=$_.DriverProviderName;version=$_.DriverVersion;date=if($_.DriverDate){$_.DriverDate.ToUniversalTime().ToString('o')}else{$null};signed=[bool]$_.IsSigned;inf=$_.InfName;deviceClass=$_.DeviceClass;problem=$problems[$_.DeviceID]}}|Sort-Object name)
    }
    'driver-backup' {return Get-DriverBackup ([string]$payload.destination)}
    'startup' {return @(Get-Startup)}
    'startup-disable' {
      $entry=@(Get-Startup|Where-Object{$_.id -ceq [string]$payload.id})
      if($entry.Count -ne 1 -or $entry[0].command -cne [string]$payload.command){throw 'STARTUP_CHANGED'}
      Remove-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name $entry[0].id
      return @{disabled=$true;entry=$entry[0]}
    }
    'startup-restore' {
      $key='HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
      if(-not (Test-Path $key)){New-Item -Path $key -Force|Out-Null}
      if([string]$payload.kind -notin @('String','ExpandString')){throw 'INVALID_STARTUP_TYPE'}
      if((Get-Item -LiteralPath $key).GetValueNames() -ccontains [string]$payload.id){throw 'RESTORE_CONFLICT'}
      New-ItemProperty -LiteralPath $key -Name ([string]$payload.id) -Value ([string]$payload.command) -PropertyType ([string]$payload.kind)|Out-Null
      return @{restored=$true}
    }
    'windows-updates' {
      $session=New-Object -ComObject Microsoft.Update.Session
      $searcher=$session.CreateUpdateSearcher()
      Write-OperationStatus 'windows-updates' 'running'
      $result=$searcher.Search("IsInstalled=0 and IsHidden=0 and Type='Driver'")
      Write-OperationStatus 'windows-updates' 'complete' $result.Updates.Count
      $firmware=@($result.Updates|Where-Object {[string]$_.DriverClass -ieq 'Firmware'});if($firmware.Count){Write-OperationStatus 'firmware' 'skipped' $firmware.Count '' 'excluded'}
      return @($result.Updates|Where-Object {[string]$_.DriverClass -ine 'Firmware'}|ForEach-Object{[pscustomobject]@{id=$_.Identity.UpdateID;revision=$_.Identity.RevisionNumber;name=$_.Title;bytes=[double]$_.MaxDownloadSize;driverClass=[string]$_.DriverClass;manufacturer=$_.DriverManufacturer;model=$_.DriverModel;date=if($_.DriverVerDate){$_.DriverVerDate.ToUniversalTime().ToString('o')}else{$null};reboot=$_.RebootRequired}})
    }
    'windows-install' {
      Assert-Admin
      $ids=@($payload.ids)
      if($payload.idsFile){
        $plan=Get-Item -LiteralPath ([string]$payload.idsFile) -ErrorAction Stop
        if($plan.PSIsContainer -or $plan.Length -gt 1048576){throw 'INVALID_SELECTION'}
        $planBytes=[IO.File]::ReadAllBytes($plan.FullName);$hasher=[Security.Cryptography.SHA256]::Create()
        try{$planHash=([BitConverter]::ToString($hasher.ComputeHash($planBytes))).Replace('-','').ToLowerInvariant()}finally{$hasher.Dispose()}
        if($planHash -cne [string]$payload.idsSha256){throw 'UPDATE_CHANGED'}
        $ids=@(([Text.Encoding]::UTF8.GetString($planBytes)|ConvertFrom-Json).ids)
      }
      if($ids.Count -eq 0 -or $ids.Count -gt 10000 -or @($ids|Select-Object -Unique).Count -ne $ids.Count){throw 'INVALID_SELECTION'}
      foreach($id in $ids){if([string]$id -notmatch '^[0-9a-fA-F-]{36}$'){throw 'INVALID_UPDATE_ID'}}
      $session=New-Object -ComObject Microsoft.Update.Session;$searcher=$session.CreateUpdateSearcher()
      $found=$searcher.Search("IsInstalled=0 and IsHidden=0 and Type='Driver'")
      $collection=New-Object -ComObject Microsoft.Update.UpdateColl
      foreach($update in $found.Updates){if($ids -contains $update.Identity.UpdateID -and [string]$update.DriverClass -ine 'Firmware'){if(-not $update.EulaAccepted){$update.AcceptEula()};$null=$collection.Add($update)}}
      if($collection.Count -ne $ids.Count){throw 'UPDATE_CHANGED'}
      $backup=$null;if($payload.backupDestination){$backup=Get-DriverBackup ([string]$payload.backupDestination)}
      Write-OperationStatus 'download' 'running' $collection.Count
      $downloader=$session.CreateUpdateDownloader();$downloader.Updates=$collection;$download=$downloader.Download()
      if([int]$download.ResultCode -ne 2){throw 'UPDATE_DOWNLOAD_FAILED'}
      Write-OperationStatus 'download' 'complete' $collection.Count
      Write-OperationStatus 'install' 'running' $collection.Count
      $installer=$session.CreateUpdateInstaller();$installer.Updates=$collection;$result=$installer.Install()
      $items=@();for($i=0;$i -lt $collection.Count;$i++){$r=$result.GetUpdateResult($i);Write-OperationStatus 'install-item' $(if([int]$r.ResultCode -eq 2){'complete'}else{'failed'}) ($i+1) $collection.Item($i).Title ([string]$r.ResultCode);$items+=@{id=$collection.Item($i).Identity.UpdateID;name=$collection.Item($i).Title;success=([int]$r.ResultCode -eq 2);code=[int]$r.ResultCode;hresult=$r.HResult}}
      return @{backup=$backup;items=$items;reboot=[bool]$result.RebootRequired;success=([int]$result.ResultCode -eq 2)}
    }
    'network' {
      $adapters=@(Get-NetAdapter|ForEach-Object{[pscustomobject]@{name=$_.Name;status=$_.Status;speed=$_.LinkSpeed}})
      $dns=@(Get-DnsClientServerAddress -AddressFamily IPv4|Where-Object{$_.ServerAddresses.Count -gt 0}|ForEach-Object{[pscustomobject]@{name=$_.InterfaceAlias;servers=@($_.ServerAddresses)}})
      return @{adapters=$adapters;dns=$dns}
    }
    'dns-flush' {Clear-DnsClientCache;return @{flushed=$true}}
    'power-profiles' {
      $active=& "$env:windir\System32\powercfg.exe" /getactivescheme|Out-String
      $lines=& "$env:windir\System32\powercfg.exe" /list
      if($LASTEXITCODE -ne 0){throw 'POWER_UNAVAILABLE'}
      return @($lines|ForEach-Object{if($_ -match '([a-fA-F0-9-]{36})\s+\((.+)\)'){@{id=$matches[1];name=$matches[2];active=($active -match $matches[1])}}})
    }
    'power-set' {
      $id=[string]$payload.id;if($id -notmatch '^[a-fA-F0-9-]{36}$'){throw 'INVALID_POWER_ID'}
      $available=& "$env:windir\System32\powercfg.exe" /list|Out-String
      if($available -notmatch [regex]::Escape($id)){throw 'POWER_UNAVAILABLE'}
      $before=& "$env:windir\System32\powercfg.exe" /getactivescheme|Out-String
      $previous=if($before -match '([a-fA-F0-9-]{36})'){$matches[1]}else{$null}
      & "$env:windir\System32\powercfg.exe" /setactive $id|Out-Null
      if($LASTEXITCODE -ne 0){throw 'POWER_FAILED'}
      $after=& "$env:windir\System32\powercfg.exe" /getactivescheme|Out-String
      if($after -notmatch [regex]::Escape($id)){throw 'POWER_FAILED'}
      return @{previous=$previous;current=$id}
    }
  }
}
try { Write-OperationStatus $Action 'running';$data=Invoke-Action;Write-OperationStatus $Action 'complete'; if($Action -in @('drivers','startup','windows-updates','power-profiles','package-inspect','ghosts','focus-apps')){if($null -eq $data){$data=@()}else{$data=@($data)}}; $output=@{ok=$true;data=$data}|ConvertTo-Json -Depth 12 -Compress }
catch { Write-OperationStatus $Action 'failed' -1 '' $_.Exception.Message;$output=@{ok=$false;error=$_.Exception.Message}|ConvertTo-Json -Compress }
if($ResultFile){[IO.File]::WriteAllText($ResultFile,$output,(New-Object Text.UTF8Encoding($false)))}else{[Console]::WriteLine($output)}
