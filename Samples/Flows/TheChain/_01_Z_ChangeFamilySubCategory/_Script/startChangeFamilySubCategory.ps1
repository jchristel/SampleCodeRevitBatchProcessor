<#
.SYNOPSIS
Renames sub categories in families (flow _01_Z_ChangeFamilySubCategory).

.DESCRIPTION
- builds the list of families to change from the sub category change directives in _Input (Pre_TaskFileListBuilder.py)
- selects those families and writes the task lists
- renames the sub categories in Revit Batch Processor sessions
- copies the changed families back and writes the changed families list _Output\ChangedFilesTaskList.csv (Post_ChangeFamilySubCategory.py)

theChain.ps1 copies the family categories report into _Input before running this.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).
#>
param (
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "ChangeFamilySubCategory" -Action {
    Write-ToLogAndConsole -Message "Building the list of families to change" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_TaskFileListBuilder.py")
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families to change (exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "File selection" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py")
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families selected (file selection exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "Renaming sub categories" -IsHeader $True
    Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.ModifyChangeFamilySubCategoryOne{0}.ALL.Settings.json" -StartIntervalSeconds 120

    Write-ToLogAndConsole -Message "Post processing" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_ChangeFamilySubCategory.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
