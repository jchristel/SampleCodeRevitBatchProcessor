# load util functions
. "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\PowerShell\BatchProcessorUtils.ps1"
# output settings header
Write-ToLogAndConsole -Message "SETTINGS" -IsHeader $True


# Define python path
$iron_python_path = "C:\Program Files\IronPython 2.7\ipy32.exe"
# Display batch processor path
Write-ToLogAndConsole -Message "Iron python file path: $iron_python_path"
$ui_file_select_path='"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\src\duHast\UI\files_select\files_select_ui.py"'
# Display the ui file select path
Write-ToLogAndConsole -Message "UI File select path: $ui_file_select_path"
# directory path from which python UI is going to show revit files
$ui_input_directory = '"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test\_rbp_flow\_sampleFiles"'
Write-ToLogAndConsole -Message "UI input directory: $ui_input_directory"
# directory path into which the python UI will write the task files into
$ui_output_directory = ("C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\test\_rbp_flow\_Output") -join ""
Write-ToLogAndConsole -Message "UI output directory: $ui_output_directory"
$ui_number_of_task_files=3
Write-ToLogAndConsole -Message "Task files: $ui_number_of_task_files"
$ui_filter_text="2022;2023"
Write-ToLogAndConsole -Message "filter text: $ui_filter_text"
# Define the arguments as a single string (escpaed double quotes due to spaces in name!!)
$python_ui_inputs = "-i $ui_input_directory -o `"$ui_output_directory`" -n $ui_number_of_task_files -f $ui_filter_text -x -e .rvt"
Write-ToLogAndConsole -Message "UI input arguments: $python_ui_inputs"

Write-ToLogAndConsole -Message "-"
Write-ToLogAndConsole -Message "-"

# start UI file selection interface
Write-ToLogAndConsole -Message "UI FILE SELECTION" -IsHeader $True
# use start warpper function to capture output from script
$process_file_selection = start-wrapper -path "$iron_python_path" -arguments $ui_file_select_path, $python_ui_inputs
$exitCode = $process_file_selection.ExitCode
Write-ToLogAndConsole -Message $exitCode
Write-ToLogAndConsole -Message "end of script" -IsHeader $True
Read-Host "Press Enter to exit."