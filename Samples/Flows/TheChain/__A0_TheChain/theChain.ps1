<#
.SYNOPSIS
Runs the flows of The Chain in order, passing each flow's results on to the next.

.DESCRIPTION
Runs the flows switched on, in this order:

 1. InitialReport           report on all families in the library
 2. FollowUpReport          report again on the families the last report could not process (SecondProcessFamilies.csv)
 3. SaveMissingFamilies     save families missing from the library out of their host families
 4. ModifyDefault           modify families with the default set of actions
 5. RenameFamilies          rename families and the nested families in them, then a follow up report
 6. ChangeFamilyCategories  change family categories, then a follow up report
 7. RenameSubCategories     rename sub categories, then a follow up report
 8. ReloadFamilies          reload the changed families into their host families, then a follow up report
                            (or with FullReportAfterReload: a full report and a follow up report)

The changed families of steps 4 to 7 are combined into one list for the reload. If none of them ran, the reload uses
the changed families list already in its _Input folder.

If a flow fails, The Chain stops: the flows after it would work on incomplete data.
A flow with nothing to process (e.g. no change directives) is skipped and The Chain carries on.

Run setupUsers.ps1 once before the first run. Each flow logs to <flow>\_Users\<user>\_Output, The Chain to __A0_TheChain\logs.

.PARAMETER FullReportAfterReload
With ReloadFamilies: run a full report after the reload instead of a follow up report on the reloaded families only.

.PARAMETER NoPause
Do not wait for Enter at the end.

.EXAMPLE
# initial report only (also what runs without any switch)
powershell -ExecutionPolicy Bypass -File theChain.ps1 -InitialReport

# rename families, change categories, and reload everything that changed
powershell -ExecutionPolicy Bypass -File theChain.ps1 -RenameFamilies -ChangeFamilyCategories -ReloadFamilies
#>
param (
    [switch]$InitialReport,
    [switch]$FollowUpReport,
    [switch]$SaveMissingFamilies,
    [switch]$ModifyDefault,
    [switch]$RenameFamilies,
    [switch]$ChangeFamilyCategories,
    [switch]$RenameSubCategories,
    [switch]$ReloadFamilies,
    [switch]$FullReportAfterReload,
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "TheChainCommon.ps1")
Set-LogFile -Path (Join-Path $chain_tools_directory ("logs\{0}_TheChain_{1}.log" -f $env:USERNAME, (Get-Date -Format "yyyy-MM-dd"))) | Out-Null

# ---------------------------------------- flows and their files ----------------------------------------

$report_directory = Get-ChainFlowDirectory -Flow "_00_ReportFamilyData"
$save_out_directory = Get-ChainFlowDirectory -Flow "_00_X_SavingMissingFamilies"
$modify_default_directory = Get-ChainFlowDirectory -Flow "_01_ModifyFamilyChange"
$rename_directory = Get-ChainFlowDirectory -Flow "_01_X_RenameFamilies"
$change_category_directory = Get-ChainFlowDirectory -Flow "_01_Y_ChangeFamilyCategory"
$change_sub_category_directory = Get-ChainFlowDirectory -Flow "_01_Z_ChangeFamilySubCategory"
$reload_directory = Get-ChainFlowDirectory -Flow "_02_ModifyFamilyLibraryReloadAdvanced"

$report_user_directory = Get-ChainUserDirectory -FlowDirectory $report_directory
$report_input = Join-Path $report_user_directory "_Input"
$report_analysis_current = Join-Path $report_user_directory "_Analysis\_Current"
# report data the other flows use
$base_data_report = Join-Path $report_analysis_current "FamilyBaseDataCombinedReport.csv"
$categories_report = Join-Path $report_analysis_current "FamilyCategoriesCombinedReport.csv"
$second_process_families_report = Join-Path $report_analysis_current "SecondProcessFamilies.csv"
$hosts_missing_families_report = Join-Path $report_analysis_current "HostsMissingFamilies.csv"

# changed families lists of the modify flows run in this run of The Chain
$changed_lists = New-Object System.Collections.Generic.List[string]

# ---------------------------------------- steps ----------------------------------------

<#
.SYNOPSIS
Runs a flow start script and returns its exit code. Stops The Chain if the flow failed.
#>
function Invoke-ChainStep {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$ScriptName,
        [hashtable]$Arguments = @{}
    )
    $script = Join-Path $FlowDirectory (Join-Path "_Script" $ScriptName)
    Write-ToLogAndConsole -Message "Starting: $script"
    # the flow's output goes to the console, so only the exit code is returned
    & $script @Arguments -NoPause | Out-Host
    $code = $LASTEXITCODE
    Write-ToLogAndConsole -Message "$ScriptName finished with exit code: $code"
    if ($code -eq $CHAIN_EXIT_NOTHING_TO_PROCESS) {
        Write-ToLogAndConsole -Message "Nothing to process in: $ScriptName"
    }
    elseif ($code -ne $CHAIN_EXIT_DONE) {
        Write-ToLogAndConsole -Message "$ScriptName failed. Stopping The Chain: the flows after it would work on incomplete data."
        Write-ToLogAndConsole -Message "The Chain stopped" -IsHeader $True
        Complete-ChainScript -ExitCode $CHAIN_EXIT_FAILED -NoPause:$NoPause
    }
    return $code
}

