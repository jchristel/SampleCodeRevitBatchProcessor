@echo off
REM Run-RemoveFiles.bat
REM Wrapper batch file to execute the PowerShell script

REM Set the path to your PowerShell script
SET SCRIPT_PATH=%~dp0CleanOut_CurrentFolderSystem.ps1

REM Set the target directory (change this to your desired path)
SET TARGET_DIR=C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.Standalone.Tests\Merge\Incoming

REM Run the PowerShell script
PowerShell.exe -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -Path "%TARGET_DIR%"

REM Keep window open to see results
REM pause
