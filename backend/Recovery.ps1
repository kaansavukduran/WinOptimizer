function Assert-NoReparseParent([string]$Path) {
  $cursor=[IO.Path]::GetFullPath($Path)
  while($cursor){if(Test-Path -LiteralPath $cursor){if((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'PACKAGE_LINK'}};$parent=[IO.Directory]::GetParent($cursor);$cursor=if($parent){$parent.FullName}else{''}}
}
function Get-PackageRoot([string]$Directory) {
  $root=[IO.Path]::GetFullPath($Directory)
  if($root -notmatch '\\WinOptimizer Aion\\(DriverBackups|DriverPackages)\\[a-zA-Z0-9-]{1,80}$'){throw 'INVALID_DESTINATION'}
  Assert-NoReparseParent $root
  $item=Get-Item -LiteralPath $root
  if(-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'PACKAGE_LINK'}
  foreach($f in Get-ChildItem -LiteralPath $root -Recurse -Force){if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'PACKAGE_LINK'}}
  return $root
}
function Get-PackageCandidates([string]$Directory) {
  $root=Get-PackageRoot $Directory
  foreach($inf in Get-ChildItem -LiteralPath $root -Recurse -Filter '*.inf' -File) {
    $text=[IO.File]::ReadAllText($inf.FullName)
    $class=[regex]::Match($text,'(?im)^\s*Class\s*=\s*([^;\r\n]+)').Groups[1].Value.Trim().Trim('"')
    $provider=[regex]::Match($text,'(?im)^\s*Provider\s*=\s*([^;\r\n]+)').Groups[1].Value.Trim().Trim('"')
    $version=[regex]::Match($text,'(?im)^\s*DriverVer\s*=\s*([^;\r\n]+)').Groups[1].Value.Trim()
    $catalogs=@([regex]::Matches($text,'(?im)^\s*CatalogFile(?:\.[\w]+)?\s*=\s*([^;\r\n]+)')|ForEach-Object {$_.Groups[1].Value.Trim().Trim('"')})
    $valid=$false;$publisher='';$catalog=''
    foreach($name in $catalogs){
      if([IO.Path]::GetFileName($name) -cne $name){continue}
      $file=Join-Path $inf.DirectoryName $name
      if(Test-Path -LiteralPath $file){$sig=Get-AuthenticodeSignature -LiteralPath $file;if($sig.Status.ToString() -eq 'Valid'){$valid=$true;$publisher=$sig.SignerCertificate.Subject;$catalog=$name;break}}
    }
    [pscustomobject]@{id=$inf.FullName.Substring($root.Length+1).Replace('\','/');name=$inf.Name;deviceClass=$class;provider=$provider;version=$version;signed=$valid;publisher=$publisher;catalog=$catalog;eligible=($valid -and $class -and $class -notmatch '^Firmware$')}
  }
}
function Test-RuntimeFile([string]$File,[string]$Id,[string]$Sha256) {
  $names=@{'vc-x64'='vc_redist.x64.exe';'vc-x86'='vc_redist.x86.exe';'directx-legacy'='directx_Jun2010_redist.exe'}
  if(-not $names.ContainsKey($Id) -or $Sha256 -notmatch '^[a-fA-F0-9]{64}$'){throw 'INVALID_SELECTION'}
  $full=[IO.Path]::GetFullPath($File)
  if($full -notmatch '\\WinOptimizer Aion\\Runtimes\\[a-fA-F0-9-]{36}\\[^\\]+$' -or [IO.Path]::GetFileName($full) -cne $names[$Id]){throw 'RUNTIME_SOURCE_INVALID'}
  if((Get-Item -LiteralPath $full).Length -gt 134217728 -or (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash -ine $Sha256){throw 'RUNTIME_SIGNATURE_INVALID'}
  $sig=Get-AuthenticodeSignature -LiteralPath $full
  if($sig.Status.ToString() -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch '(^|,\s*)CN=Microsoft Corporation(,|$)'){throw 'RUNTIME_SIGNATURE_INVALID'}
  return @{valid=$true;publisher=$sig.SignerCertificate.Subject}
}
function Invoke-Recovery {
 switch($Action){
  'focus-apps' {return @(Get-FocusApps)}
  'focus-close' {
    $allowed=@(Get-FocusApps);$items=@()
    if(@($payload.apps).Count -gt 30){throw 'INVALID_SELECTION'}
    foreach($entry in $payload.apps){
      $match=@($allowed|Where-Object {$_.id -eq [int]$entry.id -and $_.started -ceq [string]$entry.started})
      if($match.Count -ne 1){$items+=@{id=$entry.id;success=$false};continue}
      try {$p=Get-Process -Id $match[0].id -ErrorAction Stop;$requested=$p.CloseMainWindow();$items+=@{id=$p.Id;success=[bool]$requested}}catch{$items+=@{id=$entry.id;success=$false}}
    }
    return @{items=$items;success=(@($items|Where-Object {-not $_.success}).Count -eq 0)}
  }

  'package-inspect' {return @(Get-PackageCandidates ([string]$payload.directory))}
  'package-apply' {
    Assert-Admin
    $root=Get-PackageRoot ([string]$payload.directory);$ids=@($payload.ids)
    if($ids.Count -lt 1 -or $ids.Count -gt 20){throw 'INVALID_SELECTION'}
    $manifestFile=[IO.Path]::GetFullPath([string]$payload.manifestFile)
    if($manifestFile -notmatch '\\WinOptimizer Aion\\Plans\\[a-fA-F0-9-]{36}[.]json$' -or [string]$payload.manifestSha256 -notmatch '^[a-fA-F0-9]{64}$'){throw 'PACKAGE_INVALID'}
    Assert-NoReparseParent $manifestFile
    if((Get-Item -LiteralPath $manifestFile).Length -gt 2097152 -or (Get-FileHash -LiteralPath $manifestFile -Algorithm SHA256).Hash -ine [string]$payload.manifestSha256){throw 'PACKAGE_CHANGED'}
    $manifest=[IO.File]::ReadAllText($manifestFile)|ConvertFrom-Json
    if(@($manifest.files).Count -gt 6000 -or @($manifest.files).Count -lt 1){throw 'PACKAGE_INVALID'}
    foreach($f in $manifest.files){
      $relative=[string]$f.path
      if([IO.Path]::IsPathRooted($relative) -or [regex]::Split($relative,'[\\/]') -contains '..'){throw 'PACKAGE_INVALID'}
      $file=[IO.Path]::GetFullPath((Join-Path $root $relative))
      if(-not $file.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ine [string]$f.sha256){throw 'PACKAGE_CHANGED'}
    }
    $candidates=@(Get-PackageCandidates $root)
    foreach($id in $ids){if(@($candidates|Where-Object {$_.id -ceq [string]$id -and $_.eligible}).Count -ne 1){throw 'INVALID_SELECTION'}}
    $backup=Get-DriverBackup ([string]$payload.backupDestination)
    $before=@{};Get-CimInstance Win32_PnPSignedDriver|ForEach-Object {if($_.DeviceID){$before[$_.DeviceID]=($_.DriverVersion+'|'+$_.InfName)}}
    $items=@();$reboot=$false
    foreach($id in $ids){
      & "$env:windir\System32\pnputil.exe" /add-driver (Join-Path $root ([string]$id)) /install | Out-Null
      $code=$LASTEXITCODE;if($code -eq 3010){$reboot=$true}
      $items+=@{id=$id;success=($code -in @(0,3010));code=$code}
    }
    $changes=@(Get-CimInstance Win32_PnPSignedDriver|Where-Object {$_.DeviceID -and $before.ContainsKey($_.DeviceID) -and $before[$_.DeviceID] -cne ($_.DriverVersion+'|'+$_.InfName)}|ForEach-Object {@{name=$_.DeviceName;version=$_.DriverVersion;inf=$_.InfName}})
    return @{success=(@($items|Where-Object {-not $_.success}).Count -eq 0);items=$items;reboot=$reboot;changes=$changes;backup=$backup}
  }
  'runtime-verify' {return Test-RuntimeFile ([string]$payload.file) ([string]$payload.id) ([string]$payload.sha256)}
  'runtime-install' {
    Assert-Admin
    $null=Test-RuntimeFile ([string]$payload.file) ([string]$payload.id) ([string]$payload.sha256)
    # Stage into an administrator-only directory and reverify the staged bytes before execution.
    $safe=Join-Path "$env:windir\Temp" ('WinOptimizer-Aion-'+[guid]::NewGuid().ToString('N'))
    $acl=New-Object Security.AccessControl.DirectorySecurity
    $acl.SetAccessRuleProtection($true,$false)
    foreach($sid in @('S-1-5-18','S-1-5-32-544')){
      $identity=New-Object Security.Principal.SecurityIdentifier($sid)
      $rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,'FullControl','ContainerInherit,ObjectInherit','None','Allow');$acl.AddAccessRule($rule)
    }
    $info=New-Object IO.DirectoryInfo($safe);$info.Create($acl)
    try {
      $installer=Join-Path $safe ([IO.Path]::GetFileName([string]$payload.file));Copy-Item -LiteralPath ([string]$payload.file) -Destination $installer
      if((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ine [string]$payload.sha256){throw 'RUNTIME_SIGNATURE_INVALID'}
      $sig=Get-AuthenticodeSignature -LiteralPath $installer
      if($sig.Status.ToString() -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch '(^|,\s*)CN=Microsoft Corporation(,|$)'){throw 'RUNTIME_SIGNATURE_INVALID'}
      if([string]$payload.id -eq 'directx-legacy'){
        $extract=Join-Path $safe 'DirectX';New-Item -ItemType Directory -Path $extract|Out-Null
        $p=Start-Process -FilePath $installer -ArgumentList ('/Q /T:"'+$extract+'"') -Wait -PassThru
        if($p.ExitCode -ne 0){throw 'RUNTIME_INSTALL_FAILED'}
        $setup=Join-Path $extract 'DXSETUP.exe';$signature=Get-AuthenticodeSignature -LiteralPath $setup
        if($signature.Status.ToString() -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch '(^|,\s*)CN=Microsoft Corporation(,|$)'){throw 'RUNTIME_SIGNATURE_INVALID'}
        $p=Start-Process -FilePath $setup -ArgumentList '/silent' -Wait -PassThru
      }else{$p=Start-Process -FilePath $installer -ArgumentList '/install /passive /norestart' -Wait -PassThru}
      $raw=Get-Diagnostics;$runtime=@($raw.runtimes|Where-Object {$_.id -eq [string]$payload.id})
      return @{success=($p.ExitCode -in @(0,3010,1638) -and $runtime.Count -eq 1 -and $runtime[0].installed);code=$p.ExitCode;reboot=($p.ExitCode -eq 3010);runtime=$runtime}
    }finally{Remove-Item -LiteralPath $safe -Recurse -Force -ErrorAction SilentlyContinue}
  }
  'restore-points' {
    try {$points=@(Get-ComputerRestorePoint -ErrorAction Stop|ForEach-Object {@{id=$_.SequenceNumber;name=$_.Description;created=[Management.ManagementDateTimeConverter]::ToDateTime($_.CreationTime).ToUniversalTime().ToString('o')}});return @{available=$true;points=$points}} catch {return @{available=$false;points=@()}}
  }
  'restore-point-create' {
    Assert-Admin
    $description='WinOptimizer Aion '+[guid]::NewGuid().ToString('N')
    try {Checkpoint-Computer -Description $description -RestorePointType MODIFY_SETTINGS -ErrorAction Stop -WarningAction SilentlyContinue}catch{throw 'RESTORE_POINT_UNAVAILABLE'}
    $created=@(Get-ComputerRestorePoint -ErrorAction Stop|Where-Object {$_.Description -ceq $description})
    if($created.Count -ne 1){throw 'RESTORE_POINT_UNAVAILABLE'}
    return @{success=$true;created=$true;id=$created[0].SequenceNumber}
  }
  'ghosts' {return @(Get-PnpDevice|Where-Object {$_.Present -eq $false -and $_.Class -in @('MEDIA','AudioEndpoint','Bluetooth','Camera','Image','Printer','PrintQueue')}|ForEach-Object {@{id=$_.InstanceId;name=$_.FriendlyName;deviceClass=$_.Class}})}
  'ghost-remove' {
    Assert-Admin
    $id=[string]$payload.id;if($id.Length -lt 3 -or $id.Length -gt 500){throw 'INVALID_SELECTION'}
    $device=Get-PnpDevice -InstanceId $id -ErrorAction Stop
    if($device.Present -ne $false -or $device.Class -notin @('MEDIA','AudioEndpoint','Bluetooth','Camera','Image','Printer','PrintQueue')){throw 'DIAGNOSTIC_CHANGED'}
    & "$env:windir\System32\pnputil.exe" /remove-device $id|Out-Null
    $code=$LASTEXITCODE;if($code -notin @(0,3010)){throw 'DEVICE_REMOVE_FAILED'}
    $after=@(Get-PnpDevice -ErrorAction Stop|Where-Object {$_.InstanceId -ceq $id})
    return @{success=($after.Count -eq 0);reboot=($code -eq 3010);id=$id}
  }
 }
}
function Get-FocusApps {
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
  $session=(Get-Process -Id $PID).SessionId
  foreach($p in Get-Process|Where-Object {$_.SessionId -eq $session -and $_.MainWindowHandle -ne 0 -and $_.Id -ne $PID -and $_.ProcessName -notmatch '^(WinOptimizer Aion|explorer|powershell|pwsh|cmd|conhost|dwm|SearchHost|StartMenuExperienceHost|ShellExperienceHost)$'}){
    try {
      if(-not $p.Path -or $p.Path.StartsWith($env:windir+'\',[StringComparison]::OrdinalIgnoreCase)){continue}
      $cim=Get-CimInstance Win32_Process -Filter ('ProcessId='+$p.Id);$owner=Invoke-CimMethod -InputObject $cim -MethodName GetOwnerSid
      if($owner.Sid -cne $sid){continue}
      [pscustomobject]@{id=$p.Id;name=$p.ProcessName;title=$p.MainWindowTitle;started=$p.StartTime.ToUniversalTime().ToString('o')}
    }catch{}
  }
}