<#
.SYNOPSIS
Reports on all families in the library.
#>
function Invoke-FullReport {
    Write-ToLogAndConsole -Message "Report" -IsHeader $True
    Invoke-ChainStep -FlowDirectory $report_directory -ScriptName "startReportFamilyData.ps1" | Out-Null
}

<#
.SYNOPSIS
Reports on the families in the given lists only, and merges the results into the current reports.
Skipped if the lists have no families in them.
#>
function Invoke-FollowUpReport {
    param (
        [string[]]$Sources = @()
    )
    Write-ToLogAndConsole -Message "Follow up report" -IsHeader $True
    $count = Write-ChainFollowUpList -Sources $Sources -Destination (Join-Path $report_input "SecondProcessFamilies.csv")
    if ($count -eq 0) {
        Write-ToLogAndConsole -Message "No families to report on: skipping the follow up report."
        return
    }
    # marker file: merge the follow up report with the reports in _Analysis\_Current
    Write-ChainTextFile -Path (Join-Path $report_input "MergeFamilyData.csv") -Lines @($report_analysis_current)
    Invoke-ChainStep -FlowDirectory $report_directory -ScriptName "startReportFamilyData.ps1" -Arguments @{ FilesLocation = $report_input } | Out-Null
}

<#
.SYNOPSIS
Runs a flow which changes families. Returns the flow's changed families list, or nothing if no families changed.

.PARAMETER Prepare
Copies the flow's input files into place before the flow runs.
#>
function Invoke-ChangeStep {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$ScriptName,
        [scriptblock]$Prepare = {}
    )
    Write-ToLogAndConsole -Message $Name -IsHeader $True
    $output_directory = Join-Path (Get-ChainUserDirectory -FlowDirectory $FlowDirectory) "_Output"
    $changed_list = Join-Path $output_directory "ChangedFilesTaskList.csv"
    # the changed families lists of a previous run must not be passed on as this run's
    Remove-ChainFile -Path @($changed_list, (Join-Path $output_directory "FollowUpReportList.csv"))
    & $Prepare
    $code = Invoke-ChainStep -FlowDirectory $FlowDirectory -ScriptName $ScriptName
    if ($code -eq $CHAIN_EXIT_DONE -and (Test-Path $changed_list -PathType Leaf)) {
        $changed_lists.Add($changed_list)
        return $changed_list
    }
    Write-ToLogAndConsole -Message "No changed families from: $Name"
}

# ---------------------------------------- run ----------------------------------------

$any_step = $InitialReport -or $FollowUpReport -or $SaveMissingFamilies -or $ModifyDefault -or $RenameFamilies -or $ChangeFamilyCategories -or $RenameSubCategories -or $ReloadFamilies
if (-not $any_step) {
    Write-ToLogAndConsole -Message "No flow switched on: running the initial report. See Get-Help .\theChain.ps1 for the other flows."
    $InitialReport = $true
}
if ($FullReportAfterReload -and -not $ReloadFamilies) {
    Write-ToLogAndConsole -Message "FullReportAfterReload is only used with ReloadFamilies: ignored."
}

Write-ToLogAndConsole -Message "The Chain" -IsHeader $True
Write-ToLogAndConsole -Message "user: $env:USERNAME"
Write-ToLogAndConsole -Message "The Chain directory: $chain_root"
foreach ($step_name in @("InitialReport", "FollowUpReport", "SaveMissingFamilies", "ModifyDefault", "RenameFamilies", "ChangeFamilyCategories", "RenameSubCategories", "ReloadFamilies", "FullReportAfterReload")) {
    Write-ToLogAndConsole -Message ("{0}: {1}" -f $step_name, [bool](Get-Variable -Name $step_name -ValueOnly))
}

if ($InitialReport) {
    Invoke-FullReport
}

if ($FollowUpReport) {
    Invoke-FollowUpReport -Sources @($second_process_families_report)
}

