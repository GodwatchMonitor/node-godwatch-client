;NSIS Modern User Interface
;Basic Example Script
;Written by Joost Verburg

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"
  !include "InstallOptions.nsh"
  !include "LogicLib.nsh"
  !include "CharToASCII.nsh"
  !include "Base64.nsh"
  !include "x64.nsh"
  !include "nsProcess.nsh"
  !include "registry.nsh"

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

  !define APPNAME "Godwatch Client"
  !define COMPANYNAME "Samusoidal"
  !define DESCRIPTION "A reporting client for node-godwatch"
  !define VERSIONMAJOR 0
  !define VERSIONMINOR 1
  !define VERSIONBUILD 1
  !define CLIENTVERSION 0.1
  !define HELPURL "http://samusoidal.com"
  !define UPDATEURL "http://samusoidal.com"
  !define ABOUTURL "http://samusoidal.com"
  !define INSTALLSIZE 7233

  ; ################################################################
  ; appends \ to the path if missing
  ; example: !insertmacro GetCleanDir "c:\blabla"
  ; Pop $0 => "c:\blabla\"
  !macro GetCleanDir INPUTDIR
    ; ATTENTION: USE ON YOUR OWN RISK!
    ; Please report bugs here: http://stefan.bertels.org/
    !define Index_GetCleanDir 'GetCleanDir_Line${__LINE__}'
    Push $R0
    Push $R1
    StrCpy $R0 "${INPUTDIR}"
    StrCmp $R0 "" ${Index_GetCleanDir}-finish
    StrCpy $R1 "$R0" "" -1
    StrCmp "$R1" "\" ${Index_GetCleanDir}-finish
    StrCpy $R0 "$R0\"
  ${Index_GetCleanDir}-finish:
    Pop $R1
    Exch $R0
    !undef Index_GetCleanDir
  !macroend

  ; ################################################################
  ; similar to "RMDIR /r DIRECTORY", but does not remove DIRECTORY itself
  ; example: !insertmacro RemoveFilesAndSubDirs "$INSTDIR"
  !macro RemoveFilesAndSubDirs DIRECTORY
    ; ATTENTION: USE ON YOUR OWN RISK!
    ; Please report bugs here: http://stefan.bertels.org/
    !define Index_RemoveFilesAndSubDirs 'RemoveFilesAndSubDirs_${__LINE__}'

    Push $R0
    Push $R1
    Push $R2

    !insertmacro GetCleanDir "${DIRECTORY}"
    Pop $R2
    FindFirst $R0 $R1 "$R2*.*"
  ${Index_RemoveFilesAndSubDirs}-loop:
    StrCmp $R1 "" ${Index_RemoveFilesAndSubDirs}-done
    StrCmp $R1 "." ${Index_RemoveFilesAndSubDirs}-next
    StrCmp $R1 ".." ${Index_RemoveFilesAndSubDirs}-next
    IfFileExists "$R2$R1\*.*" ${Index_RemoveFilesAndSubDirs}-directory
    ; file
    Delete "$R2$R1"
    goto ${Index_RemoveFilesAndSubDirs}-next
  ${Index_RemoveFilesAndSubDirs}-directory:
    ; directory
    RMDir /r "$R2$R1"
  ${Index_RemoveFilesAndSubDirs}-next:
    FindNext $R0 $R1
    Goto ${Index_RemoveFilesAndSubDirs}-loop
  ${Index_RemoveFilesAndSubDirs}-done:
    FindClose $R0

    Pop $R2
    Pop $R1
    Pop $R0
    !undef Index_RemoveFilesAndSubDirs
  !macroend

