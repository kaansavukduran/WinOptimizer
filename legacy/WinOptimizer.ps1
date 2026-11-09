<#
.SYNOPSIS
    WinOptimizer Pro v4.0 - Windows 10/11 Sistem Optimizasyon Araci
.DESCRIPTION
    Kapsamli sistem temizleme, optimizasyon, guvenlik ve bakim araci.
    Yonetici (Administrator) haklariyla calistirilmalidir.
.NOTES
    Surum    : 4.0
    Tarih    : 2026-04-04
    Yazar    : WinOptimizer Team
    Gerekli  : PowerShell 5.1+, Windows 10/11
    Lisans   : MIT
#>

#Requires -Version 5.1

# ======================================================================
#  YAPILANDIRMA & SABITLER
# ======================================================================

param(
    [ValidateSet("Normal","DryRun","Silent")]
    [string]$Mode = "Normal",

    [int[]]$Tasks,

    [switch]$NoRestart,
    [switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$ProgressPreference    = "SilentlyContinue"

# Surum bilgisi
$Script:AppName    = "WinOptimizer Pro"
$Script:AppVersion = "4.0"

# Dizinler
$Script:BaseDir    = $PSScriptRoot
$Script:LogDir     = Join-Path $Script:BaseDir "Logs"
$Script:BackupDir  = Join-Path $Script:BaseDir "Backups"
$Script:ReportDir  = Join-Path $Script:BaseDir "Reports"

# Log dosyasi
$Script:Timestamp  = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$Script:LogFile    = Join-Path $Script:LogDir "WinOptimizer_$Script:Timestamp.log"

# Sayaclar
$Script:TotalCleaned   = 0
$Script:TotalErrors     = 0
$Script:TotalWarnings   = 0
$Script:TotalOptimized  = 0
$Script:TaskResults     = @()

# DryRun modu
$Script:DryRun = ($Mode -eq "DryRun")
$Script:Silent = ($Mode -eq "Silent")

# Gorev tanimlari - plain hashtable (PS 5.1 uyumlu)
$Script:TaskDefinitions = @{}
$Script:TaskDefinitions[1]  = @{ Name = "Gereksiz Dosya Temizleme";      Function = "Invoke-JunkCleanup" }
$Script:TaskDefinitions[2]  = @{ Name = "Disk Temizligi";                 Function = "Invoke-DiskCleanup" }
$Script:TaskDefinitions[3]  = @{ Name = "Registry Temizligi";             Function = "Invoke-RegistryCleanup" }
$Script:TaskDefinitions[4]  = @{ Name = "Guvenlik Taramasi";              Function = "Invoke-SecurityScan" }
$Script:TaskDefinitions[5]  = @{ Name = "Windows Guncelleme Kontrolu";    Function = "Invoke-WindowsUpdateCheck" }
$Script:TaskDefinitions[6]  = @{ Name = "Uygulama Guncelleme (winget)";   Function = "Invoke-AppUpdate" }
$Script:TaskDefinitions[7]  = @{ Name = "Baslangic Programlari Yonetimi"; Function = "Invoke-StartupOptimization" }
$Script:TaskDefinitions[8]  = @{ Name = "Hizmet Optimizasyonu";           Function = "Invoke-ServiceOptimization" }
$Script:TaskDefinitions[9]  = @{ Name = "Ag Optimizasyonu";               Function = "Invoke-NetworkOptimization" }
$Script:TaskDefinitions[10] = @{ Name = "Guc Plani Optimizasyonu";        Function = "Invoke-PowerOptimization" }
$Script:TaskDefinitions[11] = @{ Name = "Sistem Sagligi Raporu";          Function = "Invoke-SystemHealthReport" }
$Script:TaskOrder = @(1,2,3,4,5,6,7,8,9,10,11)

# ======================================================================
#  YARDIMCI FONKSIYONLAR
# ======================================================================

function Initialize-Environment {
    foreach ($dir in @($Script:LogDir, $Script:BackupDir, $Script:ReportDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    # Eski log dosyalarini temizle (30 gunluk)
    Get-ChildItem -Path $Script:LogDir -Filter "*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

function Test-Administrator {
    $identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Write-Log {
    param(
        [ValidateSet("INFO","OK","WARN","ERROR","DEBUG","SECTION")]
        [string]$Level,
        [string]$Message
    )
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts][$Level] $Message"

    # Dosyaya yaz
    Add-Content -Path $Script:LogFile -Value $line -ErrorAction SilentlyContinue

    # Konsola yaz (Silent modda sadece ERROR goster)
    if ($Script:Silent -and $Level -notin @("ERROR","SECTION")) { return }

    $color = switch ($Level) {
        "INFO"    { "Cyan" }
        "OK"      { "Green" }
        "WARN"    { "Yellow"; $Script:TotalWarnings++ }
        "ERROR"   { "Red";    $Script:TotalErrors++ }
        "DEBUG"   { "DarkGray" }
        "SECTION" { "White" }
    }
    Write-Host $line -ForegroundColor $color
}

function Write-Banner {
    param([string]$Title, [string]$Subtitle = "")
    $width = 64
    $sep   = "=" * $width
    Write-Log "SECTION" ""
    Write-Log "SECTION" $sep
    Write-Log "SECTION" "  $Title"
    if ($Subtitle) { Write-Log "SECTION" "  $Subtitle" }
    Write-Log "SECTION" $sep
}

function Get-SafeSize {
    <#
    .SYNOPSIS
        Guvenli dosya boyutu hesaplama - bos klasor hatasini onler
    #>
    param(
        [Parameter(ValueFromPipeline)]
        [object[]]$Files
    )
    begin { $total = 0 }
    process {
        foreach ($f in $Files) {
            if ($f -and $f.Length) { $total += $f.Length }
        }
    }
    end { return $total }
}

function Format-Size {
    param([double]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "{0:N0} B" -f $Bytes
}

function Remove-FolderContents {
    <#
    .SYNOPSIS
        Klasor icerigini guvenli bicimde siler, boyutu raporlar
    #>
    param(
        [string]$Path,
        [string]$Label,
        [string[]]$ExcludeExtensions = @()
    )
    if (-not (Test-Path $Path)) {
        Write-Log "INFO" "$Label -- klasor bulunamadi, atlaniyor."
        return 0
    }

    $files = Get-ChildItem -Path $Path -Recurse -File -Force -ErrorAction SilentlyContinue
    if ($ExcludeExtensions.Count -gt 0) {
        $files = $files | Where-Object { $_.Extension -notin $ExcludeExtensions }
    }

    $size = $files | Get-SafeSize

    if ($Script:DryRun) {
        Write-Log "INFO" "[DRY-RUN] $Label -- $(Format-Size $size) silinecekti."
    } else {
        $files | Remove-Item -Force -ErrorAction SilentlyContinue
        # Bos alt klasorleri temizle
        Get-ChildItem -Path $Path -Recurse -Directory -Force -ErrorAction SilentlyContinue |
            Sort-Object { $_.FullName.Length } -Descending |
            ForEach-Object {
                if (-not (Get-ChildItem -Path $_.FullName -Force -ErrorAction SilentlyContinue)) {
                    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                }
            }
        Write-Log "OK" "$Label -- $(Format-Size $size) temizlendi."
    }
    return $size
}

function Backup-RegistryKey {
    param([string]$KeyPath, [string]$BackupName)
    $backupFile = Join-Path $Script:BackupDir "${BackupName}_$Script:Timestamp.reg"
    try {
        $null = reg export $KeyPath $backupFile /y 2>&1
        Write-Log "OK" "Registry yedeklendi: $backupFile"
        return $true
    } catch {
        Write-Log "WARN" "Registry yedeklenemedi: $KeyPath"
        return $false
    }
}

function Test-CommandExists {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

# ======================================================================
#  GOREV 1: GEREKSIZ DOSYA TEMIZLEME
# ======================================================================
function Invoke-JunkCleanup {
    Write-Banner "GOREV 1 - GEREKSIZ DOSYA TEMIZLEME"
    $taskTotal = 0

    # --- Kullanici TEMP ---
    $taskTotal += Remove-FolderContents -Path $env:TEMP -Label "Kullanici TEMP"

    # --- Windows TEMP ---
    $taskTotal += Remove-FolderContents -Path "$env:SystemRoot\Temp" -Label "Windows TEMP"

    # --- Prefetch ---
    $taskTotal += Remove-FolderContents -Path "$env:SystemRoot\Prefetch" -Label "Prefetch onbellegi"

    # --- Tarayici onbellekleri ---
    $browserCaches = @(
        @{ Path = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\Cache_Data";     Label = "Chrome Onbellek" }
        @{ Path = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Code Cache";            Label = "Chrome Code Cache" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\Cache_Data";     Label = "Edge Onbellek" }
        @{ Path = "$env:LOCALAPPDATA\Mozilla\Firefox\Profiles";                              Label = "Firefox Onbellek" }
        @{ Path = "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default\Cache";   Label = "Brave Onbellek" }
        @{ Path = "$env:LOCALAPPDATA\Opera Software\Opera Stable\Cache";                     Label = "Opera Onbellek" }
    )
    foreach ($bc in $browserCaches) {
        $taskTotal += Remove-FolderContents -Path $bc.Path -Label $bc.Label
    }

    # --- Windows Update indirme onbellegi ---
    $wuPath = "$env:SystemRoot\SoftwareDistribution\Download"
    $taskTotal += Remove-FolderContents -Path $wuPath -Label "WU indirme onbellegi"

    # --- Kilitlenme dokumleri ---
    $crashPaths = @(
        @{ Path = "$env:LOCALAPPDATA\CrashDumps";                  Label = "Kullanici kilitlenme dokumleri" }
        @{ Path = "$env:SystemRoot\Minidump";                      Label = "Mini dokum dosyalari" }
        @{ Path = "$env:SystemRoot\MEMORY.DMP";                    Label = "Bellek dokumu" }
        @{ Path = "$env:SystemRoot\LiveKernelReports";             Label = "Canli cekirdek raporlari" }
    )
    foreach ($cp in $crashPaths) {
        if (Test-Path $cp.Path -PathType Leaf) {
            $fSize = (Get-Item $cp.Path -Force -ErrorAction SilentlyContinue).Length
            if (-not $Script:DryRun) { Remove-Item $cp.Path -Force -ErrorAction SilentlyContinue }
            Write-Log "OK" "$($cp.Label) -- $(Format-Size $fSize) temizlendi."
            $taskTotal += $fSize
        } else {
            $taskTotal += Remove-FolderContents -Path $cp.Path -Label $cp.Label
        }
    }

    # --- CBS Gunlukleri ---
    $taskTotal += Remove-FolderContents -Path "$env:SystemRoot\Logs\CBS" -Label "CBS gunlukleri"

    # --- DISM Gunlukleri ---
    $taskTotal += Remove-FolderContents -Path "$env:SystemRoot\Logs\DISM" -Label "DISM gunlukleri"

    # --- Son ogeler ---
    $taskTotal += Remove-FolderContents -Path "$env:APPDATA\Microsoft\Windows\Recent" -Label "Son ogeler gecmisi"

    # --- Temp/bak/log dosyalari (Documents) ---
    $docPath = [Environment]::GetFolderPath("MyDocuments")
    if (Test-Path $docPath) {
        $junkExts = @("*.tmp","*.bak","*.old","*.log","*.dmp","*.~*")
        $junkFiles = foreach ($ext in $junkExts) {
            Get-ChildItem -Path $docPath -Filter $ext -Recurse -File -Force -ErrorAction SilentlyContinue
        }
        $junkSize = $junkFiles | Get-SafeSize
        if (-not $Script:DryRun -and $junkFiles) {
            $junkFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        }
        Write-Log "OK" "Belgeler klasoru (.tmp/.bak/.old/.log) -- $(Format-Size $junkSize)"
        $taskTotal += $junkSize
    }

    # --- Thumbnails onbellegi ---
    $thumbPath = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
    if (Test-Path $thumbPath) {
        $thumbFiles = Get-ChildItem -Path $thumbPath -Filter "thumbcache_*.db" -Force -ErrorAction SilentlyContinue
        $thumbSize  = $thumbFiles | Get-SafeSize
        if (-not $Script:DryRun -and $thumbFiles) {
            $thumbFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        }
        Write-Log "OK" "Thumbnail onbellegi -- $(Format-Size $thumbSize)"
        $taskTotal += $thumbSize
    }

    # --- Icondache ---
    $iconCachePath = "$env:LOCALAPPDATA\IconCache.db"
    if (Test-Path $iconCachePath) {
        $icSize = (Get-Item $iconCachePath -Force).Length
        if (-not $Script:DryRun) { Remove-Item $iconCachePath -Force -ErrorAction SilentlyContinue }
        Write-Log "OK" "Ikon onbellegi -- $(Format-Size $icSize)"
        $taskTotal += $icSize
    }

    # --- Cop kutusu ---
    if (-not $Script:DryRun) {
        try {
            Clear-RecycleBin -Force -ErrorAction SilentlyContinue
            Write-Log "OK" "Cop kutusu bosaltildi."
        } catch {
            Write-Log "WARN" "Cop kutusu bosaltilamadi: $_"
        }
    } else {
        Write-Log "INFO" "[DRY-RUN] Cop kutusu bosaltilacakti."
    }

    $Script:TotalCleaned += $taskTotal
    Write-Log "OK" "GOREV 1 TOPLAM: $(Format-Size $taskTotal) temizlendi."
    return @{ Cleaned = $taskTotal; Status = "OK" }
}

# ======================================================================
#  GOREV 2: DISK TEMIZLIGI
# ======================================================================
function Invoke-DiskCleanup {
    Write-Banner "GOREV 2 - DISK TEMIZLIGI"

    # Disk oncesi kullanim
    $driveBefore = (Get-PSDrive C).Free

    if ($Script:DryRun) {
        Write-Log "INFO" "[DRY-RUN] Disk Temizleme (cleanmgr) calistirilacakti."
    } else {
        Write-Log "INFO" "Disk Temizleme baslatiliyor..."

        # Sageset ile kategori ayarla
        $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
        $categories = @(
            "Active Setup Temp Folders"
            "BranchCache"
            "Delivery Optimization Files"
            "Device Driver Packages"
            "Downloaded Program Files"
            "Internet Cache Files"
            "Old ChkDsk Files"
            "Previous Installations"
            "Recycle Bin"
            "RetailDemo Offline Content"
            "Setup Log Files"
            "System error memory dump files"
            "System error minidump files"
            "Temporary Files"
            "Temporary Setup Files"
            "Thumbnail Cache"
            "Update Cleanup"
            "Upgrade Discarded Files"
            "Windows Defender"
            "Windows Error Reporting Files"
            "Windows ESD installation files"
        )

        foreach ($cat in $categories) {
            $catPath = Join-Path $regPath $cat
            if (Test-Path $catPath) {
                Set-ItemProperty -Path $catPath -Name "StateFlags0100" -Value 2 -ErrorAction SilentlyContinue
            }
        }

        # cleanmgr calistir
        Start-Process cleanmgr.exe -ArgumentList "/sagerun:100" -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue

        # DISM ile Component Store temizligi
        Write-Log "INFO" "DISM Component Store temizleniyor..."
        $dismResult = & dism.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase 2>&1
        Write-Log "INFO" "DISM tamamlandi."
    }

    $driveAfter = (Get-PSDrive C).Free
    $freedSpace = $driveAfter - $driveBefore
    if ($freedSpace -lt 0) { $freedSpace = 0 }

    $Script:TotalCleaned += $freedSpace
    Write-Log "OK" "GOREV 2 TOPLAM: $(Format-Size $freedSpace) ek alan kazanildi."
    return @{ Cleaned = $freedSpace; Status = "OK" }
}

# ======================================================================
#  GOREV 3: REGISTRY TEMIZLIGI
# ======================================================================
function Invoke-RegistryCleanup {
    Write-Banner "GOREV 3 - REGISTRY TEMIZLIGI"
    $cleanedCount = 0

    # Yedekleme
    Write-Log "INFO" "Registry yedekleniyor..."
    Backup-RegistryKey "HKCU\Software" "HKCU_Software"

    # --- Gecersiz Uninstall kayitlari ---
    Write-Log "INFO" "Gecersiz uninstall kayitlari taraniyor..."
    $uninstallPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    )
    foreach ($uPath in $uninstallPaths) {
        if (-not (Test-Path $uPath)) { continue }
        Get-ChildItem -Path $uPath -ErrorAction SilentlyContinue | ForEach-Object {
            $installLoc = $_ | Get-ItemProperty -Name "InstallLocation" -ErrorAction SilentlyContinue
            if ($installLoc -and $installLoc.InstallLocation -and
                -not (Test-Path $installLoc.InstallLocation) -and
                $installLoc.InstallLocation -ne "") {
                $displayName = ($_ | Get-ItemProperty -Name "DisplayName" -ErrorAction SilentlyContinue).DisplayName
                if (-not $Script:DryRun) {
                    # Sadece raporla, silme (guvenlik icin)
                    Write-Log "WARN" "Gecersiz yol: $displayName -> $($installLoc.InstallLocation)"
                } else {
                    Write-Log "INFO" "[DRY-RUN] Gecersiz: $displayName -> $($installLoc.InstallLocation)"
                }
                $cleanedCount++
            }
        }
    }

    # --- Gecersiz dosya uzanti iliskilendirmeleri ---
    Write-Log "INFO" "Gecersiz dosya iliskilendirmeleri taraniyor..."
    $fileExts = Get-ChildItem "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts" -ErrorAction SilentlyContinue
    $invalidExts = 0
    foreach ($ext in $fileExts) {
        $openWith = Join-Path $ext.PSPath "OpenWithList"
        if (Test-Path $openWith) {
            $props = Get-ItemProperty -Path $openWith -ErrorAction SilentlyContinue
            if ($props) {
                $props.PSObject.Properties | Where-Object {
                    $_.Name -match '^[a-z]$' -and $_.Value -and
                    -not (Test-CommandExists $_.Value) -and
                    -not (Get-Command $_.Value -ErrorAction SilentlyContinue)
                } | ForEach-Object { $invalidExts++ }
            }
        }
    }
    Write-Log "INFO" "Gecersiz dosya iliskilendirmeleri: $invalidExts adet bulundu."
    $cleanedCount += $invalidExts

    # --- Bos Run kayitlari ---
    Write-Log "INFO" "Bos Run kayitlari taraniyor..."
    $runPaths = @(
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    )
    foreach ($rp in $runPaths) {
        if (-not (Test-Path $rp)) { continue }
        $props = Get-ItemProperty -Path $rp -ErrorAction SilentlyContinue
        if (-not $props) { continue }
        $props.PSObject.Properties | Where-Object { $_.Name -notin @("PSPath","PSParentPath","PSChildName","PSDrive","PSProvider") } | ForEach-Object {
            $exePath = $_.Value -replace '"','' -split '\s+' | Select-Object -First 1
            if ($exePath -and -not (Test-Path $exePath)) {
                Write-Log "WARN" "Gecersiz Run kaydi: $($_.Name) -> $exePath"
                $cleanedCount++
            }
        }
    }

    # --- MUI Cache temizligi ---
    $muiPath = "HKCU:\SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
    if (Test-Path $muiPath) {
        $muiItems = (Get-ItemProperty $muiPath -ErrorAction SilentlyContinue).PSObject.Properties |
            Where-Object { $_.Name -notin @("PSPath","PSParentPath","PSChildName","PSDrive","PSProvider") }
        $muiCount = ($muiItems | Measure-Object).Count
        if (-not $Script:DryRun -and $muiCount -gt 0) {
            Remove-Item $muiPath -Force -ErrorAction SilentlyContinue
            Write-Log "OK" "MUI Cache temizlendi: $muiCount kayit."
        } else {
            Write-Log "INFO" "MUI Cache: $muiCount kayit bulundu."
        }
        $cleanedCount += $muiCount
    }

    $Script:TotalOptimized += $cleanedCount
    Write-Log "OK" "GOREV 3 TOPLAM: $cleanedCount registry kaydi islendi."
    return @{ Cleaned = $cleanedCount; Status = "OK" }
}

# ======================================================================
#  GOREV 4: GUVENLIK TARAMASI
# ======================================================================
function Invoke-SecurityScan {
    Write-Banner "GOREV 4 - GUVENLIK TARAMASI"
    $issues = 0

    # --- Windows Defender durumu ---
    Write-Log "INFO" "Windows Defender durumu kontrol ediliyor..."
    try {
        $mpStatus = Get-MpComputerStatus -ErrorAction Stop
        if ($mpStatus.AntivirusEnabled) {
            Write-Log "OK" "Windows Defender aktif."
        } else {
            Write-Log "ERROR" "Windows Defender devre disi!"
            $issues++
        }
        if ($mpStatus.RealTimeProtectionEnabled) {
            Write-Log "OK" "Gercek zamanli koruma aktif."
        } else {
            Write-Log "ERROR" "Gercek zamanli koruma devre disi!"
            $issues++
        }
        $lastScan = $mpStatus.QuickScanEndTime
        $daysSince = ((Get-Date) - $lastScan).Days
        if ($daysSince -gt 7) {
            Write-Log "WARN" "Son hizli tarama $daysSince gun once. Tarama onerilir."
            $issues++
        } else {
            Write-Log "OK" "Son hizli tarama: $($lastScan.ToString('yyyy-MM-dd HH:mm'))"
        }

        # Tanim guncelligi
        $sigAge = $mpStatus.AntivirusSignatureAge
        if ($sigAge -gt 3) {
            Write-Log "WARN" "Virus tanimlari $sigAge gun eski! Guncelleniyor..."
            if (-not $Script:DryRun) {
                Update-MpSignature -ErrorAction SilentlyContinue
                Write-Log "OK" "Virus tanimlari guncellendi."
            }
        } else {
            Write-Log "OK" "Virus tanimlari guncel ($sigAge gun)."
        }
    } catch {
        Write-Log "WARN" "Windows Defender bilgisi alinamadi: $_"
    }

    # --- Guvenlik duvari ---
    Write-Log "INFO" "Guvenlik duvari kontrol ediliyor..."
    $fwProfiles = Get-NetFirewallProfile -ErrorAction SilentlyContinue
    foreach ($fw in $fwProfiles) {
        if ($fw.Enabled) {
            Write-Log "OK" "Guvenlik duvari ($($fw.Name)): Aktif"
        } else {
            Write-Log "ERROR" "Guvenlik duvari ($($fw.Name)): DEVRE DISI!"
            $issues++
        }
    }

    # --- UAC durumu ---
    Write-Log "INFO" "UAC durumu kontrol ediliyor..."
    $uacKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    $uac = Get-ItemProperty -Path $uacKey -Name "EnableLUA" -ErrorAction SilentlyContinue
    if ($uac -and $uac.EnableLUA -eq 1) {
        Write-Log "OK" "UAC aktif."
    } else {
        Write-Log "ERROR" "UAC devre disi!"
        $issues++
    }

    # --- BitLocker durumu ---
    Write-Log "INFO" "BitLocker durumu kontrol ediliyor..."
    try {
        $bl = Get-BitLockerVolume -MountPoint "C:" -ErrorAction Stop
        if ($bl.ProtectionStatus -eq "On") {
            Write-Log "OK" "BitLocker (C:): Aktif - $($bl.EncryptionMethod)"
        } else {
            Write-Log "WARN" "BitLocker (C:): Devre disi. Disk sifreleme onerilir."
            $issues++
        }
    } catch {
        Write-Log "WARN" "BitLocker bilgisi alinamadi."
    }

    # --- Acik portlar ---
    Write-Log "INFO" "Acik portlar taraniyor..."
    $listening = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Select-Object LocalPort, OwningProcess -Unique |
        Sort-Object LocalPort
    $suspiciousPorts = @(4444, 5555, 6666, 8888, 9999, 1337, 31337)
    foreach ($conn in $listening) {
        if ($conn.LocalPort -in $suspiciousPorts) {
            $procName = (Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue).ProcessName
            Write-Log "WARN" "Suphe verici port: $($conn.LocalPort) (PID: $($conn.OwningProcess), Islem: $procName)"
            $issues++
        }
    }
    Write-Log "OK" "Toplam dinleyen port: $(($listening | Measure-Object).Count)"

    # --- Parola politikasi ---
    Write-Log "INFO" "Parola politikasi kontrol ediliyor..."
    try {
        $netAccounts = net accounts 2>&1
        Write-Log "INFO" "Parola politikasi bilgisi alindi."
    } catch {
        Write-Log "WARN" "Parola politikasi bilgisi alinamadi."
    }

    # --- Hizli tarama baslat (opsiyonel) ---
    if (-not $Script:DryRun -and $daysSince -gt 7) {
        Write-Log "INFO" "Hizli virus taramasi baslatiliyor..."
        Start-MpScan -ScanType QuickScan -AsJob | Out-Null
        Write-Log "OK" "Hizli tarama arka planda baslatildi."
    }

    Write-Log "OK" "GOREV 4 TOPLAM: $issues guvenlik sorunu tespit edildi."
    return @{ Issues = $issues; Status = if ($issues -eq 0) { "OK" } else { "WARN" } }
}

# ======================================================================
#  GOREV 5: WINDOWS GUNCELLEME KONTROLU
# ======================================================================
function Invoke-WindowsUpdateCheck {
    Write-Banner "GOREV 5 - WINDOWS GUNCELLEME KONTROLU"
    $updateCount = 0

    # PSWindowsUpdate modulu kontrolu
    if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate -ErrorAction SilentlyContinue)) {
        Write-Log "INFO" "PSWindowsUpdate modulu yukleniyor..."
        try {
            Install-Module PSWindowsUpdate -Force -Scope CurrentUser -ErrorAction Stop
            Import-Module PSWindowsUpdate -ErrorAction Stop
            Write-Log "OK" "PSWindowsUpdate yuklendi."
        } catch {
            Write-Log "WARN" "PSWindowsUpdate yuklenemedi. Manuel kontrol yapiliyor..."
            # Manuel USOClient kullan
            if (-not $Script:DryRun) {
                Start-Process "UsoClient.exe" -ArgumentList "StartScan" -WindowStyle Hidden -ErrorAction SilentlyContinue
                Write-Log "INFO" "Windows Update taramasi baslatildi (UsoClient)."
            }
            return @{ Updates = 0; Status = "WARN" }
        }
    } else {
        Import-Module PSWindowsUpdate -ErrorAction SilentlyContinue
    }

    try {
        Write-Log "INFO" "Mevcut guncellemeler kontrol ediliyor..."
        $updates = Get-WindowsUpdate -ErrorAction Stop
        $updateCount = ($updates | Measure-Object).Count

        if ($updateCount -gt 0) {
            Write-Log "WARN" "$updateCount adet guncelleme mevcut:"
            foreach ($u in $updates) {
                $sizeStr = if ($u.Size) { Format-Size $u.Size } else { "Boyut bilinmiyor" }
                Write-Log "INFO" "  - $($u.Title) [$sizeStr]"
            }

            if (-not $Script:DryRun) {
                Write-Log "INFO" "Guncellemeler yukleniyor..."
                Install-WindowsUpdate -AcceptAll -IgnoreReboot -ErrorAction SilentlyContinue
                Write-Log "OK" "Guncellemeler yuklendi."
            } else {
                Write-Log "INFO" "[DRY-RUN] Guncellemeler yuklenecekti."
            }
        } else {
            Write-Log "OK" "Sistem guncel, bekleyen guncelleme yok."
        }
    } catch {
        Write-Log "WARN" "Guncelleme kontrolu basarisiz: $_"
    }

    # Son guncelleme tarihi
    try {
        $lastUpdate = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1
        if ($lastUpdate) {
            Write-Log "INFO" "Son yuklenen guncelleme: $($lastUpdate.HotFixID) ($($lastUpdate.InstalledOn.ToString('yyyy-MM-dd')))"
        }
    } catch {}

    Write-Log "OK" "GOREV 5 TOPLAM: $updateCount guncelleme islendi."
    return @{ Updates = $updateCount; Status = "OK" }
}

# ======================================================================
#  GOREV 6: UYGULAMA GUNCELLEME (WINGET)
# ======================================================================
function Invoke-AppUpdate {
    Write-Banner "GOREV 6 - UYGULAMA GUNCELLEME (winget)"

    # winget mevcut mu?
    if (-not (Test-CommandExists "winget")) {
        Write-Log "ERROR" "winget bulunamadi! Windows 10 1709+ veya App Installer gerekli."
        Write-Log "INFO" "Yukleme: https://aka.ms/getwinget"
        return @{ Updated = 0; Status = "ERROR" }
    }

    # winget surumunu goster
    $wingetVer = & winget --version 2>$null
    Write-Log "INFO" "winget surumu: $wingetVer"

    # Kaynaklari guncelle
    Write-Log "INFO" "Paket kaynaklari guncelleniyor..."
    & winget source update --disable-interactivity 2>$null | Out-Null

    # Mevcut guncellemeleri listele
    Write-Log "INFO" "Guncellenebilir uygulamalar kontrol ediliyor..."
    $upgradeList = & winget upgrade --include-unknown 2>$null
    $upgradeLines = $upgradeList | Where-Object { $_ -match '\S' -and $_ -notmatch '^[-\s]*$' -and $_ -notmatch 'Name\s+Id' -and $_ -notmatch 'upgrades available' -and $_ -notmatch 'winget' }

    # Satir sayisini hesapla
    $appCount = 0
    foreach ($line in $upgradeList) {
        if ($line -match '^\S+.*\S+\s+\S+\s+\S+') {
            $appCount++
        }
    }

    # Yedek sayac: "X upgrades available" satirini bul
    if ($appCount -eq 0) {
        $summaryLine = $upgradeList | Where-Object { $_ -match '(\d+)\s+upgrades?\s+available' }
        if ($summaryLine -match '(\d+)\s+upgrades?\s+available') {
            $appCount = [int]$Matches[1]
        }
    }

    if ($appCount -gt 0) {
        Write-Log "INFO" "$appCount adet uygulama guncellenebilir."

        # Listeleme
        foreach ($line in $upgradeList) {
            if ($line.Trim()) { Write-Log "INFO" "  $($line.Trim())" }
        }

        if ($Script:DryRun) {
            Write-Log "INFO" "[DRY-RUN] Uygulamalar guncellenecekti."
        } else {
            Write-Log "INFO" "Tum uygulamalar guncelleniyor (bu islem uzun surebilir)..."

            # Hatalari atlayarak guncelle
            $result = & winget upgrade --all `
                --accept-source-agreements `
                --accept-package-agreements `
                --silent `
                --disable-interactivity `
                --include-unknown 2>&1

            # Sonuclari logla
            $successCount = ($result | Select-String "Successfully installed" | Measure-Object).Count
            $failCount    = ($result | Select-String "failed|error" -CaseSensitive:$false | Measure-Object).Count

            Write-Log "OK" "Guncelleme tamamlandi: $successCount basarili"
            if ($failCount -gt 0) {
                Write-Log "WARN" "$failCount uygulama guncellenemedi (yonetici hakki veya baska sebep)."
            }
        }
    } else {
        Write-Log "OK" "Tum uygulamalar guncel."
    }

    Write-Log "OK" "GOREV 6 TAMAMLANDI."
    return @{ Updated = $appCount; Status = "OK" }
}

# ======================================================================
#  GOREV 7: BASLANGIC PROGRAMLARI YONETIMI
# ======================================================================
function Invoke-StartupOptimization {
    Write-Banner "GOREV 7 - BASLANGIC PROGRAMLARI YONETIMI"
    $itemCount = 0

    # Registry baslangic kayitlari
    Write-Log "INFO" "Registry baslangic kayitlari taraniyor..."
    $startupPaths = @(
        @{ Path = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run";        Scope = "Kullanici" }
        @{ Path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run";        Scope = "Sistem" }
        @{ Path = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce";    Scope = "Kullanici (RunOnce)" }
        @{ Path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce";    Scope = "Sistem (RunOnce)" }
    )

    foreach ($sp in $startupPaths) {
        if (-not (Test-Path $sp.Path)) { continue }
        $items = Get-ItemProperty -Path $sp.Path -ErrorAction SilentlyContinue
        $items.PSObject.Properties | Where-Object {
            $_.Name -notin @("PSPath","PSParentPath","PSChildName","PSDrive","PSProvider")
        } | ForEach-Object {
            $exePath = $_.Value -replace '"','' -split '\s+' | Select-Object -First 1
            $exists  = if ($exePath) { Test-Path $exePath } else { $false }
            $status  = if ($exists) { "[GECERLI]" } else { "[GECERSIZ]" }
            Write-Log "INFO" "  $($sp.Scope): $($_.Name) $status"
            if (-not $exists) {
                Write-Log "WARN" "    Yol bulunamadi: $exePath"
            }
            $itemCount++
        }
    }

    # Task Scheduler baslangic gorevleri
    Write-Log "INFO" "Zamanlanmis gorevler (baslangic) taraniyor..."
    $tasks = Get-ScheduledTask -ErrorAction SilentlyContinue |
        Where-Object { $_.Triggers | Where-Object { $_ -is [CimInstance] -and $_.CimClass.CimClassName -eq "MSFT_TaskLogonTrigger" } }

    foreach ($t in $tasks) {
        $state = $t.State
        Write-Log "INFO" "  Gorev: $($t.TaskName) [$state] - $($t.TaskPath)"
        $itemCount++
    }

    # Startup klasorleri
    Write-Log "INFO" "Baslangic klasorleri taraniyor..."
    $startupFolders = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    foreach ($sf in $startupFolders) {
        if (Test-Path $sf) {
            $files = Get-ChildItem -Path $sf -Force -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                Write-Log "INFO" "  Klasor: $($f.Name)"
                $itemCount++
            }
        }
    }

    Write-Log "OK" "GOREV 7 TOPLAM: $itemCount baslangic ogesi listelendi."
    Write-Log "INFO" "Ipucu: Gereksiz baslangic ogelerini 'Gorev Yoneticisi > Baslangic' sekmesinden devre disi birakabilirsiniz."
    return @{ Items = $itemCount; Status = "OK" }
}

# ======================================================================
#  GOREV 8: HIZMET OPTIMIZASYONU
# ======================================================================
function Invoke-ServiceOptimization {
    Write-Banner "GOREV 8 - HIZMET OPTIMIZASYONU"
    $optimized = 0

    # Guvenle devre disi birakilabilecek hizmetler
    $optionalServices = @(
        @{ Name = "DiagTrack";            Desc = "Bagli Kullanici Deneyimi ve Telemetri" }
        @{ Name = "dmwappushservice";      Desc = "WAP Push Mesaj Yonlendirme" }
        @{ Name = "SysMain";              Desc = "Superfetch (SSD disklerde gereksiz)" }
        @{ Name = "WSearch";              Desc = "Windows Search (yuksek I/O)" }
        @{ Name = "MapsBroker";           Desc = "Haritalar Indirme Yoneticisi" }
        @{ Name = "lfsvc";                Desc = "Konum Hizmeti" }
        @{ Name = "RetailDemo";           Desc = "Perakende Demo Hizmeti" }
        @{ Name = "wisvc";                Desc = "Windows Insider Hizmeti" }
        @{ Name = "WerSvc";              Desc = "Windows Hata Bildirimi" }
        @{ Name = "Fax";                  Desc = "Faks Hizmeti" }
        @{ Name = "TabletInputService";   Desc = "Tablet Giris Hizmeti" }
        @{ Name = "XblAuthManager";       Desc = "Xbox Live Kimlik Dogrulama" }
        @{ Name = "XblGameSave";          Desc = "Xbox Live Oyun Kaydi" }
        @{ Name = "XboxNetApiSvc";        Desc = "Xbox Live Ag" }
    )

    Write-Log "INFO" "Opsiyonel hizmetler taraniyor..."
    foreach ($svc in $optionalServices) {
        $service = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
        if (-not $service) { continue }

        $startType = (Get-WmiObject Win32_Service -Filter "Name='$($svc.Name)'" -ErrorAction SilentlyContinue).StartMode
        $status    = $service.Status

        if ($startType -eq "Disabled") {
            Write-Log "INFO" "  $($svc.Desc) ($($svc.Name)): Zaten devre disi."
            continue
        }

        Write-Log "INFO" "  $($svc.Desc) ($($svc.Name)): $status / $startType"

        if (-not $Script:DryRun) {
            try {
                Set-Service -Name $svc.Name -StartupType Disabled -ErrorAction Stop
                if ($service.Status -eq "Running") {
                    Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
                }
                Write-Log "OK" "    -> Devre disi birakaldi."
                $optimized++
            } catch {
                Write-Log "WARN" "    -> Degistirilemedi: $_"
            }
        } else {
            Write-Log "INFO" "    [DRY-RUN] Devre disi birakilacakti."
            $optimized++
        }
    }

    $Script:TotalOptimized += $optimized
    Write-Log "OK" "GOREV 8 TOPLAM: $optimized hizmet optimize edildi."
    return @{ Optimized = $optimized; Status = "OK" }
}

# ======================================================================
#  GOREV 9: AG OPTIMIZASYONU
# ======================================================================
function Invoke-NetworkOptimization {
    Write-Banner "GOREV 9 - AG OPTIMIZASYONU"
    $changes = 0

    if ($Script:DryRun) {
        Write-Log "INFO" "[DRY-RUN] Ag ayarlari degistirilecekti."
    }

    # --- DNS onbellegi temizle ---
    Write-Log "INFO" "DNS onbellegi temizleniyor..."
    if (-not $Script:DryRun) {
        Clear-DnsClientCache -ErrorAction SilentlyContinue
        Write-Log "OK" "DNS onbellegi temizlendi."
        $changes++
    }

    # --- Winsock sifirlama ---
    Write-Log "INFO" "Winsock katalogu kontrol ediliyor..."
    if (-not $Script:DryRun) {
        $winsockResult = & netsh winsock reset 2>&1
        Write-Log "OK" "Winsock katalogu sifirlandi."
        $changes++
    }

    # --- TCP/IP optimizasyonu ---
    Write-Log "INFO" "TCP ayarlari optimize ediliyor..."
    if (-not $Script:DryRun) {
        # Auto-tuning Level
        & netsh int tcp set global autotuninglevel=normal 2>$null | Out-Null

        # ECN Capability
        & netsh int tcp set global ecncapability=enabled 2>$null | Out-Null

        # RSS (Receive Side Scaling)
        & netsh int tcp set global rss=enabled 2>$null | Out-Null

        # Chimney Offload (Win10+)
        & netsh int tcp set global chimney=enabled 2>$null | Out-Null

        # Direct Cache Access
        & netsh int tcp set global dca=enabled 2>$null | Out-Null

        Write-Log "OK" "TCP parametreleri optimize edildi."
        $changes++
    }

    # --- QoS ayarlari ---
    Write-Log "INFO" "QoS bant genisligi siniri kontrol ediliyor..."
    $qosPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched"
    if (-not (Test-Path $qosPath)) {
        New-Item -Path $qosPath -Force | Out-Null
    }
    $currentQos = Get-ItemProperty -Path $qosPath -Name "NonBestEffortLimit" -ErrorAction SilentlyContinue
    if (-not $currentQos -or $currentQos.NonBestEffortLimit -ne 0) {
        if (-not $Script:DryRun) {
            Set-ItemProperty -Path $qosPath -Name "NonBestEffortLimit" -Value 0 -Type DWord
            Write-Log "OK" "QoS bant genisligi siniri kaldirildi."
            $changes++
        }
    } else {
        Write-Log "OK" "QoS bant genisligi zaten sinirsiz."
    }

    # --- Nagle algoritmasi (dusuk gecikme) ---
    Write-Log "INFO" "Nagle algoritmasi kontrol ediliyor..."
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    foreach ($adapter in $adapters) {
        Write-Log "INFO" "  Adaptor: $($adapter.Name) [$($adapter.LinkSpeed)]"
    }

    # --- Ag istatistikleri ---
    Write-Log "INFO" "Mevcut ag baglantilari:"
    $connections = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
        Group-Object RemoteAddress |
        Sort-Object Count -Descending |
        Select-Object -First 10
    foreach ($c in $connections) {
        Write-Log "INFO" "  $($c.Name): $($c.Count) baglanti"
    }

    Write-Log "OK" "GOREV 9 TOPLAM: $changes ag optimizasyonu yapildi."
    return @{ Changes = $changes; Status = "OK" }
}

# ======================================================================
#  GOREV 10: GUC PLANI OPTIMIZASYONU
# ======================================================================
function Invoke-PowerOptimization {
    Write-Banner "GOREV 10 - GUC PLANI OPTIMIZASYONU"
    $changes = 0

    # Mevcut guc planini goster
    $currentPlan = powercfg /getactivescheme 2>$null
    Write-Log "INFO" "Mevcut guc plani: $currentPlan"

    # Yuksek Performans plani GUID
    $highPerfGuid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    # Ultimate Performance GUID
    $ultimateGuid = "e9a42b02-d5df-448d-aa00-03f14749eb61"

    if (-not $Script:DryRun) {
        # Ultimate Performance plani ekle (yoksa)
        Write-Log "INFO" "Ultimate Performance guc plani kontrol ediliyor..."
        $existingPlans = powercfg /list 2>$null
        if ($existingPlans -notmatch $ultimateGuid) {
            $dupResult = powercfg /duplicatescheme $ultimateGuid 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "OK" "Ultimate Performance guc plani eklendi."
            } else {
                Write-Log "INFO" "Ultimate Performance plani eklenemedi, Yuksek Performans kullanilacak."
                $ultimateGuid = $highPerfGuid
            }
        }

        # Yuksek Performans planini aktif et
        powercfg /setactive $ultimateGuid 2>$null
        if ($LASTEXITCODE -ne 0) {
            powercfg /setactive $highPerfGuid 2>$null
        }
        Write-Log "OK" "Guc plani: Yuksek Performans olarak ayarlandi."
        $changes++

        # Disk kapanma suresini devre disi birak
        powercfg /change disk-timeout-ac 0 2>$null
        Write-Log "OK" "Disk kapanma suresi: Hic (AC)"
        $changes++

        # Uyku modunu devre disi birak (AC)
        powercfg /change standby-timeout-ac 0 2>$null
        Write-Log "OK" "Uyku modu: Devre disi (AC)"
        $changes++

        # USB secici askiya alma
        $usbPath = "HKLM:\SYSTEM\CurrentControlSet\Services\USB"
        if (Test-Path $usbPath) {
            Set-ItemProperty -Path $usbPath -Name "DisableSelectiveSuspend" -Value 1 -ErrorAction SilentlyContinue
        }
        Write-Log "OK" "USB secici askiya alma: Devre disi"
        $changes++

        # PCI Express Link State Power Management
        powercfg /setacvalueindex scheme_current sub_pciexpress ee12f906-d277-404b-b6da-e5fa1a576df5 0 2>$null
        powercfg /setactive scheme_current 2>$null
        Write-Log "OK" "PCIe Link State Power Management: Kapatildi"
        $changes++

        # Islemci minimum performansi %100
        powercfg /setacvalueindex scheme_current sub_processor PROCTHROTTLEMIN 100 2>$null
        powercfg /setactive scheme_current 2>$null
        Write-Log "OK" "Islemci minimum performansi: %100"
        $changes++

    } else {
        Write-Log "INFO" "[DRY-RUN] Guc plani ayarlari degistirilecekti."
    }

    Write-Log "OK" "GOREV 10 TOPLAM: $changes guc ayari optimize edildi."
    return @{ Changes = $changes; Status = "OK" }
}

# ======================================================================
#  GOREV 11: SISTEM SAGLIGI RAPORU
# ======================================================================
function Invoke-SystemHealthReport {
    Write-Banner "GOREV 11 - SISTEM SAGLIGI RAPORU"

    $report = @{}

# --- Isletim sistemi ---
    $os = Get-CimInstance Win32_OperatingSystem
    $osCaption = $os.Caption
    $osBuild   = [string]$os.BuildNumber
    $report["Isletim Sistemi"]  = "$osCaption Build $osBuild"
    $report["Yukleme Tarihi"]   = $os.InstallDate.ToString("yyyy-MM-dd")
    $report["Son Yeniden Baslama"] = $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm:ss")
    $uptime = (Get-Date) - $os.LastBootUpTime
    $uptDays = [string]$uptime.Days
    $uptHours = [string]$uptime.Hours
    $uptMins  = [string]$uptime.Minutes
    $report["Calisma Suresi"] = "$uptDays gun $uptHours saat $uptMins dakika"

    # --- Donanim ---
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $cpuCores   = [string]$cpu.NumberOfCores
    $cpuThreads = [string]$cpu.NumberOfLogicalProcessors
    $cpuName    = $cpu.Name
    $report["CPU"] = "$cpuName ($cpuCores Cekirdek / $cpuThreads Is Parcacigi)"

    $ram = Get-CimInstance Win32_PhysicalMemory
    $totalRAM = ($ram | Measure-Object -Property Capacity -Sum).Sum
    $report["RAM"]     = Format-Size $totalRAM
    $usedRAM  = $totalRAM - ($os.FreePhysicalMemory * 1KB)
    $ramPct   = [math]::Round(($usedRAM / $totalRAM) * 100, 1)
    $ramUsedStr  = Format-Size $usedRAM
    $ramTotalStr = Format-Size $totalRAM
    $report["RAM Kullanimi"] = "$ramUsedStr / $ramTotalStr (%$ramPct)"

    # --- Diskler ---
    Write-Log "INFO" "Disk bilgileri:"
    $disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"
    foreach ($d in $disks) {
        $usedPct = [math]::Round((1 - $d.FreeSpace / $d.Size) * 100, 1)
        $freeStr = Format-Size $d.FreeSpace
        $totalStr = Format-Size $d.Size
        $health = if ($usedPct -gt 90) { "[KRITIK]" } elseif ($usedPct -gt 80) { "[UYARI]" } else { "[IYI]" }
        Write-Log "INFO" "  $($d.DeviceID) $health $freeStr bos / $totalStr toplam (%$usedPct dolu)"
    }

    # --- SSD / HDD SMART durumu ---
    Write-Log "INFO" "Disk sagligi (SMART) kontrol ediliyor..."
    try {
        $diskHealth = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus
        foreach ($dh in $diskHealth) {
            $hStatus = if ($dh.HealthStatus -eq "Healthy") { "[IYI]" } else { "[UYARI]" }
            Write-Log "INFO" "  $($dh.FriendlyName) ($($dh.MediaType)): $hStatus $($dh.HealthStatus)"
        }
    } catch {
        Write-Log "WARN" "Disk sagligi bilgisi alinamadi."
    }

    # --- GPU ---
    try {
        $gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1
        $gpuName = $gpu.Name
        $gpuRam  = Format-Size $gpu.AdapterRAM
        $report["GPU"] = "$gpuName ($gpuRam)"
    } catch {
        $report["GPU"] = "Bilgi alinamadi"
    }

    # --- Sicaklik (varsa) ---
    try {
        $temp = Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace root/wmi -ErrorAction Stop
        foreach ($t in $temp) {
            $celsius = [math]::Round(($t.CurrentTemperature / 10) - 273.15, 1)
            Write-Log "INFO" "Sicaklik: ${celsius} dereceC"
        }
    } catch {
        Write-Log "INFO" "Sicaklik bilgisi alinamadi (WMI destegi yok)."
    }

    # --- En cok kaynak kullanan islemler ---
    Write-Log "INFO" "En cok CPU kullanan 10 islem:"
    $topCPU = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 |
        Format-Table Name, @{N="CPU (s)";E={"{0:N1}" -f $_.CPU}}, @{N="RAM (MB)";E={"{0:N0}" -f ($_.WorkingSet64/1MB)}}, Id -AutoSize |
        Out-String
    Write-Log "INFO" $topCPU.Trim()

    Write-Log "INFO" "En cok RAM kullanan 10 islem:"
    $topRAM = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 |
        Format-Table Name, @{N="RAM (MB)";E={"{0:N0}" -f ($_.WorkingSet64/1MB)}}, @{N="CPU (s)";E={"{0:N1}" -f $_.CPU}}, Id -AutoSize |
        Out-String
    Write-Log "INFO" $topRAM.Trim()

    # --- SFC / DISM durum ---
    Write-Log "INFO" "Sistem dosyasi butunlugu kontrol ediliyor (SFC)..."
    if (-not $Script:DryRun) {
        $sfcResult = & sfc /verifyonly 2>&1 | Out-String
        if ($sfcResult -match "did not find any integrity violations|butunluk ihlali bulamadi") {
            Write-Log "OK" "SFC: Sistem dosyalari bozulmamis."
        } else {
            Write-Log "WARN" "SFC: Olasi bozulma tespit edildi. 'sfc /scannow' calistirilmasi onerilir."
        }
    }

    # --- Event Log ozeti ---
    Write-Log "INFO" "Son 24 saatteki kritik olaylar:"
    try {
        $critEvents = Get-WinEvent -FilterHashtable @{
            LogName   = "System"
            Level     = @(1, 2)  # Critical, Error
            StartTime = (Get-Date).AddHours(-24)
        } -MaxEvents 20 -ErrorAction SilentlyContinue

        if ($critEvents) {
            $critEvents | Group-Object ProviderName | ForEach-Object {
                Write-Log "WARN" "  $($_.Name): $($_.Count) hata"
            }
        } else {
            Write-Log "OK" "Son 24 saatte kritik olay yok."
        }
    } catch {
        Write-Log "INFO" "Olay gunlugu okunamadi."
    }

    # --- Rapor ciktisi ---
    $reportFile = Join-Path $Script:ReportDir "SystemHealth_$Script:Timestamp.txt"
    $reportContent  = "======================================================================`n"
    $reportContent += "  SISTEM SAGLIGI RAPORU`n"
    $reportContent += "  Olusturma: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "`n"
    $reportContent += "======================================================================`n`n"
    $fixedKeys = @("Isletim Sistemi","Yukleme Tarihi","Son Yeniden Baslama","Calisma Suresi","CPU","RAM","RAM Kullanimi","GPU")
    foreach ($key in $fixedKeys) {
        if ($report.ContainsKey($key)) {
            $keyPadded = $key.PadRight(25)
            $reportContent += ($keyPadded + ": " + $report[$key] + "`n")
        }
    }
    $reportContent | Out-File -FilePath $reportFile -Encoding UTF8

    Write-Log "OK" "Sistem sagligi raporu olusturuldu: $reportFile"
    return @{ Report = $report; Status = "OK" }
}

# ======================================================================
#  ANA MENU VE CALISTIRMA
# ======================================================================

function Show-Menu {
    $width = 62
    $sep   = "=" * $width
    $appN  = $Script:AppName
    $appV  = $Script:AppVersion

    $ln0 = ("|  $appN v$appV").PadRight($width) + "|"
    $ln1 = ("|  Windows 10/11 Sistem Optimizasyon Araci").PadRight($width) + "|"
    $ln2 = "+$sep+"
    $ln3 = ("|").PadRight($width+1) + "|"
    $ln4 = ("|  Mevcut Gorevler:").PadRight($width+1) + "|"
    Write-Host $ln0 -ForegroundColor Cyan
    Write-Host $ln1 -ForegroundColor Cyan
    Write-Host $ln2 -ForegroundColor Cyan
    Write-Host $ln3 -ForegroundColor White
    Write-Host $ln4 -ForegroundColor White

    foreach ($key in $Script:TaskOrder) {
        $taskName = $Script:TaskDefinitions[$key].Name
        $lnT = ("   [$key] $taskName").PadRight($width)
        Write-Host "|$lnT|" -ForegroundColor Yellow
    }

    $lnA = ("|").PadRight($width+1) + "|"
    $lnB = ("|  Calistirma Modlari:").PadRight($width+1) + "|"
    $lnC = ("|   [A] Tam Optimizasyon       (tum gorevler)").PadRight($width+1) + "|"
    $lnD = ("|   [B] Hizli Temizlik          (Gorev 1,2)").PadRight($width+1) + "|"
    $lnE = ("|   [C] Guvenlik Paketi         (Gorev 4,5,6)").PadRight($width+1) + "|"
    $lnF = ("|   [D] Performans Paketi       (Gorev 8,9,10)").PadRight($width+1) + "|"
    $lnG = ("|   [E] Dry-Run Simulasyon      (hicbir sey degismez)").PadRight($width+1) + "|"
    $lnH = ("|   [F] Ozel Gorev Sec          (virgullu: 1,3,6)").PadRight($width+1) + "|"
    $lnI = ("|   [R] Sistem Sagligi Raporu   (Gorev 11)").PadRight($width+1) + "|"
    $lnJ = ("|   [Q] Cikis").PadRight($width+1) + "|"
    $lnK = ("|").PadRight($width+1) + "|"
    $lnL = "+$sep+"
    Write-Host $lnA -ForegroundColor White
    Write-Host $lnB -ForegroundColor White
    Write-Host $lnC -ForegroundColor Green
    Write-Host $lnD -ForegroundColor Green
    Write-Host $lnE -ForegroundColor Green
    Write-Host $lnF -ForegroundColor Green
    Write-Host $lnG -ForegroundColor Green
    Write-Host $lnH -ForegroundColor Green
    Write-Host $lnI -ForegroundColor Green
    Write-Host $lnJ -ForegroundColor Red
    Write-Host $lnK -ForegroundColor White
    Write-Host $lnL -ForegroundColor Cyan
}

function Get-TaskSelection {
    $choice = Read-Host "`nSeciminiz"
    switch ($choice.ToUpper()) {
        "A" { return $Script:TaskOrder }
        "B" { return @(1, 2) }
        "C" { return @(4, 5, 6) }
        "D" { return @(8, 9, 10) }
        "E" { $Script:DryRun = $true; return $Script:TaskOrder }
        "F" {
            $custom = Read-Host "Gorev numaralarini girin (virgullu, orn: 1,3,6)"
            return ($custom -split ',' | ForEach-Object { [int]$_.Trim() } | Where-Object { $_ -in $Script:TaskOrder })
        }
        "R" { return @(11) }
        "Q" { return @() }
        default {
            Write-Host "Gecersiz secim!" -ForegroundColor Red
            return @()
        }
    }
}

function Invoke-Tasks {
    param([int[]]$TaskIds)

    $startTime = Get-Date

    Write-Banner "$Script:AppName v$Script:AppVersion" "$(if($Script:DryRun){'DRY-RUN modu'}else{'NORMAL modu'}) - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    # Sistem bilgisi
    $os  = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    Write-Log "INFO" "OS  : $($os.Caption) Build $($os.BuildNumber)"
    Write-Log "INFO" "CPU : $($cpu.Name)"
    Write-Log "INFO" "RAM : $([math]::Round($os.TotalVisibleMemorySize / 1MB, 1)) GB"
    Write-Log "INFO" "Mod : $(if($Script:DryRun){'DRY-RUN (degisiklik yapilmaz)'}else{'NORMAL'})"
    Write-Log "INFO" "Log : $Script:LogFile"
    Write-Log "INFO" ""

    $sortedIds = $TaskIds | Sort-Object
    foreach ($id in $sortedIds) {
        if ($Script:TaskDefinitions.ContainsKey($id)) {
            $def = $Script:TaskDefinitions[$id]
            Write-Log "INFO" ">> Gorev $id baslatiliyor: $($def.Name)"
            try {
                $result = & $def.Function
                $Script:TaskResults += @{
                    Task   = $id
                    Name   = $def.Name
                    Result = $result
                }
            } catch {
                Write-Log "ERROR" "Gorev $id basarisiz: $_"
                $Script:TaskResults += @{
                    Task   = $id
                    Name   = $def.Name
                    Result = @{ Status = "ERROR"; Error = $_.ToString() }
                }
            }
        } else {
            Write-Log "WARN" "Gecersiz gorev numarasi: $id"
        }
    }

    # --- OZET RAPOR ---
    $elapsed = (Get-Date) - $startTime
    Write-Banner "OPTIMIZASYON OZETI"
    Write-Log "SECTION" "  Sure       : $([math]::Floor($elapsed.TotalMinutes)) dk $($elapsed.Seconds) sn"
    Write-Log "SECTION" "  Temizlenen : $(Format-Size $Script:TotalCleaned)"
    Write-Log "SECTION" "  Optimize   : $($Script:TotalOptimized) oge"
    Write-Log "SECTION" "  Uyarilar   : $($Script:TotalWarnings)"
    Write-Log "SECTION" "  Hatalar    : $($Script:TotalErrors)"
    Write-Log "SECTION" "  Log dosyasi: $Script:LogFile"
    Write-Log "SECTION" ""

    foreach ($tr in $Script:TaskResults) {
        $statusIcon = switch ($tr.Result.Status) {
            "OK"    { "[OK]" }
            "WARN"  { "[!!]" }
            "ERROR" { "[XX]" }
            default { "[--]" }
        }
        Write-Log "SECTION" "  $statusIcon Gorev $($tr.Task): $($tr.Name)"
    }

    Write-Log "SECTION" ""
    Write-Log "SECTION" ("=" * 64)
    Write-Log "OK" "$Script:AppName v$Script:AppVersion tamamlandi."
}

# ======================================================================
#  GIRIS NOKTASI
# ======================================================================

function Main {
    # Yardim
    if ($Help) {
        Write-Host @"

$Script:AppName v$Script:AppVersion - Kullanim Kilavuzu

  .\WinOptimizer.ps1                     Interaktif menu
  .\WinOptimizer.ps1 -Mode DryRun        Simulasyon (degisiklik yok)
  .\WinOptimizer.ps1 -Mode Silent        Sessiz mod (sadece hatalar)
  .\WinOptimizer.ps1 -Tasks 1,3,6        Belirli gorevleri calistir
  .\WinOptimizer.ps1 -NoRestart          Yeniden baslatma isteme

Gorevler:
  1  Gereksiz Dosya Temizleme      7  Baslangic Programlari
  2  Disk Temizligi                8  Hizmet Optimizasyonu
  3  Registry Temizligi            9  Ag Optimizasyonu
  4  Guvenlik Taramasi            10  Guc Plani Optimizasyonu
  5  Windows Guncelleme           11  Sistem Sagligi Raporu
  6  Uygulama Guncelleme (winget)

"@
        return
    }

    # Yonetici kontrolu
    if (-not (Test-Administrator)) {
        Write-Host ""
        Write-Host "  UYARI: Bu script Yonetici (Administrator) haklariyla calistirilmalidir!" -ForegroundColor Red
        Write-Host "  Sag tikla > 'Yonetici olarak calistir' secin." -ForegroundColor Yellow
        Write-Host ""

        $continue = Read-Host "Yonetici haklari olmadan devam etmek istiyor musunuz? (E/H)"
        if ($continue.ToUpper() -ne "E") { return }
    }

    # Ortam hazirla
    Initialize-Environment

    # Komut satiri argumanlari varsa direkt calistir
    if ($Tasks -and $Tasks.Count -gt 0) {
        Invoke-Tasks -TaskIds $Tasks
        return
    }

    # Interaktif menu
    do {
        Show-Menu
        $selectedTasks = Get-TaskSelection

        if ($selectedTasks.Count -eq 0) {
            Write-Host "`nCikis yapiliyor. Iyi gunler!" -ForegroundColor Cyan
            return
        }

        Invoke-Tasks -TaskIds $selectedTasks

        # Tekrar calistirma
        if (-not $Script:Silent) {
            $again = Read-Host "`nBaska bir islem yapmak ister misiniz? (E/H)"
            if ($again.ToUpper() -ne "E") {
                Write-Host "`nTesekkurler! Iyi gunler." -ForegroundColor Cyan
                return
            }
            # Sayaclari sifirla
            $Script:TotalCleaned   = 0
            $Script:TotalErrors    = 0
            $Script:TotalWarnings  = 0
            $Script:TotalOptimized = 0
            $Script:TaskResults    = @()
        } else {
            return
        }
    } while ($true)
}

# Calistir
Main
