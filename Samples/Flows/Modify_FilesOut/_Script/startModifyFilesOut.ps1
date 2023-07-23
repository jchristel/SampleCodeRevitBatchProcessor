# check for arguments (need to be first line , not counting comments, in a script)
Param (
    [string]$exo #indication whether step 2 (export only) should be run
)
# load util functions
. "C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"

Write-ToLogAndConsole -Message "Argument 1: $exo"

Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True

# Define the paths to your batch processor settings as a list
$settings_step_one = @(
    "BatchRvt.2022.ModifyFilesOutOneA.Settings.json", 
    "BatchRvt.2022.ModifyFilesOutOneB.Settings.json",
    "BatchRvt.2022.ModifyFilesOutOneC.Settings.json"
)

# Define the paths to your batch processor settings as a list
$settings_step_two = @(
    "BatchRvt.2022.ModifyFilesOutTwoA.Settings.json", 
    "BatchRvt.2022.ModifyFilesOutTwoB.Settings.json",
    "BatchRvt.2022.ModifyFilesOutTwoC.Settings.json"
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
$ui_file_select_path='"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src\duHast\UI\script.py"'
# Display theui fiole select path
Write-ToLogAndConsole -Message "UI File select path: $ui_file_select_path"
# directory path from which python UI is going to show revit files
$ui_input_directory = '"C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\Flows\Modify_FilesOut\_sampleFiles"'
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
# file path to post step one script
$_post_step_one_script = "`"$root_flow_directory`"\_Script\Post_StepOne_FilesOut.py"
Write-ToLogAndConsole -Message "post step one script file path: $_post_step_one_script"
# file path to clean up script run at the very end
$clean_up_script_path = "`"$root_flow_directory`"\_Script\Post_FilesOut.py"
Write-ToLogAndConsole -Message "Final clean up script file path: $clean_up_script_path"

Write-ToLogAndConsole -Message "-"
Write-ToLogAndConsole -Message "-"

# check if an export only is to be done ( in case some files failed to complete that step in the first attempt )
if($exo.ToLower() -eq "no") {
    # start UI file selection interface
    Write-ToLogAndConsole -Message "UI FILE SELECTION" -IsHeader $True
    # use start warpper function to capture output from script
    $process_file_selection = start-wrapper -path "$iron_python_path" -arguments $ui_file_select_path, $python_ui_inputs
    $exitCode = $process_file_selection.ExitCode

    # check whether any files got selected before proceeding
    if ($exitCode -eq 0) {
        # start batch processor
        Write-ToLogAndConsole -Message "step one" -IsHeader $True
    
        # start batch processor sessions with individual settings scripts
        start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one
    
        # post step one script
        Write-ToLogAndConsole -Message "*" -IsHeader $True
        Write-ToLogAndConsole -Message "-"
        Write-ToLogAndConsole -Message "post step one" -IsHeader $True
    
        $process_post_step_one = start-wrapper -path "$iron_python_path" -arguments $_post_step_one_script
        $exit_code_post_step_one = $process_post_step_one.ExitCode
    
        Write-ToLogAndConsole -Message "Post step script finished with code: $exit_code_post_step_one"
        Write-ToLogAndConsole -Message "-"

        # start batch processor
        Write-ToLogAndConsole -Message "step two" -IsHeader $True
        # start batch processor sessions with individual settings scripts
        start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_two
        # post step one script
        Write-ToLogAndConsole -Message "*" -IsHeader $True
        Write-ToLogAndConsole -Message "-"
        Write-ToLogAndConsole -Message "final clean up" -IsHeader $True

        $process_post_step_two = start-wrapper -path "$iron_python_path" -arguments $clean_up_script_path
        $exit_code_post_step_two = $process_post_step_two.ExitCode
    
        Write-ToLogAndConsole -Message "Final clean up script finished with code: $exit_code_post_step_two"
        Write-ToLogAndConsole -Message "-"

    } else {
        Write-ToLogAndConsole -Message "File selection script failed with exit code: $exitCode"
    }
} else {

    # start batch processor for step 2 only
    Write-ToLogAndConsole -Message "step two" -IsHeader $True
    # start batch processor sessions with individual settings scripts
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_two
    # post step one script
    Write-ToLogAndConsole -Message "*" -IsHeader $True
    Write-ToLogAndConsole -Message "-"
    Write-ToLogAndConsole -Message "final clean up" -IsHeader $True

    $process_post_step_two = start-wrapper -path "$iron_python_path" -arguments $clean_up_script_path
    $exit_code_post_step_two = $process_post_step_two.ExitCode

    Write-ToLogAndConsole -Message "Final clean up script finished with code: $exit_code_post_step_two"
    Write-ToLogAndConsole -Message "-"
}
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."