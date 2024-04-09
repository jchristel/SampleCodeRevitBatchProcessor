
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

:: ---------------------- modify - default -----------------------

:: flow modify default directory
set projectModifyDefaultDirectory=%_rootFolderPath%_01_ModifyFamilyChange\_Users\%USERNAME%\_Output
:: default file names for log files
set logfileModifyFamiliesDefault="%projectModifyDefaultDirectory%\%USERNAME%_FamilyModifyDefault_%ldt%.log"
:: flow modify families default script
set modifyFamiliesDefaultScript="%_rootFolderPath%_01_ModifyFamilyChange\_Script\ModifyDefault.LibraryFamily.NHR_4Parallel.generic.bat"
:: flow modify families input folder
set modifyFamiliesDefaultScriptInput=%_rootFolderPath%_01_ModifyFamilyChange\_Users\%USERNAME%\_Input
:: flow modify families task list folder
set modifyFamiliesDefaultTaskListLocation=%_rootFolderPath%_01_ModifyFamilyChange\_Users\%USERNAME%\_TaskList\


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values - Modify Default *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo projectModifyDefaultDirectory : %projectModifyDefaultDirectory%
    %stamp% & echo modifyFamiliesDefaultScript: %modifyFamiliesDefaultScript%
    %stamp% & echo logfileModifyFamiliesDefault: %logfileModifyFamiliesDefault%
    %stamp% & echo modifyFamiliesDefaultScriptInput: %modifyFamiliesDefaultScriptInput%
    %stamp% & echo modifyFamiliesDefaultTaskListLocation: %modifyFamiliesDefaultTaskListLocation%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
    REM goto outOfHere
)

%stamp% & echo.
%stamp% & echo ********************************* Modifying Families - Default actions ***********************************************************
%stamp% & echo logging to: %logfileModifyFamiliesDefault%
%stamp% & echo.
%stamp% & echo Checking for .task files in: %modifyFamiliesDefaultScriptInput%

if exist "%modifyFamiliesDefaultScriptInput%\*.task" (
    :: file exists copy them to task directory
    %stamp% & echo found files.
    %stamp% & echo copy files from: "%modifyFamiliesDefaultScriptInput%\*.task"
    %stamp% & echo copy files to: %modifyFamiliesDefaultTaskListLocation%
    xcopy "%modifyFamiliesDefaultScriptInput%\*.task" "%modifyFamiliesDefaultTaskListLocation%" /y
) else (
    :: file does not exist...
    %stamp% & echo No task files found, proceeding with entire library.
)

REM call default modify fam script
call %modifyFamiliesDefaultScript% >> %logfileModifyFamiliesDefault%

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "