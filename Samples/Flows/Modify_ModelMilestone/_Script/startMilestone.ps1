# check for arguments (need to be first line , not counting comments, in a script)
Param (
    [string]$UI #indication whether a UI (yes) is uded to select files or all files (no) are to be milestoned
)
# load util functions
. "C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"

Write-ToLogAndConsole -Message "Argument 1: $UI"

Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True
# Define the paths to your batch processor settings as a list
$settings_step_one = @(
    "BatchRvt.2022.ModifyModelMilestoneOneA.Settings.json", 
    "BatchRvt.2022.ModifyModelMilestoneOneB.Settings.json",
    "BatchRvt.2022.ModifyModelMilestoneOneC.Settings.json"
) 

$user_name = $env:USERNAME.ToLower()
#Write-ToLogAndConsole ( "The current user is: $user_name" , $log_file_path)
Write-ToLogAndConsole -Message "user: $user_name"
# Get the directory where the script is being executed in
$script_directory = $PSScriptRoot
# Display the script directory
Write-ToLogAndConsole -Message "Script directory: $script_directory"
$root_flow_directory = Split-Path -Path $script_directory -Parent
Write-ToLogAndConsole -Message "flow root directory: $root_flow_directory"
# Define python path
$iron_python_path = "C:\Program Files (x86)\IronPython 2.7\ipy64.exe"
# Display batch processor path
Write-ToLogAndConsole -Message "Iron python file path: $iron_python_path"
# path to UI script allowing individual file selection
$ui_file_select_path='"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src\duHast\UI\script.py"'
# Display the ui file select path
Write-ToLogAndConsole -Message "UI File select path: $ui_file_select_path"
# path to script which selects all files in a given directory
$file_select_path = "`"$root_flow_directory`"\_Script\Pre_ModelMilestoneStandAlone.py"
# display path to no UI file selection script
Write-ToLogAndConsole -Message "File selection script, no uI: $file_select_path"
# directory path from which python UI is going to show revit files
$ui_input_directory = '"C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\Samples\Flows\Modify_ModelMilestone\_sampleFiles"'
Write-ToLogAndConsole -Message "UI input directory: $ui_input_directory"
# directory path into which the python UI will write the task files into
$ui_output_directory = ($root_flow_directory, "\_TaskList") -join ""
Write-ToLogAndConsole -Message "UI output directory: $ui_output_directory"
# number of task files to be written out by python UI
$ui_number_of_task_files = $settings_step_one.Count
Write-ToLogAndConsole -Message "Number of task files: $ui_number_of_task_files"
# Define the arguments as a single string (escpaed double quotes due to spaces in name!!)
$python_ui_inputs = "-i $ui_input_directory -o `"$ui_output_directory`" -n $ui_number_of_task_files -e .rvt"
Write-ToLogAndConsole -Message "UI input arguments: $python_ui_inputs"
# get the settings directory
$settings_directory = $root_flow_directory + "\_settings\"
# Display the settings directory
Write-ToLogAndConsole -Message "settings directory: $settings_directory"

Write-ToLogAndConsole -Message "-"
Write-ToLogAndConsole -Message "-"

# start UI file selection interface
Write-ToLogAndConsole -Message "UI FILE SELECTION" -IsHeader $True

# default value for file selection outcome
$exitCode = 0
if($UI.ToLower() -eq "no") {
    # use file selection without an UI
    $process_file_selection = start-wrapper -path "$iron_python_path" -arguments "$file_select_path"
    $exitCode = $process_file_selection.ExitCode
} else {
    # use file selection with UI
    $process_file_selection = start-wrapper -path "$iron_python_path" -arguments $ui_file_select_path, $python_ui_inputs
    $exitCode = $process_file_selection.ExitCode
}
# check whether any files got selected before proceeding
if ($exitCode -eq 0) {
    # start batch processor
    Write-ToLogAndConsole -Message "creating milestone(s)" -IsHeader $True
    
    # start batch processor sessions with individual settings scripts
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one

} else {
    Write-ToLogAndConsole -Message "File selection script failed with exit code: $exitCode"
}
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."