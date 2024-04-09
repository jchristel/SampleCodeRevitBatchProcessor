@echo off
setlocal EnableDelayedExpansion

REM ------------------------------------- time stamp set up code -------------------------------------
set "stamp=call :stamp"
:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

:: check if a path was passt in to be used as script location
if "%~1"=="" goto bad
:: argument script location (first arg)
set _rootFolderPath=%~f1

%stamp% & echo.
%stamp% & echo Using passed in path: %_rootFolderPath%
%stamp% & echo.

goto start
:bad

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

%stamp% & echo.
%stamp% & echo script location: %_rootFolderPath%
%stamp% & echo.

:start

:: the user specific folder
set userFolder=%_rootFolderPath%_Users\%USERNAME%

%stamp% & echo **************************** checking if user folder exists *******************************************
%stamp% & echo.
%stamp% & echo user folder: %userFolder%

:: check if user folder exists
if exist "%userFolder%" (
    %stamp% & echo User directory does exist.
    exit /b
) else (
    %stamp% & echo User directory does not exist. Please run setupUser.bat script located in '__AO_TheChain' directory.
    REM exit with error level set to other then 0
    exit /b 2
)

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "

:outOfHere