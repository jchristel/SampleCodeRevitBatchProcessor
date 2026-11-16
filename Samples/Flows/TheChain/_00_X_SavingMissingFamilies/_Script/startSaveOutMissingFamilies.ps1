<#
.SYNOPSIS
Saves out families missing from the library (flow _00_X_SavingMissingFamilies).

.DESCRIPTION
- selects the host families of missing families (_Input\HostsMissingFamilies.csv) and writes the task lists
- saves the missing families out of their hosts in Revit Batch Processor sessions, into _FamilyOut
- copies the saved families from _FamilyOut into _Output\combined
- writes the saved families report (Post_SaveOutMissingData.py)

theChain.ps1 puts HostsMissingFamilies.csv and the SaveOutMissingFams.csv marker file into _Input before running this.

.PARAMETER NoPause
Do not wait for Enter at the end (used by theChain.ps1).
#>
param (
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "..\..\__A0_TheChain\TheChainCommon.ps1")

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

$exit_code = Invoke-ChainFlow -FlowDirectory $flow_directory -Name "SaveOutMissingFamilies" -Action {
    $user_directory = Get-ChainUserDirectory -FlowDirectory $flow_directory

    Write-ToLogAndConsole -Message "File selection" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Pre_FileSelectNoUI.py")
    if ($code -ne 0) {
        Write-ToLogAndConsole -Message "No families selected (file selection exit code: $code)"
        return $CHAIN_EXIT_NOTHING_TO_PROCESS
    }

    Write-ToLogAndConsole -Message "Saving out missing families" -IsHeader $True
    Start-ChainSessions -FlowDirectory $flow_directory -SettingsFileNamePattern "BatchRvt.2022.SaveOutOne{0}.ALL.Settings.json" -StartIntervalSeconds 180

    Write-ToLogAndConsole -Message "Combining saved families" -IsHeader $True
    $family_out_directory = Join-Path $user_directory "_FamilyOut"
    $combined_directory = Join-Path $user_directory "_Output\combined"
    if (!(Test-Path $combined_directory)) {
        New-Item -ItemType Directory -Path $combined_directory | Out-Null
    }
    foreach ($session_directory in (Get-ChildItem -Path $family_out_directory -Directory -ErrorAction SilentlyContinue)) {
        Copy-Item -Path (Join-Path $session_directory.FullName "*") -Destination $combined_directory -Recurse -Force
        if ($?) {
            Remove-Item -LiteralPath $session_directory.FullName -Recurse -Force
            Write-ToLogAndConsole -Message "Moved saved families from: $($session_directory.FullName)"
        }
        else {
            Write-ToLogAndConsole -Message "Failed to copy saved families from: $($session_directory.FullName)"
            return $CHAIN_EXIT_FAILED
        }
    }

    Write-ToLogAndConsole -Message "Post processing" -IsHeader $True
    $code = Invoke-ChainPython -Script (Join-Path $script_directory "Post_SaveOutMissingData.py")
    if ($code -ne 0) {
        return $CHAIN_EXIT_FAILED
    }
    return $CHAIN_EXIT_DONE
}

Complete-ChainScript -ExitCode $exit_code -NoPause:$NoPause
