@echo off
setlocal EnableDelayedExpansion

REM time stamp

set "stamp=call :stamp"
:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

echo Local date is [%ldt%]



REM ---------------------------------------------------------------------------------------------------------------
REM ------------------------------------- setting up variables used --------------------------------------
REM ---------------------------------------------------------------------------------------------------------------

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

:: default file name for lock files
set "_lock=%temp%\wait%random%.lock"
:: file path of Revit batch processor
set _targetPath=%LocalAppData%\RevitBatchProcessor\BatchRvt.exe
:: default path for python installation
set _pythonPath="C:\Program Files (x86)%\IronPython 2.7\ipy64.exe"
:: file path to UI file select python script
set _FileSelectPath="%_rootFolderPath%_Script\Pre_FileSelectNoUI.py"
:: file path to rename family files python script
set _FileRenamePath="%_rootFolderPath%_Script\Pre_ModifyLibraryRenameFamilyFiles.py"
:: directory containing files required as inputs
set _InputDirectory="%_rootFolderPath%_Users\%USERNAME%\_Input"
:: directory where settings files are saved
set "_settingsDiretoryPath=%_rootFolderPath%_Users\%USERNAME%\_Settings\"
:: settings file name for step one. Note %%j variable in name which will be used to cycle through A, B, C...
set "_settingsStepOneFileName=BatchRvt.2022.ModifyFamiliesOne%%j.ALL.Settings.json"
:: file path to clean up script run at the very end
set "_cleanUpScriptPath=%_rootFolderPath%_Script\Post_ModifyLibraryFamily.py"
:: spinner stuff - back space character
for /f %%a in ('copy /Z "%~dpf0" nul') do set "_CR=%%a"
:: array which has the task settings file name counters (A,B,C,...) used in OneA, OneB,OneC and TwoA, TwoB, TwoC
set _obj[0]=A
set _obj[1]=B
set _obj[2]=C
set _obj[3]=D
:: length of the batch array
set _len=4

:: debug toggle
set toggleDebug=0

if %toggleDebug%==1 (
  %stamp% & echo ********************************* DEBUG: variable values *****************************************************
  %stamp% & echo.
  %stamp% & echo _targetPath: %_targetPath%
  %stamp% & echo _pythonPath: %_pythonPath%
  %stamp% & echo _FileSelectPath: %_FileSelectPath%
  %stamp% & echo _FileRenamePath: %_FileRenamePath%
  %stamp% & echo _InputDirectory: %_InputDirectory%
  %stamp% & echo _settingsDiretoryPath: %_settingsDiretoryPath%
  %stamp% & echo _settingsStepOneFileName: %_settingsStepOneFileName%
  %stamp% & echo _cleanUpScriptPath: %_cleanUpScriptPath%
  %stamp% & echo _len of batch array: %_len%
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

echo.
echo ********************************* Pre-Processing Scripts **********************************************************
echo.
:: these can be any scripts which need to run before any files are selected...i.e family file rename.
echo Starting file rename pre processing... please wait.
call %_pythonPath% %_FileRenamePath% %_InputDirectory%
echo File Rename pre processing: Done

echo.
echo ********************************* File Selection by task list *******************************************************
echo.
echo Starting file selection  ... please wait.
echo [task list folder path: %_InputDirectory%]
echo.

:: write inividual task buckets into task lists
call %_pythonPath% %_FileSelectPath% %_InputDirectory%

echo File Selection : Done
echo.
echo ********************************* Rename loaded Families ******************************************
echo.
echo [settings folder path: %_settingsDiretoryPath%]
echo.

:: starting of tasks, loop over lists
:: set counter to start at 0
set _counter=0
:: set displayed counter to start at 1
set /a "_taskCounterDisplay=_counter+1"
:loopOne
if %_counter% lss %_len% (
  for /f "usebackq delims== tokens=2" %%j in (`set _obj[%_counter%]`) do (
    if NOT %_counter%==0 timeout /t 120 /nobreak
    start "TaskRenameFiles%_counter%" 9>"%_lock%%_counter%" %_targetPath% --settings_file "%_settingsDiretoryPath%%_settingsStepOneFileName%"
    echo started Revit Batch Processor...Rename families actions... %_taskCounterDisplay% of %_len%
    echo [settings file used: %_settingsStepOneFileName%]
  )
  set /a "_counter=_counter+1"
  set /a "_taskCounterDisplay=_counter+1"
  goto loopOne
)

echo.
:: wait on processes to finish...
call :waitForIt

:: Finish up
echo Renaming Files : Done
echo.
echo ********************************* Post clean up *************************************************************
echo.
echo starting clean up script
echo [python folder path: %_pythonPath%]

call %_pythonPath% "%_cleanUpScriptPath%"

echo Cleaning up : Done
echo.
echo ********************************** Finished ****************************************************************

REM spinner code
:spinner
set /a "spinner=(spinner + 1) %% 4"
set "spinChars=\|/-"
<nul set /p ".=Waiting on process(es) to finish.... !spinChars:~%spinner%,1!!_CR!"
exit /b

REM wait loop to check whether lock files still exist
:waitForIt
1>nul 2>nul ping /n 2 ::1
for %%N in ("%_lock%*") do (
  REM call :spinner
  (call ) 9>"%%N" || goto :waitForIt
) 2>nul

:: process has finished message
<nul set /p ".=Waiting on process(es) to finish.... Finished!"

echo.
echo deleting lock files
::delete the lock files
del "%_lock%*"

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "

:outOfHere
exit /b