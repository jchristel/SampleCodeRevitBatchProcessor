
@echo off
setlocal EnableDelayedExpansion
set "stamp=call :stamp"

:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

:: check if a debug toggle was passt in
if "%~1"=="" goto bad
:: debug toggle
set toggleDebug=%~1

%stamp% & echo.
%stamp% & echo Using debug toggle: %toggleDebug%
%stamp% & echo.

goto start

:bad
%stamp% & echo.
%stamp% & echo no argument was supplied. Exiting.
%stamp% & echo.
goto outOfHere

:start

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"


:: source and targets for base data report used in relaod and modify script
set baseDataReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\FamilyBaseDataCombinedReport.csv"
:: flow modify rename loaded
set projectModifyRenameLoadedDirectory=%_rootFolderPath%_01_X_RenameFamilies\_Users\%USERNAME%\_Output
:: default file names for log files
set logfileRenameFams="%projectModifyRenameLoadedDirectory%\%USERNAME%_RenameFamilies_%ldt%.log"
set baseDataReportTargetModifyRename="%_rootFolderPath%_01_X_RenameFamilies\_Users\%USERNAME%\_Input"
:: project modify rename loaded script
set modifyFamiliesRenameLoaded="%_rootFolderPath%_01_X_RenameFamilies\_Script\Modify.LibraryFamilyRename.NHR_4Parallel.generic.bat"
:: source and target for rename directives in modify family script
set familyRenameSource="%_rootFolderPath%_01_X_RenameFamilies\_Users\%USERNAME%\_Analysis\actionNow\*.csv"
set familyRenameTarget="%_rootFolderPath%_01_X_RenameFamilies\_Users\%USERNAME%\_Input"

if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values - Modify rename families *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo baseDataReportSource: %baseDataReportSource%
    %stamp% & echo baseDataReportTargetModifyRename: %baseDataReportTargetModifyRename%
    %stamp% & echo modifyFamiliesRenameLoaded: %modifyFamiliesRenameLoaded%
    %stamp% & echo logfileRenameFams: %logfileRenameFams%
    %stamp% & echo familyRenameSource: %familyRenameSource%
    %stamp% & echo familyRenameTarget: %familyRenameTarget%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    goto outOfHere
)

%stamp% & echo.
%stamp% & echo ********************************* Modifying Families - Renaming Families ***********************************************************
%stamp% & echo copy files rename directives:
%stamp% & copy %familyRenameSource% %familyRenameTarget%
%stamp% & echo copy files base report:
%stamp% & copy %baseDataReportSource% %baseDataReportTargetModifyRename%

%stamp% & echo starting script: %modifyFamiliesRenameLoaded%
%stamp% & echo logging to: %logfileRenameFams%

REM call modify fam script with argument (rename families : yes)
call %modifyFamiliesRenameLoaded% >> %logfileRenameFams%

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "