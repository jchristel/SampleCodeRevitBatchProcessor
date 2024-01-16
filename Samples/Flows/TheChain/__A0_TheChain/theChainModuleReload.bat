
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
:: flow reload directory
set projectReloadDirectory=%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Users\%USERNAME%\_Output
:: flow modify default directory
set logfileReloadFamilies="%projectReloadDirectory%\%USERNAME%_FamilyReload_%ldt%.log"
set baseDataReportTargetReload="%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Users\%USERNAME%\_Input"
:: project reload script
set modifyReloadScript="%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Script\FamilyReloadMaster_FromDir.bat"

if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values - relaod families *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo projectReloadDirectory : %projectReloadDirectory%
    %stamp% & echo baseDataReportSource: %baseDataReportSource%
    %stamp% & echo baseDataReportTargetReload: %baseDataReportTargetReload%
    %stamp% & echo modifyReloadScript: %modifyReloadScript%
    %stamp% & echo logfileReloadFamilies: %logfileReloadFamilies%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    goto outOfHere
)

%stamp% & echo.
%stamp% & echo ********************************* Reload Families ***********************************************************
%stamp% & echo copy files base report:
%stamp% & copy %baseDataReportSource% %baseDataReportTargetReload%

%stamp% & echo Starting script: %modifyReloadScript%
%stamp% & echo logging to: %logfileReloadFamilies%

call %modifyReloadScript% >> %logfileReloadFamilies%


:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "