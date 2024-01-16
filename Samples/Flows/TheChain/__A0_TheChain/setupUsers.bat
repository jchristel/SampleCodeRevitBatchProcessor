@echo off
setlocal EnableDelayedExpansion

REM ------------------------------------- time stamp set up code -------------------------------------
set "stamp=call :stamp"
:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

:: check if a path was passt in to be used as script location
if "%~1"=="" goto bad
:: argument script location (first arg)
set _rootFolderPath=%~f1

%stamp% & echo.
%stamp% & echo Using passed in path: %_rootFolderPath%
%stamp% & echo.

goto start
:bad

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

%stamp% & echo.
%stamp% & echo script root location: %_rootFolderPath%
%stamp% & echo.

:start

:: some default folder names
:: the '_default' foler within the _Users folder
set defaultFolderName=\_default
:: the '_Settings' folder within the _Users\username\ folder
set settingsFolderName=\_Settings\

:: seting up various user folder locations
:: reporting
set userRootFolderReporting=%_rootFolderPath%_00_ReportFamilyData\_Users
:: saving missing families
set userRootFolderSaveMissingFams=%_rootFolderPath%_00_X_SavingMissingFamilies\_Users
:: modifying default
set userRootFolderModifyingDefault=%_rootFolderPath%_01_ModifyFamilyChange\_Users
:: rename loaded fams
set userRootFolderModRename=%_rootFolderPath%_01_X_RenameFamilies\_Users
:: change family category
set userRootFolderChangeFamCat=%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Users
:: rename family subcategories
set userRootFolderRenameFamSubCat=%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Users
:: reloading
set userRootFolderReloading=%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Users

:: location of single module user setup file
set setupSingle="%_rootFolderPath%__A0_TheChain\setupSingleUser.bat"

::  ........................................setup folder........................................

:: reporting module
call %setupSingle% "%userRootFolderReporting%"
:: save out missing fams module
call %setupSingle% "%userRootFolderSaveMissingFams%"
:: default modify module
call %setupSingle% "%userRootFolderModifyingDefault%"
:: rename fams module
call %setupSingle% "%userRootFolderModRename%"
:: change family category
call %setupSingle% "%userRootFolderChangeFamCat%"
:: rename family subcategories
call %setupSingle% "%userRootFolderRenameFamSubCat%"
:: reload fams module
call %setupSingle% "%userRootFolderReloading%"


goto outOfHere

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "

:outOfHere
REM pause
REM get out of here
exit /b