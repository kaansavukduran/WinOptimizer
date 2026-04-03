#Requires -RunAsAdministrator
#Requires -Version 5.1
<#
.SYNOPSIS
    WinOptimizer Pro v3.1 - Windows 11 Sistem Optimizasyon Araci
.DESCRIPTION
    7 ana gorev: Gereksiz dosya temizleme, disk optimizasyonu, guncelleme onarimi,
    virus tarama, dosya sistemi onarimi, optimizasyon/hizlandirma, otomatik baslama.
    v3.1: Rollback, Dry-Run, Beyaz Liste, Kismi calisma, RAM temizleyici,
    Donanim izleme, Ag optimizasyonu, Toast bildirimi, HTML rapor,
    Zamanlama profilleri, Servis zaman asimi korumasi.
.PARAMETER DryRun
    Gercek islem yapmaz, sadece ne yapilacagini raporlar.
.PARAMETER Tasks
    Calistirilacak gorev numaralari (1-7). Bos birakilirsa tumU calisir.
    Ornek: -Tasks 1,3,5
.PARAMETER Profile
    Zamanlama profili: "Daily" | "Weekly" | "Monthly" | "Manual"
.PARAMETER AutoMode
    Gorev Zamanlayici tarafindan cagrildiginda kullanilir.
.EXAMPLE
    .\WinOptimizer.ps1 -DryRun
    .\WinOptimizer.ps1 -Tasks 1,4,5
    .\WinOptimizer.ps1 -Tasks 2 -DryRun
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [int[]]$Tasks,
    [ValidateSet("Daily","Weekly","Monthly","Manual")]
    [string]$Profile = "Manual",
    [switch]$AutoMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ============================================================
#  SABITLER VE GLOBAL YAPILAR
# ============================================================
$Script:Version = "3.1"
$Script:BaseDir = "$env:ProgramData\WinOptimizer"
$Script:LogDir  = "$Script:BaseDir\Logs"
$Script:SnapDir = "$Script:BaseDir\Snapshots"
$Script:CfgFile = "$Script:BaseDir\config.json"
$Script:LogFile = "$Script:LogDir\optimizer_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Script:HtmlRpt = "$Script:BaseDir\son_rapor.html"
$Script:TxtRpt  = "$Script:BaseDir\son_rapor.txt"

$Script:Results = [System.Collections.Generic.List[hashtable]]::new()
$Script:Stats   = @{
    FreedMB      = 0.0
    TasksDone    = 0
    TasksFailed  = 0
    ThreatsFound = 0
    StartTime    = $null
    Hostname     = $env:COMPUTERNAME
    OS           = ""
    RAM_GB       = 0
    CPU          = ""
}

# ============================================================
#  DIZIN KURULUMU
# ============================================================
foreach ($d in @($Script:BaseDir, $Script:LogDir, $Script:SnapDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# ============================================================
#  YAPILANDIRMA
# ============================================================
function Get-Config {
    $default = @{
        Whitelist = @(
            "C:\\Windows\\System32",
            "C:\\Windows\\SysWOW64",
            "C:\\Program Files\\WindowsApps",
            "C:\\ProgramData\\Microsoft\\Windows Defender"
        )
        StartupBlacklist = @(
            "OneDriveSetup","DiscordUpdate","EpicGamesLauncher",
            "Spotify","Steam","AdobeAAMUpdater","iTunesHelper",
            "googledrivesync","GoogleDriveFS","Teams"
        )
        MaxLogAgeDays    = 30
        EnableToast      = $true
        EnableHtmlReport = $true
        ScheduleProfile  = "Weekly"
    }
    if (Test-Path $Script:CfgFile) {
        try {
            $loaded = Get-Content $Script:CfgFile -Raw -Encoding UTF8 | ConvertFrom-Json
            foreach ($k in $default.Keys) {
                if (-not ($loaded.PSObject.Properties.Name -contains $k)) {
                    $loaded | Add-Member -NotePropertyName $k -NotePropertyValue $default[$k]
                }
            }
            return $loaded
        } catch {
            Write-Host "[WARN] Config okunamadi, varsayilan kullaniliyor." -ForegroundColor Yellow
        }
    }
    $default | ConvertTo-Json -Depth 5 | Out-File $Script:CfgFile -Encoding UTF8 -Force
    return $default
}

$Script:Config = Get-Config

# ============================================================
#  LOG SISTEMI
# ============================================================
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO','WARN','ERROR','OK','DRY')]$Level = 'INFO'
    )
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $tag  = if ($DryRun -and $Level -eq 'INFO') { 'DRY' } else { $Level }
    $line = "[$ts][$tag] $Message"
    Add-Content -Path $Script:LogFile -Value $line -Encoding UTF8 -ErrorAction SilentlyContinue
    $color = switch ($tag) {
        'OK'    { 'Green'   }
        'WARN'  { 'Yellow'  }
        'ERROR' { 'Red'     }
        'DRY'   { 'Magenta' }
        default { 'Cyan'    }
    }
    Write-Host $line -ForegroundColor $color
}

function Write-Section {
    param([string]$Title)
    $sep = "=" * 62
    Write-Log $sep
    Write-Log "  $Title"
    Write-Log $sep
}

function Add-Result {
    param([string]$Task, [string]$Action, [string]$Status, [string]$Detail = "")
    $Script:Results.Add(@{
        Task   = $Task
        Action = $Action
        Status = $Status
        Detail = $Detail
        Time   = (Get-Date -Format "HH:mm:ss")
    })
}

