Unicode true
!include "MUI2.nsh"
!include "FileFunc.nsh"
Name "WinOptimizer Aion"
OutFile "..\release\WinOptimizer-Aion-${APP_VERSION}-Windows-x64-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\WinOptimizer Aion"
InstallDirRegKey HKCU "Software\WinOptimizer Aion" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ICON "..\public\assets\aion.ico"
!define MUI_UNICON "..\public\assets\aion.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\WinOptimizer Aion.exe"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Turkish"
!insertmacro MUI_LANGUAGE "English"
Var Parameters
Var ForceRun
Function .onInit
  ReadRegStr $0 HKCU "Software\WinOptimizer Aion" "InstallDir"
  StrCmp $0 "" 0 existing_directory
  ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\6adb52f1-8d9b-50c2-aa35-cea78349cdbd" "InstallLocation"
  existing_directory:
  StrCmp $0 "" no_existing_directory
  StrCpy $INSTDIR $0
  no_existing_directory:
  ${GetParameters} $Parameters
  ${GetOptions} $Parameters "--force-run" $ForceRun
FunctionEnd
Section "WinOptimizer Aion"
  ; Wait for an older app's normal close before replacing its executable.
  StrCpy $1 0
  wait_window:
    FindWindow $0 "" "WinOptimizer Aion"
    StrCmp $0 0 ready
    IntOp $1 $1 + 1
    IntCmp $1 120 blocked
    Sleep 500
    Goto wait_window
  blocked:
    MessageBox MB_ICONSTOP "WinOptimizer Aion uygulamasini kapat / Close WinOptimizer Aion."
    SetErrorLevel 1
    Abort
  ready:
  SetOutPath "$INSTDIR"
  File "/oname=WinOptimizer Aion.exe" "..\release\WinOptimizer-Aion-${APP_VERSION}-Windows-x64-Portable.exe"
  WriteUninstaller "$INSTDIR\Uninstall WinOptimizer Aion.exe"
  WriteRegStr HKCU "Software\WinOptimizer Aion" "InstallDir" "$INSTDIR"
  ; Preserve the existing Electron installation's exact uninstall identity.
  !define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\6adb52f1-8d9b-50c2-aa35-cea78349cdbd"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "WinOptimizer Aion"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "Kaan Savukduran"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "UninstallString" '$\"$INSTDIR\Uninstall WinOptimizer Aion.exe$\"'
  CreateDirectory "$SMPROGRAMS\WinOptimizer Aion"
  CreateShortcut "$SMPROGRAMS\WinOptimizer Aion\WinOptimizer Aion.lnk" "$INSTDIR\WinOptimizer Aion.exe" "" "$INSTDIR\WinOptimizer Aion.exe" 0
  CreateShortcut "$DESKTOP\WinOptimizer Aion.lnk" "$INSTDIR\WinOptimizer Aion.exe" "" "$INSTDIR\WinOptimizer Aion.exe" 0
  System::Call 'shell32::SHChangeNotify(i 0x2000, i 0x5, w "$INSTDIR\WinOptimizer Aion.exe", p 0)'
  System::Call 'shell32::SHChangeNotify(i 0x2000, i 0x5, w "$DESKTOP\WinOptimizer Aion.lnk", p 0)'
  IfSilent 0 done
  ${GetOptions} $Parameters "--force-run" $0
  IfErrors done 0
  Exec '$\"$INSTDIR\WinOptimizer Aion.exe$\"'
  done:
SectionEnd
Section "Uninstall"
  Delete "$INSTDIR\WinOptimizer Aion.exe"
  Delete "$INSTDIR\Uninstall WinOptimizer Aion.exe"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\WinOptimizer Aion.lnk"
  Delete "$SMPROGRAMS\WinOptimizer Aion\WinOptimizer Aion.lnk"
  RMDir "$SMPROGRAMS\WinOptimizer Aion"
  DeleteRegKey HKCU "${UNINSTALL_KEY}"
  DeleteRegKey HKCU "Software\WinOptimizer Aion"
  ; User settings/history/backups are intentionally preserved.
SectionEnd