;--------------------------------
;General

  ;Name and file
  Name "Godwatch Client"
  Icon "base.ico"
  !define MUI_ICON "base.ico"
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "base.bmp"
  !define MUI_HEADERIMAGE_BITMAP_STRETCH AspectFitHeight
  !define MUI_HEADERIMAGE_RIGHT
  !define OutFile "godwatch-client-setup.exe"
  OutFile "${OutFile}"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"

  ;Get installation folder from registry if available
  InstallDirRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  Page custom OptionsPage OptionsPageLeave
  !insertmacro MUI_PAGE_INSTFILES
  !define MUI_FINISHPAGE_RUN
  !define MUI_FINISHPAGE_RUN_TEXT "Start Godwatch Service"
  !define MUI_FINISHPAGE_RUN_FUNCTION "StartService"
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  UninstPage custom un.DeleteCPage un.DeleteCPageLeave
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Custom Functions

Function StartService
  nsExec::Exec '"$SYSDIR\sc.exe" start GodwatchClient'
FunctionEnd

!macro VerifyUserIsAdmin
  UserInfo::GetAccountType
  pop $0
  ${If} $0 != "admin" ;Require admin rights on NT4+
          messageBox mb_iconstop "Administrator rights required!"
          setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
          quit
  ${EndIf}
!macroend

Function .onInit

  var /GLOBAL ARCHITECTURE
  ${If} ${RunningX64}
      StrCpy $ARCHITECTURE 64
      SetRegView 64
  ${Else}
      StrCpy $ARCHITECTURE 86
      SetRegView 32
  ${EndIf}

  !insertmacro VerifyUserIsAdmin

  !insertmacro INSTALLOPTIONS_EXTRACT "InstallOptionsFile.ini"

  ReadRegStr $0 HKLM "Software\${COMPANYNAME}\${APPNAME}" "serveraddress"
  !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFile.ini" "Field 6" "State" "$0"

  ReadRegStr $0 HKLM "Software\${COMPANYNAME}\${APPNAME}" "clientname"
  !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFile.ini" "Field 9" "State" "$0"

  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFile.ini" "Field 9" "State"
  ${If} $R0 == ""
    ReadRegStr $0 HKLM "System\CurrentControlSet\Control\ComputerName\ActiveComputerName" "ComputerName"
    StrCpy $1 $0 4 3
    !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFile.ini" "Field 9" "State" "$0"
  ${EndIf}

  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFile.ini" "Field 6" "State"
  ${If} $R0 == ""
    !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFile.ini" "Field 6" "State" "localhost:7001"
  ${EndIf}

FunctionEnd

Function OptionsPage
  # If you need to skip the page depending on a condition, call Abort.

  #ReserveFile "InstallOptionsFile.ini"
  !insertmacro INSTALLOPTIONS_DISPLAY "InstallOptionsFile.ini"
FunctionEnd

