
@echo off
setlocal EnableDelayedExpansion
set "stamp=call :stamp"

:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

:: check if a report toggle was passt in
if "%~1"=="" goto bad
:: argument toggle
set followUpReport=%~1

%stamp% & echo.
%stamp% & echo Using report toggle: %followUpReport%
%stamp% & echo.

:: check if a report toggle was passt in
if "%~2"=="" goto bad
:: debug toggle
set toggleDebug=%~2

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

:: ---------------------- report - initial -----------------------

:: flow report directory
set projectReportDirectory=%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Output
REM set reportFamiliesScript="%_rootFolderPath%_00_ReportFamilyData\_Script\Report.2022.FamilyData.NH2.generic.bat"
set reportFamiliesScript="%_rootFolderPath%_00_ReportFamilyData\_Script\Report.2022.FamilyData.NH2.WithUI.bat"
:: default file names for log files
set logfileReportData="%projectReportDirectory%\%USERNAME%_FamilyReport_%ldt%.log"
:: source and targets for base data report used in relaod and modify script
set baseDataReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\FamilyBaseDataCombinedReport.csv"

:: ---------------------- report - follow up ---------------------

:: default file names for log files
set logfileReportDataFollowUp="%projectReportDirectory%\%USERNAME%_FamilyReport_FollowUp_%ldt%.log"
:: merge reports marker file data
:: the actual marker file name
set mergeReportDataFileName="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Input\MergeFamilyData.csv"
:: locatio of other report files
set mergeReportRowOne=%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current
:: merge reports: process exceptions report location
set mergeReportsProcessExceptionsReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\SecondProcessFamilies.csv"
:: merge reports: process exceptions report target location
set mergeReportsProcessExceptionsReportTarget="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Input"


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values - reporting *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo followUpReport: %followUpReport%
    %stamp% & echo projectReportDirectory %projectReportDirectory%
    %stamp% & echo reportFamiliesScript: %reportFamiliesScript%
    %stamp% & echo logfileReportData: %logfileReportData%
    %stamp% & echo logfileReportDataFollowUp: %logfileReportDataFollowUp%
    %stamp% & echo baseDataReportSource: %baseDataReportSource%
    %stamp% & echo mergeReportDataFileName: %mergeReportDataFileName%
    %stamp% & echo mergeReportRowOne: %mergeReportRowOne%
    %stamp% & echo mergeReportsProcessExceptionsReportSource: %mergeReportsProcessExceptionsReportSource%
    %stamp% & echo mergeReportsProcessExceptionsReportTarget: %mergeReportsProcessExceptionsReportTarget%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    REM goto outOfHere
)

:: check if full report is required
if %followUpReport%==0 (
    %stamp% & echo.
    %stamp% & echo ********************************* Reporting Family Data ***********************************************************
    %stamp% & echo.
    %stamp% & echo logging to: %logfileReportData%
    %stamp% & echo calling reporting script at: %reportFamiliesScript%
    REM call reporting family data
    call %reportFamiliesScript% >> %logfileReportData%
) else (
    %stamp% & echo.
    %stamp% & echo Skipping initial report
    %stamp% & echo.
)

:: check if follow up report is required 
:: (note files listing families to be processed located in _\Input need to be in place already when calling this)
if %followUpReport%==1 (
    %stamp% & echo.
    %stamp% & echo ******************** Reporting Family Data - fixing any familes not processed properly ****************
    %stamp% & echo.
    %stamp% & echo logging to: %logfileReportDataFollowUp%
    %stamp% & echo writing marker file...
    echo %mergeReportRowOne%> %mergeReportDataFileName%
    REM call reporting family data with an argument specifying where process exceptions script is located
    call %reportFamiliesScript% %mergeReportsProcessExceptionsReportTarget% >> %logfileReportDataFollowUp%
) else (
    %stamp% & echo.
    %stamp% & echo Skipping follow up report
    %stamp% & echo.
)

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "