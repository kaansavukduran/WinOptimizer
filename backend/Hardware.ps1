# Read-only local hardware inventory. No internet, installation, registry writes or elevation.
function Read-HardwareSection([string]$Name,[string]$Source,[scriptblock]$Read) {
  Write-OperationStatus ('hardware-'+$Name) 'running'
  try {
    $items=@(& $Read);$total=$items.Count;$limited=$total -gt 5000
    if($limited){$items=@($items|Select-Object -First 5000)}
    Write-OperationStatus ('hardware-'+$Name) 'complete' $items.Count
    if($limited){Write-OperationStatus ('hardware-'+$Name) 'skipped' -1 '' 'inventory-limit'}
    return @{id=$Name;source=$Source;status=if($total){'available'}else{'empty'};items=$items;total=$total;limited=$limited}
  }catch {
    Write-OperationStatus ('hardware-'+$Name) 'failed' -1 '' 'provider-unavailable'
    return @{id=$Name;source=$Source;status='unavailable';items=@();total=0;limited=$false}
  }
}
function Get-HardwareGpus {
  $cim=@();try{$cim=@(Get-CimInstance Win32_VideoController -OperationTimeoutSec 10)}catch{}
  $dxgi=@();$dxgiAvailable=$false
  try {
    if(-not ('AionHardware.Dxgi' -as [type])){Add-Type -Path (Join-Path $PSScriptRoot 'HardwareDxgi.cs') -ErrorAction Stop}
    $dxgi=@([AionHardware.Dxgi]::Read());$dxgiAvailable=$true
  }catch{}
  $seen=@{}
  foreach($g in $dxgi){
    $pci='PCI\VEN_'+$g.VendorId.ToString('X4')+'&DEV_'+$g.DeviceId.ToString('X4')+'*'
    $device=$cim|Where-Object {$_.PNPDeviceID -like $pci -or $_.Name -eq $g.Name}|Select-Object -First 1
    if($device){$seen[[string]$device.PNPDeviceID]=$true}
    [pscustomobject]@{name=$g.Name;dedicatedVideoBytes=[uint64]$g.DedicatedVideoBytes;dedicatedSystemBytes=[uint64]$g.DedicatedSystemBytes;sharedSystemBytes=[uint64]$g.SharedSystemBytes;memorySource='DXGI';software=[bool]$g.Software;remote=[bool]$g.Remote;vendorId=$g.VendorId.ToString('X4');deviceId=$g.DeviceId.ToString('X4');driverVersion=$device.DriverVersion;videoProcessor=$device.VideoProcessor;resolution=if($device.CurrentHorizontalResolution -and $device.CurrentVerticalResolution){[string]$device.CurrentHorizontalResolution+' x '+$device.CurrentVerticalResolution}else{$null};refreshHz=$device.CurrentRefreshRate;status=$device.Status}
  }
  foreach($g in $cim){if(-not $seen.ContainsKey([string]$g.PNPDeviceID)){
    # Win32_VideoController.AdapterRAM is uint32 and can overflow above 4 GiB. Never use it as exact VRAM.
    [pscustomobject]@{name=$g.Name;dedicatedVideoBytes=$null;dedicatedSystemBytes=$null;sharedSystemBytes=$null;memorySource='unavailable';software=$null;remote=$null;driverVersion=$g.DriverVersion;videoProcessor=$g.VideoProcessor;resolution=if($g.CurrentHorizontalResolution -and $g.CurrentVerticalResolution){[string]$g.CurrentHorizontalResolution+' x '+$g.CurrentVerticalResolution}else{$null};refreshHz=$g.CurrentRefreshRate;status=$g.Status}
  }}
  if(-not $dxgiAvailable -and -not $cim.Count){throw 'HARDWARE_GPU_UNAVAILABLE'}
}
function Get-LocalHardware {
  $sections=@()
  $sections+=Read-HardwareSection 'system' 'CIM/Win32_ComputerSystem' {
    Get-CimInstance Win32_ComputerSystem -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Model;manufacturer=$_.Manufacturer;systemType=$_.SystemType;usableMemoryBytes=$_.TotalPhysicalMemory;processorSockets=$_.NumberOfProcessors;logicalProcessors=$_.NumberOfLogicalProcessors;hypervisorPresent=$_.HypervisorPresent}}
  }
  $sections+=Read-HardwareSection 'cpu' 'CIM/Win32_Processor' {
    Get-CimInstance Win32_Processor -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Name;manufacturer=$_.Manufacturer;socket=$_.SocketDesignation;cores=$_.NumberOfCores;enabledCores=$_.NumberOfEnabledCore;threads=$_.NumberOfLogicalProcessors;maxClockMHz=$_.MaxClockSpeed;currentClockMHz=$_.CurrentClockSpeed;l2CacheKiB=$_.L2CacheSize;l3CacheKiB=$_.L3CacheSize;virtualizationFirmware=$_.VirtualizationFirmwareEnabled;architecture=$_.Architecture}}
  }
  $sections+=Read-HardwareSection 'gpu' 'DXGI 64-bit + CIM/Win32_VideoController' {Get-HardwareGpus}
  $sections+=Read-HardwareSection 'memory' 'CIM/Win32_PhysicalMemory' {
    Get-CimInstance Win32_PhysicalMemory -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.DeviceLocator;bank=$_.BankLabel;manufacturer=$_.Manufacturer;partNumber=([string]$_.PartNumber).Trim();capacityBytes=$_.Capacity;speedReported=$_.Speed;configuredSpeedReported=$_.ConfiguredClockSpeed;memoryType=$_.SMBIOSMemoryType;formFactor=$_.FormFactor;dataWidthBits=$_.DataWidth;totalWidthBits=$_.TotalWidth}}
  }
  $sections+=Read-HardwareSection 'memoryArrays' 'CIM/Win32_PhysicalMemoryArray' {
    Get-CimInstance Win32_PhysicalMemoryArray -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Location;slotsReported=$_.MemoryDevices;maxCapacityKiBReported=if($_.MaxCapacityEx){$_.MaxCapacityEx}else{$_.MaxCapacity};errorCorrection=$_.MemoryErrorCorrection}}
  }
  $sections+=Read-HardwareSection 'motherboard' 'CIM/Win32_BaseBoard' {
    Get-CimInstance Win32_BaseBoard -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Product;manufacturer=$_.Manufacturer;version=$_.Version;status=$_.Status}}
  }
  $sections+=Read-HardwareSection 'bios' 'CIM/Win32_BIOS' {
    Get-CimInstance Win32_BIOS -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.SMBIOSBIOSVersion;manufacturer=$_.Manufacturer;version=$_.Version;releaseDate=if($_.ReleaseDate){$_.ReleaseDate.ToUniversalTime().ToString('o')}else{$null};status=$_.Status}}
  }
  $sections+=Read-HardwareSection 'storage' 'CIM/Win32_DiskDrive + Get-Disk' {
    $disks=@();try{$disks=@(Get-Disk -ErrorAction Stop)}catch{}
    Get-CimInstance Win32_DiskDrive -OperationTimeoutSec 10|ForEach-Object {$d=$_;$extra=$disks|Where-Object {$_.Number -eq $d.Index}|Select-Object -First 1;[pscustomobject]@{name=$d.Model;manufacturer=$d.Manufacturer;capacityBytes=$d.Size;firmware=$d.FirmwareRevision;interface=$d.InterfaceType;mediaType=$d.MediaType;partitions=$d.Partitions;busType=if($extra){$extra.BusType.ToString()}else{$null};partitionStyle=if($extra){$extra.PartitionStyle.ToString()}else{$null};isBoot=if($extra){$extra.IsBoot}else{$null};isSystem=if($extra){$extra.IsSystem}else{$null};status=$d.Status}}
  }
  $sections+=Read-HardwareSection 'volumes' 'CIM/Win32_LogicalDisk' {
    Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=2 OR DriveType=3' -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.DeviceID;volumeLabel=$_.VolumeName;fileSystem=$_.FileSystem;capacityBytes=$_.Size;freeBytes=$_.FreeSpace;driveType=$_.DriveType}}
  }
  $sections+=Read-HardwareSection 'displays' 'CIM/root/wmi/WmiMonitorID + Win32_DesktopMonitor' {
    $ids=@();try{$ids=@(Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorID -OperationTimeoutSec 10 -ErrorAction Stop)}catch{}
    if($ids.Count){foreach($m in $ids){[pscustomobject]@{name=(-join @($m.UserFriendlyName|Where-Object {$_ -ne 0}|ForEach-Object {[char]$_}));manufacturer=(-join @($m.ManufacturerName|Where-Object {$_ -ne 0}|ForEach-Object {[char]$_}));active=$m.Active;source='EDID'}}}
    else{Get-CimInstance Win32_DesktopMonitor -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Name;manufacturer=$_.MonitorManufacturer;widthPixels=$_.ScreenWidth;heightPixels=$_.ScreenHeight;status=$_.Status;source='CIM'}}}
  }
  $sections+=Read-HardwareSection 'network' 'Get-NetAdapter' {
    Get-NetAdapter -IncludeHidden -ErrorAction Stop|ForEach-Object {[pscustomobject]@{name=$_.InterfaceDescription;connection=$_.Name;linkSpeed=$_.LinkSpeed;physical=$_.HardwareInterface;virtual=$_.Virtual;driverVersion=$_.DriverVersion;status=$_.Status.ToString()}}
  }
  $sections+=Read-HardwareSection 'audio' 'CIM/Win32_SoundDevice' {
    Get-CimInstance Win32_SoundDevice -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Name;manufacturer=$_.Manufacturer;status=$_.Status}}
  }
  $sections+=Read-HardwareSection 'battery' 'CIM/Win32_Battery' {
    Get-CimInstance Win32_Battery -OperationTimeoutSec 10|ForEach-Object {[pscustomobject]@{name=$_.Name;chargePercent=$_.EstimatedChargeRemaining;designVoltageMv=$_.DesignVoltage;batteryStatus=$_.BatteryStatus;status=$_.Status}}
  }
  $sections+=Read-HardwareSection 'devices' 'CIM/Win32_PnPEntity' {
    Get-CimInstance Win32_PnPEntity -OperationTimeoutSec 10|Where-Object {$_.Name}|ForEach-Object {[pscustomobject]@{name=$_.Name;manufacturer=$_.Manufacturer;deviceClass=$_.PNPClass;service=$_.Service;windowsErrorCode=$_.ConfigManagerErrorCode;present=$_.Present;status=$_.Status}}
  }
  return @{schema=1;at=(Get-Date).ToUniversalTime().ToString('o');readOnly=$true;online=$false;success=(-not @($sections|Where-Object {$_.status -eq 'unavailable' -or $_.limited}).Count);sections=$sections}
}