if ($SaveMissingFamilies) {
    Write-ToLogAndConsole -Message "Save out missing families" -IsHeader $True
    $save_out_input = Join-Path (Get-ChainUserDirectory -FlowDirectory $save_out_directory) "_Input"
    if (Copy-ChainFile -Source $hosts_missing_families_report -Destination $save_out_input) {
        # marker file: the family base data report to compare against, and where to save the missing families to
        Write-ChainTextFile -Path (Join-Path $save_out_input "SaveOutMissingFams.csv") -Lines @(
            $base_data_report,
            (Join-Path (Get-ChainUserDirectory -FlowDirectory $save_out_directory) "_FamilyOut")
        )
        Invoke-ChainStep -FlowDirectory $save_out_directory -ScriptName "startSaveOutMissingFamilies.ps1" | Out-Null
    }
    else {
        Write-ToLogAndConsole -Message "No hosts of missing families report from the last report: skipping saving out missing families."
    }
}

if ($ModifyDefault) {
    Invoke-ChangeStep -Name "Modify families - default actions" -FlowDirectory $modify_default_directory -ScriptName "startModifyFamiliesDefault.ps1" -Prepare {
        # any .task files listing specific families to modify, otherwise the entire library is modified
        $modify_user_directory = Get-ChainUserDirectory -FlowDirectory $modify_default_directory
        $task_files = @(Get-ChildItem -Path (Join-Path $modify_user_directory "_Input") -Filter "*.task" -File -ErrorAction SilentlyContinue)
        foreach ($task_file in $task_files) {
            Copy-ChainFile -Source $task_file.FullName -Destination (Join-Path $modify_user_directory "_TaskList") | Out-Null
        }
        if ($task_files.Count -eq 0) {
            Write-ToLogAndConsole -Message "No .task files in _Input: modifying the entire library."
        }
    } | Out-Null
}

if ($RenameFamilies) {
    $changed = Invoke-ChangeStep -Name "Rename families" -FlowDirectory $rename_directory -ScriptName "startRenameFamilies.ps1" -Prepare {
        $rename_user_directory = Get-ChainUserDirectory -FlowDirectory $rename_directory
        $rename_input = Join-Path $rename_user_directory "_Input"
        foreach ($directive in @(Get-ChildItem -Path (Join-Path $rename_user_directory "_Analysis\actionNow") -Filter "*.csv" -File -ErrorAction SilentlyContinue)) {
            Copy-ChainFile -Source $directive.FullName -Destination $rename_input | Out-Null
        }
        Copy-ChainFile -Source $base_data_report -Destination $rename_input | Out-Null
    }
    # the reload needs the report to know the families' new names
    if ($changed) {
        Invoke-FollowUpReport -Sources @($changed)
    }
}

if ($ChangeFamilyCategories) {
    $changed = Invoke-ChangeStep -Name "Change family categories" -FlowDirectory $change_category_directory -ScriptName "startChangeFamilyCategory.ps1" -Prepare {
        Copy-ChainFile -Source $categories_report -Destination (Join-Path (Get-ChainUserDirectory -FlowDirectory $change_category_directory) "_Input") | Out-Null
    }
    if ($changed) {
        Invoke-FollowUpReport -Sources @($changed)
    }
}

if ($RenameSubCategories) {
    $changed = Invoke-ChangeStep -Name "Rename sub categories" -FlowDirectory $change_sub_category_directory -ScriptName "startChangeFamilySubCategory.ps1" -Prepare {
        Copy-ChainFile -Source $categories_report -Destination (Join-Path (Get-ChainUserDirectory -FlowDirectory $change_sub_category_directory) "_Input") | Out-Null
    }
    if ($changed) {
        Invoke-FollowUpReport -Sources @($changed)
    }
}

if ($ReloadFamilies) {
    Write-ToLogAndConsole -Message "Reload families" -IsHeader $True
    $reload_user_directory = Get-ChainUserDirectory -FlowDirectory $reload_directory
    $reload_input = Join-Path $reload_user_directory "_Input"
    $reload_changed_list = Join-Path $reload_user_directory "_Output\ChangedFilesTaskList.csv"
    if ($changed_lists.Count -gt 0) {
        # every family changed in this run
        Write-ChainChangedList -Sources $changed_lists.ToArray() -Destination (Join-Path $reload_input "ChangedFilesTaskList.csv") | Out-Null
    }
    else {
        Write-ToLogAndConsole -Message "No families changed in this run: reloading the families in: $(Join-Path $reload_input 'ChangedFilesTaskList.csv')"
    }
    Copy-ChainFile -Source $base_data_report -Destination $reload_input | Out-Null
    Remove-ChainFile -Path @($reload_changed_list)
    $code = Invoke-ChainStep -FlowDirectory $reload_directory -ScriptName "startReloadFamilies.ps1"

    if ($FullReportAfterReload) {
        Invoke-FullReport
        Invoke-FollowUpReport -Sources @($second_process_families_report)
    }
    elseif ($code -eq $CHAIN_EXIT_DONE) {
        Invoke-FollowUpReport -Sources @($reload_changed_list)
    }
}

Write-ToLogAndConsole -Message "The Chain finished" -IsHeader $True
Complete-ChainScript -ExitCode $CHAIN_EXIT_DONE -NoPause:$NoPause
