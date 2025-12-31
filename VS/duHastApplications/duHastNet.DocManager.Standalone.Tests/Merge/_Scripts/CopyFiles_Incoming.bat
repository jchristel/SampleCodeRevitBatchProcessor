@echo off
REM Run-CopyFiles.bat
REM Wrapper batch file to execute the PowerShell copy script

REM Set the path to your PowerShell script
SET SCRIPT_PATH=%~dp0Copy-AllFiles.ps1

REM Set the source and destination directories (change these to your desired paths)
SET SOURCE_DIR=C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.Standalone.Tests\Merge\TestSet
SET DEST_DIR=C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\duHastNet.DocManager.Standalone.Tests\Merge\Incoming

echo Copying files...
echo Source: %SOURCE_DIR%
echo Destination: %DEST_DIR%
echo.

REM Run the PowerShell script
REM Add -IncludeSubfolders flag if you want to copy from subdirectories too
PowerShell.exe -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -Source "%SOURCE_DIR%" -Destination "%DEST_DIR%"

echo.
echo Script completed.
REM pause