function Remove-OldLogs {
    $cutoff = (Get-Date).AddDays(-$Script:Config.MaxLogAgeDays)
    Get-ChildItem "$Script:LogDir\*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

# ============================================================
#  BEYAZ LISTE KONTROLU
# ============================================================
function Test-Whitelisted {
    param([string]$Path)
    foreach ($entry in $Script:Config.Whitelist) {
        if ($Path -like "$entry*") { return $true }
    }
    return $false
}

# ============================================================
#  ROLLBACK - REGISTRY SNAPSHOT
# ============================================================
function New-RegistrySnapshot {
    param([string]$Label)
    if ($DryRun) { Write-Log "[DRY-RUN] Snapshot atlaniyor: $Label" 'DRY'; return }
    try {
        $keys = @(
            "HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        )
        foreach ($key in $keys) {
            $leaf    = ($key -split '\\')[-1]
            $ts      = Get-Date -Format 'yyyyMMdd_HHmmss'
            $outFile = "$Script:SnapDir\reg_${ts}_${Label}_${leaf}.reg"
            & reg export $key $outFile /y 2>$null | Out-Null
        }
        Write-Log "Registry snapshot alindi: $Label" 'OK'
        Add-Result "Rollback" "Snapshot: $Label" "OK" $Script:SnapDir
    } catch {
        Write-Log "Snapshot alinamadi: $_" 'WARN'
    }
}

# ============================================================
#  SERVIS YONETIMI - ZAMAN ASIMI KORUMALI
# ============================================================
function Stop-ServiceSafe {
    param([string]$Name, [int]$TimeoutSec = 30)
    try {
        $svc = Get-Service -Name $Name -ErrorAction SilentlyContinue
        if (-not $svc -or $svc.Status -eq 'Stopped') { return $true }
        Stop-Service -Name $Name -Force -ErrorAction SilentlyContinue
        $deadline = (Get-Date).AddSeconds($TimeoutSec)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 500
            $svc.Refresh()
            if ($svc.Status -eq 'Stopped') { return $true }
        }
        Write-Log "Servis durdurulamadi (zaman asimi): $Name" 'WARN'
        return $false
    } catch {
        Write-Log "Servis durdurma hatasi [$Name]: $_" 'WARN'
        return $false
    }
}

function Start-ServiceSafe {
    param([string]$Name, [int]$TimeoutSec = 30)
    try {
        $svc = Get-Service -Name $Name -ErrorAction SilentlyContinue
        if (-not $svc) { return $false }
        if ($svc.Status -eq 'Running') { return $true }
        Start-Service -Name $Name -ErrorAction SilentlyContinue
        $deadline = (Get-Date).AddSeconds($TimeoutSec)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 500
            $svc.Refresh()
            if ($svc.Status -eq 'Running') { return $true }
        }
        Write-Log "Servis baslatillamadi (zaman asimi): $Name" 'WARN'
        return $false
    } catch {
        Write-Log "Servis baslatma hatasi [$Name]: $_" 'WARN'
        return $false
    }
}

# ============================================================
#  DONANIM BILGISI
# ============================================================
function Get-HardwareInfo {
    try {
        $os  = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
        $cpu = Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue | Select-Object -First 1
        $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue).TotalPhysicalMemory / 1GB, 1)
        $Script:Stats.OS     = if ($os)  { "$($os.Caption) Build $($os.BuildNumber)" } else { "Bilinmiyor" }
        $Script:Stats.CPU    = if ($cpu) { $cpu.Name.Trim() } else { "Bilinmiyor" }
        $Script:Stats.RAM_GB = $ram
        Write-Log "OS  : $($Script:Stats.OS)" 'INFO'
        Write-Log "CPU : $($Script:Stats.CPU)" 'INFO'
        Write-Log "RAM : $($Script:Stats.RAM_GB) GB" 'INFO'
    } catch {
        Write-Log "Donanim bilgisi alinamadi." 'WARN'
    }
}

# ============================================================
#  YARDIMCI: BOYUT HESAPLAMA
# ============================================================
function Get-FolderSizeMB {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0.0 }
    try {
        $sum = (Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
        if (-not $sum) { return 0.0 }
        return [math]::Round($sum / 1MB, 2)
    } catch { return 0.0 }
}

function Remove-DirectoryContents {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path $Path)) {
        Write-Log "$Description -- bulunamadi, atlaniyor." 'WARN'
        Add-Result "Temizlik" $Description "SKIP" "Klasor yok"
        return 0.0
    }
    if (Test-Whitelisted $Path) {
        Write-Log "$Description -- BEYAZ LISTEDE, atlaniyor." 'WARN'
        Add-Result "Temizlik" $Description "SKIP" "Beyaz listede"
        return 0.0
    }
    $before = Get-FolderSizeMB $Path
    if ($DryRun) {
        Write-Log "[DRY-RUN] Temizlenecek: $Description -- $before MB" 'DRY'
        Add-Result "Temizlik" $Description "DRY" "$before MB"
        return $before
    }
    Get-ChildItem -Path $Path -Force -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $after = Get-FolderSizeMB $Path
    $freed = [math]::Round($before - $after, 2)
    Write-Log "$Description -- $freed MB temizlendi." 'OK'
    Add-Result "Temizlik" $Description "OK" "$freed MB"
    return $freed
}

# ============================================================
#  GOREV 1 -- GEREKSIZ DOSYA TEMIZLEME
# ============================================================
function Invoke-JunkCleaner {
    Write-Section "GOREV 1 -- GEREKSIZ DOSYA TEMIZLEME"
    $totalFreed = 0.0

    $targets = @(
        @{ Path = $env:TEMP;                                                     Desc = "Kullanici TEMP" }
        @{ Path = "C:\Windows\Temp";                                             Desc = "Windows TEMP" }
        @{ Path = "C:\Windows\Prefetch";                                         Desc = "Prefetch onbellegi" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Windows\INetCache";               Desc = "Internet onbellegi" }
        @{ Path = "$env:LOCALAPPDATA\Temp";                                      Desc = "AppData Temp" }
        @{ Path = "C:\Windows\SoftwareDistribution\Download";                    Desc = "WU indirme onbellegi" }
        @{ Path = "$env:LOCALAPPDATA\CrashDumps";                                Desc = "Kilitlenme dokumu" }
        @{ Path = "C:\Windows\Minidump";                                         Desc = "Mini dokum dosyalari" }
        @{ Path = "$env:APPDATA\Microsoft\Windows\Recent\AutomaticDestinations"; Desc = "Son ogeler gecmisi" }
        @{ Path = "C:\Windows\LiveKernelReports";                                Desc = "Canli cekirdek raporlari" }
        @{ Path = "C:\Windows\Logs\CBS";                                         Desc = "CBS gunlukleri" }
    )

    foreach ($t in $targets) { $totalFreed += Remove-DirectoryContents -Path $t.Path -Description $t.Desc }

    # Windows.old
    if (Test-Path "C:\Windows.old") {
        Write-Log "Windows.old bulundu." 'WARN'
        $totalFreed += Remove-DirectoryContents -Path "C:\Windows.old" -Description "Windows.old"
    }

    # Kullanici klasorlerindeki .tmp / .bak
    foreach ($dir in @("$env:USERPROFILE\Downloads","$env:USERPROFILE\Desktop","$env:USERPROFILE\Documents")) {
        if (-not (Test-Path $dir)) { continue }
        $removed = 0.0
        Get-ChildItem -Path $dir -Recurse -Force -Include "*.tmp","*.bak" -ErrorAction SilentlyContinue |
            ForEach-Object {
                $removed += $_.Length / 1MB
                if (-not $DryRun) { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
            }
        if ($removed -gt 0) {
            $mb  = [math]::Round($removed, 2)
            $tag = if ($DryRun) { "[DRY-RUN]" } else { "" }
            Write-Log "$tag $dir -- .tmp/.bak: $mb MB" 'OK'
            $totalFreed += $removed
        }
    }

    # Cop kutusu
    if (-not $DryRun) {
        try { Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Log "Cop kutusu bosaltildi." 'OK' }
        catch { Write-Log "Cop kutusu bosaltilamadi." 'WARN' }
    } else {
        Write-Log "[DRY-RUN] Cop kutusu bosaltilacak." 'DRY'
    }

    $Script:Stats.FreedMB += $totalFreed
    Write-Log "GOREV 1 TOPLAM: $([math]::Round($totalFreed,2)) MB temizlendi." 'OK'
    return $totalFreed
}

# ============================================================
#  GOREV 2 -- DISK TEMIZLIGI VE OPTIMIZASYON
# ============================================================
function Invoke-DiskCleanup {
    Write-Section "GOREV 2 -- DISK TEMIZLIGI"

    if ($DryRun) {
        Write-Log "[DRY-RUN] cleanmgr /sagerun:99 calistirilacak." 'DRY'
        Write-Log "[DRY-RUN] Surucu Optimize-Volume calistirilacak." 'DRY'
        Add-Result "Disk" "cleanmgr" "DRY" ""
        return
    }

    # Cleanmgr kategori kaydi
    $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
    $categories = @(
        "Active Setup Temp Folders","BranchCache","Content Indexer Cleaner",
        "D3D Shader Cache","Delivery Optimization Files","Device Driver Packages",
        "Diagnostic Data Viewer database files","Downloaded Program Files",
        "Internet Cache Files","Language Pack","Memory Dump Files",
        "Offline Pages Files","Old ChkDsk Files","Previous Installations",
        "Recycle Bin","Setup Log Files","System error memory dump files",
        "System error minidump files","Temporary Files","Temporary Setup Files",
        "Temporary Sync Files","Thumbnail Cache","Update Cleanup",
        "Upgrade Discarded Files","User file versions","Windows Defender",
        "Windows Error Reporting Files","Windows Reset Log Files",
        "Windows Upgrade Log Files"
    )
    foreach ($cat in $categories) {
        $key = "$regPath\$cat"
        if (Test-Path $key) {
            Set-ItemProperty -Path $key -Name "StateFlags0099" -Value 2 -Type DWord -ErrorAction SilentlyContinue
        }
    }

    Write-Log "Disk Temizleme baslatiliyor..." 'INFO'
    try {
        $proc = Start-Process "cleanmgr.exe" -ArgumentList "/sagerun:99" -PassThru -WindowStyle Hidden
        if ($proc.WaitForExit(180000)) {
            Write-Log "Disk Temizleme tamamlandi." 'OK'
            Add-Result "Disk" "cleanmgr /sagerun:99" "OK" ""
        } else {
            $proc.Kill()
            Write-Log "Disk Temizleme zaman asimina ugradi (3 dk), sonlandirildi." 'WARN'
            Add-Result "Disk" "cleanmgr" "WARN" "Zaman asimi"
        }
    } catch {
        Write-Log "Disk Temizleme baslatillamadi: $_" 'ERROR'
        Add-Result "Disk" "cleanmgr" "ERROR" "$_"
    }

    # Surucu optimizasyonu
    Write-Log "Surucu optimizasyonu baslatiliyor..." 'INFO'
    try {
        Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' } |
            ForEach-Object {
                $letter = $_.DriveLetter
                Write-Log "  Optimize ediliyor: ${letter}:" 'INFO'
                Optimize-Volume -DriveLetter $letter -ReTrim -ErrorAction SilentlyContinue 2>$null
                Add-Result "Disk" "Optimize ${letter}:" "OK" ""
            }
        Write-Log "Surucu optimizasyonu tamamlandi." 'OK'
    } catch {
        Write-Log "Surucu optimizasyonu hatasi: $_" 'WARN'
    }
}

# ============================================================
#  GOREV 3 -- GUNCELLEME ONARIMI
# ============================================================
function Invoke-UpdateRepair {
    Write-Section "GOREV 3 -- GUNCELLEME ONARIMI"

    $wuServices = @("wuauserv","bits","cryptsvc","msiserver")

    if ($DryRun) {
        Write-Log "[DRY-RUN] WU servisleri durdurulup yeniden baslatilacak." 'DRY'
        Write-Log "[DRY-RUN] SoftwareDistribution ve catroot2 sifirllanacak." 'DRY'
        Write-Log "[DRY-RUN] DLL'ler yeniden kaydedilecek, WinSock sifirllanacak." 'DRY'
        Add-Result "Guncelleme" "Tum onarim adimlari" "DRY" ""
        return
    }

    New-RegistrySnapshot "Before_UpdateRepair"

    Write-Log "WU servisleri durduruluyor..." 'INFO'
    foreach ($svc in $wuServices) {
        $ok = Stop-ServiceSafe -Name $svc -TimeoutSec 45
        Write-Log "  $svc : $(if($ok){'Durduruldu'}else{'Durdurulamadi'})" $(if($ok){'OK'}else{'WARN'})
    }
    Start-Sleep -Seconds 2

    # SoftwareDistribution ve catroot2 sifirla
    $foldersToReset = @(
        @{ Src = "C:\Windows\SoftwareDistribution"; Bak = "C:\Windows\SoftwareDistribution.bak" }
        @{ Src = "C:\Windows\System32\catroot2";    Bak = "C:\Windows\System32\catroot2.bak"    }
    )
    foreach ($f in $foldersToReset) {
        if (Test-Path $f.Bak) { Remove-Item $f.Bak -Recurse -Force -ErrorAction SilentlyContinue }
        if (Test-Path $f.Src) {
            try {
                Rename-Item -Path $f.Src -NewName $f.Bak -ErrorAction Stop
                Write-Log "  Yeniden adlandirildi: $($f.Src)" 'OK'
            } catch {
                Remove-Item "$($f.Src)\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "  Icerik temizlendi: $($f.Src)" 'WARN'
            }
        }
    }

    # DLL kaydi
    Write-Log "Windows Update DLL'leri kaydediliyor..." 'INFO'
    $dlls = @(
        "atl.dll","urlmon.dll","mshtml.dll","shdocvw.dll","browseui.dll",
        "jscript.dll","vbscript.dll","scrrun.dll","msxml.dll","msxml3.dll",
        "msxml6.dll","actxprxy.dll","softpub.dll","wintrust.dll","dssenh.dll",
        "rsaenh.dll","gpkcsp.dll","sccbase.dll","slbcsp.dll","cryptdlg.dll",
        "oleaut32.dll","ole32.dll","shell32.dll","initpki.dll","wuapi.dll",
        "wuaueng.dll","wuaueng1.dll","wucltui.dll","wups.dll","wups2.dll",
        "wuweb.dll","qmgr.dll","qmgrprxy.dll","wucltux.dll","muweb.dll","wuwebv.dll"
    )
    $dllErrors = 0
    foreach ($dll in $dlls) {
        & regsvr32.exe /s $dll 2>$null
        if ($LASTEXITCODE -ne 0) { $dllErrors++ }
    }
    $dllMsg = "DLL kaydi tamamlandi. ($dllErrors hata)"
    Write-Log $dllMsg $(if($dllErrors -eq 0){'OK'}else{'WARN'})

    # WinSock ve WinHTTP sifirla
    & netsh winsock reset 2>$null | Out-Null
    & netsh winhttp reset proxy 2>$null | Out-Null
    Write-Log "WinSock ve WinHTTP sifirlandi." 'OK'

    # Servisleri yeniden basla
    Write-Log "WU servisleri yeniden baslatiliyor..." 'INFO'
    foreach ($svc in $wuServices) {
        $ok = Start-ServiceSafe -Name $svc -TimeoutSec 45
        Write-Log "  $svc : $(if($ok){'Baslatildi'}else{'Baslatillamadi'})" $(if($ok){'OK'}else{'WARN'})
    }

    # WU tetikle
    try {
        (New-Object -ComObject Microsoft.Update.AutoUpdate).DetectNow()
        Write-Log "Guncelleme kontrolu tetiklendi." 'OK'
    } catch {
        Write-Log "Guncelleme kontrolu tetiklenemedi." 'WARN'
    }

    Add-Result "Guncelleme" "WU onarim dongusu" "OK" "$dllErrors DLL hatasi"
    Write-Log "Guncelleme onarimi tamamlandi." 'OK'
}

# ============================================================
#  GOREV 4 -- VIRUS TARAMA
# ============================================================
function Invoke-VirusScan {
    Write-Section "GOREV 4 -- VIRUS VE KOTU AMACLI YAZILIM TARAMA"

    if ($DryRun) {
        Write-Log "[DRY-RUN] Defender imza guncellemesi ve QuickScan calistirilacak." 'DRY'
        Add-Result "Virus" "Defender Quick Scan" "DRY" ""
        return
    }

    # Imza guncelle
    Write-Log "Defender imzalari guncelleniyor..." 'INFO'
    try {
        Update-MpSignature -ErrorAction Stop
        Write-Log "Imza guncellemesi tamamlandi." 'OK'
    } catch {
        Write-Log "Imza guncellemesi basarisiz: $_" 'WARN'
    }

    # Hizli tarama
    Write-Log "Hizli tarama baslatiliyor..." 'INFO'
    $scanOk = $false
    try {
        Start-MpScan -ScanType QuickScan -ErrorAction Stop
        $scanOk = $true
        Write-Log "Hizli tarama tamamlandi." 'OK'
    } catch {
        Write-Log "Defender PS API basarisiz, MpCmdRun deneniyor..." 'WARN'
        $mpCmd = "$env:ProgramFiles\Windows Defender\MpCmdRun.exe"
        if (Test-Path $mpCmd) {
            $p = Start-Process $mpCmd -ArgumentList "-Scan -ScanType 1" -PassThru -WindowStyle Hidden
            if ($p.WaitForExit(300000)) {
                $scanOk = $true
                Write-Log "MpCmdRun taramasi tamamlandi." 'OK'
            } else {
                $p.Kill()
                Write-Log "MpCmdRun zaman asimi." 'WARN'
            }
        }
    }

    # Tehdit listesi - ThreatID bazli temizlik
    try {
        $threats = Get-MpThreatDetection -ErrorAction SilentlyContinue
        if ($threats -and $threats.Count -gt 0) {
            $Script:Stats.ThreatsFound = $threats.Count
            Write-Log "UYARI: $($threats.Count) tehdit tespit edildi!" 'WARN'
            $activeThreatIds = $threats | Select-Object -ExpandProperty ThreatID -Unique
            foreach ($id in $activeThreatIds) {
                try {
                    Remove-MpThreat -ThreatID $id -ErrorAction SilentlyContinue
                    Write-Log "  Temizlendi: ThreatID $id" 'OK'
                } catch {
                    Write-Log "  Temizlenemedi: ThreatID $id" 'WARN'
                }
            }
            Add-Result "Virus" "Tehdit Temizleme" "WARN" "$($threats.Count) tehdit"
        } else {
            Write-Log "Tehdit bulunamadi. Sistem temiz." 'OK'
            Add-Result "Virus" "Quick Scan" "OK" "Temiz"
        }
    } catch {
        Write-Log "Tehdit gecmisi okunamadi." 'WARN'
        Add-Result "Virus" "Tehdit Gecmisi" "WARN" "$_"
    }

    # Gercek zamanli koruma durumu
    try {
        $mpStatus = Get-MpComputerStatus -ErrorAction SilentlyContinue
        if ($mpStatus) {
            $rtpState = $mpStatus.RealTimeProtectionEnabled
            Write-Log "Gercek Zamanli Koruma: $rtpState" 'INFO'
            if (-not $rtpState) {
                Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
                Write-Log "Gercek zamanli koruma yeniden etkinlestirildi." 'OK'
                Add-Result "Virus" "RTP Yeniden Etkinlestirme" "OK" ""
            }
        }
    } catch {}

    Write-Log "Virus taramasi tamamlandi." 'OK'
}

# ============================================================
#  GOREV 5 -- DOSYA SISTEMI ONARIMI
# ============================================================
function Invoke-FileSystemRepair {
    Write-Section "GOREV 5 -- DOSYA SISTEMI ONARIMI"

    if ($DryRun) {
        Write-Log "[DRY-RUN] SFC /scannow calistirilacak." 'DRY'
        Write-Log "[DRY-RUN] DISM /ScanHealth ve /CheckHealth calistirilacak." 'DRY'
        Write-Log "[DRY-RUN] CHKDSK /scan calistirilacak." 'DRY'
        Add-Result "Onarim" "SFC + DISM + CHKDSK" "DRY" ""
        return
    }

    # SFC
    Write-Log "SFC /scannow baslatiliyor..." 'INFO'
    try {
        $sfcOut    = & sfc /scannow 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $sfcOut -Encoding UTF8 -ErrorAction SilentlyContinue
        $sfcStatus = if     ($sfcOut -match "did not find any integrity violations")    { "Temiz" }
                     elseif ($sfcOut -match "found corrupt files and successfully repaired") { "Onarildi" }
                     elseif ($sfcOut -match "found corrupt files but was unable to fix")     { "Onarilamadi" }
                     else   { "Tamamlandi" }
        Write-Log "SFC: $sfcStatus" $(if($sfcStatus -eq "Onarilamadi"){'WARN'}else{'OK'})
        Add-Result "Onarim" "SFC /scannow" $(if($sfcStatus -eq "Onarilamadi"){'WARN'}else{'OK'}) $sfcStatus
    } catch {
        Write-Log "SFC calistirilamadi: $_" 'ERROR'
        Add-Result "Onarim" "SFC /scannow" "ERROR" "$_"
    }

    # DISM ScanHealth -> CheckHealth -> RestoreHealth (kosullu)
    Write-Log "DISM ScanHealth baslatiliyor..." 'INFO'
    try {
        $dismScan = & dism /online /cleanup-image /scanhealth 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $dismScan -Encoding UTF8 -ErrorAction SilentlyContinue
        Write-Log "DISM ScanHealth tamamlandi." 'OK'

        $dismCheck = & dism /online /cleanup-image /checkhealth 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $dismCheck -Encoding UTF8 -ErrorAction SilentlyContinue

        if ($dismCheck -match "repairable") {
            Write-Log "DISM: Bilesem magazasi onarilabilir, RestoreHealth baslatiliyor..." 'WARN'
            $dismRestore = & dism /online /cleanup-image /restorehealth 2>&1 | Out-String
            Add-Content -Path $Script:LogFile -Value $dismRestore -Encoding UTF8 -ErrorAction SilentlyContinue
            Write-Log "DISM RestoreHealth tamamlandi." 'OK'
            Add-Result "Onarim" "DISM RestoreHealth" "OK" ""
        } else {
            Write-Log "DISM: Bilesem magazasi saglikli." 'OK'
            Add-Result "Onarim" "DISM CheckHealth" "OK" "Saglikli"
        }
    } catch {
        Write-Log "DISM calistirilamadi: $_" 'ERROR'
        Add-Result "Onarim" "DISM" "ERROR" "$_"
    }

    # CHKDSK /scan (cevrimici, surucu kilitlenmez)
    Write-Log "CHKDSK /scan baslatiliyor..." 'INFO'
    try {
        $chkOut    = & chkdsk C: /scan 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $chkOut -Encoding UTF8 -ErrorAction SilentlyContinue
        $needsFix  = $chkOut -match "Windows found problems"
        if ($needsFix) {
            Write-Log "CHKDSK: Sorunlar bulundu. Bir sonraki yeniden baslatmada onarilacak." 'WARN'
            & chkdsk C: /f /perf 2>$null | Out-Null
            Add-Result "Onarim" "CHKDSK" "WARN" "Sorun bulundu, reboot'ta onarilacak"
        } else {
            Write-Log "CHKDSK: Sorun bulunamadi." 'OK'
            Add-Result "Onarim" "CHKDSK /scan" "OK" "Temiz"
        }
    } catch {
        Write-Log "CHKDSK calistirilamadi: $_" 'WARN'
        Add-Result "Onarim" "CHKDSK" "WARN" "$_"
    }

    Write-Log "Dosya sistemi onarimi tamamlandi." 'OK'
}

# ============================================================
#  GOREV 6 -- OPTIMIZASYON, HIZLANDIRMA VE YENi MODUELLER
# ============================================================
function Invoke-SystemOptimization {
    Write-Section "GOREV 6 -- OPTIMIZASYON VE HIZLANDIRMA"

    New-RegistrySnapshot "Before_Optimization"

    # -- 6a: Baslangic programlari --
    Write-Log "Baslangic programlari analiz ediliyor..." 'INFO'
    $startupPaths = @(
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
    )
    $blacklist = $Script:Config.StartupBlacklist
    foreach ($regPath in $startupPaths) {
        if (-not (Test-Path $regPath)) { continue }
        $props = (Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue).PSObject.Properties |
                 Where-Object { $_.Name -notin @('PSPath','PSParentPath','PSChildName','PSDrive','PSProvider') }
        foreach ($prop in $props) {
            if ($blacklist -contains $prop.Name) {
                if ($DryRun) {
                    Write-Log "[DRY-RUN] Baslangic kaldirilacak: $($prop.Name)" 'DRY'
                } else {
                    Remove-ItemProperty -Path $regPath -Name $prop.Name -ErrorAction SilentlyContinue
                    Write-Log "  Baslangic kaldirildi: $($prop.Name)" 'INFO'
                    Add-Result "Optimizasyon" "Baslangic: $($prop.Name)" "OK" ""
                }
            }
        }
    }

    # -- 6b: Guc plani --
    if (-not $DryRun) {
        try {
            & powercfg /setactive SCHEME_MIN 2>$null
            Write-Log "Guc plani: Yuksek Performans aktif." 'OK'
            Add-Result "Optimizasyon" "Guc Plani" "OK" "Yuksek Performans"
        } catch { Write-Log "Guc plani degistirilemedi." 'WARN' }
    } else {
        Write-Log "[DRY-RUN] Guc plani Yuksek Performans'a alinacak." 'DRY'
    }

    # -- 6c: Gorsel efektler --
    if (-not $DryRun) {
        $vfxPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        try {
            if (-not (Test-Path $vfxPath)) { New-Item -Path $vfxPath -Force | Out-Null }
            Set-ItemProperty -Path $vfxPath -Name "VisualFXSetting" -Value 2 -Type DWord -ErrorAction SilentlyContinue
            Write-Log "Gorsel efektler: Performans modu." 'OK'
            Add-Result "Optimizasyon" "Gorsel Efektler" "OK" "Performans modu"
        } catch { Write-Log "Gorsel efektler ayarlanamadi." 'WARN' }
    }

    # -- 6d: Gereksiz servisler --
    $unusedServices = @(
        @{ Name = "Fax";                Desc = "Faks" }
        @{ Name = "XblGameSave";        Desc = "Xbox Oyun Kaydetme" }
        @{ Name = "XboxNetApiSvc";      Desc = "Xbox Ag API" }
        @{ Name = "WMPNetworkSvc";      Desc = "WMP Ag Paylasimi" }
        @{ Name = "MapsBroker";         Desc = "Haritalar Yoneticisi" }
        @{ Name = "RetailDemo";         Desc = "Perakende Demo" }
        @{ Name = "TabletInputService"; Desc = "Tablet Girisi" }
    )
    Write-Log "Gereksiz servisler kontrol ediliyor..." 'INFO'
    foreach ($svc in $unusedServices) {
        try {
            $s = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
            if ($s -and $s.StartType -ne 'Disabled') {
                if ($DryRun) {
                    Write-Log "[DRY-RUN] Devre disi birakilacak: $($svc.Desc)" 'DRY'
                } else {
                    Set-Service -Name $svc.Name -StartupType Disabled -ErrorAction SilentlyContinue
                    Stop-ServiceSafe -Name $svc.Name -TimeoutSec 15 | Out-Null
                    Write-Log "  Devre disi: $($svc.Desc)" 'OK'
                    Add-Result "Optimizasyon" "Servis: $($svc.Desc)" "OK" "Disabled"
                }
            }
        } catch {}
    }

    # -- 6e: DNS onbellegi --
    if (-not $DryRun) {
        Clear-DnsClientCache -ErrorAction SilentlyContinue
        & ipconfig /flushdns 2>$null | Out-Null
        Write-Log "DNS onbellegi temizlendi." 'OK'
        Add-Result "Optimizasyon" "DNS Onbellegi" "OK" ""
    }

    # -- 6f: Sayfa dosyasi --
    if (-not $DryRun) {
        try {
            $cs = Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue
            if ($cs -and -not $cs.AutomaticManagedPagefile) {
                Set-CimInstance -InputObject $cs -Property @{AutomaticManagedPagefile = $true} -ErrorAction SilentlyContinue
            }
            Write-Log "Sayfa dosyasi: Otomatik yonetim aktif." 'OK'
            Add-Result "Optimizasyon" "Sayfa Dosyasi" "OK" "Otomatik"
        } catch { Write-Log "Sayfa dosyasi yapilandirillamadi." 'WARN' }
    }

    # -- 6g: RAM Temizleyici --
    Write-Log "RAM optimizasyonu baslatiliyor..." 'INFO'
    if (-not $DryRun) {
        try {
            $osBefore  = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
            $ramBefore = if ($osBefore) { [math]::Round($osBefore.FreePhysicalMemory / 1MB, 1) } else { 0 }
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            [System.GC]::Collect()
            # Surecler icin MinWorkingSet trick
            Get-Process -ErrorAction SilentlyContinue |
                Where-Object { -not $_.HasExited -and $_.Id -gt 4 } |
                ForEach-Object {
                    try { $_.MinWorkingSet = [IntPtr](-1) } catch {}
                }
            Start-Sleep -Seconds 1
            $osAfter  = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
            $ramAfter = if ($osAfter) { [math]::Round($osAfter.FreePhysicalMemory / 1MB, 1) } else { 0 }
            $gained   = [math]::Round($ramAfter - $ramBefore, 1)
            Write-Log "RAM optimizasyonu: $gained GB serbest birakildi (once: $ramBefore GB, sonra: $ramAfter GB)." 'OK'
            Add-Result "Optimizasyon" "RAM Temizleyici" "OK" "+$gained GB serbest"
        } catch {
            Write-Log "RAM optimizasyonu sirasinda hata: $_" 'WARN'
        }
    } else {
        Write-Log "[DRY-RUN] RAM temizleyici calistirilacak." 'DRY'
    }

    # -- 6h: Ag Optimizasyonu (TCP tuning) --
    Write-Log "Ag optimizasyonu baslatiliyor..." 'INFO'
    if (-not $DryRun) {
        try {
            & netsh int tcp set global autotuninglevel=normal  2>$null | Out-Null
            & netsh int tcp set global dca=enabled             2>$null | Out-Null
            & netsh int tcp set global chimney=automatic       2>$null | Out-Null
            & netsh int tcp set global ecncapability=enabled   2>$null | Out-Null
            & netsh int tcp set global rss=enabled             2>$null | Out-Null
            Write-Log "Ag TCP parametreleri optimize edildi." 'OK'
            Add-Result "Optimizasyon" "TCP/IP Tuning" "OK" "autotuninglevel=normal, RSS=enabled"
        } catch {
            Write-Log "Ag optimizasyonu hatasi: $_" 'WARN'
        }
    } else {
        Write-Log "[DRY-RUN] TCP/IP parametreleri optimize edilecek." 'DRY'
    }

    # -- 6i: Donanim Izleme --
    Write-Log "Donanim durumu kontrol ediliyor..." 'INFO'
    try {
        $diskStatus = Get-PhysicalDisk -ErrorAction SilentlyContinue |
                      Select-Object FriendlyName, HealthStatus, Size
        foreach ($disk in $diskStatus) {
            $sizGB = [math]::Round($disk.Size / 1GB, 0)
            Write-Log "  Disk: $($disk.FriendlyName) | $($disk.HealthStatus) | $sizGB GB" 'INFO'
            if ($disk.HealthStatus -ne 'Healthy') {
                Write-Log "  UYARI: Disk saglik sorunu tespit edildi!" 'WARN'
                Add-Result "Izleme" "Disk Sagligi" "WARN" "$($disk.FriendlyName): $($disk.HealthStatus)"
            }
        }
        $cpuLoad = (Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue |
                    Measure-Object LoadPercentage -Average).Average
        $freeRam = [math]::Round((Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).FreePhysicalMemory / 1MB, 1)
        Write-Log "  CPU Yuku: $cpuLoad%" 'INFO'
        Write-Log "  Bos RAM : $freeRam GB" 'INFO'
        Add-Result "Izleme" "Donanim Durumu" "OK" "CPU: $cpuLoad% | Bos RAM: $freeRam GB"
    } catch {
        Write-Log "Donanim izleme hatasi: $_" 'WARN'
    }

    # -- 6j: Registry temizligi --
    if (-not $DryRun) {
        $regClean = @(
            "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
            "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
        )
        foreach ($rp in $regClean) {
            if (Test-Path $rp) {
                try {
                    Remove-Item -Path $rp -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Log "  Registry temizlendi: $(Split-Path $rp -Leaf)" 'INFO'
                } catch {}
            }
        }
        Add-Result "Optimizasyon" "Registry Temizligi" "OK" ""
    }

    # -- 6k: Geri yukleme noktasi --
    if (-not $DryRun) {
        try {
            $vss = Get-Service -Name "VSS" -ErrorAction SilentlyContinue
            if ($vss) {
                Checkpoint-Computer -Description "WinOptimizer v$($Script:Version) -- $(Get-Date -Format 'yyyy-MM-dd')" `
                    -RestorePointType "MODIFY_SETTINGS" -ErrorAction SilentlyContinue
                Write-Log "Sistem geri yukleme noktasi olusturuldu." 'OK'
                Add-Result "Optimizasyon" "Geri Yukleme Noktasi" "OK" ""
            }
        } catch { Write-Log "Geri yukleme noktasi olusturulamadi." 'WARN' }
    }

    Write-Log "Optimizasyon ve hizlandirma tamamlandi." 'OK'
}

# ============================================================
#  GOREV 7 -- OTOMATIK BASLAMA KURULUMU
# ============================================================
function Install-AutoStart {
    Write-Section "GOREV 7 -- OTOMATIK BASLAMA KURULUMU"

    $scriptSrc  = $PSCommandPath
    $scriptDest = "$Script:BaseDir\WinOptimizer.ps1"

    if ($scriptSrc -and $scriptSrc -ne $scriptDest -and (Test-Path $scriptSrc)) {
        try {
            Copy-Item -Path $scriptSrc -Destination $scriptDest -Force -ErrorAction Stop
            Write-Log "Script kalici konuma kopyalandi: $scriptDest" 'OK'
        } catch {
            Write-Log "Script kopyalanamadi, mevcut konum kullanilacak." 'WARN'
            $scriptDest = $scriptSrc
        }
    } elseif (-not (Test-Path $scriptDest)) {
        $scriptDest = $scriptSrc
    }

    # Zamanlama profili
    $triggerObj = switch ($Script:Config.ScheduleProfile) {
        "Daily"   { New-ScheduledTaskTrigger -Daily   -At "03:00" }
        "Weekly"  { New-ScheduledTaskTrigger -Weekly  -DaysOfWeek Monday -At "03:00" }
        "Monthly" { New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At "03:00" }
        default   { New-ScheduledTaskTrigger -AtStartup }
    }

    $taskName  = "WinOptimizer_AutoRun"
    $psArgs    = "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$scriptDest`" -AutoMode -Profile $($Script:Config.ScheduleProfile)"
    $action    = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument $psArgs
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings  = New-ScheduledTaskSettingsSet `
                     -ExecutionTimeLimit (New-TimeSpan -Hours 3) `
                     -RestartCount 2 `
                     -RestartInterval (New-TimeSpan -Minutes 10) `
                     -StartWhenAvailable `
                     -MultipleInstances IgnoreNew `
                     -RunOnlyIfNetworkAvailable $false

    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask `
            -TaskName    $taskName `
            -Action      $action `
            -Trigger     $triggerObj `
            -Principal   $principal `
            -Settings    $settings `
            -Description "WinOptimizer Pro v$($Script:Version) -- Otomatik calisma" `
            -Force | Out-Null
        Write-Log "Gorev Zamanlayici gorevi olusturuldu: $taskName" 'OK'
        Write-Log "Profil: $($Script:Config.ScheduleProfile)" 'INFO'
        Add-Result "Baslama" "Gorev Zamanlayici" "OK" $taskName
    } catch {
        Write-Log "Gorev Zamanlayici hatasi, Registry fallback deneniyor: $_" 'WARN'
        try {
            Set-ItemProperty `
                -Path  "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" `
                -Name  "WinOptimizer" `
                -Value "PowerShell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptDest`" -AutoMode" `
                -ErrorAction Stop
            Write-Log "Registry baslangic girisi olusturuldu (yedek)." 'OK'
            Add-Result "Baslama" "Registry Startup (fallback)" "OK" $scriptDest
        } catch {
            Write-Log "Otomatik baslama kurulamadi: $_" 'ERROR'
            Add-Result "Baslama" "Otomatik Baslama" "ERROR" "$_"
        }
    }
}

# ============================================================
#  HTML RAPOR URETICI
# ============================================================
function Export-HtmlReport {
    param([timespan]$Elapsed)

    $statusColor = @{
        OK    = "#22c55e"
        WARN  = "#f59e0b"
        ERROR = "#ef4444"
        DRY   = "#a855f7"
        SKIP  = "#6b7280"
    }

    $rows = ($Script:Results | ForEach-Object {
        $col = if ($statusColor[$_.Status]) { $statusColor[$_.Status] } else { "#6b7280" }
        $colBg = $col + "20"
        "<tr>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Time)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Task)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Action)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>
            <span style='background:$colBg;color:$col;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600'>$($_.Status)</span>
          </td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b;color:#94a3b8;font-size:12px'>$($_.Detail)</td>
        </tr>"
    }) -join "`n"

    $dryBanner = if ($DryRun) {
        "<div style='background:#581c87;color:#e9d5ff;padding:12px 20px;border-radius:8px;margin-bottom:20px;font-weight:600'>DRY-RUN MODU -- Gercek islem yapilmadi.</div>"
    } else { "" }

    $elMin  = [int]$Elapsed.Minutes
    $elSec  = [int]$Elapsed.Seconds
    $dateStr = Get-Date -Format "dd.MM.yyyy HH:mm:ss"
    $freed  = [math]::Round($Script:Stats.FreedMB, 0)
    $done   = $Script:Stats.TasksDone
    $threat = if ($Script:Stats.ThreatsFound -gt 0) { "$($Script:Stats.ThreatsFound) Tehdit" } else { "Temiz" }
    $threatColor = if ($Script:Stats.ThreatsFound -gt 0) { "#ff3d71" } else { "#00e676" }

    $html = @"
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>WinOptimizer Pro v$($Script:Version) - Rapor</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e1a;color:#cbd5e1;font-family:'Segoe UI',sans-serif;padding:32px}
h1{font-size:22px;font-weight:700;color:#fff;margin-bottom:4px}
.sub{font-size:12px;color:#475569;margin-bottom:28px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.card{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:18px}
.card-val{font-size:24px;font-weight:700;color:#fff;margin-bottom:4px}
.card-lbl{font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px}
table{width:100%;border-collapse:collapse;background:#0f172a;border-radius:10px;overflow:hidden}
th{padding:10px 12px;background:#1e293b;color:#94a3b8;font-size:11px;text-align:left;text-transform:uppercase}
.footer{margin-top:20px;font-size:11px;color:#334155;text-align:center}
</style>
</head>
<body>
<h1>WinOptimizer Pro <span style="color:#00d4ff">v$($Script:Version)</span> - Optimizasyon Raporu</h1>
<div class="sub">$dateStr | $($Script:Stats.Hostname) | $($Script:Stats.OS)</div>
$dryBanner
<div class="grid">
  <div class="card">
    <div class="card-val" style="color:#00e676">$freed MB</div>
    <div class="card-lbl">Temizlenen Alan</div>
  </div>
  <div class="card">
    <div class="card-val">$done / 7</div>
    <div class="card-lbl">Tamamlanan Gorev</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:$threatColor">$threat</div>
    <div class="card-lbl">Virus Durumu</div>
  </div>
  <div class="card">
    <div class="card-val">${elMin}dk ${elSec}sn</div>
    <div class="card-lbl">Toplam Sure</div>
  </div>
</div>
<table>
  <thead><tr><th>Saat</th><th>Gorev</th><th>Islem</th><th>Durum</th><th>Detay</th></tr></thead>
  <tbody>$rows</tbody>
</table>
<div class="footer">WinOptimizer Pro v$($Script:Version) | Log: $Script:LogFile | CPU: $($Script:Stats.CPU) | RAM: $($Script:Stats.RAM_GB) GB</div>
</body>
</html>
"@
    $html | Out-File -FilePath $Script:HtmlRpt -Encoding UTF8 -Force
    Write-Log "HTML rapor: $Script:HtmlRpt" 'OK'
}

# ============================================================
#  TOAST BILDIRIMI
# ============================================================
function Send-ToastNotification {
    param([string]$Title, [string]$Body)
    if (-not $Script:Config.EnableToast) { return }
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = "<toast><visual><binding template='ToastGeneric'><text>$Title</text><text>$Body</text></binding></visual></toast>"
        $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
        $xml.LoadXml($template)
        $toast    = [Windows.UI.Notifications.ToastNotification]::new($xml)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("WinOptimizer Pro")
        $notifier.Show($toast)
    } catch {
        # WinRT olmadan sessizce atla
    }
}

# ============================================================
#  ANA AKIS
# ============================================================
function Main {
    $Script:Stats.StartTime = Get-Date
    $modeTag = if ($DryRun) { "DRY-RUN" } else { "NORMAL" }

    Write-Log "=========================================================="
    Write-Log "     WinOptimizer Pro v$($Script:Version) -- $modeTag modu"
    Write-Log "     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Log "=========================================================="

    # Yonetici kontrolu
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Log "HATA: Yonetici yetkisi gerekiyor!" 'ERROR'
        exit 1
    }

    Get-HardwareInfo
    Remove-OldLogs

    # Tum gorevler tanimi
    $allTasks = @(
        @{ Id = 1; Fn = { Invoke-JunkCleaner }      ; Name = "Gereksiz Dosya Temizleme" }
        @{ Id = 2; Fn = { Invoke-DiskCleanup }      ; Name = "Disk Temizligi" }
        @{ Id = 3; Fn = { Invoke-UpdateRepair }      ; Name = "Guncelleme Onarimi" }
        @{ Id = 4; Fn = { Invoke-VirusScan }         ; Name = "Virus Tarama" }
        @{ Id = 5; Fn = { Invoke-FileSystemRepair }  ; Name = "Dosya Sistemi Onarimi" }
        @{ Id = 6; Fn = { Invoke-SystemOptimization }; Name = "Optimizasyon ve Hizlandirma" }
        @{ Id = 7; Fn = { Install-AutoStart }         ; Name = "Otomatik Baslama" }
    )

    # Kismi calisma modu
    $selected = if ($Tasks -and $Tasks.Count -gt 0) {
        Write-Log "Secili gorevler: $($Tasks -join ', ')" 'INFO'
        $allTasks | Where-Object { $Tasks -contains $_.Id }
    } else {
        $allTasks
    }

    # AutoMode'da Gorev 7 atla
    if ($AutoMode) { $selected = $selected | Where-Object { $_.Id -ne 7 } }

    # Gorevleri calistir
    foreach ($task in $selected) {
        Write-Log ">> Gorev $($task.Id) baslatiliyor: $($task.Name)" 'INFO'
        try {
            & $task.Fn
            $Script:Stats.TasksDone++
        } catch {
            Write-Log "GOREV $($task.Id) HATA: $_" 'ERROR'
            $Script:Stats.TasksFailed++
            Add-Result $task.Name "Gorev calistirma" "ERROR" "$_"
        }
    }

    # Bitis ozeti
    $elapsed = (Get-Date) - $Script:Stats.StartTime
    Write-Section "TAMAMLANDI"
    Write-Log "Basarili gorev  : $($Script:Stats.TasksDone)" 'OK'
    if ($Script:Stats.TasksFailed -gt 0) {
        Write-Log "Basarisiz gorev : $($Script:Stats.TasksFailed)" 'WARN'
    }
    Write-Log "Temizlenen alan : $([math]::Round($Script:Stats.FreedMB,2)) MB" 'OK'
    Write-Log "Toplam sure     : $([int]$elapsed.Minutes) dk $([int]$elapsed.Seconds) sn" 'OK'
    Write-Log "Log dosyasi     : $Script:LogFile" 'INFO'

    # HTML rapor
    if ($Script:Config.EnableHtmlReport) { Export-HtmlReport -Elapsed $elapsed }

    # Duz metin rapor
    $txtContent = @"
WinOptimizer Pro v$($Script:Version) -- Optimizasyon Raporu
Tarih   : $(Get-Date -Format 'dd.MM.yyyy HH:mm:ss')
Mod     : $modeTag
Sure    : $([int]$elapsed.Minutes) dk $([int]$elapsed.Seconds) sn
Temizlik: $([math]::Round($Script:Stats.FreedMB,2)) MB
Gorev   : $($Script:Stats.TasksDone) basarili, $($Script:Stats.TasksFailed) basarisiz
Tehdit  : $($Script:Stats.ThreatsFound)
Log     : $Script:LogFile
HTML    : $Script:HtmlRpt
"@
    $txtContent | Out-File -FilePath $Script:TxtRpt -Encoding UTF8 -Force

    # Toast bildirimi
    $toastBody = "Temizlendi: $([math]::Round($Script:Stats.FreedMB,0)) MB | Sure: $([int]$elapsed.Minutes)dk $([int]$elapsed.Seconds)sn"
    if ($Script:Stats.ThreatsFound -gt 0) { $toastBody += " | UYARI: $($Script:Stats.ThreatsFound) tehdit temizlendi!" }
    Send-ToastNotification -Title "WinOptimizer Pro -- Tamamlandi" -Body $toastBody

    Write-Log "Ozet rapor: $Script:TxtRpt" 'OK'
}

# ============================================================
#  GIRIS NOKTASI
# ============================================================
Main
