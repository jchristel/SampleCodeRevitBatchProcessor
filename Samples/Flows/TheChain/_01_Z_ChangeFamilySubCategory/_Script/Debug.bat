@echo off
setlocal EnableDelayedExpansion

REM time stamp

set "stamp=call :stamp"
:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- setting up variables used --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

:: default file name for lock files
set "_lock=%temp%\wait%random%.lock"
:: file path of Revit batch processor
set _targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe
:: default path for python installation
set _pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"
:: file path to file select python script
set _FileSelectPath="%_rootFolderPath%_Script\Pre_ChangeFamilySubCategoryStandAlone.py"
:: file path to file select python script
set _FileBuilderPath="%_rootFolderPath%_Script\Pre_TaskFileListBuilder.py"
:: directory where settings files are saved
set "_settingsDiretoryPath=%_rootFolderPath%_Users\%USERNAME%\_Settings\"
:: settings file name for step one. Note %%j variable in name which will be used to cycle through A, B, C...
set "_settingsStepOneFileName=BatchRvt.2022.ModifyChangeFamilySubCategoryOne%%j.ALL.Settings.json"
:: file path to clean up script run at the very end
set "_cleanUpScriptPath=%_rootFolderPath%_Script\Post_ChangeFamilySubCategory.py"
:: spinner stuff - back space character
for /f %%a in ('copy /Z "%~dpf0" nul') do set "_CR=%%a"
:: array which has the task settings file name counters (A,B,C,...) used in OneA, OneB,OneC and TwoA, TwoB, TwoC
set _obj[0]=A
set _obj[1]=B
set _obj[2]=C
set _obj[3]=D
:: length of the batch array
set _len=4

:: debug toggle
set toggleDebug=0

if %toggleDebug%==1 (
  %stamp% & echo ********************************* DEBUG: variable values *****************************************************
  %stamp% & echo.
  %stamp% & echo _targetPath: %_targetPath%
  %stamp% & echo _pythonPath: %_pythonPath%
  %stamp% & echo _FileSelectPath: %_FileSelectPath%
  %stamp% & echo _settingsDiretoryPath: %_settingsDiretoryPath%
  %stamp% & echo _settingsStepOneFileName: %_settingsStepOneFileName%
  %stamp% & echo _cleanUpScriptPath: %_cleanUpScriptPath%
  %stamp% & echo _len of batch array: %_len%
  %stamp% & echo.
  %stamp% & echo ********************************* DEBUG END *****************************************************
  goto outOfHere
)

REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- code execution --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

%stamp% & echo.
%stamp% & echo ********************************* build file Selection from change directives and report *******************************************************
%stamp% & echo.
%stamp% & echo Starting file selection ... please wait.
%stamp% & echo [script path : %_FileBuilderPath%]
%stamp% & echo.

:: Launch file selection script with no argument (default behaviour)
call %_pythonPath% %_FileBuilderPath%

:: check for errors in file selection
IF NOT ERRORLEVEL 1 GOTO no_error_one
:: errorhandling, errorlevel >= 1
%stamp% & echo Build file selection failed with an exception. Exiting now...
exit

:no_error_one


%stamp% & echo.
%stamp% & echo ********************************* build task buckets from task list  *******************************************************
%stamp% & echo.
%stamp% & echo Starting file selection interface ... please wait.
%stamp% & echo [script path : %_FileSelectPath%]
%stamp% & echo.

:: Launch file selection script with no argument (default behaviour)
call %_pythonPath% %_FileSelectPath%

:: check for errors in file selection
IF NOT ERRORLEVEL 1 GOTO no_error
:: errorhandling, errorlevel >= 1
%stamp% & echo File selection failed with an exception. Exiting now...
exit

:no_error

:outOfHere
REM pause
REM get out before executing the spinner code below
exit /b

REM spinner code
:spinner
set /a "spinner=(spinner + 1) %% 4"
set "spinChars=\|/-"
<nul set /p ".=Waiting on process(es) to finish.... !spinChars:~%spinner%,1!!_CR!"
exit /b

REM wait loop to check whether lock files still exist
:waitForIt
1>nul 2>nul ping /n 2 ::1
for %%N in ("%_lock%*") do (
  REM call :spinner
  (call ) 9>"%%N" || goto :waitForIt
) 2>nul

:: process has finished message
<nul set /p ".=Waiting on process(es) to finish.... Finished!"

echo.
echo deleting lock files
::delete the lock files
del "%_lock%*"

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "
