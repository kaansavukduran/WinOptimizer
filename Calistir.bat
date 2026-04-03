@echo off
chcp 437 >nul
:: WinOptimizer Pro v3.1 -- Baslatic
title WinOptimizer Pro v3.1

:: Yonetici kontrolu
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Yonetici yetkisi gerekiyor, yeniden baslatiliyor...
    powershell -Command "Start-Process '%~f0' -ArgumentList '%*' -Verb RunAs"
    exit /b
)

echo.
echo  +================================================+
echo  ^|       WinOptimizer Pro v3.1                   ^|
echo  ^|   Windows 11 Sistem Optimizasyon Araci        ^|
echo  ^|                                               ^|
echo  ^|  Kullanim:                                    ^|
echo  ^|   [1] Tam Optimizasyon    (tum gorevler)      ^|
echo  ^|   [2] Hizli Temizlik      (Gorev 1,2)         ^|
echo  ^|   [3] Guvenlik Paketi     (Gorev 4,5)         ^|
echo  ^|   [4] Dry-Run Simulasyon  (hicbir sey silmez) ^|
echo  ^|   [5] Ozel Gorev Sec                          ^|
echo  +================================================+
echo.

set /p CHOICE= Seciminiz (1-5): 

if "%CHOICE%"=="1" goto FULL
if "%CHOICE%"=="2" goto QUICK
if "%CHOICE%"=="3" goto SECURITY
if "%CHOICE%"=="4" goto DRYRUN
if "%CHOICE%"=="5" goto CUSTOM
goto FULL

:FULL
echo  Tam optimizasyon baslatiliyor...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0WinOptimizer.ps1"
goto END

:QUICK
echo  Hizli temizlik (Gorev 1,2) baslatiliyor...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0WinOptimizer.ps1" -Tasks 1,2
goto END

:SECURITY
echo  Guvenlik paketi (Gorev 4,5) baslatiliyor...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0WinOptimizer.ps1" -Tasks 4,5
goto END

:DRYRUN
echo  Dry-Run: Hicbir dosya silinmeyecek, sadece rapor uretilecek...
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0WinOptimizer.ps1" -DryRun
goto END

:CUSTOM
set /p TASKS= Gorev numaralari (ornek: 1,3,5): 
echo  Secili gorevler baslatiliyor: %TASKS%
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0WinOptimizer.ps1" -Tasks %TASKS%
goto END

:END
echo.
echo  Islem tamamlandi.
echo  HTML rapor : %ProgramData%\WinOptimizer\son_rapor.html
echo  Log klasoru: %ProgramData%\WinOptimizer\Logs\
echo.
pause
