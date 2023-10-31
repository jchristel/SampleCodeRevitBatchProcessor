# check for arguments (need to be first line , not counting comments, in a script)
Param (
    [string]$UI #indication whether a UI (yes) is needed to select files or all files (no) are to be processed
)
# load util functions
. "C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"

Write-ToLogAndConsole -Message "Argument 1: $UI"

Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True
# Define the paths to your batch processor settings as a list
$settings_step_one = @(
    "BatchRvt.2022.DailyModelMaintenanceOneA.Settings.json", 
    "BatchRvt.2022.DailyModelMaintenanceOneB.Settings.json",
    "BatchRvt.2022.DailyModelMaintenanceOneC.Settings.json"
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
# Define iron python path
$iron_python_path = "C:\Program Files (x86)\IronPython 2.7\ipy64.exe"
# Define standard python path
$standard_python_path = "C:\Program Files\Python311\python.exe"
# Display standard python path
Write-ToLogAndConsole -Message "Standard python file path: $standard_python_path"
# Display batch processor path
Write-ToLogAndConsole -Message "Iron python file path: $iron_python_path"
# path to UI script allowing individual file selection
$ui_file_select_path='"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src\duHast\UI\script.py"'
# Display the ui file select path
Write-ToLogAndConsole -Message "UI File select path: $ui_file_select_path"
# path to script which selects all files in a given directory
$file_select_path = Join-Path -Path $root_flow_directory -ChildPath "_Script\Pre_ModifyDailyModelMaintenanceStandAlone.py"
# display path to no UI file selection script
Write-ToLogAndConsole -Message "File selection script, no uI: $file_select_path"
# directory path from which python UI is going to show revit files
$ui_input_directory = '"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\Flows\Modify_DailyModelMaintenance\_sampleFiles"'
Write-ToLogAndConsole -Message "UI input directory: $ui_input_directory"
# directory path into which the python UI will write the task files into
$ui_output_directory = Join-Path -Path $root_flow_directory -ChildPath "_TaskList"
Write-ToLogAndConsole -Message "UI output directory: $ui_output_directory"
# number of task files to be written out by python UI
$ui_number_of_task_files = $settings_step_one.Count
Write-ToLogAndConsole -Message "Number of task files: $ui_number_of_task_files"
# Define the arguments as a single string (escpaed double quotes due to spaces in name!!)
$python_ui_inputs = "-i $ui_input_directory -o `"$ui_output_directory`" -n $ui_number_of_task_files -e .rvt"
Write-ToLogAndConsole -Message "UI input arguments: $python_ui_inputs"
# get the settings directory
$settings_directory = Join-Path -Path $root_flow_directory -ChildPath "_settings\"
# Display the settings directory
Write-ToLogAndConsole -Message "settings directory: $settings_directory"
# get the flow output directory
$out_directory = Join-Path -Path $root_flow_directory -ChildPath "_Output"
# Display the flows output directory
Write-ToLogAndConsole -Message "output directory: $out_directory"
# file path to post step one script (in this case executed in flow directory rather then secure enclave)
$_post_step_one_script = Join-Path -Path $script_directory -ChildPath "Post_DailyModelMaintenance.py"
Write-ToLogAndConsole -Message "post step one script file name: $_post_step_one_script"
# file path to post step one clean up script
$_post_step_one_clean_up_script = Join-Path -Path $script_directory -ChildPath "Post_DailyModelMaintenance_cleanUp.py"
Write-ToLogAndConsole -Message "post step one clean up script: $_post_step_one_clean_up_script"
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
    Write-ToLogAndConsole -Message "starting model maintenance" -IsHeader $True
    
    # start batch processor sessions with individual settings scripts
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one

    # post processing script¶
    Write-ToLogAndConsole -Message "*" -IsHeader $True
    Write-ToLogAndConsole -Message "-"
    Write-ToLogAndConsole -Message "Post Processing Script" -IsHeader $True
    # execute post processing script using c-python in order to get access to latest python libraries
    # this particular bit of code may need to run in secure enclave...
    $process_post = start-wrapper -path "$standard_python_path" -arguments $_post_step_one_script
    $exit_code_post_processing = $process_post
    Write-ToLogAndConsole -Message "Post processing script finished with code: $exit_code_post_processing"

    # clean up script
    Write-ToLogAndConsole -Message "*" -IsHeader $True
    Write-ToLogAndConsole -Message "-"
    Write-ToLogAndConsole -Message "clean up" -IsHeader $True

    # if all worked out run clean up scripts
    if ( $exit_code_post_processing -eq 0) {
        $process_clean_up = start-wrapper -path "$iron_python_path" -arguments `"$_post_step_one_clean_up_script`"
        $exit_code_clean_up = $process_clean_up.ExitCode
        Write-ToLogAndConsole -Message "Cean up script finished with code: $exit_code_clean_up"
    }
    else{
        Write-ToLogAndConsole -Message "Did not run clean up script"
    }
} else {
    Write-ToLogAndConsole -Message "File selection script failed with exit code: $exitCode"
}
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."