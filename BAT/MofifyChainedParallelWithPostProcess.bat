:: this sample demonstrates how to:
:: - run 2 different task (Alpha and Beta) where each task itself is executed in 2 parallel running sessions (session 1 and 2) of batchprocessor
::    - session 1 and 2 use two different settings files where the only difference between them is the task file list. All other settings are identical.
:: - task Beta is dependent on task Alpha to finish first before it can start
:: - run a post process script outside of the revit environment whcih will only start off after all task Beta sessions have finished processing  

:: based on stack overflow scripts:
:: https://stackoverflow.com/questions/18758502/wait-for-multiple-applications-run-asynchronously-from-batch-file-to-finish

@echo off
setlocal
set "lock=%temp%\wait%random%.lock"
:: default batchprocessor installation path
set targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe
:: Local Iron Python installation path
set pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"

echo.
echo ********************************************************************************

echo.
echo starting Revit Batch Processor...First Script Name here
echo   [batch processor folder path: %targetPath%]


:: Launch processes asynchronously, with stream 9 redirected to a lock file.
:: The lock file will remain locked until the script ends.
:: this can be the same script but each settings file points to a different file task list

start "TaskAlphaOne" 9>"%lock%1" %targetPath% --settings_file "C:\temp\SettingsAlpha1.json"
start "TaskAlphaTwo" 9>"%lock%2" %targetPath% --settings_file "C:\temp\SettingsAlpha2.json"

:WaitOne for both processes to finish (wait until lock files are no longer locked)
1>nul 2>nul ping /n 2 ::1
for %%N in (1 2) do (
  (call ) 9>"%lock%%%N" || goto :WaitOne
) 2>nul

echo deleting lock files
::delete the lock files
del "%lock%*"

:: Finish up
echo First Script Name here : Done
echo.
echo ********************************************************************************
echo.
echo starting Revit Batch Processor...Second Script Name here


:: Launch processes asynchronously, with stream 9 redirected to a lock file.
:: The lock file will remain locked until the script ends.
start "TaskBetaOne" 9>"%lock%1" %targetPath% --settings_file "C:\temp\SettingsBeta1.json"
start "TaskBetaTwo" 9>"%lock%2" %targetPath% --settings_file "C:\temp\SettingsBeta2.json"

:WaitTwo for both processes to finish (wait until lock files are no longer locked)
1>nul 2>nul ping /n 2 ::1
for %%N in (1 2) do (
  (call ) 9>"%lock%%%N" || goto :WaitTwo
) 2>nul

echo deleting lock files
::delete the lock files
del "%lock%*"

:: Finish up
echo Second Script Name here : Done
echo.
echo ********************************************************************************
echo.
echo starting post processing script (running outside of Revit!)
echo [python folder path: %pythonPath%]

call %pythonPath% "C:\temp\PostProcessingScript.py"

echo Cleaning up : Done
echo.
echo ********************************************************************************

pause