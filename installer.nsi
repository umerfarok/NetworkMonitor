; NetworkMonitor Installer Script
; One-Click Installation for Non-Technical Users

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

; Product info
!define PRODUCT_NAME "NetworkMonitor"
!define PRODUCT_VERSION "0.1.0"
!define PRODUCT_PUBLISHER "NetworkMonitor"
!define PRODUCT_WEB_SITE "https://github.com/umerfarok/networkmonitor"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\NetworkMonitor.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; Modern UI settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

; Welcome page customization
!define MUI_WELCOMEPAGE_TITLE "Welcome to NetworkMonitor"
!define MUI_WELCOMEPAGE_TEXT "This wizard will install NetworkMonitor on your computer.$\r$\n$\r$\nNetworkMonitor lets you:$\r$\n• See all devices on your network$\r$\n• Control device connections$\r$\n• Monitor bandwidth usage$\r$\n$\r$\nClick Next to continue."

; Finish page - auto launch
!define MUI_FINISHPAGE_RUN "$INSTDIR\NetworkMonitor.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch NetworkMonitor now"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_LINK "Visit NetworkMonitor Website"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEB_SITE}"

; Installer pages - simplified for non-technical users
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer attributes
Name "${PRODUCT_NAME}"
OutFile "dist\NetworkMonitor-Setup-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES64\NetworkMonitor"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails nevershow  ; Hide details for non-technical users
ShowUnInstDetails nevershow
RequestExecutionLevel admin

; Variables
Var NpcapInstalled

Function .onInit
  ; Check Windows version
  ${IfNot} ${AtLeastWin10}
    MessageBox MB_OK|MB_ICONSTOP "NetworkMonitor requires Windows 10 or later.$\r$\n$\r$\nPlease upgrade your Windows version."
    Abort
  ${EndIf}
  
  ; Check if running on 64-bit Windows
  ${IfNot} ${RunningX64}
    MessageBox MB_OK|MB_ICONSTOP "NetworkMonitor requires 64-bit Windows.$\r$\n$\r$\nYour system appears to be 32-bit."
    Abort
  ${EndIf}
  
  ; Check if running with admin privileges
  UserInfo::GetAccountType
  Pop $0
  ${If} $0 != "admin"
    MessageBox MB_OK|MB_ICONSTOP "Please right-click the installer and select 'Run as administrator'."
    Abort
  ${EndIf}
  
  ; Check if Npcap is already installed
  StrCpy $NpcapInstalled "0"
  
  ; Check for Npcap DLL
  IfFileExists "$SYSDIR\Npcap\wpcap.dll" 0 +2
    StrCpy $NpcapInstalled "1"
  
  ; Also check WinPcap compatibility location
  IfFileExists "$SYSDIR\wpcap.dll" 0 +3
    StrCpy $NpcapInstalled "1"
FunctionEnd

Section "NetworkMonitor" SEC_CORE
  SectionIn RO
  
  ; Show progress
  DetailPrint "Installing NetworkMonitor..."
  SetOutPath "$INSTDIR"
  
  ; Main executable (single-file build)
  File "dist\NetworkMonitor.exe"
  
  ; Copy icon for shortcuts
  File "assets\icon.ico"
  
  ; Create shortcuts
  DetailPrint "Creating shortcuts..."
  CreateDirectory "$SMPROGRAMS\NetworkMonitor"
  CreateShortCut "$SMPROGRAMS\NetworkMonitor\NetworkMonitor.lnk" "$INSTDIR\NetworkMonitor.exe" "" "$INSTDIR\NetworkMonitor.exe" 0
  CreateShortCut "$SMPROGRAMS\NetworkMonitor\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortCut "$DESKTOP\NetworkMonitor.lnk" "$INSTDIR\NetworkMonitor.exe" "" "$INSTDIR\NetworkMonitor.exe" 0
  
  ; Write registry keys
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\NetworkMonitor.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\NetworkMonitor.exe"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" 1
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Install Npcap if not present
  ${If} $NpcapInstalled == "0"
    DetailPrint "Installing network driver (Npcap)..."
    DetailPrint "This may take a minute..."
    
    SetOutPath "$TEMP\NetworkMonitor"
    File "bundled_resources\Npcap\npcap-installer.exe"
    
    ; Silent install with WinPcap compatibility mode
    ExecWait '"$TEMP\NetworkMonitor\npcap-installer.exe" /S /winpcap_mode=yes' $0
    
    ${If} $0 != 0
      MessageBox MB_OK|MB_ICONEXCLAMATION "Npcap installation may have failed.$\r$\n$\r$\nIf NetworkMonitor doesn't work, please install Npcap manually from npcap.com"
    ${EndIf}
    
    Delete "$TEMP\NetworkMonitor\npcap-installer.exe"
    RMDir "$TEMP\NetworkMonitor"
  ${Else}
    DetailPrint "Network driver already installed (Npcap/WinPcap found)"
  ${EndIf}
  
  ; Install VC++ Runtime if bundled
  IfFileExists "bundled_resources\vcruntime\vc_redist.x64.exe" 0 SkipVCRuntime
    DetailPrint "Installing Visual C++ Runtime..."
    SetOutPath "$TEMP\NetworkMonitor"
    File "bundled_resources\vcruntime\vc_redist.x64.exe"
    ExecWait '"$TEMP\NetworkMonitor\vc_redist.x64.exe" /quiet /norestart'
    Delete "$TEMP\NetworkMonitor\vc_redist.x64.exe"
    RMDir "$TEMP\NetworkMonitor"
  SkipVCRuntime:
  
  ; Add firewall exception
  DetailPrint "Configuring firewall..."
  nsExec::ExecToLog 'netsh advfirewall firewall add rule name="NetworkMonitor API" dir=in action=allow program="$INSTDIR\NetworkMonitor.exe" enable=yes'
  nsExec::ExecToLog 'netsh advfirewall firewall add rule name="NetworkMonitor Port 5000" dir=in action=allow protocol=TCP localport=5000'
  
  DetailPrint "Installation complete!"
SectionEnd

Section "Uninstall"
  ; Remove firewall rules
  nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="NetworkMonitor API"'
  nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="NetworkMonitor Port 5000"'
  
  ; Remove application files
  Delete "$INSTDIR\NetworkMonitor.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\NetworkMonitor\NetworkMonitor.lnk"
  Delete "$SMPROGRAMS\NetworkMonitor\Uninstall.lnk"
  Delete "$DESKTOP\NetworkMonitor.lnk"
  RMDir "$SMPROGRAMS\NetworkMonitor"
  
  ; Remove registry keys
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd

; Description for components (not shown but required)
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "NetworkMonitor application and all required components"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

