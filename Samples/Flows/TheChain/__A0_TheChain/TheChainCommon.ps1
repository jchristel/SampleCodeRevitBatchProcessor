# Functions shared by theChain.ps1, setupUsers.ps1 and the start script of each flow.
# Loads TheChainSettings.ps1 and the shared PowerShell helpers (BatchProcessorUtils.ps1).
#
# Exit codes used by the flow start scripts:
#   0: done
#   1: failed
#   2: nothing to process (e.g. no families selected, no change directives)

# folder of The Chain (parent of __A0_TheChain) and of this script
$chain_tools_directory = $PSScriptRoot
$chain_root = Split-Path -Path $PSScriptRoot -Parent

. (Join-Path $PSScriptRoot "TheChainSettings.ps1")

if (-not (Test-Path $chain_utils_path -PathType Leaf)) {
    Write-Host "Shared PowerShell helpers not found at: $chain_utils_path"
    Write-Host "Set chain_utils_path in $(Join-Path $PSScriptRoot 'TheChainSettings.ps1')"
    throw "Shared PowerShell helpers not found at: $chain_utils_path"
}
. $chain_utils_path

$CHAIN_EXIT_DONE = 0
$CHAIN_EXIT_FAILED = 1
$CHAIN_EXIT_NOTHING_TO_PROCESS = 2

<#
.SYNOPSIS
Returns the fully qualified directory of a flow of The Chain, e.g. _00_ReportFamilyData.
#>
function Get-ChainFlowDirectory {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Flow
    )
    return Join-Path $chain_root $Flow
}

<#
.SYNOPSIS
Returns the current user's directory in a flow: <flow>\_Users\<user name>
#>
function Get-ChainUserDirectory {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory
    )
    return Join-Path (Join-Path $FlowDirectory "_Users") $env:USERNAME
}

<#
.SYNOPSIS
Checks the current user has a directory in the flow (set up by setupUsers.ps1).
#>
function Test-ChainUser {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory
    )
    $user_directory = Get-ChainUserDirectory -FlowDirectory $FlowDirectory
    if (Test-Path $user_directory -PathType Container) {
        Write-ToLogAndConsole -Message "User directory: $user_directory"
        return $true
    }
    Write-ToLogAndConsole -Message "User directory does not exist: $user_directory"
    Write-ToLogAndConsole -Message "Run $(Join-Path $chain_tools_directory 'setupUsers.ps1') first."
    return $false
}

<#
.SYNOPSIS
Switches logging to the flow's log file: <flow>\_Users\<user>\_Output\<user>_<Name>_<date>.log
Returns the previous log file path, to switch back with Set-LogFile.
#>
function Start-ChainFlowLog {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$Name
    )
    $output_directory = Join-Path (Get-ChainUserDirectory -FlowDirectory $FlowDirectory) "_Output"
    $log_file = Join-Path $output_directory ("{0}_{1}_{2}.log" -f $env:USERNAME, $Name, (Get-Date -Format "yyyy-MM-dd"))
    $previous = Set-LogFile -Path $log_file
    Write-ToLogAndConsole -Message "Logging to: $log_file"
    return $previous
}

<#
.SYNOPSIS
Quotes a command line argument for a python script if it contains spaces or quotes.
#>
function ConvertTo-ChainArgument {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Value
    )
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    $quoted = $Value -replace '"', '\"'
    # a trailing backslash would escape the closing quote
    if ($quoted.EndsWith('\')) {
        $quoted = $quoted + '\'
    }
    return '"' + $quoted + '"'
}

<#
.SYNOPSIS
Runs a python script with IronPython and returns its exit code.

.PARAMETER Script
The fully qualified file path of the python script.

.PARAMETER Arguments
Arguments passed to the script (quoted as required).
#>
function Invoke-ChainPython {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Script,
        [string[]]$Arguments = @()
    )
    $all_arguments = @(ConvertTo-ChainArgument -Value $Script)
    foreach ($argument in $Arguments) {
        $all_arguments += ConvertTo-ChainArgument -Value $argument
    }
    Write-ToLogAndConsole -Message "Running: $($all_arguments -join ' ')"
    $process = start-wrapper -path $iron_python_path -arguments $all_arguments
    $exit_code = $process.ExitCode
    if ($null -eq $exit_code) {
        Write-ToLogAndConsole -Message "Could not read the exit code of: $Script"
        return $CHAIN_EXIT_FAILED
    }
    Write-ToLogAndConsole -Message "Finished with exit code: $exit_code"
    return [int]$exit_code
}

<#
.SYNOPSIS
Starts one Revit Batch Processor session per settings file of the flow and waits for them to finish.

.PARAMETER FlowDirectory
The fully qualified directory of the flow.

.PARAMETER SettingsFileNamePattern
Settings file name with {0} where the session letter goes, e.g. BatchRvt.2022.FamilyCategoriesOne{0}.ALL.Settings.json
The settings files are in <flow>\_Users\<user>\_Settings

.PARAMETER StartIntervalSeconds
How long to wait between starting sessions, so Revit can start up fully before the next session.
#>
function Start-ChainSessions {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$SettingsFileNamePattern,
        [int]$StartIntervalSeconds = 180
    )
    $settings_directory = (Join-Path (Get-ChainUserDirectory -FlowDirectory $FlowDirectory) "_Settings") + "\"
    $settings_file_names = @()
    foreach ($letter in $chain_session_letters) {
        $settings_file_names += ($SettingsFileNamePattern -f $letter)
    }
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_file_names -batch_processor_path $batch_processor_path -start_interval_seconds $StartIntervalSeconds
}

<#
.SYNOPSIS
Copies a file, returns True if it was copied. A missing source file is logged and not copied.
#>
function Copy-ChainFile {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )
    if (-not (Test-Path $Source -PathType Leaf)) {
        Write-ToLogAndConsole -Message "Not copied, file does not exist: $Source"
        return $false
    }
    Copy-Item -Path $Source -Destination $Destination -Force
    if ($?) {
        Write-ToLogAndConsole -Message "Copied: $Source"
        Write-ToLogAndConsole -Message "To: $Destination"
        return $true
    }
    Write-ToLogAndConsole -Message "Failed to copy: $Source to: $Destination"
    return $false
}

<#
.SYNOPSIS
Deletes files if they exist, e.g. a flow's output from a previous run, so it can't be passed on as if it were new.
#>
function Remove-ChainFile {
    param (
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$Path
    )
    foreach ($file in $Path) {
        if (Test-Path $file -PathType Leaf) {
            Remove-Item -Path $file -Force
            Write-ToLogAndConsole -Message "Deleted previous file: $file"
        }
    }
}

<#
.SYNOPSIS
Writes lines to a text file as UTF-8 without a byte order mark (which the python scripts would read as part of the first value).
#>
function Write-ChainTextFile {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [string[]]$Lines = @()
    )
    $directory = Split-Path -Path $Path -Parent
    if (!(Test-Path $directory)) {
        New-Item -ItemType Directory -Path $directory | Out-Null
    }
    [System.IO.File]::WriteAllLines($Path, [string[]]$Lines)
}

<#
.SYNOPSIS
Combines changed family lists (ChangedFilesTaskList.csv: header, then file name, file path, revit category)
into one list, so every family changed in this run gets reloaded. Returns the number of families in the list.
#>
function Write-ChainChangedList {
    param (
        [string[]]$Sources = @(),
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )
    $header = $null
    $rows = New-Object System.Collections.Generic.List[string]
    foreach ($source in $Sources) {
        if (-not (Test-Path $source -PathType Leaf)) {
            continue
        }
        $lines = @(Get-Content -Path $source | Where-Object { $_.Trim() -ne "" })
        if ($lines.Count -eq 0) {
            continue
        }
        if ($null -eq $header) {
            $header = $lines[0]
        }
        foreach ($line in ($lines | Select-Object -Skip 1)) {
            if (-not $rows.Contains($line)) {
                $rows.Add($line)
            }
        }
    }
    if ($null -eq $header) {
        $header = "file Name,file Path,revit category"
    }
    Write-ChainTextFile -Path $Destination -Lines (@($header) + $rows.ToArray())
    Write-ToLogAndConsole -Message "Wrote changed families list ($($rows.Count) families): $Destination"
    return $rows.Count
}

<#
.SYNOPSIS
Writes the list of families a follow up report runs on: one fully qualified family file path per line.
Returns the number of families in the list.

