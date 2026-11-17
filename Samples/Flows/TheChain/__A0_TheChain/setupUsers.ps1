<#
.SYNOPSIS
Sets up the current user's folder in every flow of The Chain.

.DESCRIPTION
For each flow (folders next to __A0_TheChain containing _Users\_default):
- copies _Users\_default to _Users\<user name>, unless the user folder exists already
- points the paths in the user's Revit Batch Processor settings files (_Settings\*.json) at the flow's actual location
  and the user's folder, wherever The Chain is located

The flows do not run without the user folder.

.PARAMETER RefreshSettings
Also updates the settings files of user folders that exist already, e.g. after The Chain was moved or copied to another location.
The user's other files are left as they are.

.PARAMETER NoPause
Do not wait for Enter at the end.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File setupUsers.ps1
powershell -ExecutionPolicy Bypass -File setupUsers.ps1 -RefreshSettings
#>
param (
    [switch]$RefreshSettings,
    [switch]$NoPause
)

. (Join-Path $PSScriptRoot "TheChainCommon.ps1")
Set-LogFile -Path (Join-Path $chain_tools_directory ("logs\{0}_setupUsers_{1}.log" -f $env:USERNAME, (Get-Date -Format "yyyy-MM-dd"))) | Out-Null

Write-ToLogAndConsole -Message "Setting up user folders" -IsHeader $True
Write-ToLogAndConsole -Message "user: $env:USERNAME"
Write-ToLogAndConsole -Message "The Chain directory: $chain_root"

$exit_code = $CHAIN_EXIT_DONE
$flow_directories = Get-ChildItem -Path $chain_root -Directory | Where-Object { Test-Path (Join-Path $_.FullName "_Users\_default") -PathType Container }

foreach ($flow in $flow_directories) {
    Write-ToLogAndConsole -Message "-"
    Write-ToLogAndConsole -Message "Flow: $($flow.Name)"
    $default_directory = Join-Path $flow.FullName "_Users\_default"
    $user_directory = Get-ChainUserDirectory -FlowDirectory $flow.FullName

    if (Test-Path $user_directory -PathType Container) {
        Write-ToLogAndConsole -Message "User folder exists already: $user_directory"
        if (-not $RefreshSettings) {
            continue
        }
    }
    else {
        Copy-Item -Path $default_directory -Destination $user_directory -Recurse
        if (-not $?) {
            Write-ToLogAndConsole -Message "Failed to copy: $default_directory to: $user_directory"
            $exit_code = $CHAIN_EXIT_FAILED
            continue
        }
        Write-ToLogAndConsole -Message "Created user folder: $user_directory"
    }

    $settings_files = Get-ChildItem -Path (Join-Path $user_directory "_Settings") -Filter "*.json" -File -ErrorAction SilentlyContinue
    foreach ($settings_file in $settings_files) {
        try {
            Update-ChainSettingsFile -Path $settings_file.FullName -FlowDirectory $flow.FullName -UserName $env:USERNAME
            Write-ToLogAndConsole -Message "Updated settings file: $($settings_file.Name)"
        }
        catch {
            Write-ToLogAndConsole -Message "Failed to update settings file: $($settings_file.FullName): $_"
            $exit_code = $CHAIN_EXIT_FAILED
        }
    }
}

Write-ToLogAndConsole -Message "end of script" -IsHeader $True
if (-not $NoPause) {
    Read-Host "Press Enter to exit."
}
exit $exit_code