Function OptionsPageLeave # On clicking a button on the Configuration page

  # Load form values into variables
  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFile.ini" "Settings" "State" #Button clicked
  !insertmacro INSTALLOPTIONS_READ $R1 "InstallOptionsFile.ini" "Field 12" "State" #Existing CheckBox
  !insertmacro INSTALLOPTIONS_READ $R2 "InstallOptionsFile.ini" "Field 7" "State" #Username
  !insertmacro INSTALLOPTIONS_READ $R3 "InstallOptionsFile.ini" "Field 8" "State" #Password
  !insertmacro INSTALLOPTIONS_READ $R5 "InstallOptionsFile.ini" "Field 6" "State" #Server
  !insertmacro INSTALLOPTIONS_READ $R6 "InstallOptionsFile.ini" "Field 9" "State" #Client Name
  !insertmacro INSTALLOPTIONS_READ $R7 "InstallOptionsFile.ini" "Field 10" "State" #Interval
  !insertmacro INSTALLOPTIONS_READ $R8 "InstallOptionsFile.ini" "Field 11" "State" #Tolerance

  ${If} $R0 == 0 # Next button clicked

    ${If} $R1 == 0 # New Client Request

      Var /GLOBAL POSTDATA

      # Organize data for the POST
      Var /GLOBAL SERVERNAME
      StrCpy $SERVERNAME $R5

      Var /GLOBAL CLIENTNAME
      StrCpy $CLIENTNAME $R6

      StrCpy $POSTDATA '{ "name": "$R6", "interval": $R7, "tolerance": $R8, "version": ${CLIENTVERSION} }' # JSON for New Client Request

      # Properly encoded authentication token pulled from the form
      ${Base64_Encode} "$R2:$R3"
      pop $R4

      # Make request. Generates file PostReply.html
      inetc::post $POSTDATA /CONNECTTIMEOUT 15 /BANNER "Creating new client $R6 with interval $R7 and tolerance $R8..." /HEADER 'Authorization: Basic $R4' "http://$R5/clients/inst/new" "PostReply.html"

      # Create Install Directory - This is the first time this happens. Ensures that directory exists.
      CreateDirectory $INSTDIR

      # Save settings to a text file
      FileOpen $1 "$INSTDIR\initsettings.txt" w
      FileWrite $1 "$R5$\r$\n$R2$\r$\n$R3$\r$\n$R6$\r$\n$R7$\r$\n"
      FileClose $1

      # Alerts and Cleanup
      Pop $0
      ${If} $0 == "OK"
        MessageBox MB_OK "New client created: $R6 with interval $R7 and tolerance $R8."
        Delete "pr.html"
      ${Else}
        MessageBox MB_OK "Error: $0"
        Delete "pr.html"
        Abort
      ${EndIf}

    ${Else} # Existing Client

      # Save settings to a text file
      FileOpen $1 "$INSTDIR\initsettings.txt" w
      FileWrite $1 "$R5$\r$\n$R2$\r$\n$R3$\r$\n$R6$\r$\n$R7$\r$\n"
      FileClose $1

    ${EndIf}

  ${EndIf}

FunctionEnd

Function un.DeleteCPage
  # If you need to skip the page depending on a condition, call Abort.

  #ReserveFile "InstallOptionsFile.ini"
  !insertmacro INSTALLOPTIONS_DISPLAY "InstallOptionsFileUn.ini"
FunctionEnd

Function un.DeleteCPageLeave

  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFileUn.ini" "Settings" "State" #Button clicked
  !insertmacro INSTALLOPTIONS_READ $R6 "InstallOptionsFileUn.ini" "Field 6" "State" #Username
  !insertmacro INSTALLOPTIONS_READ $R7 "InstallOptionsFileUn.ini" "Field 7" "State" #Password
  !insertmacro INSTALLOPTIONS_READ $R5 "InstallOptionsFileUn.ini" "Field 5" "State" #Server
  !insertmacro INSTALLOPTIONS_READ $R8 "InstallOptionsFileUn.ini" "Field 8" "State" #Client Name
  ${If} $R0 == 0 # Next button
    ${un.Base64_Encode} "$R6:$R7"
    pop $R4
    Var /GLOBAL DELDATA
    StrCpy $DELDATA '{ "name": "$R8" }'
    inetc::post $DELDATA /CONNECTTIMEOUT 15 /BANNER "Removing client..." /HEADER 'Authorization: Basic $R4' "http://$R5/clients/inst/$R8" "pr.html" /END
    Pop $0
    ${If} $0 == "OK"
      MessageBox MB_OK "Client removed."
    ${Else}
      MessageBox MB_OK "Error: $0"
      Abort
    ${EndIf}
    Delete "pr.html"
  ${EndIf}

FunctionEnd

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections [or Components?]

