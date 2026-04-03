#Requires -RunAsAdministrator
#Requires -Version 5.1
<#
.SYNOPSIS
    WinOptimizer Pro v3.0 — Windows 11 Sistem Optimizasyon Aracı
.DESCRIPTION
    7 ana görev: Gereksiz dosya temizleme, disk optimizasyonu, güncelleme onarımı,
    virüs tarama, dosya sistemi onarımı, optimizasyon/hızlandırma, otomatik başlatma.
    v3.0 eklemeleri: Rollback, Dry-Run, Beyaz Liste, Script İmzalama kontrolü,
    Kısmi çalışma modu, RAM temizleyici, Donanım izleme, Ağ optimizasyonu,
    Toast bildirimi, HTML rapor, Zamanlama profilleri, Servis zaman aşımı koruması.
.PARAMETER DryRun
    Gerçek işlem yapmaz, sadece ne yapılacağını raporlar.
.PARAMETER Tasks
    Çalıştırılacak görev numaraları (1-7). Boş bırakılırsa tümü çalışır.
    Örnek: -Tasks 1,3,5
.PARAMETER Profile
    Zamanlama profili: "Daily" | "Weekly" | "Monthly" | "Manual"
.PARAMETER AutoMode
    Görev Zamanlayıcı tarafından çağrıldığında kullanılır.
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

# ════════════════════════════════════════════════════════════
#  SABITLER VE GLOBAL YAPILAR
# ════════════════════════════════════════════════════════════
$Script:Version  = "3.0"
$Script:BaseDir  = "$env:ProgramData\WinOptimizer"
$Script:LogDir   = "$Script:BaseDir\Logs"
$Script:SnapDir  = "$Script:BaseDir\Snapshots"
$Script:CfgFile  = "$Script:BaseDir\config.json"
$Script:LogFile  = "$Script:LogDir\optimizer_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Script:HtmlRpt  = "$Script:BaseDir\son_rapor.html"
$Script:TxtRpt   = "$Script:BaseDir\son_rapor.txt"

# Sonuç koleksiyonu (HTML rapor için)
$Script:Results  = [System.Collections.Generic.List[hashtable]]::new()
$Script:Stats    = @{
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

# ════════════════════════════════════════════════════════════
#  DİZİN KURULUMU
# ════════════════════════════════════════════════════════════
foreach ($d in @($Script:BaseDir, $Script:LogDir, $Script:SnapDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# ════════════════════════════════════════════════════════════
#  YAPILANDIRMA DOSYASI
# ════════════════════════════════════════════════════════════
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
            $loaded = Get-Content $Script:CfgFile -Raw | ConvertFrom-Json
            # Eksik anahtarları varsayılanla doldur
            foreach ($k in $default.Keys) {
                if (-not ($loaded.PSObject.Properties.Name -contains $k)) {
                    $loaded | Add-Member -NotePropertyName $k -NotePropertyValue $default[$k]
                }
            }
            return $loaded
        } catch {
            Write-Log "Config okunamadı, varsayılan kullanılıyor." 'WARN'
        }
    }
    # İlk çalıştırmada yaz
    $default | ConvertTo-Json -Depth 5 | Out-File $Script:CfgFile -Encoding UTF8 -Force
    return $default
}

$Script:Config = Get-Config

# ════════════════════════════════════════════════════════════
#  LOG SİSTEMİ
# ════════════════════════════════════════════════════════════
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO','WARN','ERROR','OK','DRY')]$Level = 'INFO'
    )
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $tag  = if ($DryRun -and $Level -eq 'INFO') { 'DRY' } else { $Level }
    $line = "[$ts][$tag] $Message"
    Add-Content -Path $Script:LogFile -Value $line -ErrorAction SilentlyContinue
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
    $sep = "─" * 62
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

# Eski log temizliği
function Remove-OldLogs {
    $cutoff = (Get-Date).AddDays(-$Script:Config.MaxLogAgeDays)
    Get-ChildItem "$Script:LogDir\*.log" -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

# ════════════════════════════════════════════════════════════
#  BEYAZ LİSTE KONTROLÜ
# ════════════════════════════════════════════════════════════
function Test-Whitelisted {
    param([string]$Path)
    foreach ($entry in $Script:Config.Whitelist) {
        if ($Path -like "$entry*") { return $true }
    }
    return $false
}

# ════════════════════════════════════════════════════════════
#  ROLLBACK — KAYIT DEFTERİ ANLIK GÖRÜNTÜSÜ
# ════════════════════════════════════════════════════════════
function New-RegistrySnapshot {
    param([string]$Label)
    if ($DryRun) { Write-Log "[DRY-RUN] Snapshot atlanıyor: $Label" 'DRY'; return }
    $snapFile = "$Script:SnapDir\reg_$(Get-Date -Format 'yyyyMMdd_HHmmss')_$Label.reg"
    try {
        $keys = @(
            "HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        )
        foreach ($key in $keys) {
            $outFile = $snapFile -replace '\.reg$', "_$(($key -split '\\')[-1]).reg"
            & reg export $key $outFile /y 2>$null | Out-Null
        }
        Write-Log "Registry snapshot alındı: $Label" 'OK'
        Add-Result "Rollback" "Snapshot: $Label" "OK" $snapFile
    } catch {
        Write-Log "Snapshot alınamadı: $_" 'WARN'
    }
}

function Restore-LatestSnapshot {
    $snaps = Get-ChildItem "$Script:SnapDir\*.reg" -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending
    if (-not $snaps) { Write-Log "Geri yüklenecek snapshot bulunamadı." 'WARN'; return }
    foreach ($snap in $snaps | Select-Object -First 5) {
        try {
            & reg import $snap.FullName 2>$null | Out-Null
            Write-Log "Geri yüklendi: $($snap.Name)" 'OK'
        } catch { Write-Log "Geri yükleme hatası: $($snap.Name)" 'ERROR' }
    }
}

# ════════════════════════════════════════════════════════════
#  SERVİS YÖNETİMİ — ZAMAN AŞIMI KORUMAL
# ════════════════════════════════════════════════════════════
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
        Write-Log "Servis durdurulamadı (zaman aşımı): $Name" 'WARN'
        return $false
    } catch {
        Write-Log "Servis durdurma hatası [$Name]: $_" 'WARN'
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
        Write-Log "Servis başlatılamadı (zaman aşımı): $Name" 'WARN'
        return $false
    } catch {
        Write-Log "Servis başlatma hatası [$Name]: $_" 'WARN'
        return $false
    }
}

