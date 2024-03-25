# check for arguments (need to be first line , not counting comments, in a script)
Param (
    [string]$pre #indication whether only pre revit test scripts should be run
)
# load util functions
. "C:\Users\jchristel\dev\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"


Write-ToLogAndConsole -Message "Argument 1: $pre"

# output settings header
Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True

# Define the paths to your batch processor settings as a list
# by revit version
$settings_step_one = @(
    @("BatchRvt.2022.Tests.Settings.json", "Revit_2022"),
    @("BatchRvt.2023.Tests.Settings.json", "Revit_2023")
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

# file path to pre rbp task files script
$_pre_step_one_task_script="`"$root_flow_directory`"\_Script\Pre_GetFiles_StandAlone.py"
# Display the file path to pre rbp script
Write-ToLogAndConsole -Message "pre step one task files script: $_pre_step_one_task_script"
# file path to pre rbp tests script
$_pre_step_one_script="`"$root_flow_directory`"\_Script\Pre_NonRevitTests_StandAlone.py"
# Display the file path to pre rbp script
Write-ToLogAndConsole -Message "pre step one script: $_pre_step_one_script"
# file path to post step one script
$_post_step_one_script="`"$root_flow_directory`"\_Script\Post_RevitTests.py"
Write-ToLogAndConsole -Message "post step one script file path: $_post_step_one_script"

Write-ToLogAndConsole -Message "-"

# start running non revit tests
Write-ToLogAndConsole -Message "running non Revit tests" -IsHeader $True
# use start warpper function to capture output from script
$process_non_revit_tests = start-wrapper -path "$iron_python_3_4_path" -arguments $_pre_step_one_script
$exitCode = $process_non_revit_tests.ExitCode

# check whether any files got selected before proceeding
if ($exitCode -eq 0) {

    # give user feedback
    Write-ToLogAndConsole -Message "Non revit tests completed successfully"

    if($pre.ToLower() -eq "no") {
        $write_task_files=0
        # write task lists by Revit version:
        foreach ($row in $settings_step_one) {
            $secondValue = $row[1]
            $process_revit_task_list = start-wrapper -path "$iron_python_3_4_path" -arguments $_pre_step_one_task_script, $secondValue
            $exitCode = $process_revit_task_list.ExitCode
            if ($exitCode -ne 0){
                $write_task_files=1
                break
            }
        }

        if($write_task_files -eq 0){
            # start batch processor sessions
            Write-ToLogAndConsole -Message "running Revit tests" -IsHeader $True

            # create new array from 2D array containing just the settings file names
            $settingsFilesArray = @()
            foreach ($row in $settings_step_one) {
                $firstValue = $row[0]
                $settingsFilesArray += $firstValue
            }

            # start batch processor sessions with individual settings scripts
            start-batchProcessor -settings_directory $settings_directory -settings_file_names $settingsFilesArray
                
            # clean up script
            Write-ToLogAndConsole -Message "*" -IsHeader $True
            Write-ToLogAndConsole -Message "-"
            Write-ToLogAndConsole -Message "clean up" -IsHeader $True
                
            $process_clean_up = start-wrapper -path "$iron_python_path" -arguments $_post_step_one_script
            $exit_code_clean_up = $process_clean_up.ExitCode
                
            Write-ToLogAndConsole -Message "Cean up script finished with code: $exit_code_clean_up"
            Write-ToLogAndConsole -Message "-"
        }else {
            Write-ToLogAndConsole -Message "Failes to create task files with exit code:$write_task_files"
        }
    }
    else {
        Write-ToLogAndConsole -Message "Only pre Revit tests were run"
    }
} else {
    Write-ToLogAndConsole -Message "Non Revit tests failed with exit code: $exitCode"
}
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."
