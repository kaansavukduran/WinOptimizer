# Read-only inventory. A failed provider is reported as unavailable, never healthy.
function Get-Diagnostics {
  $data=@{devices=@();audio=@();network=$null;display=@();runtimes=@();unavailable=@()}
  try {
    $signed=@{};Get-CimInstance Win32_PnPSignedDriver | ForEach-Object {if($_.DeviceID){$signed[$_.DeviceID]=$_}}
    $data.devices=@(Get-CimInstance Win32_PnPEntity | ForEach-Object {
      $driver=$signed[$_.PNPDeviceID]
      [pscustomobject]@{id=$_.PNPDeviceID;name=$_.Name;code=$_.ConfigManagerErrorCode;present=$_.Present;deviceClass=$_.PNPClass;service=$_.Service;hardwareIds=@($_.HardwareID);version=$driver.DriverVersion;provider=$driver.DriverProviderName}
    })
  } catch {$data.unavailable+= 'devices'}
  try {$data.audio=@('AudioEndpointBuilder','Audiosrv'|ForEach-Object {$s=Get-Service -Name $_;[pscustomobject]@{id=$s.Name;status=$s.Status.ToString();startType=$s.StartType.ToString()}})} catch {$data.unavailable+= 'audio'}
  try {
    $adapters=@(Get-NetAdapter | ForEach-Object {[pscustomobject]@{name=$_.Name;status=$_.Status.ToString();speed=$_.LinkSpeed}})
    $data.network=@{adapters=$adapters;dnsChecked=$false;dnsOk=$null}
    if($payload.online -eq $true -and @($adapters|Where-Object {$_.status -eq 'Up'}).Count -gt 0){
      $data.network.dnsChecked=$true
      try {$answer=@(Resolve-DnsName -Name 'www.microsoft.com' -DnsOnly -QuickTimeout -ErrorAction Stop);$data.network.dnsOk=(@($answer|Where-Object {$_.IPAddress}).Count -gt 0)} catch {$data.network.dnsOk=$false}
    }
  } catch {$data.unavailable+= 'network'}
  try {$data.display=@(Get-CimInstance Win32_VideoController | ForEach-Object {[pscustomobject]@{name=$_.Name;service=$_.InstalledDisplayDrivers;width=$_.CurrentHorizontalResolution;height=$_.CurrentVerticalResolution;code=$_.ConfigManagerErrorCode}})} catch {$data.unavailable+= 'display'}
  try {
    # Both registry views are explicit: the host's bitness must not hide x86 runtimes.
    foreach($arch in @('x64','x86')) {
      $installed=$false;$version=''
      foreach($view in @([Microsoft.Win32.RegistryView]::Registry64,[Microsoft.Win32.RegistryView]::Registry32)) {
        $base=[Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine,$view)
        $key=$null
        try {
          $key=$base.OpenSubKey("SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\$arch")
          if($null -ne $key -and $key.GetValue('Installed',0) -eq 1){$installed=$true;$version=[string]$key.GetValue('Version','')}
        } finally {if($key){$key.Dispose()};$base.Dispose()}
      }
      $data.runtimes+=@{id="vc-$arch";installed=$installed;version=$version}
    }
    $data.runtimes+=@{id='directx-legacy';installed=((Test-Path "$env:windir\System32\d3dx9_43.dll") -and (Test-Path "$env:windir\SysWOW64\d3dx9_43.dll") -and (Test-Path "$env:windir\System32\XAudio2_7.dll") -and (Test-Path "$env:windir\SysWOW64\XAudio2_7.dll"));version='June 2010'}
  } catch {$data.unavailable+= 'runtimes'}
  return $data
}
function Invoke-DiagnosticRepair {
  switch([string]$payload.kind) {
    'audio-start' {
      Assert-Admin
      if([string]$payload.target -notin @('Audiosrv','AudioEndpointBuilder')){throw 'INVALID_SELECTION'}
      $service=Get-Service -Name ([string]$payload.target)
      if($service.StartType.ToString() -eq 'Disabled'){throw 'DIAGNOSTIC_CHANGED'}
      if($service.Status.ToString() -ne 'Running'){Start-Service -Name $service.Name}
      $service=Get-Service -Name $service.Name
      return @{completed=($service.Status.ToString() -eq 'Running')}
    }
    'device-rescan' {
      Assert-Admin
      & "$env:windir\System32\pnputil.exe" /scan-devices | Out-Null
      if($LASTEXITCODE -ne 0){throw 'DEVICE_RESCAN_FAILED'}
      return @{completed=$true}
    }
    'dns-flush' {Clear-DnsClientCache;return @{completed=$true}}
    default {throw 'INVALID_SELECTION'}
  }
}
