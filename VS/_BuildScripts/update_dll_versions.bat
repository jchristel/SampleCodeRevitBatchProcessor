@echo off
cd /d "%~dp0"
set /p version="Enter new version number: "
set /p confirm="Preview mode (WhatIf)? (y/N): "

if /i "%confirm%"=="y" (
    powershell.exe -ExecutionPolicy Bypass -NoExit -File "buildAllCascading.ps1" -NewVersion "%version%" -WhatIf
) else (
    powershell.exe -ExecutionPolicy Bypass -NoExit -File "buildAllCascading.ps1" -NewVersion "%version%"
)