# load util functions
. "C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"

# output settings header
Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True

# Define the paths to your batch processor settings as a list
$settings_step_one = @(
    "BatchRvt.2022.Tests.Settings.json"
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
# Display iron python path
Write-ToLogAndConsole -Message "Iron python file path: $iron_python_path"
# Define python 3.4 path
$iron_python_3_4_path = "C:\Program Files\IronPython 3.4\ipy.exe"
# Display iron python path
Write-ToLogAndConsole -Message "Iron python 3.4 file path: $iron_python_3_4_path"
# get the settings directory
$settings_directory = $root_flow_directory + "\_settings\"
# Display the settings directory
Write-ToLogAndConsole -Message "settings directory: $settings_directory"
# file path to pre rbp script
$_pre_step_one_script="`"$root_flow_directory`"\_Script\Pre_NonRevitTests_StandAlone.py"
# Display the file path to pre rbp script
Write-ToLogAndConsole -Message "pre step one script: $_pre_step_one_script"
# file path to post step one script
$_post_step_one_script="`"$root_flow_directory`"\_Script\Post_RevitTests.py"
Write-ToLogAndConsole -Message "post step one script file path: $_post_step_one_script"


Write-ToLogAndConsole -Message "-"


# start running non revit tests
Write-ToLogAndConsole -Message "runnin non Revit tests" -IsHeader $True
# use start warpper function to capture output from script
$process_file_selection = start-wrapper -path "$iron_python_3_4_path" -arguments $_pre_step_one_script
$exitCode = $process_file_selection.ExitCode

# check whether any files got selected before proceeding
if ($exitCode -eq 0) {

    # start batch processor
    Write-ToLogAndConsole -Message "Non revit tests completed successfully"

    # start batch processor
    Write-ToLogAndConsole -Message "runnin Revit tests" -IsHeader $True
    # start batch processor sessions with individual settings scripts
    start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one
        
    # clean up script
    Write-ToLogAndConsole -Message "*" -IsHeader $True
    Write-ToLogAndConsole -Message "-"
    Write-ToLogAndConsole -Message "clean up" -IsHeader $True
        
    $process_clean_up = start-wrapper -path "$iron_python_path" -arguments $_post_step_one_script
    $exit_code_clean_up = $process_clean_up.ExitCode
        
    Write-ToLogAndConsole -Message "Cean up script finished with code: $exit_code_clean_up"
    Write-ToLogAndConsole -Message "-"

} else {
    Write-ToLogAndConsole -Message "Non Revit tests failed with exit code: $exitCode"
}
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."
