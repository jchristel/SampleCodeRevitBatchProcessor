@echo off
REM DocManager Revit Add-in - Easy Deployment Batch File
REM This batch file provides a simple double-click deployment option

setlocal enabledelayedexpansion

echo ========================================
echo DocManager Revit Add-in Deployment
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
    set SCOPE=AllUsers
) else (
    echo Not running as administrator - deploying for current user only
    set SCOPE=CurrentUser
)
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Check if files exist in current directory
if not exist "%SCRIPT_DIR%duHastNet.DocManager.Revit.dll" (
    echo ERROR: Required files not found in: %SCRIPT_DIR%
    echo.
    echo Please ensure all DLL files are in the same directory as this batch file.
    pause
    exit /b 1
)

echo Source Directory: %SCRIPT_DIR%
echo.

REM Prompt for Revit version
echo Which Revit version(s) do you want to deploy to?
echo.
echo   1. Revit 2024 (recommended)
echo   2. Revit 2025
echo   3. Revit 2023
echo   4. All versions (2020-2025)
echo   5. Custom selection
echo.
set /p VERSION_CHOICE="Enter your choice (1-5): "

if "%VERSION_CHOICE%"=="1" set VERSIONS=2024
if "%VERSION_CHOICE%"=="2" set VERSIONS=2025
if "%VERSION_CHOICE%"=="3" set VERSIONS=2023
if "%VERSION_CHOICE%"=="4" set VERSIONS=2020 2021 2022 2023 2024 2025
if "%VERSION_CHOICE%"=="5" goto CUSTOM_VERSIONS

if not defined VERSIONS (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

goto START_DEPLOYMENT

:CUSTOM_VERSIONS
echo.
echo Enter Revit versions separated by spaces (e.g., 2023 2024 2025):
set /p VERSIONS="Versions: "

:START_DEPLOYMENT
echo.
echo ========================================
echo Deployment Configuration
echo ========================================
echo Scope: %SCOPE%
echo Versions: %VERSIONS%
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Determine base path
if "%SCOPE%"=="AllUsers" (
    set BASE_PATH=%ProgramData%\Autodesk\Revit\Addins
) else (
    set BASE_PATH=%APPDATA%\Autodesk\Revit\Addins
)

echo.
echo Starting deployment...
echo.

set SUCCESS_COUNT=0
set FAIL_COUNT=0

REM Deploy to each version
for %%V in (%VERSIONS%) do (
    echo Processing Revit %%V...
    
    set TARGET_DIR=%BASE_PATH%\%%V\duHastNet.DocManager.bundle\Contents
    
    REM Create directory if it doesn't exist
    if not exist "!TARGET_DIR!" (
        echo   Creating directory...
        mkdir "!TARGET_DIR!" 2>nul
        if errorlevel 1 (
            echo   ERROR: Failed to create directory
            set /a FAIL_COUNT+=1
            goto NEXT_VERSION
        )
    )
    
    REM Copy files
    echo   Copying files...
    xcopy "%SCRIPT_DIR%*" "!TARGET_DIR!\" /Y /I /E /Q >nul 2>&1
    if errorlevel 1 (
        echo   ERROR: Failed to copy files
        set /a FAIL_COUNT+=1
        goto NEXT_VERSION
    )
    
    REM Verify critical files
    if exist "!TARGET_DIR!\duHastNet.DocManager.Revit.dll" (
        echo   SUCCESS: Revit %%V deployment complete
        set /a SUCCESS_COUNT+=1
    ) else (
        echo   ERROR: Critical files missing
        set /a FAIL_COUNT+=1
    )
    
    :NEXT_VERSION
    echo.
)

REM Summary
echo ========================================
echo Deployment Summary
echo ========================================
echo Successful: %SUCCESS_COUNT%
echo Failed: %FAIL_COUNT%
echo.

if %SUCCESS_COUNT% GTR 0 (
    echo Next Steps:
    echo 1. Restart Revit if currently running
    echo 2. Look for 'DocManager' panel on Add-Ins tab
    echo 3. Click 'Launch DocManager' button to verify
    echo.
)

if %FAIL_COUNT% EQU 0 (
    echo All deployments completed successfully!
) else (
    echo Some deployments failed. Please check the output above.
)

echo.
pause
exit /b 0
