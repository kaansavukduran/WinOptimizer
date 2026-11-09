@echo off
:: ═══════════════════════════════════════════════════════════════
::  WinOptimizer Pro v4.0 — Baslatici
::  Otomatik olarak Yonetici haklariyla calistirir
:: ═══════════════════════════════════════════════════════════════

title WinOptimizer Pro v4.0

:: Yonetici hakki kontrolu
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  Yonetici haklari isteniyor...
    echo.
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Script dizinine git
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║        WinOptimizer Pro v4.0 baslatiliyor...            ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ExecutionPolicy ayarla ve scripti calistir
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0WinOptimizer.ps1" %*

echo.
echo  Islem tamamlandi. Kapatmak icin bir tusa basin...
pause >nul
