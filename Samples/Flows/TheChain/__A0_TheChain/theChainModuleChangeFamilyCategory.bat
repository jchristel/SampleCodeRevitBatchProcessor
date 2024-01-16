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

:: ---------------------- report - change sub categories in families ------

:: flow change family category
set projectChangeFamilyCategory=%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Users\%USERNAME%\_Output
:: default file names for log files
set logfileChangeFamilyCategory="%projectChangeFamilyCategory%\%USERNAME%_ChangeFamilyCategory_%ldt%.log"
:: path to flow chaning family categories
set changeFamilyCategoryScript="%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Script\ModifyChangeFamilyCat.LibraryFamily.ALL_4Parallel.generic.bat"
set baseDataReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\FamilyCategoriesCombinedReport.csv"
set baseDataReportTargetRename="%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Users\%USERNAME%\_Input"


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values changing family categories *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo projectChangeFamilyCategory: %projectChangeFamilyCategory%
    %stamp% & echo logfileChangeFamilyCategory : %logfileChangeFamilyCategory%
    %stamp% & echo changeFamilyCategoryScript: %changeFamilyCategoryScript%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    goto outOfHere
)

%stamp% & echo.
%stamp% & echo ******************** Modify Family - changing family categories ****************
%stamp% & echo.
%stamp% & echo copy categories report:
%stamp% & copy %baseDataReportSource% %baseDataReportTargetRename%
%stamp% & echo logging to: %logfileChangeFamilyCategory%

REM call reporting family data
call %changeFamilyCategoryScript% >> %logfileChangeFamilyCategory%

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "