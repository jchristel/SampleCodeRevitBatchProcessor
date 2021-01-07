:: this sample demonstrates how to:
:: - run a pre process outside the revit environment which allows the user to select files via a UI 
::    - refer to SampleCodeRevitBatchProcessor/UI/SelectFIles/ for UI script
:: - run 2 different task (Alpha and Beta) where each task itself is executed in 2 parallel running sessions (session 1 and 2) of batchprocessor
::    - session 1 and 2 use two different settings files where the only difference between them is the task file list. All other settings are identical.
:: - task Beta is dependent on task Alpha to finish first before it can start
:: - run a post process script outside of the revit environment which will only start off after all task Beta sessions have finished processing  

:: based on stack overflow scripts:
:: https://stackoverflow.com/questions/18758502/wait-for-multiple-applications-run-asynchronously-from-batch-file-to-finish


@echo off
setlocal
set "lock=%temp%\wait%random%.lock"
set targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe
set pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"

echo.
echo ********************************************************************************

echo.
echo starting Revit Batch Processor...UI File Selection

:: Launch UI file selection script
:: -i revit projet files are located in : C:\temp\in
:: -o task files will be written to C:\temp\out
:: -n two task files will be written out
:: -e files with extension .rvt will be displayed in UI
call %pythonPath% "C:\temp\script.py" -i "C:\temp\in" -o "C:\temp\out" -n 2 -e .rvt

echo File Selection : Done
echo.
echo ********************************************************************************

echo.
echo starting Revit Batch Processor...Task Alpha
echo   [batch processor folder path: %targetPath%]

:: Launch processes asynchronously, with stream 9 redirected to a lock file.
:: The lock file will remain locked until the script ends.
start "TaskAlphaOne" 9>"%lock%1" %targetPath% --settings_file "C:\temp\SettingsAlpha1.json"

:: wait a few seconds in between revit start ups
timeout /t 30 /nobreak

start "TaskAlphaTwo" 9>"%lock%2" %targetPath% --settings_file "C:\temp\SettingsAlpha2.json"

:Wait for both processes to finish (wait until lock files are no longer locked)
1>nul 2>nul ping /n 2 ::1
for %%N in (1 2) do (
  (call ) 9>"%lock%%%N" || goto :Wait
) 2>nul

echo deleting lock files
::delete the lock files
del "%lock%*"

:: Finish up
echo Task Alpha : Done
echo.
echo ********************************************************************************
echo.
echo starting Revit Batch Processor...Task Beta



:: Launch processes asynchronously, with stream 9 redirected to a lock file.
:: The lock file will remain locked until the script ends.
start "TaskBetaOne" 9>"%lock%1" %targetPath% --settings_file "C:\temp\SettingsBeta1.json"

REM wait a few seconds in between revit start ups
timeout /t 30 /nobreak

start "TaskBetaTwo" 9>"%lock%2" %targetPath% --settings_file "C:\temp\SettingsBeta2.json"

:WaitAgain for both processes to finish (wait until lock files are no longer locked)
1>nul 2>nul ping /n 2 ::1
for %%N in (1 2) do (
  (call ) 9>"%lock%%%N" || goto :WaitAgain
) 2>nul

echo deleting lock files
::delete the lock files
del "%lock%*"

:: Finish up
echo Task Beta : Done
echo.
echo ********************************************************************************
echo.
echo starting post processing script (running outside of Revit!)
echo [python folder path: %pythonPath%]

call %pythonPath% "C:\temp\PostProcessingScript.py"

echo Post Processing : Done
echo.
echo ********************************************************************************

pause