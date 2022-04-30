:: this sample demonstrates how to:
:: - run a pre process outside the revit environment which allows the user to select files via a UI 
::    - refer to SampleCodeRevitBatchProcessor/UI/SelectFIles/ for UI script
:: - run 2 different task (Step One and Step Two) where each task itself is executed in 3 parallel running sessions (session 1 and 2) of batchprocessor
::    - session 1 and 2 use two different settings files where the only difference between them is the task file list. All other settings are identical.
:: - task Step Two is dependent on task Step One to finish first before it can start
:: - run a post process script outside of the revit environment which will only start off after all task Beta sessions have finished processing  
@echo off
setlocal EnableDelayedExpansion
:: default file name for lock files
set "_lock=%temp%\wait%random%.lock"
:: file path of Revit batch processor
set _targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe
:: default path for python installation
set _pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"
:: file path to UI file select python script
set _UIFileSelectPath="C:\temp\script.py"
:: directory path from which python UI is going to show revit files
set _UIInputDirectory="C:\temp\in"
:: directory path into which the python UI will write the task files into
set _UIOutputDirectory="C:\temp\out"
:: number of task files to be written out by python UI
set _UINumberOfTaskfiles=3
:: directory where settings files are saved
set "_settingsDiretoryPath=C:\temp\out\_settings\"
:: settings file name for step one. Note %%j variable in name which will be used to cycle through A, B, C...
set "_settingsStepOneFileName=BatchRvt.2019.TaskNameOne%%j.Settings.json"
:: settings file name for step two. Note %%j variable in name which will be used to cycle through A, B, C...
set "_settingsStepTwoFileName=BatchRvt.2019.TaskNameTwo%%j.Settings.json"
:: file path to clean up script run at the very end
set "_cleanUpScriptPath=C:\temp\Post_Script.py"
:: spinner stuff - back space character
for /f %%a in ('copy /Z "%~dpf0" nul') do set "_CR=%%a"
:: array which has the task settings file name counters (A,B,C,...) used in OneA, OneB,OneC and TwoA, TwoB, TwoC
set _obj[0]=A
set _obj[1]=B
set _obj[2]=C
:: length of the batch array
set _len=3

:: code execution
echo.
echo ********************************* UI File Selection ***********************************************************
echo.
echo Starting file selection interface ... please wait.
echo.

:: Launch UI file selection script 
call %_pythonPath% %_UIFileSelectPath% -i %_UIInputDirectory% -o %_UIOutputDirectory% -n %_UINumberOfTaskfiles% -e .rvt

:: check for errors in file selection
IF NOT ERRORLEVEL 1 GOTO no_error
:: errorhandling, errorlevel >= 1
echo File selection was cancelled. Exiting now...
pause
exit

:no_error

echo File Selection : Done
echo.
echo ********************************* Step One ************************************************
echo.
echo [settings folder path: %_settingsDiretoryPath%]
echo.

:: starting of tasks, loop over lists
:: set counter to start at 0
set _counter=0
:: set displayed counter to start at 1
set /a "_taskCounterDisplay=_counter+1"
:loopOne
if %_counter% lss %_len% (
  for /f "usebackq delims== tokens=2" %%j in (`set _obj[%_counter%]`) do (
    if NOT %_counter%==0 timeout /t 30 /nobreak
    start "StepOne%_counter%" 9>"%_lock%%_counter%" %_targetPath% --settings_file "%_settingsDiretoryPath%%_settingsStepOneFileName%"
    echo started Revit Batch Processor...step one ... %_taskCounterDisplay% of %_len%
    echo [settings file used: %_settingsStepOneFileName%]
  )
  set /a "_counter=_counter+1"
  set /a "_taskCounterDisplay=_counter+1"
  goto loopOne
)

echo.
:: wait on processes to finish...
call :waitForIt

:: Finish up
echo.
echo Step One : Done
echo.
echo ********************************* Step Two ***********************************************************
echo.
echo [settings folder path: %_settingsDiretoryPath%]
echo.

:: starting of tasks, loop over lists
:: set counter to start at 0
set _counter=0
:: set displayed counter to start at 1
set /a "_taskCounterDisplay=_counter+1"
:loopTwo
if %_counter% lss %_len% (
  for /f "usebackq delims== tokens=2" %%j in (`set _obj[%_counter%]`) do (
    if NOT %_counter%==0 timeout /t 30 /nobreak
    start "StepTwo%_counter%" 9>"%_lock%%_counter%" %_targetPath% --settings_file "%_settingsDiretoryPath%%_settingsStepTwoFileName%"
    echo started Revit Batch Processor...step two ... %_taskCounterDisplay% of %_len%
    echo [settings file used: %_settingsStepTwoFileName%]
  )
  set /a "_counter=_counter+1"
  set /a "_taskCounterDisplay=_counter+1"
  goto loopTwo
)

echo.
:: wait on processes to finish...
call :waitForIt

:: Finish up
echo.
echo Step Two : Done
echo.
echo ********************************* Post clean up ************************************************************
echo.
echo starting clean up script
echo [python folder path: %_pythonPath%]

call %_pythonPath% "%_cleanUpScriptPath%"

echo Cleaning up : Done
echo.
echo ********************************** Finished ****************************************************************

pause

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