# load util functions
. "C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"
# output settings header
Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True

# Define the paths to your batch processor settings as a list 
$settings_step_one = @(
    "BatchRvt.2022.ModifyFilesInA.Settings.json"
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
# get the settings directory
$settings_directory = $root_flow_directory + "\_settings\"
# Display the settings directory
Write-ToLogAndConsole -Message "settings directory: $settings_directory"

Write-ToLogAndConsole -Message "-"
Write-ToLogAndConsole -Message "-"

# start batch processor
Write-ToLogAndConsole -Message "Consultant files in" -IsHeader $True
    
# start batch processor sessions with individual settings scripts
start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one

Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."