<#
.SYNOPSIS
Renames families, and the nested families in them (flow _01_X_RenameFamilies).

.DESCRIPTION
- renames family files as per the rename directives in _Input (Pre_ModifyLibraryRenameFamilyFiles.py)
- selects the families to process and writes the task lists
- renames nested families in Revit Batch Processor sessions
- copies the changed families back and writes the changed families list _Output\ChangedFilesTaskList.csv (Post_ModifyLibraryFamily.py)

theChain.ps1 copies the rename directives (_Analysis\actionNow\*.csv) and the family base data report into _Input before running this.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).
#>
param (
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "RenameFamilies" -Action {
    $input_directory = Join-Path (Get-ChainUserDirectory -FlowDirectory $flow_directory) "_Input"

    Write-ToLogAndConsole -Message "Renaming family files" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_ModifyLibraryRenameFamilyFiles.py") -Arguments @($input_directory)
    if ($code -ne 0) {
        # the exit code covers all renames: carry on with the host families of the renames that worked
        Write-ToLogAndConsole -Message "Not all family files were renamed (exit code: $code), see the messages above. Carrying on."
    }

    Write-ToLogAndConsole -Message "File selection" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py") -Arguments @($input_directory)
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families selected (file selection exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "Renaming nested families" -IsHeader $True
    Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.ModifyFamiliesOne{0}.ALL.Settings.json" -StartIntervalSeconds 120

    Write-ToLogAndConsole -Message "Post processing" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_ModifyLibraryFamily.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
