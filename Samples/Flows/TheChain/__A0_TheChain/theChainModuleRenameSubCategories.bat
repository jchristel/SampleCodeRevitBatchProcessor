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

:: flow save out missing families directory
set projectRenameSubCatsDirectory=%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Users\%USERNAME%\_Output
:: default file names for log files
set logfileChangeSubcategories="%projectRenameSubCatsDirectory%\%USERNAME%_SaveOutRenameSubCategories_%ldt%.log"
:: path to flow renaming sub categories in families
set renameSubCategoriesScript="%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Script\ModifyChangeFamilySubCat.LibraryFamily.ALL_4Parallel.generic.bat"
set baseDataReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\FamilyCategoriesCombinedReport.csv"
set baseDataReportTargetRename="%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Users\%USERNAME%\_Input"


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values renaming sub categories *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo projectRenameSubCatsDirectory: %projectRenameSubCatsDirectory%
    %stamp% & echo logfileChangeSubcategories : %logfileChangeSubcategories%
    %stamp% & echo renameSubCategoriesScript: %renameSubCategoriesScript%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    goto outOfHere
)

%stamp% & echo.
%stamp% & echo ******************** Modify Family - renaming sub categories ****************
%stamp% & echo.
%stamp% & echo copy categories report:
%stamp% & copy %baseDataReportSource% %baseDataReportTargetRename%
%stamp% & echo logging to: %logfileChangeSubcategories%

REM call reporting family data
call %renameSubCategoriesScript% >> %logfileChangeSubcategories%

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "