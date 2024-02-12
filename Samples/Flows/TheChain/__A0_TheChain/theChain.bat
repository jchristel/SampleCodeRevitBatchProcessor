@echo off
setlocal EnableDelayedExpansion
set "stamp=call :stamp"

:: get the local date
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%

%stamp% & echo Local date is [%ldt%]


:: script root location...amend to suite
:: use current script directories parent folder...
FOR %%A IN ("%~dp0.") DO set "_rootFolderPath=%%~dpA"

:: ---------------------- modules -------------------------------

set moduleReporting="%_rootFolderPath%__A0_TheChain\theChainModuleReporting.bat"
set moduleSavingMissingFams="%_rootFolderPath%__A0_TheChain\theChainModuleSavingMissingFams.bat"
set moduleModifyDefault="%_rootFolderPath%__A0_TheChain\theChainModuleModifyDefault.bat"
set moduleModifyRenameFamilies="%_rootFolderPath%__A0_TheChain\theChainModuleModifyRenameFams.bat"
set moduleModifyRenameFamilySubCategories="%_rootFolderPath%__A0_TheChain\theChainModuleRenameSubCategories.bat"
set moduleModifyChangeFamilyCategory="%_rootFolderPath%__A0_TheChain\theChainModuleChangeFamilyCategory.bat"
set moduleModifyReloadFamilies="%_rootFolderPath%__A0_TheChain\theChainModuleReload.bat"

:: -------- \Input locations containing changed family report files --------

:: merge reports: file path to file listing specific families to be reported on only
set mergeReportsSpecificFamiliesReportTarget="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Input\SecondProcessFamilies.csv"
:: reload families
set reloadSpecificFamiliesReportTarget="%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Users\%USERNAME%\_Input\ChangedFilesTaskList.csv"

:: -------- \Output locations containing saved family report files --------

:: saved out families
set saveOutMissingFamiliesReport="%_rootFolderPath%_00_X_SavingMissingFamilies\_Users\%USERNAME%\_Output\SecondProcessFamilies.csv"
:: renamed families
set familyRenameChangedfamilyReport="%_rootFolderPath%_01_X_RenameFamilies\_Users\%USERNAME%\_Output\ChangedFilesTaskList.csv"

:: renamed subcategories families - reload report
set renameSubCatsFamilyReport="%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Users\%USERNAME%\_Output\ChangedFilesTaskList.csv"
:: renamed subcategories families - follow up report
set renameSubCatsFamilyFollowUpReport="%_rootFolderPath%_01_Z_ChangeFamilySubCategory\_Users\%USERNAME%\_Output\FollowUpReportList.csv"

:: changed categories families - reload report
set changeFamilyCatsReport="%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Users\%USERNAME%\_Output\ChangedFilesTaskList.csv"
:: changed categories families - follow up report
set changeFamilyCategoriesFollowUpReport="%_rootFolderPath%_01_Y_ChangeFamilyCategory\_Users\%USERNAME%\_Output\FollowUpReportList.csv"

:: modify default families
set familyModifyDefaultChangedFamilyReport="%_rootFolderPath%_01_ModifyFamilyChange\_Users\%USERNAME%\_Output\ChangedFilesTaskList.csv"
:: merge reports: process exceptions report location
set mergeReportsProcessExceptionsReportSource="%_rootFolderPath%_00_ReportFamilyData\_Users\%USERNAME%\_Analysis\_Current\SecondProcessFamilies.csv"
:: reload families changes
set familyReloadChangedFamilyReport="%_rootFolderPath%_02_ModifyFamilyLibraryReloadAdvanced\_Users\%USERNAME%\_Output\ChangedFilesTaskList.csv"

:: --------------------------------batch action toggles..........................................

:: these toggles drive which process is run
:: a value of 1 :yes run action, 0 do not run action
:: might try to populate those via a UI ???

:: toggle to run initial report
set initialReport=0
:: toggle to run follow up report
set followUpReport=0
:: toggle write out missing families
set writeOutMissingFamilies=0

:: overall modify family toggle
set modifyFamilyDefault=1

:: rename families 
set renameFamilies=0

:: rename sub categories
set renameSubCategories=0

:: change family categories
set changeFamilyCategories=0

:: reload any changed families
set reloadFamilies=0
:: will do a full report after a reload
set reportFullAfterReload=0

:: debug toggle
set toggleDebug=1

:: end toggles ...........................................................................................


if %toggleDebug%==1 (
    %stamp% & echo ********************************* DEBUG: variable values *****************************************************
    %stamp% & echo.
    %stamp% & echo _rootFolderPath: %_rootFolderPath%
    %stamp% & echo Modules:
    %stamp% & echo moduleReporting: %moduleReporting%
    %stamp% & echo moduleSavingMissingFams: %moduleSavingMissingFams%
    %stamp% & echo moduleModifyDefault: %moduleModifyDefault%
    %stamp% & echo moduleModifyRenameFamilies: %moduleModifyRenameFamilies%
    %stamp% & echo moduleModifyReloadFamilies: %moduleModifyReloadFamilies%
    %stamp% & echo.
    %stamp% & echo Inputs:
    %stamp% & echo mergeReportsSpecificFamiliesReportTarget: %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo reloadSpecificFamiliesReportTarget: %reloadSpecificFamiliesReportTarget%
    %stamp% & echo.
    %stamp% & echo Outputs:
    %stamp% & echo mergeReportsProcessExceptionsReportSource: %mergeReportsProcessExceptionsReportSource%
    %stamp% & echo saveOutMissingFamiliesReport: %saveOutMissingFamiliesReport%
    %stamp% & echo familyRenameChangedfamilyReport: %familyRenameChangedfamilyReport%
    %stamp% & echo familyModifyDefaultChangedFamilyReport: %familyModifyDefaultChangedFamilyReport%
    %stamp% & echo changeFamilyCatsReport: %changeFamilyCatsReport%
    %stamp% & echo changeFamilyCategoriesFollowUpReport: %changeFamilyCategoriesFollowUpReport%
    %stamp% & echo renameSubCatsFamilyReport: %renameSubCatsFamilyReport%
    %stamp% & echo renameSubCatsFamilyFollowUpReport: %renameSubCatsFamilyFollowUpReport%
    %stamp% & echo.
    %stamp% & echo ********************************* DEBUG END *****************************************************
)

:: check if initial report is required
if %initialReport%==1 (
    REM call initial reporting family data (arg = 0)
    call %moduleReporting% 0 %toggleDebug%
) else (
    %stamp% & echo.
    %stamp% & echo Skipping initial report
    %stamp% & echo.
)

:: check if follow up report is required
if %followUpReport%==1 (
    %stamp% & echo.
    %stamp% & echo copy process exceptions report to specific families processing list:
    %stamp% & copy %mergeReportsProcessExceptionsReportSource% %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo.
    REM call follow up reporting family data (arg = 1)
    call %moduleReporting% 1 %toggleDebug%
) else (
    %stamp% & echo.
    %stamp% & echo Skipping follow up report
    %stamp% & echo.
)

if %writeOutMissingFamilies%==1 (
    REM call saving missing fams (no args)
    call %moduleSavingMissingFams% %toggleDebug%
    
    :: reporting...should be done when familiesa are moved into final location (not in WIP...)
    REM %stamp% & echo.
    REM %stamp% & echo copy saved out families report to specific families processing list:
    REM %stamp% & echo copy from: %saveOutMissingFamiliesReport%
    REM %stamp% & echo copy to: %mergeReportsSpecificFamiliesReportTarget%
    REM %stamp% & copy %saveOutMissingFamiliesReport% %mergeReportsSpecificFamiliesReportTarget%
    REM %stamp% & echo.
    REM call follow up reporting family data (arg = 1)
    REM call %moduleReporting% 1 %toggleDebug%
) else (
    %stamp% & echo.
    %stamp% & echo Skipping writing out missing families
    %stamp% & echo.
)

if %modifyFamilyDefault%==1 (
    REM call modify default (no args)
    call %moduleModifyDefault% %toggleDebug%
    
    REM NOTE: this action should be followed up by a reload, which will update nested families as well as run a report!
    REM copy change list to report and reload \Input
    %stamp% & echo.
    %stamp% & echo copy changed families report to specific families processing list locations:
    %stamp% & echo Follow up report:
    %stamp% & copy %familyModifyDefaultChangedFamilyReport% %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo Reload families:
    %stamp% & copy %familyModifyDefaultChangedFamilyReport% %reloadSpecificFamiliesReportTarget%
    %stamp% & echo.

) else (
    %stamp% & echo.
    %stamp% & echo Skipping modifying families - default actions
    %stamp% & echo.
)

if %renameFamilies%==1 (
    REM call rename families (no args)
    call %moduleModifyRenameFamilies% %toggleDebug%
    
    REM NOTE: this action should be followed up by a reload!! Which will update nested families as well as run a report!
    REM copy change list to report and reload in

    :: follow up report is required in order to build reload tree with the correct family names!
    %stamp% & echo.
    %stamp% & echo copy changed families report to specific families processing list locations:
    %stamp% & echo Follow up report:
    %stamp% & copy %familyRenameChangedfamilyReport% %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo Reload families:
    %stamp% & copy %familyRenameChangedfamilyReport% %reloadSpecificFamiliesReportTarget%
    REM call follow up reporting family data (arg = 1)
    call %moduleReporting% 1 %toggleDebug%
    
) else (
    %stamp% & echo.
    %stamp% & echo Skipping modify rename families
    %stamp% & echo.
)


if %changeFamilyCategories%==1 (
    REM call change family categories (no args)
    call %moduleModifyChangeFamilyCategory% %toggleDebug%
    
    REM NOTE: this action should be followed up by a reload!! Which will update nested families as well as run a report!
    REM copy change list to report and reload in

    :: follow up report is required in order to build reload tree with the correct family names!
    %stamp% & echo.
    %stamp% & echo copy changed families report to specific families processing list locations:
    %stamp% & echo Follow up report:
    %stamp% & copy %changeFamilyCategoriesFollowUpReport% %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo Reload families:
    %stamp% & copy %changeFamilyCatsReport% %reloadSpecificFamiliesReportTarget%
    REM call follow up reporting family data (arg = 1)
    call %moduleReporting% 1 %toggleDebug%
    
) else (
    %stamp% & echo.
    %stamp% & echo Skipping modify change family category
    %stamp% & echo.
)

if %renameSubCategories%==1 (
    REM call rename sub categories (no args)
    call %moduleModifyRenameFamilySubCategories% %toggleDebug%
    
    REM NOTE: this action should be followed up by a reload!! Which will update nested families as well as run a report!
    REM copy change list to report and reload in

    :: follow up report is required in order to build reload tree with the correct family names!
    %stamp% & echo.
    %stamp% & echo copy changed families report to specific families processing list locations:
    %stamp% & echo Follow up report:
    %stamp% & copy %renameSubCatsFamilyFollowUpReport% %mergeReportsSpecificFamiliesReportTarget%
    %stamp% & echo Reload families:
    %stamp% & copy %renameSubCatsFamilyReport% %reloadSpecificFamiliesReportTarget%
    REM call follow up reporting family data (arg = 1)
    call %moduleReporting% 1 %toggleDebug%
    
) else (
    %stamp% & echo.
    %stamp% & echo Skipping modify change family subcategories
    %stamp% & echo.
)

if %reloadFamilies%==1 (
    REM call modify reload (no args)
    call %moduleModifyReloadFamilies% %toggleDebug%

    REM copy changed files report
    %stamp% & echo copy changed families report to specific families processing list locations
    %stamp% & echo Follow up report:
    %stamp% & copy %familyReloadChangedFamilyReport% %mergeReportsSpecificFamiliesReportTarget%
    
    :: check if a report is required
    if %reportFullAfterReload%==1 (
        REM call initial reporting family data (arg = 0)
        call %moduleReporting% 0 %toggleDebug%

        REM copy files required
        %stamp% & echo.
        %stamp% & echo copy process exceptions report to specific families processing list:
        %stamp% & copy %mergeReportsProcessExceptionsReportSource% %mergeReportsSpecificFamiliesReportTarget%
        %stamp% & echo.
        REM call follow up reporting family data (arg = 1)
        call %moduleReporting% 1 %toggleDebug%
    ) else (
        REM do at least a partial report...
        %stamp% & echo.
        %stamp% & echo Skipping full report after reloading families, doing partial report instead.
        %stamp% & echo.
        REM call follow up reporting family data (arg = 1)
        call %moduleReporting% 1 %toggleDebug%
    )
    
) else (
    %stamp% & echo.
    %stamp% & echo Skipping reloading families
    %stamp% & echo.
)

:outOfHere
pause

REM get out before executing the spinner code below
exit /b

REM time stamp code
:stamp
set "t=%time: =0%"
<nul set /p "=%t:~0,-3%: "