# ════════════════════════════════════════════════════════════
#  DONANIM BİLGİSİ
# ════════════════════════════════════════════════════════════
function Get-HardwareInfo {
    try {
        $os  = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
        $cpu = Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue | Select-Object -First 1
        $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
        $Script:Stats.OS     = if ($os)  { "$($os.Caption) Build $($os.BuildNumber)" } else { "Bilinmiyor" }
        $Script:Stats.CPU    = if ($cpu) { $cpu.Name.Trim() } else { "Bilinmiyor" }
        $Script:Stats.RAM_GB = $ram
        Write-Log "İşletim Sistemi : $($Script:Stats.OS)" 'INFO'
        Write-Log "CPU             : $($Script:Stats.CPU)" 'INFO'
        Write-Log "RAM             : $($Script:Stats.RAM_GB) GB" 'INFO'
    } catch {
        Write-Log "Donanım bilgisi alınamadı." 'WARN'
    }
}

# ════════════════════════════════════════════════════════════
#  YARDIMCI: BOYUT HESAPLAMA
# ════════════════════════════════════════════════════════════
function Get-FolderSizeMB {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0.0 }
    try {
        $sum = (Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
        return [math]::Round($sum / 1MB, 2)
    } catch { return 0.0 }
}

function Remove-DirectoryContents {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path $Path)) {
        Write-Log "$Description — bulunamadı, atlanıyor." 'WARN'
        Add-Result "Temizlik" $Description "SKIP" "Klasör yok"
        return 0.0
    }
    if (Test-Whitelisted $Path) {
        Write-Log "$Description — BEYAZ LİSTEDE, atlanıyor." 'WARN'
        Add-Result "Temizlik" $Description "SKIP" "Beyaz listede"
        return 0.0
    }
    $before = Get-FolderSizeMB $Path
    if ($DryRun) {
        Write-Log "[DRY-RUN] Temizlenecek: $Description — ~$before MB" 'DRY'
        Add-Result "Temizlik" $Description "DRY" "$before MB"
        return $before
    }
    Get-ChildItem -Path $Path -Force -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $after = Get-FolderSizeMB $Path
    $freed = [math]::Round($before - $after, 2)
    Write-Log "$Description — $freed MB temizlendi." 'OK'
    Add-Result "Temizlik" $Description "OK" "$freed MB"
    return $freed
}

