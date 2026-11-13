; Inno Setup script for the duHast pyRevit extension (Inno Setup 6).
;
; Packages the extension built by build_extension.py (duHast bundled in lib/duHast, bin filled from the
; Visual Studio output) into a per user installer. No admin rights needed.
;
; Build the extension first, then compile from the repository root:
;
;   python Samples/pyRevit/installer/build_extension.py
;   iscc Samples\pyRevit\installer\duHast-extension.iss
;
; Optional defines:
;   /DMyAppVersion=1.0.5      version shown by the installer (default: lib\duHast\_bundled_version.txt of the build)
;   /DExtensionDir=<folder>   the built extension folder (default: dist\pyRevit\duHast-2025.extension)
;   /DOutputDir=<folder>      where the setup exe goes (default: dist\pyRevit)
;
; The installer is not code signed: Windows SmartScreen will show a warning when it is run.

#define ExtensionName "duHast-2025.extension"
#define RepoRoot SourcePath + "..\..\.."

#ifndef ExtensionDir
  #define ExtensionDir RepoRoot + "\dist\pyRevit\" + ExtensionName
#endif

#ifndef OutputDir
  #define OutputDir RepoRoot + "\dist\pyRevit"
#endif

#if !DirExists(ExtensionDir)
  #error Built extension not found. Run build_extension.py first, or pass /DExtensionDir=<folder>.
#endif

#ifndef MyAppVersion
  #define VersionFile ExtensionDir + "\lib\duHast\_bundled_version.txt"
  #if !FileExists(VersionFile)
    #error Version file lib\duHast\_bundled_version.txt not found in the built extension. Pass /DMyAppVersion=<version>.
  #endif
  #define VersionFileHandle FileOpen(VersionFile)
  #define MyAppVersion Trim(FileRead(VersionFileHandle))
  #expr FileClose(VersionFileHandle)
#endif

[Setup]
AppId={{23E3545C-3572-4E69-B062-7907AA9D05D8}
AppName=duHast pyRevit extension
AppVersion={#MyAppVersion}
AppVerName=duHast pyRevit extension {#MyAppVersion}
AppPublisher=Jan Christel
AppPublisherURL=https://github.com/jchristel/SampleCodeRevitBatchProcessor
AppSupportURL=https://github.com/jchristel/SampleCodeRevitBatchProcessor/issues
LicenseFile={#RepoRoot}\LICENSE
; per user install, no admin rights
PrivilegesRequired=lowest
; {app} is the pyRevit extensions folder the extension folder goes into
DefaultDirName={userappdata}\pyRevit\Extensions
AppendDefaultDirName=no
DirExistsWarning=no
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
; keep the uninstaller out of the extensions folder pyRevit scans
UninstallFilesDir={localappdata}\duHast\pyRevit extension
UninstallDisplayName=duHast pyRevit extension
OutputDir={#OutputDir}
OutputBaseFilename={#ExtensionName}-setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Messages]
SelectDirLabel3=The extension folder {#ExtensionName} will be placed in the folder below.%n%nKeep the default to have pyRevit load it without further setup. A different folder is added to pyRevit's extension folders for you.

[InstallDelete]
; remove the previous version first so no files from it stay behind
Type: filesandordirs; Name: "{app}\{#ExtensionName}"

[Files]
Source: "{#ExtensionDir}\*"; DestDir: "{app}\{#ExtensionName}"; Flags: recursesubdirs createallsubdirs ignoreversion

[UninstallDelete]
; files pyRevit created at run time (e.g. __pycache__)
Type: filesandordirs; Name: "{app}\{#ExtensionName}"

[Code]
function DefaultExtensionsDir(): String;
begin
  Result := ExpandConstant('{userappdata}\pyRevit\Extensions');
end;

function IsDefaultExtensionsDir(Dir: String): Boolean;
begin
  Result := CompareText(RemoveBackslashUnlessRoot(Dir), DefaultExtensionsDir()) = 0;
end;

function IsRevitRunning(): Boolean;
var
  Locator, Service, Processes: Variant;
begin
  Result := False;
  try
    Locator := CreateOleObject('WbemScripting.SWbemLocator');
    Service := Locator.ConnectServer('.', 'root\CIMV2');
    Processes := Service.ExecQuery('SELECT ProcessId FROM Win32_Process WHERE Name = ''Revit.exe''');
    Result := Processes.Count > 0;
  except
    // can't tell: carry on, file copies fail with a retry prompt if DLLs are locked
  end;
end;

// Revit locks the DLLs in bin and lib\duHast\lib while it runs
function WaitForRevitToClose(Action: String): Boolean;
begin
  Result := True;
  while IsRevitRunning() do
  begin
    if SuppressibleMsgBox('Revit is running. Close all Revit sessions before you ' + Action + ' the duHast extension, then click Retry.',
      mbError, MB_RETRYCANCEL, IDCANCEL) = IDCANCEL then
    begin
      Result := False;
      exit;
    end;
  end;
end;

function IsPyRevitInstalled(): Boolean;
begin
  Result := DirExists(ExpandConstant('{userappdata}\pyRevit'))
    or DirExists(ExpandConstant('{userappdata}\pyRevit-Master'))
    or DirExists(ExpandConstant('{commonpf}\pyRevit-Master'));
end;

// runs the pyRevit command line tool, returns True if it ran and succeeded
function RunPyRevitCli(Arguments: String): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec(ExpandConstant('{cmd}'), '/C pyrevit ' + Arguments, '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
    and (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
begin
  Result := WaitForRevitToClose('install');
  if Result and not IsPyRevitInstalled() then
    Result := SuppressibleMsgBox('pyRevit does not seem to be installed. The duHast extension needs pyRevit to run.' + #13#10#13#10 +
      'Install it from https://github.com/pyrevitlabs/pyRevit first. Continue anyway?',
      mbConfirmation, MB_YESNO, IDYES) = IDYES;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Dir: String;
begin
  if CurStep = ssPostInstall then
  begin
    Dir := RemoveBackslashUnlessRoot(ExpandConstant('{app}'));
    if not IsDefaultExtensionsDir(Dir) then
      if not RunPyRevitCli('extensions paths add "' + Dir + '"') then
        SuppressibleMsgBox('The extension was installed, but the folder could not be added to pyRevit automatically.' + #13#10#13#10 +
          'Add this folder in pyRevit settings under Custom Extension Directories:' + #13#10 + Dir,
          mbInformation, MB_OK, IDOK);
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := WaitForRevitToClose('uninstall');
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Dir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    Dir := RemoveBackslashUnlessRoot(ExpandConstant('{app}'));
    // best effort: the folder may hold other extensions, so only stop pyRevit looking in it when it is empty
    if (not IsDefaultExtensionsDir(Dir)) and (not DirExists(Dir)) then
      RunPyRevitCli('extensions paths forget "' + Dir + '"');
  end;
end;
