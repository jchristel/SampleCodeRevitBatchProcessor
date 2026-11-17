<#
.SYNOPSIS
Runs the RoomMate room tasks queued for a chosen set of Revit models, with nobody asked (flow Modify_RoomMateTasks).

.DESCRIPTION
- selects the Revit files to process and writes the task lists (with a UI, or every file in PATH_TO_FILES_TO_PROCESS)
- opens each model in Revit Batch Processor and runs ModifyRoomMateTasks.py: every queued RoomMate task of the
  model is claimed, written and reported back to the RoomMate server, and the model is synchronised when one was written
- checks the Revit Batch Processor logs and cleans up the marker files (Post_RoomMateTasks.py)

Needs the RoomMate pyRevit extension installed on this machine and the RoomMate server reachable from it.
The flow's settings are in _Script\settings.py.

.PARAMETER UI
"yes" to choose the files in a window, "no" to take every file in PATH_TO_FILES_TO_PROCESS (settings.py).

.PARAMETER NoPause
Do not wait for Enter at the end.
#>
param (
    [string]$UI = "yes",
    [switch]$NoPause
)

$script_directory = $PSScriptRoot
$flow_directory = Split-Path -Path $script_directory -Parent

# load util functions (Samples\PowerShell, relative to this flow)
. (Join-Path $flow_directory "..\..\PowerShell\BatchProcessorUtils.ps1")

Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True

# one Revit Batch Processor session per settings file; each reads its own task list (_TaskList\Tasklist_n.txt).
# The server hands a model's tasks to one session only, so more sessions are safe: add a settings file and raise
# NO_OF_TASK_LIST_FILES in settings.py to match.
$settings_files = @(
    "BatchRvt.RoomMateTasksA.Settings.json"
)
$settings_directory = (Join-Path $flow_directory "_settings") + "\"
Write-ToLogAndConsole -Message "settings directory: $settings_directory"

$iron_python_path = "C:\Program Files (x86)\IronPython 2.7\ipy64.exe"
Write-ToLogAndConsole -Message "Iron python file path: $iron_python_path"

# the installed RoomMate extension's duHast, the same copy settings.py puts first on the path
$roommate_lib = Join-Path $env:APPDATA "pyRevit\Extensions\RoomMate.extension\lib"
if (-not (Test-Path (Join-Path $roommate_lib "room_m"))) {
    Write-ToLogAndConsole -Message "The RoomMate extension is not installed: no room_m in $roommate_lib"
    if (-not $NoPause) { Read-Host "Press Enter to exit." }
    exit 1
}

$ui_file_select_path = "`"" + (Join-Path $roommate_lib "duHast\UI\files_select\files_select_ui.py") + "`""
$file_select_path = "`"" + (Join-Path $script_directory "Pre_RoomMateTasksStandAlone.py") + "`""
$post_path = "`"" + (Join-Path $script_directory "Post_RoomMateTasks.py") + "`""

# the folder the file selection window opens in
$ui_input_directory = "`"" + (Join-Path $flow_directory "_sampleFiles") + "`""
$ui_output_directory = "`"" + (Join-Path $flow_directory "_TaskList") + "`""
$python_ui_inputs = "-i $ui_input_directory -o $ui_output_directory -n $($settings_files.Count) -e .rvt"
Write-ToLogAndConsole -Message "UI input arguments: $python_ui_inputs"

Write-ToLogAndConsole -Message "FILE SELECTION" -IsHeader $True
if ($UI.ToLower() -eq "no") {
    $process = start-wrapper -path "$iron_python_path" -arguments "$file_select_path"
} else {
    $process = start-wrapper -path "$iron_python_path" -arguments $ui_file_select_path, $python_ui_inputs
}
$exit_code = $process.ExitCode

if ($exit_code -eq 0) {
    Write-ToLogAndConsole -Message "running RoomMate tasks" -IsHeader $True
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_files -start_interval_seconds 60

    Write-ToLogAndConsole -Message "POST PROCESSING" -IsHeader $True
    $process = start-wrapper -path "$iron_python_path" -arguments "$post_path"
    $exit_code = $process.ExitCode
} else {
    Write-ToLogAndConsole -Message "No files selected (file selection exit code: $exit_code)"
}

Write-ToLogAndConsole -Message "end of script" -IsHeader $True
if (-not $NoPause) { Read-Host "Press Enter to exit." }
exit $exit_code
