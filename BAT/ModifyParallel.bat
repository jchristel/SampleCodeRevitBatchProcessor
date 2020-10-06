:: this sample demonstrates how to:
:: - run 2 different task (Alpha and Beta) in 2 parallel running sessions of batchprocessor
:: - session Alpha and Beta use two different settings files where the only difference between them is the task file list. All other settings are identical.

@echo off
:: default batchprocessor installation path
set targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe

echo.
echo ********************************************************************************

echo.
echo starting Revit Batch Processor...
echo   [folder path: %targetPath%]

start "TaskAlphaOne" %targetPath% --settings_file "C:\temp\SettingsAlpha1.json"

:: wait a few seconds in between revit start ups
timeout /t 5 /nobreak

::  starting second session
ECHO starting second task
start "TaskBetaOne" %targetPath% --settings_file "C:\temp\SettingsBeta1.json"

