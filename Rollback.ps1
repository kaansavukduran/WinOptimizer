#Requires -RunAsAdministrator
<#
.SYNOPSIS
    WinOptimizer Rollback Araci v3.1
.DESCRIPTION
    WinOptimizer'in aldigi en son Registry snapshot'ini geri yukler.
#>

$SnapDir = "$env:ProgramData\WinOptimizer\Snapshots"

if (-not (Test-Path $SnapDir)) {
    Write-Host "Snapshot klasoru bulunamadi: $SnapDir" -ForegroundColor Red
    exit 1
}

$snaps = Get-ChildItem "$SnapDir\*.reg" -ErrorAction SilentlyContinue |
         Sort-Object LastWriteTime -Descending

if (-not $snaps) {
    Write-Host "Geri yuklenecek snapshot bulunamadi." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "  Mevcut Snapshot'lar:" -ForegroundColor Cyan
$snaps | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.Name)  ($($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))"
}

Write-Host ""
Write-Host "  En son 5 snapshot geri yuklenecek. Devam edilsin mi? (E/H): " -NoNewline -ForegroundColor Yellow
$ans = Read-Host
if ($ans -notmatch '^[Ee]') { Write-Host "Iptal edildi." -ForegroundColor Gray; exit 0 }

$restored = 0
foreach ($snap in $snaps | Select-Object -First 5) {
    try {
        Write-Host "  Geri yukleniyor: $($snap.Name)" -ForegroundColor Cyan
        & reg import $snap.FullName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  OK: Basariyla geri yuklendi." -ForegroundColor Green
            $restored++
        } else {
            Write-Host "  HATA: Geri yukleme basarisiz." -ForegroundColor Red
        }
    } catch {
        Write-Host "  HATA: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  $restored snapshot geri yuklendi." -ForegroundColor Green
Write-Host "  Degisikliklerin tam gecerli olmasi icin sistemi yeniden baslatin." -ForegroundColor Yellow
