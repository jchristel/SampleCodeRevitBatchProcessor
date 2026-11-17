<#
.SYNOPSIS
Modifies families with the default set of actions (flow _01_ModifyFamilyChange).

.DESCRIPTION
- selects the families to modify and writes the task lists: the families in any .task files in _TaskList, otherwise all
  families in REVIT_LIBRARY_PATH (settings.py)
- modifies the families in Revit Batch Processor sessions
- copies the changed families back and writes the changed families list _Output\ChangedFilesTaskList.csv (Post_ModifyLibraryFamily.py)

theChain.ps1 copies any .task files from _Input into _TaskList before running this.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).
#>
param (
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "FamilyModifyDefault" -Action {
    Write-ToLogAndConsole -Message "File selection" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py")
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families selected (file selection exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "Modifying families" -IsHeader $True
    Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.ModifyFamiliesDefaultOne{0}.ALL.Settings.json" -StartIntervalSeconds 120

    Write-ToLogAndConsole -Message "Post processing" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_ModifyLibraryFamily.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