Section "Godwatch Client" SecClient

  SectionIn RO

  SetOutPath "$INSTDIR"

  ;Executable and icons
  File "/oname=${APPNAME}.exe" main.exe
  SetOutPath "$INSTDIR\bin"
  File "/oname=godwatch.bat" godwatch.bat
  file "/oname=base.ico" base.ico

  ;Store installation folder
  WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  # Start Menu
  SetOutPath "$INSTDIR"
	createDirectory "$SMPROGRAMS\${COMPANYNAME}"
	createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\bin\godwatch.bat" "" "$INSTDIR\bin\base.ico"
  createShortCut "$DESKTOP\Start ${APPNAME}.lnk" "$INSTDIR\bin\godwatch.bat" "" "$INSTDIR\bin\base.ico"
  createShortCut "$SMPROGRAMS\${COMPANYNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\Uninstall.exe" "" ""

  WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "serveraddress" "$SERVERNAME"
  WriteRegStr HKLM "Software\${COMPANYNAME}\${APPNAME}" "clientname" "$CLIENTNAME"

	# Registry information for add/remove programs
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\ico\base.ico$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "$\"${COMPANYNAME}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "$\"${HELPURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "$\"${UPDATEURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}$\""
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	# There is no option for modifying or repairing the install
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
	# Set the INSTALLSIZE constant (!defined at the top of this script) so Add/Remove Programs can accurately report the size
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}


  nsExec::Exec '"$INSTDIR\${APPNAME}.exe" install'
  nsExec::Exec '"$SYSDIR\sc.exe" config GodwatchClient start=auto'


SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecClient ${LANG_ENGLISH} "The reporting client for Godwatch."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecClient} $(DESC_SecClient)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

function un.onInit
	SetShellVarContext all

  var /GLOBAL ARCHITECTUREUN
  ${If} ${RunningX64}
      StrCpy $ARCHITECTUREUN 64
      SetRegView 64
  ${Else}
      StrCpy $ARCHITECTUREUN 86
      SetRegView 32
  ${EndIf}

  !insertmacro INSTALLOPTIONS_EXTRACT "InstallOptionsFileUn.ini"

  ReadRegStr $0 HKLM "Software\${COMPANYNAME}\${APPNAME}" "serveraddress"
  !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFileUn.ini" "Field 5" "State" "$0"

  ReadRegStr $0 HKLM "Software\${COMPANYNAME}\${APPNAME}" "clientname"
  !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFileUn.ini" "Field 8" "State" "$0"

  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFileUn.ini" "Field 8" "State"
  ${If} $R0 == ""
    ReadRegStr $0 HKLM "System\CurrentControlSet\Control\ComputerName\ActiveComputerName" "ComputerName"
    StrCpy $1 $0 4 3
    !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFileUn.ini" "Field 8" "State" "$0"
  ${EndIf}

  !insertmacro INSTALLOPTIONS_READ $R0 "InstallOptionsFileUn.ini" "Field 5" "State"
  ${If} $R0 == ""
    !insertmacro INSTALLOPTIONS_WRITE "InstallOptionsFileUn.ini" "Field 5" "State" "localhost:7001"
  ${EndIf}

	#Verify the uninstaller - last chance to back out
	MessageBox MB_OKCANCEL "Permanantly remove ${APPNAME}?" IDOK next
		Abort
	next:
	!insertmacro VerifyUserIsAdmin
  SetShellVarContext current
functionEnd

Section "Uninstall"

  ${nsProcess::KillProcess} "${APPNAME}.exe" $R0

  ${If} $R0 == 0
  ${ElseIf} $R0 == 603
  ${Else}
    MessageBox MB_OK "Error stopping Godwatch. Please kill application manually before uninstalling."
    Abort
  ${EndIf}

  ${nsProcess::KillProcess} "${OutFile}" $R0

  ${If} $R0 == 0
  ${ElseIf} $R0 == 603
  ${Else}
    MessageBox MB_OK "Error stopping Godwatch. Please kill application manually before uninstalling."
    Abort
  ${EndIf}

  delete "$DESKTOP\Start ${APPNAME}.lnk"

  !insertmacro RemoveFilesAndSubDirs "$SMPROGRAMS\${COMPANYNAME}\"
	rmDir "$SMPROGRAMS\${COMPANYNAME}"

  nsExec::Exec '"$INSTDIR\${APPNAME}.exe" remove'

  !insertmacro RemoveFilesAndSubDirs "$INSTDIR"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"

SectionEnd
