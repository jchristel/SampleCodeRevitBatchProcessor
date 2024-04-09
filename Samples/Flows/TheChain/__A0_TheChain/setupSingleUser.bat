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
set userRootFolder=%~f1

%stamp% & echo.
%stamp% & echo Using passed in root path: %userRootFolder%
%stamp% & echo.

goto start

:bad
%stamp% & echo.
%stamp% & echo No path was supplied. Terminating user folder setup.
%stamp% & echo.
goto outOfHere

:start

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

%stamp% & echo.
%stamp% & echo script root location: %_rootFolderPath%
%stamp% & echo.


:: some default folder names
:: the '_default' foler within the _Users folder
set defaultFolderName=\_default
:: the '_Settings' folder within the _Users\username\ folder
set settingsFolderName=\_Settings\

:: the user specific folder
set userFolder=%userRootFolder%\%USERNAME%
:: location of find and replace batch file
set findAndReplacePathBat="%_rootFolderPath%__A0_TheChain\FindAndReplace.bat"


:: root folders 
set userRootFolderExists=0
:: user folders exist 
set userFolderExists=0

:: check if user folders exists
if exist "%userRootFolder%" (
    set userRootFolderExists=1
    if exist "%userFolder% " (
        set userFolderExists=1
    )
)

%stamp% & echo ********************************* check of user folder start *************************************************
%stamp% & echo.
%stamp% & echo checking folders...

if %userRootFolderExists%==1 (
    if %userFolderExists%==1 (
        %stamp% & echo.
        %stamp% & echo userFolder: [%userFolder%]
        %stamp% & echo User specific directory in module allready exists.
        %stamp% & echo.
    ) else (
        %stamp% & echo.
        %stamp% & echo User directory does not exist...setting it up now:
        %stamp% & echo.
        %stamp% & echo copying default directory structure:
        %stamp% & echo from: %userRootFolder%%defaultFolderName%
        %stamp% & echo to: %userFolder%
        xcopy /E /I /C "%userRootFolder%%defaultFolderName%" "%userFolder%"
        
        %stamp% & echo Fix up settings file...replace user name
        %stamp% & echo Find and Replace: %findAndReplacePathBat%

        REM replace the _default user with the current user (needs temp files)
        for %%f in ("%userFolder%%settingsFolderName%*.json") do (
            set /p val=<%%f
            %stamp% & echo "settings file: %%f"
            REM replace the user name and create temp settings file
            call %findAndReplacePathBat% "_default" %USERNAME% "%%f">"%userFolder%%settingsFolderName%%%~nf.jsof"
            %stamp% & echo created temp settings file: "%userFolder%%settingsFolderName%%%~nf.jsof"
            REM delete old file
            DEL "%%f"
        )

        %stamp% & echo.

        REM rename temp settings files
        for %%f in ("%userFolder%%settingsFolderName%*.jsof") do (
            %stamp% & echo renaming temp settings file
            %stamp% & echo from: "%%f"
            %stamp% & echo to: "%userFolder%%settingsFolderName%%%~nf.json"
            rename "%%f" "%%~nf.json"
        )
    )
) else (
    %stamp% & echo.
    %stamp% & echo userRootFolder: [%userFolder%] 
    %stamp% & echo Failed to set up user specific folder in module since user root folder in this module does not exist. Exiting user setup...
    %stamp% & echo.
    goto outOfHere
)

%stamp% & echo.
%stamp% & echo ********************************* check of user folder end *************************************************

goto outOfHere

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "

:outOfHere
REM pause
REM get out of here
exit /b