@echo off
setlocal EnableDelayedExpansion
:: This script loops over a directory containing overall task files
:: it starts a reload process for each overall task file
:: which breaks those overall task files into tasks lists (work buckets) and processes them with 
:: the standard reload script


REM ------------------------------------- time stamp set up code -------------------------------------
set "stamp=call :stamp"
:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- setting up variables used --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

:: location of overall task files ( one file per reload run containing all families to be relaoded)
set _filesLocation="%_rootFolderPath%_Users\%USERNAME%\_TaskList\OverAll"
:: path to python file which builds overall task list
set "_taskListBuilder=%_rootFolderPath%_Script\Pre_TaskFileReloadListBuilder.py"
:: path to python file which builds overall changed families list
set "_changedFamiliesListBuilder=%_rootFolderPath%_Script\Post_Everything.py"
:: path to python file which splits overall task list into work chunks
:: location of change list files (maybe do GUI?)
set _changeListFilesLocation="%_rootFolderPath%_Users\%USERNAME%\_Input\ChangedFilesTaskList.csv"
:: script to split over all task into 4 task files to be processed by reloader script
set "_taskSplitter=%_rootFolderPath%_Script\Pre_TaskFileListBuilder.py"
:: batch file which processes single overall task list once it is split into work chunks 
set _batchReloadScript="%_rootFolderPath%_Script\Modify.LibraryFamilyReload.ALL_4Parallel.generic.bat"
:: default path for python installation
set _pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"

: debug toggle
set toggleDebug=0

if %toggleDebug%==1 (
  %stamp% & echo ********************************* variable values *****************************************************
  %stamp% & echo _filesLocation: %_filesLocation%
  %stamp% & echo _taskListBuilder: %_taskListBuilder%
  %stamp% & echo _changedFamiliesListBuilder: %_changedFamiliesListBuilder%
  %stamp% & echo _changeListFilesLocation: %_changeListFilesLocation%
  %stamp% & echo _taskSplitter: %_taskSplitter%
  %stamp% & echo _batchReloadScript: %_batchReloadScript%
  %stamp% & echo _pythonPath: %_pythonPath%
  %stamp% & echo.
  %stamp% & echo ********************************* DEBUG END *****************************************************
  goto outOfHere
)

REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- code execution --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

%stamp% & echo .
%stamp% & echo ********************************* checking user exists **************************************************
%stamp% & echo.
%stamp% & echo user: %USERNAME%

call "%_rootFolderPath%_Script\CheckUser.bat"
set saveErrorLevel=%errorlevel% 
REM save the error level in the above line since it will get re-set after the next echo comand!!!
%stamp% & echo error level: %saveErrorLevel%

REM check whether user exists
If %saveErrorLevel% EQU 2 (
  %stamp% & echo exiting...
  GOTO outOfHere
) else (
  %stamp% & echo user: %USERNAME% ok %saveErrorLevel%
)

%stamp% & echo ********************************** Starting Reload list builder ********************************************
%stamp% & echo.

:: call overall task file writer script with path in high commas to cater for path with spaces!!!
call %_pythonPath% "%_taskListBuilder%" %_changeListFilesLocation%

:: check for any exceptions
if !errorlevel! == 0 (echo Proceeding with no file selection errors)
if !errorlevel! == 1 (GOTO exitError)

%stamp% & echo ********************************** Starting reload script instances ********************************************
%stamp% & echo.

:: set displayed counter to start at 1
set /a _taskCounterDisplay=1

:: get number of text files in directory
set /a count=0
for /f "tokens=* delims= " %%a in ('dir/s/b/a-d %_filesLocation%"\*.txt"') do (
  set /a count+=1
)

:: loop over files
if %count% gtr 0 (
  echo found files: %count% in folder: %_filesLocation%
  for /f %%a IN ('dir /b %_filesLocation%') do (
    echo.
    echo ********************************** Reload script instance summary ********************************************
    echo starting task file pre processor... "%_taskSplitter%" 
    echo with path: %_filesLocation%
    echo with file: "%%a"
    :: exclamation marks around variable required for delayed expansion of counter within for loop!!
    echo task: !_taskCounterDisplay! of %count%
    echo **************************************************************************************************************
    echo.
    :: call task file writer script with path in high commas to cater for path with spaces!!!
    call %_pythonPath% "%_taskSplitter%" %_filesLocation% "%%a"
    :: check for any exceptions
    if !errorlevel! == 0 (echo Proceeding with no file selection errors)
    if !errorlevel! == 1 (GOTO exitError)

    echo starting reload script: %_batchReloadScript%
    :: call batch file which in turn will do the reload process. Note :: is not the same as REM it appears!
    call %_batchReloadScript%
    :: upgrade task counter
    set /a _taskCounterDisplay+=1
  )
) else (
  echo No .txt files in directory %_filesLocation%
)

%stamp% & echo.
%stamp% & echo ********************************** Finished reload script instances ********************************************
%stamp% & echo.
%stamp% & echo Deleting over all task lists at: %_filesLocation%

DEL %_filesLocation%"\*.*?"

%stamp% & echo starting combining changed families reports script: %_changedFamiliesListBuilder%
:: call script building overall changed files list
call %_pythonPath% "%_changedFamiliesListBuilder%" 

%stamp% & echo.
%stamp% & echo ********************************** Finished  ********************************************

:outOfHere
REM get out before executing code below
REM pause
exit /b


:exitError
echo A fatal exception occured...Terminating workflow.
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "