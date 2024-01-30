@echo off
setlocal EnableDelayedExpansion

REM ------------------------------------- time stamp set up code -------------------------------------
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
:: file path to UI file select python script
set _UIFileSelectPath="%_rootFolderPath%_Script\Pre_FileSelectUI.py"
:: directory path from which python UI is going to show revit files
set _UIInputDirectory="C:\Users\jchristel\dev\test_lib"
:: directory path into which the python UI will write the task files into (includes the user name)
set _UIOutputDirectory="%_rootFolderPath%_Users\%USERNAME%\_TaskList"
:: file path to file select python script
set _FileSelectPath="%_rootFolderPath%_Script\Pre_FileSelectNoUI.py"
:: directory where settings files are saved (includes the user name)
set "_settingsDiretoryPath=%_rootFolderPath%_Users\%USERNAME%\_Settings\"
:: settings file name for step one. Note %%j variable in name which will be used to cycle through A, B, C...
set "_settingsStepOneFileName=BatchRvt.2019.FamilyCategoriesOne%%j.NHR2.Settings.json"
:: settings file name for step two. Note %%j variable in name which will be used to cycle through A, B, C...Not required for this task!
set "_settingsStepTwoFileName="
:: file path to clean up script run at the very end
set "_cleanUpScriptPath=%_rootFolderPath%_Script\Post_FamilyData.py"
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
  %stamp% & echo ********************************* variable values *****************************************************
  %stamp% & echo.
  %stamp% & echo _rootFolderPath: %_rootFolderPath%
  %stamp% & echo _targetPath: %_targetPath%
  %stamp% & echo _pythonPath: %_pythonPath%
  %stamp% & echo _FileSelectPath: %_FileSelectPath%
  %stamp% & echo _settingsDiretoryPath: %_settingsDiretoryPath%
  %stamp% & echo _settingsStepOneFileName: %_settingsStepOneFileName%
  %stamp% & echo _settingsStepTwoFileName: %_settingsStepTwoFileName%
  %stamp% & echo _cleanUpScriptPath: %_cleanUpScriptPath%
  %stamp% & echo _len of batch array: %_len%
)

REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- code execution --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

%stamp% & echo .
%stamp% & echo ********************************* checking user exists **************************************************
%stamp% & echo.
%stamp% & echo user: %USERNAME%

call "%_rootFolderPath%_Script\CheckUser.bat"
set saveErrorLevel=%errorlevel% 
REM save the error level in the above line since it will get re-set after the next echo comand!!!
%stamp% & echo error level: %saveErrorLevel%

REM check whether user exists
If %saveErrorLevel% EQU 2 (
  %stamp% & echo exiting...
  GOTO outOfHere
) else (
  %stamp% & echo user: %USERNAME% ok %saveErrorLevel%
)

%stamp% & echo.
%stamp% & echo ********************************* UI File Selection ******************************************************
%stamp% & echo.
%stamp% & echo Starting file selection interface ... please wait.
%stamp% & echo.

:: Launch file selection script
:: Launch UI file selection script 
call %_pythonPath% %_UIFileSelectPath% %_UIInputDirectory%

:: check for errors in file selection
IF NOT ERRORLEVEL 1 GOTO no_error
:: errorhandling, errorlevel >= 1
%stamp% & echo File selection was cancelled. Exiting now...
pause
exit

:no_error

%stamp% & echo File Selection : Done
%stamp% & echo.
%stamp% & echo ********************************* Running report tasks in Revit files **************************
%stamp% & echo.
%stamp% & echo [settings folder path: %_settingsDiretoryPath%]
%stamp% & echo.

:: starting of tasks, loop over lists
:: set counter to start at 0
set _counter=0
:: set displayed counter to start at 1
set /a "_taskCounterDisplay=_counter+1"
:loopOne
if %_counter% lss %_len% (
  for /f "usebackq delims== tokens=2" %%j in (`set _obj[%_counter%]`) do (
    if NOT %_counter%==0 timeout /t 180 /nobreak
    start "ReportFamilyData%_counter%" 9>"%_lock%%_counter%" %_targetPath% --settings_file "%_settingsDiretoryPath%%_settingsStepOneFileName%"
    %stamp% & echo started Revit Batch Processor...Reporting Families ... %_taskCounterDisplay% of %_len%
    %stamp% & echo [settings file used: "%_settingsDiretoryPath%%_settingsStepOneFileName%"]
  )
  set /a "_counter=_counter+1"
  set /a "_taskCounterDisplay=_counter+1"
  goto loopOne
)

%stamp% & echo.
:: wait on processes to finish...
call :waitForIt

:: Finish up
%stamp% & echo.
%stamp% & echo Reporting family properties : Done
%stamp% & echo.

%stamp% & echo ********************************* Post clean up **************************************************
%stamp% & echo.
%stamp% & echo starting clean up script
%stamp% & echo [python folder path: %_pythonPath%]

call %_pythonPath% "%_cleanUpScriptPath%"

%stamp% & echo Cleaning up : Done
%stamp% & echo.
%stamp% & echo ********************************** Finished *******************************************************


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
  call :spinner
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

:outOfHere
exit /b