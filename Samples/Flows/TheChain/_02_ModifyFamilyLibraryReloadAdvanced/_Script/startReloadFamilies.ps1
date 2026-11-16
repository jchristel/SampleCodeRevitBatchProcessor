<#
.SYNOPSIS
Reloads changed families into their host families (flow _02_ModifyFamilyLibraryReloadAdvanced).

.DESCRIPTION
- builds one overall task list per nesting level from the changed families list _Input\ChangedFilesTaskList.csv
  and the family base data report in _Input (Pre_TaskFileReloadListBuilder.py), into _TaskList\OverAll
- for each overall task list, in order:
    - splits it into the session task lists (Pre_TaskFileListBuilder.py)
    - reloads the families in Revit Batch Processor sessions
    - copies the changed families back (Post_ModifyLibraryFamilyReload.py)
- writes the list of all families changed by the reload, _Output\ChangedFilesTaskList.csv (Post_Everything.py)

theChain.ps1 puts ChangedFilesTaskList.csv and the family base data report into _Input before running this.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).
#>
param (
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "FamilyReload" -Action {
    $user_directory = Get-ChainUserDirectory -FlowDirectory $flow_directory
    $change_list = Join-Path $user_directory "_Input\ChangedFilesTaskList.csv"
    $overall_directory = Join-Path $user_directory "_TaskList\OverAll"

    Write-ToLogAndConsole -Message "Building overall task lists" -IsHeader $True
    if (-not (Test-Path $change_list -PathType Leaf)) {
        Write-ToLogAndConsole -Message "No changed families list: $change_list"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }
    # overall task lists left over from a run that stopped part way
    Remove-ChainFile -Path @(Get-ChildItem -Path $overall_directory -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_TaskFileReloadListBuilder.py") -Arguments @($change_list)
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "Failed to build the overall task lists (exit code: $code)"
        return $CHAIN_EXIT_FAILED
    }

    # one overall task list per nesting level, processed in name order
    $overall_task_lists = @(Get-ChildItem -Path $overall_directory -Filter "*.txt" -File -ErrorAction SilentlyContinue | Sort-Object Name)
    Write-ToLogAndConsole -Message "Overall task lists: $($overall_task_lists.Count)"
    if ($overall_task_lists.Count -eq 0) {
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    $counter = 0
    foreach ($overall_task_list in $overall_task_lists) {
        $counter++
        Write-ToLogAndConsole -Message "Reloading families $counter of $($overall_task_lists.Count): $($overall_task_list.Name)" -IsHeader $True
        $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_TaskFileListBuilder.py") -Arguments @($overall_directory, $overall_task_list.Name)
        if ($code -eq $CHAIN_EXIT_NOTHING_TO_PROCESS) {
            Write-ToLogAndConsole -Message "No families in: $($overall_task_list.Name), skipping it."
            continue
        }
        if ($code -ne 0) {
            Write-ToLogAndConsole -Message "Failed to split: $($overall_task_list.Name) (exit code: $code)"
            return $CHAIN_EXIT_FAILED
        }

        Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.ModifyReloadFamiliesOne{0}.ALL.Settings.json" -StartIntervalSeconds 120

        $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_ModifyLibraryFamilyReload.py")
        if ($code -ne 0) {
            return $CHAIN_EXIT_FAILED
        }
    }

    # the overall task lists are done with
    Remove-Item -Path (Join-Path $overall_directory "*") -Force

    Write-ToLogAndConsole -Message "Writing the changed families list" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_Everything.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
