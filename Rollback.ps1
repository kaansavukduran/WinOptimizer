#Requires -RunAsAdministrator
<#
.SYNOPSIS
    WinOptimizer Rollback Aracı v3.1
.DESCRIPTION
    WinOptimizer'ın aldığı en son Registry snapshot'ını geri yükler.
#>

$SnapDir = "$env:ProgramData\WinOptimizer\Snapshots"

if (-not (Test-Path $SnapDir)) {
    Write-Host "Snapshot klasörü bulunamadı: $SnapDir" -ForegroundColor Red
    exit 1
}

$snaps = Get-ChildItem "$SnapDir\*.reg" -ErrorAction SilentlyContinue |
         Sort-Object LastWriteTime -Descending

if (-not $snaps) {
    Write-Host "Geri yüklenecek snapshot bulunamadı." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "  Mevcut Snapshot'lar:" -ForegroundColor Cyan
$snaps | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.Name)  ($($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))"
}

Write-Host ""
Write-Host "  En son 5 snapshot geri yüklenecek. Devam edilsin mi? (E/H): " -NoNewline -ForegroundColor Yellow
$ans = Read-Host
if ($ans -notmatch '^[Ee]') { Write-Host "İptal edildi." -ForegroundColor Gray; exit 0 }

$restored = 0
foreach ($snap in $snaps | Select-Object -First 5) {
    try {
        Write-Host "  Geri yükleniyor: $($snap.Name)" -ForegroundColor Cyan
        & reg import $snap.FullName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK: Başarıyla geri yüklendi." -ForegroundColor Green
            $restored++
        } else {
            Write-Host "  HATA: Geri yükleme başarısız." -ForegroundColor Red
        }
    } catch {
        Write-Host "  HATA: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  $restored snapshot geri yüklendi." -ForegroundColor Green
Write-Host "  Değişikliklerin tam geçerli olması için sistemi yeniden başlatın." -ForegroundColor Yellow