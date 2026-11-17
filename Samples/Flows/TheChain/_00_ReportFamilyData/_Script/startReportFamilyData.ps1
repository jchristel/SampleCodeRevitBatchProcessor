<#
.SYNOPSIS
Reports family data (flow _00_ReportFamilyData).

.DESCRIPTION
- selects the families to report on and writes the task lists
- runs the report in Revit Batch Processor sessions
- combines and analyses the reports (Post_FamilyData.py)

.PARAMETER FilesLocation
Follow up report: a folder containing SecondProcessFamilies.csv, a list of the families to report on (one family file path per line).
Without it, all families in REVIT_LIBRARY_PATH (settings.py) are reported on.

.PARAMETER UIDirectory
Select the families in a window, from the families in this folder.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).

.EXAMPLE
powershell -ExecutionPolicy Bypass -File startReportFamilyData.ps1
powershell -ExecutionPolicy Bypass -File startReportFamilyData.ps1 -UIDirectory "C:\family library"
#>
param (
    [string]$FilesLocation = "",
    [string]$UIDirectory = "",
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "FamilyReport" -Action {
    Write-ToLogAndConsole -Message "File selection" -IsHeader $True
    if ($UIDirectory) {
        $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectUI.py") -Arguments @($UIDirectory)
    }
    elseif ($FilesLocation) {
        $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py") -Arguments @($FilesLocation)
    }
    else {
        $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py")
    }
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families selected (file selection exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "Reporting families" -IsHeader $True
    Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.FamilyCategoriesOne{0}.ALL.Settings.json" -StartIntervalSeconds 180

    Write-ToLogAndConsole -Message "Combining and analysing reports" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_FamilyData.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