.DESCRIPTION
Reads either a changed family list with a header (file Name, file Path, revit category: the file Path column is used),
or a list without a header with the file path in the first column (SecondProcessFamilies.csv, the reload flow's changed list).
#>
function Write-ChainFollowUpList {
    param (
        [string[]]$Sources = @(),
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )
    $paths = New-Object System.Collections.Generic.List[string]
    foreach ($source in $Sources) {
        if (-not (Test-Path $source -PathType Leaf)) {
            Write-ToLogAndConsole -Message "Follow up list source does not exist: $source"
            continue
        }
        $rows = @(Import-Csv -Path $source -Header "c0", "c1", "c2")
        if ($rows.Count -eq 0) {
            continue
        }
        $column = "c0"
        if ($rows[0].c1 -eq "file Path") {
            $column = "c1"
            $rows = @($rows | Select-Object -Skip 1)
        }
        foreach ($row in $rows) {
            $path = $row.$column
            if ($path -and -not $paths.Contains($path)) {
                $paths.Add($path)
            }
        }
    }
    $lines = @()
    foreach ($path in $paths) {
        if ($path -match '[",]') {
            $lines += '"' + ($path -replace '"', '""') + '"'
        }
        else {
            $lines += $path
        }
    }
    Write-ChainTextFile -Path $Destination -Lines $lines
    Write-ToLogAndConsole -Message "Wrote follow up list ($($paths.Count) families): $Destination"
    return $paths.Count
}

<#
.SYNOPSIS
Points the paths in a Revit Batch Processor settings file at the flow's current location and the given user.

.DESCRIPTION
Every path in the settings files is in the format <any folder>\<flow>\_Script\... or <any folder>\<flow>\_Users\<user>\...
The part up to and including the flow folder is replaced with the flow's actual directory, and the user folder with the given user.
Values without the flow folder in them are left as they are.
#>
function Update-ChainSettingsFile {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$UserName
    )
    $flow_name = Split-Path -Path $FlowDirectory -Leaf
    $flow_marker = "\" + $flow_name + "\"
    $text = [System.IO.File]::ReadAllText($Path)
    $evaluator = {
        param($match)
        # JSON escapes backslashes
        $value = $match.Groups["value"].Value -replace '\\\\', '\'
        $index = $value.IndexOf($flow_marker, [System.StringComparison]::OrdinalIgnoreCase)
        if ($index -lt 0) {
            return $match.Value
        }
        $value = $FlowDirectory + $value.Substring($index + $flow_name.Length + 1)
        $value = [regex]::Replace($value, '\\_Users\\[^\\]+(\\|$)', ('\_Users\' + $UserName + '$1'))
        return '"' + $match.Groups["key"].Value + '": "' + ($value -replace '\\', '\\') + '"'
    }.GetNewClosure()
    $updated = [regex]::Replace($text, '"(?<key>[A-Za-z]+)"\s*:\s*"(?<value>[^"]*)"', [System.Text.RegularExpressions.MatchEvaluator]$evaluator)
    [System.IO.File]::WriteAllText($Path, $updated)
}

<#
.SYNOPSIS
Runs the steps of a flow: checks the user folder, logs to the flow's log file, catches failures. Returns the exit code.

.PARAMETER FlowDirectory
The fully qualified directory of the flow.

.PARAMETER Name
Name of the flow, used in the console header and the log file name.

.PARAMETER Action
The flow's steps. Returns one of the exit codes: $CHAIN_EXIT_DONE, $CHAIN_EXIT_FAILED, $CHAIN_EXIT_NOTHING_TO_PROCESS
#>
function Invoke-ChainFlow {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FlowDirectory,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )
    Write-ToLogAndConsole -Message $Name -IsHeader $True
    if (-not (Test-ChainUser -FlowDirectory $FlowDirectory)) {
        return $CHAIN_EXIT_FAILED
    }
    $flow_exit_code = $CHAIN_EXIT_FAILED
    $previous_log = Start-ChainFlowLog -FlowDirectory $FlowDirectory -Name $Name
    $flow_log = $global:log_file_path
    try {
        # the last value the steps return is the exit code
        $flow_result = & $Action
        $flow_exit_code = [int](@($flow_result)[-1])
    }
    catch {
        Write-ToLogAndConsole -Message "Failed with exception: $_"
        $flow_exit_code = $CHAIN_EXIT_FAILED
    }
    finally {
        Write-ToLogAndConsole -Message "$Name finished with exit code: $flow_exit_code"
        Set-LogFile -Path $previous_log | Out-Null
    }
    Write-ToLogAndConsole -Message "$Name finished with exit code: $flow_exit_code (log: $flow_log)"
    return $flow_exit_code
}

<#
.SYNOPSIS
Ends a flow start script: waits for Enter unless NoPause is set, then exits with the exit code.
#>
function Complete-ChainScript {
    param (
        [Parameter(Mandatory = $true)]
        [int]$ExitCode,
        [switch]$NoPause
    )
    if (-not $NoPause) {
        Read-Host "Press Enter to exit." | Out-Null
    }
    exit $ExitCode
}