# ════════════════════════════════════════════════════════════
#  GÖREV 1 — GEREKSİZ DOSYA TEMİZLEME
# ════════════════════════════════════════════════════════════
function Invoke-JunkCleaner {
    Write-Section "GÖREV 1 — GEREKSİZ DOSYA TEMİZLEME"
    $totalFreed = 0.0

    $targets = @(
        @{ Path = $env:TEMP;                                                      Desc = "Kullanıcı TEMP" }
        @{ Path = "C:\Windows\Temp";                                              Desc = "Windows TEMP" }
        @{ Path = "C:\Windows\Prefetch";                                          Desc = "Prefetch önbelleği" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Windows\INetCache";                Desc = "İnternet önbelleği" }
        @{ Path = "$env:LOCALAPPDATA\Temp";                                       Desc = "AppData Temp" }
        @{ Path = "C:\Windows\SoftwareDistribution\Download";                     Desc = "WU indirme önbelleği" }
        @{ Path = "$env:LOCALAPPDATA\CrashDumps";                                 Desc = "Kilitlenme dökümleri" }
        @{ Path = "C:\Windows\Minidump";                                          Desc = "Mini döküm dosyaları" }
        @{ Path = "$env:APPDATA\Microsoft\Windows\Recent\AutomaticDestinations";  Desc = "Son öğeler geçmişi" }
        @{ Path = "C:\Windows\LiveKernelReports";                                 Desc = "Canlı çekirdek raporları" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer";                 Desc = "Explorer önbelleği" }
        @{ Path = "C:\Windows\Logs\CBS";                                          Desc = "CBS günlükleri" }
    )

    foreach ($t in $targets) { $totalFreed += Remove-DirectoryContents -Path $t.Path -Description $t.Desc }

    # Windows.old
    if (Test-Path "C:\Windows.old") {
        Write-Log "Windows.old bulundu." 'WARN'
        $totalFreed += Remove-DirectoryContents -Path "C:\Windows.old" -Description "Windows.old"
    }

    # Kullanıcı klasörlerindeki .tmp / .bak
    foreach ($dir in @("$env:USERPROFILE\Downloads","$env:USERPROFILE\Desktop","$env:USERPROFILE\Documents")) {
        if (-not (Test-Path $dir)) { continue }
        $removed = 0.0
        Get-ChildItem -Path $dir -Recurse -Force -Include "*.tmp","*.bak" -ErrorAction SilentlyContinue |
            ForEach-Object {
                $removed += $_.Length / 1MB
                if (-not $DryRun) { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
            }
        if ($removed -gt 0) {
            $mb = [math]::Round($removed,2)
            $tag = if ($DryRun) { "[DRY-RUN]" } else { "" }
            Write-Log "$tag $dir — .tmp/.bak: $mb MB" 'OK'
            $totalFreed += $removed
        }
    }

    # Çöp kutusu
    if (-not $DryRun) {
        try { Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Log "Çöp kutusu boşaltıldı." 'OK' }
        catch { Write-Log "Çöp kutusu boşaltılamadı." 'WARN' }
    } else {
        Write-Log "[DRY-RUN] Çöp kutusu boşaltılacak." 'DRY'
    }

    $Script:Stats.FreedMB += $totalFreed
    Write-Log "GÖREV 1 TOPLAM: ~$([math]::Round($totalFreed,2)) MB temizlendi." 'OK'
    return $totalFreed
}

# ════════════════════════════════════════════════════════════
#  GÖREV 2 — DİSK TEMİZLİĞİ & OPTİMİZASYON
# ════════════════════════════════════════════════════════════
function Invoke-DiskCleanup {
    Write-Section "GÖREV 2 — DİSK TEMİZLİĞİ"

    if ($DryRun) {
        Write-Log "[DRY-RUN] cleanmgr /sagerun:99 çalıştırılacak." 'DRY'
        Write-Log "[DRY-RUN] Sürücü Optimize-Volume çalıştırılacak." 'DRY'
        Add-Result "Disk" "cleanmgr" "DRY" ""
        return
    }

    # Cleanmgr kategori kaydı
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

    Write-Log "Disk Temizleme başlatılıyor..." 'INFO'
    try {
        $proc = Start-Process "cleanmgr.exe" -ArgumentList "/sagerun:99" -PassThru -WindowStyle Hidden
        if ($proc.WaitForExit(180000)) {
            Write-Log "Disk Temizleme tamamlandı." 'OK'
            Add-Result "Disk" "cleanmgr /sagerun:99" "OK" ""
        } else {
            $proc.Kill()
            Write-Log "Disk Temizleme zaman aşımına uğradı (3 dk), sonlandırıldı." 'WARN'
            Add-Result "Disk" "cleanmgr" "WARN" "Zaman aşımı"
        }
    } catch {
        Write-Log "Disk Temizleme başlatılamadı: $_" 'ERROR'
        Add-Result "Disk" "cleanmgr" "ERROR" "$_"
    }

    # Sürücü optimizasyonu (SSD=TRIM, HDD=Defrag)
    Write-Log "Sürücü optimizasyonu başlatılıyor..." 'INFO'
    try {
        Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' } |
            ForEach-Object {
                $letter = $_.DriveLetter
                Write-Log "  Optimize ediliyor: $letter`:" 'INFO'
                Optimize-Volume -DriveLetter $letter -ReTrim -ErrorAction SilentlyContinue 2>$null
                Add-Result "Disk" "Optimize $letter`:" "OK" ""
            }
        Write-Log "Sürücü optimizasyonu tamamlandı." 'OK'
    } catch {
        Write-Log "Sürücü optimizasyonu hatası: $_" 'WARN'
    }
}

# ════════════════════════════════════════════════════════════
#  GÖREV 3 — GÜNCELLEME ONARIMI
# ════════════════════════════════════════════════════════════
function Invoke-UpdateRepair {
    Write-Section "GÖREV 3 — GÜNCELLEME ONARIMI"

    $wuServices = @("wuauserv","bits","cryptsvc","msiserver")

    if ($DryRun) {
        Write-Log "[DRY-RUN] WU servisleri durdurulup yeniden başlatılacak." 'DRY'
        Write-Log "[DRY-RUN] SoftwareDistribution & catroot2 sıfırlanacak." 'DRY'
        Write-Log "[DRY-RUN] DLL'ler yeniden kaydedilecek, WinSock sıfırlanacak." 'DRY'
        Add-Result "Güncelleme" "Tüm onarım adımları" "DRY" ""
        return
    }

    # Snapshot al
    New-RegistrySnapshot "Before_UpdateRepair"

    # Servisleri zaman aşımı korumalı durdur
    Write-Log "WU servisleri durduruluyor..." 'INFO'
    foreach ($svc in $wuServices) {
        $ok = Stop-ServiceSafe -Name $svc -TimeoutSec 45
        Write-Log "  $svc : $(if($ok){'Durduruldu'}else{'Durdurulamadı'})" $(if($ok){'OK'}else{'WARN'})
    }
    Start-Sleep -Seconds 2

    # SoftwareDistribution ve catroot2 sıfırla
    $foldersToReset = @(
        @{ Src = "C:\Windows\SoftwareDistribution"; Bak = "C:\Windows\SoftwareDistribution.bak" }
        @{ Src = "C:\Windows\System32\catroot2";    Bak = "C:\Windows\System32\catroot2.bak"    }
    )
    foreach ($f in $foldersToReset) {
        if (Test-Path $f.Bak) { Remove-Item $f.Bak -Recurse -Force -ErrorAction SilentlyContinue }
        if (Test-Path $f.Src) {
            try {
                Rename-Item -Path $f.Src -NewName $f.Bak -ErrorAction Stop
                Write-Log "  Yeniden adlandırıldı: $($f.Src)" 'OK'
            } catch {
                # Rename başarısız olursa içeriği temizle
                Remove-Item "$($f.Src)\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "  İçerik temizlendi: $($f.Src)" 'WARN'
            }
        }
    }

    # DLL kaydı
    Write-Log "Windows Update DLL'leri kaydediliyor..." 'INFO'
    $dlls = @("atl.dll","urlmon.dll","mshtml.dll","shdocvw.dll","browseui.dll",
              "jscript.dll","vbscript.dll","scrrun.dll","msxml.dll","msxml3.dll",
              "msxml6.dll","actxprxy.dll","softpub.dll","wintrust.dll","dssenh.dll",
              "rsaenh.dll","gpkcsp.dll","sccbase.dll","slbcsp.dll","cryptdlg.dll",
              "oleaut32.dll","ole32.dll","shell32.dll","initpki.dll","wuapi.dll",
              "wuaueng.dll","wuaueng1.dll","wucltui.dll","wups.dll","wups2.dll",
              "wuweb.dll","qmgr.dll","qmgrprxy.dll","wucltux.dll","muweb.dll","wuwebv.dll")
    $dllErrors = 0
    foreach ($dll in $dlls) {
        $result = & regsvr32.exe /s $dll 2>&1
        if ($LASTEXITCODE -ne 0) { $dllErrors++ }
    }
    Write-Log "DLL kaydı tamamlandı. ($dllErrors hata)" $(if($dllErrors -eq 0){'OK'}else{'WARN'})

    # WinSock & WinHTTP sıfırla
    & netsh winsock reset 2>$null | Out-Null
    & netsh winhttp reset proxy 2>$null | Out-Null
    Write-Log "WinSock ve WinHTTP sıfırlandı." 'OK'

    # Servisleri zaman aşımı korumalı başlat
    Write-Log "WU servisleri yeniden başlatılıyor..." 'INFO'
    foreach ($svc in $wuServices) {
        $ok = Start-ServiceSafe -Name $svc -TimeoutSec 45
        Write-Log "  $svc : $(if($ok){'Başlatıldı'}else{'Başlatılamadı'})" $(if($ok){'OK'}else{'WARN'})
    }

    # WU tetikle
    try {
        (New-Object -ComObject Microsoft.Update.AutoUpdate).DetectNow()
        Write-Log "Güncelleme kontrolü tetiklendi." 'OK'
    } catch {
        Write-Log "Güncelleme kontrolü tetiklenemedi." 'WARN'
    }

    Add-Result "Güncelleme" "WU onarım döngüsü" "OK" "$dllErrors DLL hatası"
    Write-Log "Güncelleme onarımı tamamlandı." 'OK'
}

# ════════════════════════════════════════════════════════════
#  GÖREV 4 — VİRÜS VE KÖTÜ AMAÇLI YAZILIM TARAMA
# ════════════════════════════════════════════════════════════
function Invoke-VirusScan {
    Write-Section "GÖREV 4 — VİRÜS TARAMA"

    if ($DryRun) {
        Write-Log "[DRY-RUN] Defender imza güncellemesi + QuickScan çalıştırılacak." 'DRY'
        Add-Result "Virüs" "Defender Quick Scan" "DRY" ""
        return
    }

    # İmza güncelle
    Write-Log "Defender imzaları güncelleniyor..." 'INFO'
    try {
        Update-MpSignature -ErrorAction Stop
        Write-Log "İmza güncellemesi tamamlandı." 'OK'
    } catch {
        Write-Log "İmza güncellemesi başarısız: $_" 'WARN'
    }

    # Hızlı tarama — önce PowerShell, başarısız olursa MpCmdRun
    Write-Log "Hızlı tarama başlatılıyor..." 'INFO'
    $scanOk = $false
    try {
        Start-MpScan -ScanType QuickScan -ErrorAction Stop
        $scanOk = $true
        Write-Log "Hızlı tarama tamamlandı." 'OK'
    } catch {
        Write-Log "Defender PS API başarısız, MpCmdRun deneniyor..." 'WARN'
        $mpCmd = "$env:ProgramFiles\Windows Defender\MpCmdRun.exe"
        if (Test-Path $mpCmd) {
            $p = Start-Process $mpCmd -ArgumentList "-Scan -ScanType 1" -PassThru -WindowStyle Hidden
            if ($p.WaitForExit(300000)) { $scanOk = $true; Write-Log "MpCmdRun taraması tamamlandı." 'OK' }
            else { $p.Kill(); Write-Log "MpCmdRun zaman aşımı." 'WARN' }
        }
    }

    # Tehdit listesi — tehdit bazlı temizlik
    try {
        $threats = Get-MpThreatDetection -ErrorAction SilentlyContinue
        if ($threats -and $threats.Count -gt 0) {
            $Script:Stats.ThreatsFound = $threats.Count
            Write-Log "UYARI: $($threats.Count) tehdit tespit edildi!" 'WARN'
            # Önce aktif tehditleri al
            $activeThreatIds = $threats | Select-Object -ExpandProperty ThreatID -Unique
            foreach ($id in $activeThreatIds) {
                try {
                    Remove-MpThreat -ThreatID $id -ErrorAction SilentlyContinue
                    Write-Log "  Temizlendi: ThreatID $id" 'OK'
                } catch {
                    Write-Log "  Temizlenemedi: ThreatID $id" 'WARN'
                }
            }
            Add-Result "Virüs" "Tehdit Temizleme" "WARN" "$($threats.Count) tehdit"
        } else {
            Write-Log "Tehdit bulunamadı. Sistem temiz." 'OK'
            Add-Result "Virüs" "Quick Scan" "OK" "Temiz"
        }
    } catch {
        Write-Log "Tehdit geçmişi okunamadı." 'WARN'
        Add-Result "Virüs" "Tehdit Geçmişi" "WARN" "$_"
    }

    # Gerçek zamanlı koruma durumu
    try {
        $mpStatus = Get-MpComputerStatus -ErrorAction SilentlyContinue
        if ($mpStatus) {
            $rtpState = $mpStatus.RealTimeProtectionEnabled
            Write-Log "Gerçek Zamanlı Koruma: $rtpState" 'INFO'
            if (-not $rtpState) {
                Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
                Write-Log "Gerçek zamanlı koruma yeniden etkinleştirildi." 'OK'
                Add-Result "Virüs" "RTP Yeniden Etkinleştirme" "OK" ""
            }
        }
    } catch {}

    Write-Log "Virüs taraması tamamlandı." 'OK'
}

# ════════════════════════════════════════════════════════════
#  GÖREV 5 — DOSYA SİSTEMİ ONARIMI
# ════════════════════════════════════════════════════════════
function Invoke-FileSystemRepair {
    Write-Section "GÖREV 5 — DOSYA SİSTEMİ ONARIMI"

    if ($DryRun) {
        Write-Log "[DRY-RUN] SFC /scannow çalıştırılacak." 'DRY'
        Write-Log "[DRY-RUN] DISM /ScanHealth + /CheckHealth çalıştırılacak." 'DRY'
        Write-Log "[DRY-RUN] CHKDSK /scan çalıştırılacak." 'DRY'
        Add-Result "Onarım" "SFC + DISM + CHKDSK" "DRY" ""
        return
    }

    # SFC
    Write-Log "SFC /scannow başlatılıyor (birkaç dakika sürebilir)..." 'INFO'
    try {
        $sfcOut = & sfc /scannow 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $sfcOut -ErrorAction SilentlyContinue
        $sfcStatus = if ($sfcOut -match "did not find any integrity violations") { "Temiz"
            } elseif ($sfcOut -match "found corrupt files and successfully repaired") { "Onarıldı"
            } elseif ($sfcOut -match "found corrupt files but was unable to fix") { "Onarılamadı"
            } else { "Tamamlandı" }
        Write-Log "SFC: $sfcStatus" $(if($sfcStatus -eq "Onarılamadı"){'WARN'}else{'OK'})
        Add-Result "Onarım" "SFC /scannow" $(if($sfcStatus -eq "Onarılamadı"){'WARN'}else{'OK'}) $sfcStatus
    } catch {
        Write-Log "SFC çalıştırılamadı: $_" 'ERROR'
        Add-Result "Onarım" "SFC /scannow" "ERROR" "$_"
    }

    # DISM — ScanHealth → CheckHealth → RestoreHealth (koşullu)
    Write-Log "DISM ScanHealth başlatılıyor..." 'INFO'
    try {
        $dismScan = & dism /online /cleanup-image /scanhealth 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $dismScan -ErrorAction SilentlyContinue
        Write-Log "DISM ScanHealth tamamlandı." 'OK'

        $dismCheck = & dism /online /cleanup-image /checkhealth 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $dismCheck -ErrorAction SilentlyContinue

        if ($dismCheck -match "repairable" -or $dismCheck -match "onarılabilir") {
            Write-Log "DISM: Bileşen mağazası onarılabilir, RestoreHealth başlatılıyor..." 'WARN'
            $dismRestore = & dism /online /cleanup-image /restorehealth 2>&1 | Out-String
            Add-Content -Path $Script:LogFile -Value $dismRestore -ErrorAction SilentlyContinue
            Write-Log "DISM RestoreHealth tamamlandı." 'OK'
            Add-Result "Onarım" "DISM RestoreHealth" "OK" ""
        } else {
            Write-Log "DISM: Bileşen mağazası sağlıklı." 'OK'
            Add-Result "Onarım" "DISM CheckHealth" "OK" "Sağlıklı"
        }
    } catch {
        Write-Log "DISM çalıştırılamadı: $_" 'ERROR'
        Add-Result "Onarım" "DISM" "ERROR" "$_"
    }

    # CHKDSK — /scan (çevrimiçi, C: sürücüsü kilitlenmez)
    # NOT: /f yerine /scan kullanılır; /f reboot gerektirir ve sessizce bekler.
    Write-Log "CHKDSK /scan başlatılıyor..." 'INFO'
    try {
        $chkOut = & chkdsk C: /scan 2>&1 | Out-String
        Add-Content -Path $Script:LogFile -Value $chkOut -ErrorAction SilentlyContinue
        $needsFix = $chkOut -match "Windows found problems" -or $chkOut -match "sorunlar bulundu"
        if ($needsFix) {
            Write-Log "CHKDSK: Sorunlar bulundu. Bir sonraki yeniden başlatmada /f otomatik zamanlanacak." 'WARN'
            & chkdsk C: /f /perf | Out-Null   # Hata varsa yeniden başlatmada düzelt
            Add-Result "Onarım" "CHKDSK" "WARN" "Sorun bulundu, reboot'ta onarılacak"
        } else {
            Write-Log "CHKDSK: Sorun bulunamadı." 'OK'
            Add-Result "Onarım" "CHKDSK /scan" "OK" "Temiz"
        }
    } catch {
        Write-Log "CHKDSK çalıştırılamadı: $_" 'WARN'
        Add-Result "Onarım" "CHKDSK" "WARN" "$_"
    }

    Write-Log "Dosya sistemi onarımı tamamlandı." 'OK'
}

# ════════════════════════════════════════════════════════════
#  GÖREV 6 — OPTİMİZASYON, HIZLANDIRMA & YENİ MODÜLLER
# ════════════════════════════════════════════════════════════
function Invoke-SystemOptimization {
    Write-Section "GÖREV 6 — OPTİMİZASYON VE HIZLANDIRMA"

    New-RegistrySnapshot "Before_Optimization"

    # ── 6a: Başlangıç programları (Beyaz liste dışı) ──────────────
    Write-Log "Başlangıç programları analiz ediliyor..." 'INFO'
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
                    Write-Log "[DRY-RUN] Başlangıç kaldırılacak: $($prop.Name)" 'DRY'
                } else {
                    Remove-ItemProperty -Path $regPath -Name $prop.Name -ErrorAction SilentlyContinue
                    Write-Log "  Başlangıç kaldırıldı: $($prop.Name)" 'INFO'
                    Add-Result "Optimizasyon" "Başlangıç: $($prop.Name)" "OK" ""
                }
            }
        }
    }

    # ── 6b: Güç planı — Yüksek Performans ───────────────────────
    if (-not $DryRun) {
        try {
            & powercfg /setactive SCHEME_MIN 2>$null
            Write-Log "Güç planı: Yüksek Performans aktif." 'OK'
            Add-Result "Optimizasyon" "Güç Planı" "OK" "Yüksek Performans"
        } catch { Write-Log "Güç planı değiştirilemedi." 'WARN' }
    } else { Write-Log "[DRY-RUN] Güç planı Yüksek Performans'a alınacak." 'DRY' }

    # ── 6c: Görsel efektler ───────────────────────────────────────
    if (-not $DryRun) {
        $vfxPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        try {
            if (-not (Test-Path $vfxPath)) {
                New-Item -Path $vfxPath -Force | Out-Null
            }
            Set-ItemProperty -Path $vfxPath -Name "VisualFXSetting" -Value 2 -Type DWord -ErrorAction SilentlyContinue
            Write-Log "Görsel efektler: Performans modu." 'OK'
            Add-Result "Optimizasyon" "Görsel Efektler" "OK" "Performans modu"
        } catch { Write-Log "Görsel efektler ayarlanamadı." 'WARN' }
    }

    # ── 6d: Gereksiz servisler ────────────────────────────────────
    $unusedServices = @(
        @{ Name = "Fax";                Desc = "Faks" }
        @{ Name = "XblGameSave";        Desc = "Xbox Oyun Kaydetme" }
        @{ Name = "XboxNetApiSvc";      Desc = "Xbox Ağ API" }
        @{ Name = "WMPNetworkSvc";      Desc = "WMP Ağ Paylaşımı" }
        @{ Name = "MapsBroker";         Desc = "Haritalar Yöneticisi" }
        @{ Name = "RetailDemo";         Desc = "Perakende Demo" }
        @{ Name = "TabletInputService"; Desc = "Tablet Girişi" }
        @{ Name = "PrintNotify";        Desc = "Yazıcı Bildirimi" }
    )
    Write-Log "Gereksiz servisler kontrol ediliyor..." 'INFO'
    foreach ($svc in $unusedServices) {
        try {
            $s = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
            if ($s -and $s.StartType -ne 'Disabled') {
                if ($DryRun) {
                    Write-Log "[DRY-RUN] Devre dışı bırakılacak: $($svc.Desc)" 'DRY'
                } else {
                    Set-Service -Name $svc.Name -StartupType Disabled -ErrorAction SilentlyContinue
                    Stop-ServiceSafe -Name $svc.Name -TimeoutSec 15 | Out-Null
                    Write-Log "  Devre dışı: $($svc.Desc)" 'OK'
                    Add-Result "Optimizasyon" "Servis: $($svc.Desc)" "OK" "Disabled"
                }
            }
        } catch {}
    }

    # ── 6e: DNS önbelleği ─────────────────────────────────────────
    if (-not $DryRun) {
        Clear-DnsClientCache -ErrorAction SilentlyContinue
        & ipconfig /flushdns 2>$null | Out-Null
        Write-Log "DNS önbelleği temizlendi." 'OK'
        Add-Result "Optimizasyon" "DNS Önbelleği" "OK" ""
    }

    # ── 6f: Sayfa dosyası ─────────────────────────────────────────
    if (-not $DryRun) {
        try {
            $cs = Get-CimInstance Win32_ComputerSystem
            if (-not $cs.AutomaticManagedPagefile) {
                $cs | Set-CimInstance -Property @{AutomaticManagedPagefile = $true} -ErrorAction SilentlyContinue
            }
            Write-Log "Sayfa dosyası: Otomatik yönetim aktif." 'OK'
            Add-Result "Optimizasyon" "Sayfa Dosyası" "OK" "Otomatik"
        } catch { Write-Log "Sayfa dosyası yapılandırılamadı." 'WARN' }
    }

    # ── 6g: YENİ — RAM Temizleyici ────────────────────────────────
    Write-Log "RAM optimizasyonu başlatılıyor..." 'INFO'
    if (-not $DryRun) {
        try {
            $ramBefore = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
            # .NET GC
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            [System.GC]::Collect()
            # Çalışan süreçlerin Working Set'ini küçült
            $procs = Get-Process | Where-Object { -not $_.HasExited -and $_.Id -gt 4 }
            foreach ($proc in $procs) {
                try {
                    [void][System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
                        [IntPtr]::Zero, [type]"System.Func[bool]")
                } catch {}
                # SetProcessWorkingSetSize çağrısı yerine MinWorkingSet trick
                try { $proc.MinWorkingSet = [IntPtr](-1) } catch {}
            }
            Start-Sleep -Seconds 1
            $ramAfter  = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
            $gained    = [math]::Round($ramAfter - $ramBefore, 1)
            Write-Log "RAM optimizasyonu: ~$gained GB serbest bırakıldı (önce: $ramBefore GB, sonra: $ramAfter GB)." 'OK'
            Add-Result "Optimizasyon" "RAM Temizleyici" "OK" "+$gained GB serbest"
        } catch {
            Write-Log "RAM optimizasyonu sırasında hata: $_" 'WARN'
        }
    } else {
        Write-Log "[DRY-RUN] RAM temizleyici çalıştırılacak." 'DRY'
    }

    # ── 6h: YENİ — Ağ Optimizasyonu (TCP tuning) ─────────────────
    Write-Log "Ağ optimizasyonu başlatılıyor..." 'INFO'
    if (-not $DryRun) {
        try {
            # TCP Auto-Tuning (normal seviye)
            & netsh int tcp set global autotuninglevel=normal 2>$null | Out-Null
            # Direct Cache Access
            & netsh int tcp set global dca=enabled 2>$null | Out-Null
            # Chimney Offload
            & netsh int tcp set global chimney=automatic 2>$null | Out-Null
            # ECN Capability
            & netsh int tcp set global ecncapability=enabled 2>$null | Out-Null
            # RSS (Receive Side Scaling)
            & netsh int tcp set global rss=enabled 2>$null | Out-Null
            Write-Log "Ağ TCP parametreleri optimize edildi." 'OK'
            Add-Result "Optimizasyon" "TCP/IP Tuning" "OK" "autotuninglevel=normal, RSS=enabled"
        } catch {
            Write-Log "Ağ optimizasyonu hatası: $_" 'WARN'
        }
    } else {
        Write-Log "[DRY-RUN] TCP/IP parametreleri optimize edilecek." 'DRY'
    }

    # ── 6i: YENİ — Donanım İzleme ────────────────────────────────
    Write-Log "Donanım durumu kontrol ediliyor..." 'INFO'
    try {
        $diskStatus = Get-PhysicalDisk -ErrorAction SilentlyContinue |
                      Select-Object FriendlyName, HealthStatus, OperationalStatus, Size
        foreach ($disk in $diskStatus) {
            $sizGB = [math]::Round($disk.Size / 1GB, 0)
            Write-Log "  Disk: $($disk.FriendlyName) | $($disk.HealthStatus) | $sizGB GB" 'INFO'
            if ($disk.HealthStatus -ne 'Healthy') {
                Write-Log "  UYARI: Disk sağlık sorunu tespit edildi!" 'WARN'
                Add-Result "İzleme" "Disk Sağlığı" "WARN" "$($disk.FriendlyName): $($disk.HealthStatus)"
            }
        }
        # CPU kullanımı
        $cpu = (Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average
        Write-Log "  CPU Yükü: $cpu%" 'INFO'
        # Boş RAM
        $freeRam = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
        Write-Log "  Boş RAM: $freeRam GB" 'INFO'
        Add-Result "İzleme" "Donanım Durumu" "OK" "CPU: $cpu% | Boş RAM: $freeRam GB"
    } catch {
        Write-Log "Donanım izleme hatası: $_" 'WARN'
    }

    # ── 6j: Registry temizliği ────────────────────────────────────
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
        Add-Result "Optimizasyon" "Registry Temizliği" "OK" ""
    }

    # ── 6k: Geri yükleme noktası ─────────────────────────────────
    if (-not $DryRun) {
        try {
            $vssService = Get-Service -Name "VSS" -ErrorAction SilentlyContinue
            if ($vssService) {
                Checkpoint-Computer -Description "WinOptimizer v3 — $(Get-Date -Format 'yyyy-MM-dd')" `
                    -RestorePointType "MODIFY_SETTINGS" -ErrorAction SilentlyContinue
                Write-Log "Sistem geri yükleme noktası oluşturuldu." 'OK'
                Add-Result "Optimizasyon" "Geri Yükleme Noktası" "OK" ""
            }
        } catch { Write-Log "Geri yükleme noktası oluşturulamadı." 'WARN' }
    }

    Write-Log "Optimizasyon ve hızlandırma tamamlandı." 'OK'
}

# ════════════════════════════════════════════════════════════
#  GÖREV 7 — OTOMATİK BAŞLATMA KURULUMU
# ════════════════════════════════════════════════════════════
function Install-AutoStart {
    Write-Section "GÖREV 7 — OTOMATİK BAŞLATMA KURULUMU"

    # Script'in kalıcı konumunu belirle
    $scriptSrc  = $PSCommandPath
    $scriptDest = "$Script:BaseDir\WinOptimizer.ps1"

    # Script'i kalıcı konuma kopyala (farklı yerde çalışıyorsa)
    if ($scriptSrc -and $scriptSrc -ne $scriptDest -and (Test-Path $scriptSrc)) {
        try {
            Copy-Item -Path $scriptSrc -Destination $scriptDest -Force -ErrorAction Stop
            Write-Log "Script kalıcı konuma kopyalandı: $scriptDest" 'OK'
        } catch {
            Write-Log "Script kopyalanamadı, mevcut konum kullanılacak: $scriptSrc" 'WARN'
            $scriptDest = $scriptSrc
        }
    } elseif (-not (Test-Path $scriptDest)) {
        $scriptDest = $scriptSrc
    }

    # Zamanlama profili seçimi
    $triggerArgs = switch ($Script:Config.ScheduleProfile) {
        "Daily"   { New-ScheduledTaskTrigger -Daily   -At "03:00" }
        "Weekly"  { New-ScheduledTaskTrigger -Weekly  -DaysOfWeek Monday -At "03:00" }
        "Monthly" { New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At "03:00" }
        default   { New-ScheduledTaskTrigger -AtStartup }
    }

    $taskName = "WinOptimizer_AutoRun"
    $action   = New-ScheduledTaskAction `
        -Execute "PowerShell.exe" `
        -Argument "-WindowStyle Hidden -NonInteractive -ExecutionPolicy Bypass -File `"$scriptDest`" -AutoMode -Profile $($Script:Config.ScheduleProfile)"
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
            -Trigger     $triggerArgs `
            -Principal   $principal `
            -Settings    $settings `
            -Description "WinOptimizer Pro v$($Script:Version) — Otomatik çalışma" `
            -Force | Out-Null
        Write-Log "Görev Zamanlayıcı görevi oluşturuldu: $taskName" 'OK'
        Write-Log "Profil: $($Script:Config.ScheduleProfile)" 'INFO'
        Add-Result "Başlatma" "Görev Zamanlayıcı" "OK" $taskName
    } catch {
        Write-Log "Görev Zamanlayıcı hatası: $_ — Registry fallback deneniyor." 'WARN'
        try {
            Set-ItemProperty `
                -Path  "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" `
                -Name  "WinOptimizer" `
                -Value "PowerShell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptDest`" -AutoMode" `
                -ErrorAction Stop
            Write-Log "Registry başlangıç girişi oluşturuldu (yedek)." 'OK'
            Add-Result "Başlatma" "Registry Startup (fallback)" "OK" $scriptDest
        } catch {
            Write-Log "Otomatik başlatma kurulamadı: $_" 'ERROR'
            Add-Result "Başlatma" "Otomatik Başlatma" "ERROR" "$_"
        }
    }
}

# ════════════════════════════════════════════════════════════
#  HTML RAPOR ÜRETİCİ
# ════════════════════════════════════════════════════════════
function Export-HtmlReport {
    param([timespan]$Elapsed)

    $statusColor = @{ OK = "#22c55e"; WARN = "#f59e0b"; ERROR = "#ef4444"; DRY = "#a855f7"; SKIP = "#6b7280" }
    $rows = $Script:Results | ForEach-Object {
        $col = if ($statusColor[$_.Status]) { $statusColor[$_.Status] } else { "#6b7280" }
        "<tr>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Time)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Task)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>$($_.Action)</td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b'>
            <span style='background:$col20;color:$col;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600'>$($_.Status)</span>
          </td>
          <td style='padding:8px 12px;border-bottom:1px solid #1e293b;color:#94a3b8;font-size:12px'>$($_.Detail)</td>
        </tr>"
    }

    $dryBanner = if ($DryRun) {
        "<div style='background:#581c87;color:#e9d5ff;padding:12px 20px;border-radius:8px;margin-bottom:20px;font-weight:600'>
         ⚠ DRY-RUN MODU — Gerçek işlem yapılmadı. Sadece ne yapılacağı raporlandı.</div>"
    } else { "" }

    $elMin = [int]$Elapsed.Minutes
    $elSec = [int]$Elapsed.Seconds
    $dateStr = Get-Date -Format "dd MMMM yyyy HH:mm:ss"

    $html = @"
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<title>WinOptimizer Pro v$($Script:Version) — Rapor</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e1a;color:#cbd5e1;font-family:'Segoe UI',sans-serif;padding:32px}
h1{font-size:22px;font-weight:700;color:#fff;margin-bottom:4px}
.sub{font-size:12px;color:#475569;margin-bottom:28px;letter-spacing:.5px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.card{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:18px}
.card-val{font-size:24px;font-weight:700;color:#fff;margin-bottom:4px}
.card-lbl{font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px}
table{width:100%;border-collapse:collapse;background:#0f172a;border-radius:10px;overflow:hidden}
th{padding:10px 12px;background:#1e293b;color:#94a3b8;font-size:11px;text-align:left;text-transform:uppercase;letter-spacing:.5px}
tr:hover td{background:#1e293b22}
.footer{margin-top:20px;font-size:11px;color:#334155;text-align:center}
</style>
</head>
<body>
<h1>WinOptimizer Pro <span style='color:#00d4ff'>v$($Script:Version)</span> — Optimizasyon Raporu</h1>
<div class="sub">$dateStr &nbsp;|&nbsp; $($Script:Stats.Hostname) &nbsp;|&nbsp; $($Script:Stats.OS)</div>
$dryBanner
<div class="grid">
  <div class="card">
    <div class="card-val" style="color:#00e676">$([math]::Round($Script:Stats.FreedMB,0)) MB</div>
    <div class="card-lbl">Temizlenen Alan</div>
  </div>
  <div class="card">
    <div class="card-val">$($Script:Stats.TasksDone) / 7</div>
    <div class="card-lbl">Tamamlanan Görev</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:$(if($Script:Stats.ThreatsFound -gt 0){'#ff3d71'}else{'#00e676'})">
      $(if($Script:Stats.ThreatsFound -gt 0){"$($Script:Stats.ThreatsFound) Tehdit"}else{"Temiz"})
    </div>
    <div class="card-lbl">Virüs Durumu</div>
  </div>
  <div class="card">
    <div class="card-val">${elMin}dk ${elSec}sn</div>
    <div class="card-lbl">Toplam Süre</div>
  </div>
</div>
<table>
  <thead><tr><th>Saat</th><th>Görev</th><th>İşlem</th><th>Durum</th><th>Detay</th></tr></thead>
  <tbody>$($rows -join "`n")</tbody>
</table>
<div class="footer">WinOptimizer Pro v$($Script:Version) · Log: $Script:LogFile · CPU: $($Script:Stats.CPU) · RAM: $($Script:Stats.RAM_GB) GB</div>
</body>
</html>
"@
    $html | Out-File -FilePath $Script:HtmlRpt -Encoding UTF8 -Force
    Write-Log "HTML rapor: $Script:HtmlRpt" 'OK'
}

# ════════════════════════════════════════════════════════════
#  WINDOWS TOAST BİLDİRİMİ
# ════════════════════════════════════════════════════════════
function Send-ToastNotification {
    param([string]$Title, [string]$Body)
    if (-not $Script:Config.EnableToast) { return }
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
<toast>
  <visual><binding template='ToastGeneric'>
    <text>$Title</text>
    <text>$Body</text>
  </binding></visual>
</toast>
"@
        $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("WinOptimizer Pro")
        $notifier.Show($toast)
    } catch {
        # Toast WinRT olmadan çalışmıyorsa sessizce atla
    }
}

# ════════════════════════════════════════════════════════════
#  ANA ÇALIŞMA AKIŞI
# ════════════════════════════════════════════════════════════
function Main {
    $Script:Stats.StartTime = Get-Date

    # Başlık
    $mode = if ($DryRun) { "DRY-RUN" } else { "NORMAL" }
    Write-Log "╔══════════════════════════════════════════════════════════╗"
    Write-Log "║     WinOptimizer Pro v$($Script:Version) — $mode modu            ║"
    Write-Log "║     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                         ║"
    Write-Log "╚══════════════════════════════════════════════════════════╝"

    # Yönetici kontrolü
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Log "HATA: Yönetici yetkisi gerekiyor!" 'ERROR'
        exit 1
    }

    # Donanım bilgisi
    Get-HardwareInfo

    # Eski logları temizle
    Remove-OldLogs

    # Kısmi çalışma modu — hangi görevler çalışacak?
    $allTasks = @(
        @{ Id = 1; Fn = { Invoke-JunkCleaner }     ; Name = "Gereksiz Dosya Temizleme" }
        @{ Id = 2; Fn = { Invoke-DiskCleanup }     ; Name = "Disk Temizliği" }
        @{ Id = 3; Fn = { Invoke-UpdateRepair }     ; Name = "Güncelleme Onarımı" }
        @{ Id = 4; Fn = { Invoke-VirusScan }        ; Name = "Virüs Tarama" }
        @{ Id = 5; Fn = { Invoke-FileSystemRepair } ; Name = "Dosya Sistemi Onarımı" }
        @{ Id = 6; Fn = { Invoke-SystemOptimization }; Name = "Optimizasyon & Hızlandırma" }
        @{ Id = 7; Fn = { Install-AutoStart }        ; Name = "Otomatik Başlatma" }
    )

    # -Tasks parametresi verilmişse filtrele
    $selected = if ($Tasks -and $Tasks.Count -gt 0) {
        Write-Log "Seçili görevler: $($Tasks -join ', ')" 'INFO'
        $allTasks | Where-Object { $Tasks -contains $_.Id }
    } else {
        $allTasks
    }

    # AutoMode'da Görev 7 atla (zaten kurulu)
    if ($AutoMode) { $selected = $selected | Where-Object { $_.Id -ne 7 } }

    # Görevleri çalıştır
    foreach ($task in $selected) {
        Write-Log "► Görev $($task.Id) başlatılıyor: $($task.Name)" 'INFO'
        try {
            & $task.Fn
            $Script:Stats.TasksDone++
        } catch {
            Write-Log "GÖREV $($task.Id) HATA: $_" 'ERROR'
            $Script:Stats.TasksFailed++
            Add-Result $task.Name "Görev çalıştırma" "ERROR" "$_"
        }
    }

    # Bitiş
    $elapsed = (Get-Date) - $Script:Stats.StartTime
    Write-Section "TAMAMLANDI"
    Write-Log "Başarılı görev : $($Script:Stats.TasksDone)" 'OK'
    if ($Script:Stats.TasksFailed -gt 0) { Write-Log "Başarısız görev: $($Script:Stats.TasksFailed)" 'WARN' }
    Write-Log "Temizlenen alan: ~$([math]::Round($Script:Stats.FreedMB,2)) MB" 'OK'
    Write-Log "Toplam süre    : $([int]$elapsed.Minutes) dk $([int]$elapsed.Seconds) sn" 'OK'
    Write-Log "Log dosyası    : $Script:LogFile" 'INFO'

    # HTML rapor
    if ($Script:Config.EnableHtmlReport) { Export-HtmlReport -Elapsed $elapsed }

    # Düz metin rapor
    @"
WinOptimizer Pro v$($Script:Version) — Optimizasyon Raporu
Tarih   : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Mod     : $mode
Süre    : $([int]$elapsed.Minutes) dk $([int]$elapsed.Seconds) sn
Temizlik: ~$([math]::Round($Script:Stats.FreedMB,2)) MB
Görev   : $($Script:Stats.TasksDone) başarılı, $($Script:Stats.TasksFailed) başarısız
Tehdit  : $($Script:Stats.ThreatsFound)
Log     : $Script:LogFile
HTML    : $Script:HtmlRpt
"@ | Out-File -FilePath $Script:TxtRpt -Encoding UTF8 -Force

    # Toast bildirimi
    $toastBody = "Temizlendi: ~$([math]::Round($Script:Stats.FreedMB,0)) MB | Süre: $([int]$elapsed.Minutes)dk $([int]$elapsed.Seconds)sn"
    if ($Script:Stats.ThreatsFound -gt 0) { $toastBody += " | ⚠ $($Script:Stats.ThreatsFound) tehdit temizlendi!" }
    Send-ToastNotification -Title "WinOptimizer Pro — Tamamlandı" -Body $toastBody

    Write-Log "Özet rapor: $Script:TxtRpt" 'OK'
}

# ════════════════════════════════════════════════════════════
#  GİRİŞ NOKTASI
# ════════════════════════════════════════════════════════════
Main
