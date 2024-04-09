
@echo off
setlocal EnableDelayedExpansion
set "stamp=call :stamp"

:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]

:: check if a debug toggle was passt in
if "%~1"=="" goto bad
:: debug toggle
set toggleDebug=%~1

%stamp% & echo.
%stamp% & echo Using debug toggle: %toggleDebug%
%stamp% & echo.

goto start

:bad
%stamp% & echo.
%stamp% & echo no argument was supplied. Exiting.
%stamp% & echo.
goto outOfHere

:start

:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

:: ---------------------- report - save out missing families ------

:: flow save out missing families directory
set projectSaveMissingFamsDirectory=%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_Output
:: default file names for log files
set logfileSaveOutMissingFams="%projectSaveMissingFamsDirectory%\%USERNAME%_SaveOutMissingFamilies_%ldt%.log"
:: path to flow saving out missing families
set saveOutMissingFamiliesScript="%_rootFolderPath%_00_X_SavingMissingFamilies\_Script\SaveOut.2022.FamilyData.ALL.generic.bat"
:: save missing families marker file data
:: the actual marker file name
set saveOutMissingFamiliesFileName="%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_Input\SaveOutMissingFams.csv"
:: location of current family base data report file (any family not in there is regarded as a missing family)
set saveOutRowOne=%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\FamilyBaseDataCombinedReport.csv
:: location of where to save missing families to
set saveOutRowTwo=%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_FamilyOut
:: in case of very long file names use this path
REM set saveOutRowTwo=C:\Users\%USERNAME%\Documents\Temp\FamOut
:: location containing savd family report file
REM set saveOutMissingFamiliesReport="%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_Output\SecondProcessFamilies.csv"
:: from where to copy the host missing families report
set missingFamiliesHostReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\HostsMissingFamilies.csv"
:: where to copy the host missing families report to:
set missingFamiliesHostTarget="%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_Input"


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values save missing families *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo projectSaveMissingFamsDirectory: %projectSaveMissingFamsDirectory%
    %stamp% & echo logfileSaveOutMissingFams : %logfileSaveOutMissingFams%
    %stamp% & echo saveOutMissingFamiliesScript: %saveOutMissingFamiliesScript%
    %stamp% & echo saveOutMissingFamiliesFileName: %saveOutMissingFamiliesFileName%
    %stamp% & echo saveOutRowOne: %saveOutRowOne%
    %stamp% & echo saveOutRowTwo: %saveOutRowTwo%
    REM %stamp% & echo saveOutMissingFamiliesReport: %saveOutMissingFamiliesReport%
    %stamp% & echo missingFamiliesHostReportSource: %missingFamiliesHostReportSource%
    %stamp% & echo missingFamiliesHostTarget: %missingFamiliesHostTarget%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
   
)

%stamp% & echo.
%stamp% & echo ******************** Reporting Family Data - writing out missing families ****************
%stamp% & echo.
%stamp% & echo copy missing families host report:
%stamp% & echo copy from: %missingFamiliesHostReportSource%
%stamp% & echo copy to: %missingFamiliesHostTarget%
%stamp% & copy %missingFamiliesHostReportSource% %missingFamiliesHostTarget%
%stamp% & echo logging to: %logfileSaveOutMissingFams%

%stamp% & echo writing marker file...
echo %saveOutRowOne%> %saveOutMissingFamiliesFileName%
echo %saveOutRowTwo%>> %saveOutMissingFamiliesFileName%
REM call reporting family data
call %saveOutMissingFamiliesScript% >> %logfileSaveOutMissingFams%

:outOfHere
REM get out before executing the time stamp code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "