
<#
.SYNOPSIS
Pads out any text marked as a header with asteriks

.DESCRIPTION
The padding is applied before and after the input string at equal length

.PARAMETER InputString
The input string to be padded.

.PARAMETER Length
The overall length of the final padded string.

.EXAMPLE
Add-Padding -InputString "Test" -Length 90

.NOTES
General notes
#>
function Add-Padding {
    param (
        [string]$InputString,
        [int]$Length
    )

    # Calculate the length of the padding needed
    $paddingLength = $Length - $InputString.Length
    # If the padding length is negative, truncate the input string
    if ($paddingLength -le 0) {
        return $InputString.Substring(0, $Length)
    }

    # Calculate the length of padding on each side
    $paddingLengthLeft = [math]::Floor($paddingLength / 2)
    $paddingLengthRight = $paddingLength - $paddingLengthLeft

    # Add the padding to the input string
    $paddedString = ('*' * $paddingLengthLeft) + $InputString + ('*' * $paddingLengthRight)

    # Return the padded string
    return $paddedString
}

<#
.SYNOPSIS
Pipes output, the message past in, into a log file and console.

.DESCRIPTION
Used to record any powershell output in a log file as well as displaying it in the console window.
For log file location refer to global settings below.

.PARAMETER Message
The message.

.PARAMETER IsHeader
Boolean, Default is False. If true the message will be padded.

.EXAMPLE
An example

.NOTES
General notes
#>
function Write-ToLogAndConsole {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [bool]$IsHeader = $False
    )

    # check if message is a header, if so padd with asteriks 
    if ($IsHeader) {
        $Message = Add-Padding -InputString $Message.ToUpper() -Length 90
    }

    # get the current dated formatted
    $now = Get-Date -Format "yy-MM-dd HH_mm_ss"
    $Message = $now + ' : ' + $Message

    # Display the message to the console
    Write-Host $Message

    # Append the message to the log file
    $Message | Out-File -Append -FilePath $log_file_path

    #$Message | Tee-Object -FilePath $log_file_path -Append
}

<#
.SYNOPSIS
Creates a temp file which receives the output from Start-Process and then pipes that output into the log file.
Used by any python scripts which output to console.

.DESCRIPTION
Long description

.PARAMETER path
Fully qualified file path of python version to be used to execute python script.

.PARAMETER arguments
The arguments to be used width the python engine. Usually the fully qualified filew path of the python script to be executed.

.EXAMPLE
# Define iron python path
$iron_python_path = "C:\Program Files (x86)\IronPython 2.7\ipy64.exe"
$file_select_path = "C:\flow directory path\_Script\script.py"
$process_file_selection = start-wrapper -path "$iron_python_path" -arguments "$file_select_path"

.NOTES
General notes
#>
function start-wrapper {
    param (
        [Parameter(Mandatory = $true)]
        [string]$path,
        [Parameter(Mandatory = $true)]
        [string[]]$arguments
    )
    # create a temp file to capture output of the ui file selection script
    $tempFile = New-TemporaryFile
    # stat the process and wait for it to finish
    $process_result = Start-Process $path -ArgumentList $arguments -NoNewWindow -PassThru -RedirectStandardOutput $tempFile.FullName -Wait
    # Read the contents of the temporary file into a variable
    $output_temp_file = Get-Content $tempFile.FullName
    $output_temp_file | Tee-Object -FilePath $log_file_path -Append
    Write-Host $output_temp_file
    # Remove the temporary file
    Remove-Item $tempFile.FullName
    # return the process result object (checking for errors...)
    return $process_result
}

<#
.SYNOPSIS
A count down with progress bar...

.DESCRIPTION
Counts for 180 seconds.

.EXAMPLE
wait-seconds

.NOTES
General notes
#>
function wait-seconds() {
    $progressId = 2
    for ($i = 0; $i -le 180; $i++) {
        $timeLeft = 180 - $i
        $percentComplete = ($i / 180) * 100
        $status = "Time left: $($timeLeft)s"
        Write-Progress -Id $progressId -Activity "Countdown till next Revit session start" -Status $status -PercentComplete $percentComplete
        Start-Sleep 1
    }
    Write-Progress -Id $progressId -Activity "Countdown till next Revit session start" -Status "Finished" -Completed
}

<#
.SYNOPSIS
Starts a number of batch processor scripts in a given intervall and waits for them to finish

.DESCRIPTION
Starts a number of Revit Batch Procesor session in a given intervall (180s) in order to allow Revit to initialise completely 
before the next session is started. The start intervall is visualized with a progress bar.
Once all sessions have started, another progressbar will be displayed, indicating the script is waiting for all sessions to finish.
The number of sessions depends on number of settings file names past in. 

.PARAMETER settings_directory
The fully qualified directory path containing the Revit Batch Processor settings files.

.PARAMETER settings_file_names
A list containing the individual Revit Batch Processor settings file names.

.EXAMPLE
# Define the paths to your batch processor settings as a list
$settings_step_one = @(
    "BatchRvt.2019.DailyModelMaintenanceOneA.Settings.json", 
    "BatchRvt.2019.DailyModelMaintenanceOneB.Settings.json",
    "BatchRvt.2019.DailyModelMaintenanceOneC.Settings.json"
)
$settings_directory = "C:\flow directory path\_settings\"
# start batch processor sessions with individual settings scripts
start-batchProcessor -settings_directory $settings_directory -settings_file_names $settings_step_one

.NOTES
General notes
#>
function start-batchProcessor {
    param (
        [Parameter(Mandatory = $true)]
        [string]$settings_directory,
        [Parameter(Mandatory = $true)]
        [string[]]$settings_file_names
    )

    # Define batch processor path
    #$batch_processor_path = "$env:LOCALAPPDATA\RevitBatchProcessor\BatchRvt.exe"
    $batch_processor_path = "C:\Program Files\BVN\RevitBatchProcessor\BatchRvt.exe"
    for ($i = 0; $i -lt $settings_file_names.Length; $i++) {
        $settings = $settings_file_names[$i]
        Write-ToLogAndConsole -Message "Starting Revit Batch Processor with settings: $settings_directory$settings"
        Start-Process $batch_processor_path -ArgumentList "--settings_file `"$settings_directory$settings`""
        if ($i -ne $settings_file_names.Length) {
            #This won't execute on the final iteration
            wait-seconds
        }
    }

    # Wait for all scripts to finish and display an indeterminate progress bar 
    Write-ToLogAndConsole -Message "Waiting for all scripts to finish..." 
    $progress = 0 

    $progressId = 1
    # display a progress bar waiting for batch p to finish
    while ((Get-Process BatchRvt -ErrorAction SilentlyContinue | Where-Object { $_.HasExited -eq $false }).Count -gt 0) {
        Write-Progress -Id $progressId -Activity "Waiting for scripts to finish" -Status "Waiting" -PercentComplete $progress -CurrentOperation "Running Revit Batch Processor script(s)"
        $progress = ($progress + 10) % 100
        Start-Sleep -Seconds 2 
    } 

    # need this to make progress bar go away once finished
    Write-Progress -Id $progressId -Activity "Waiting for scripts to finish" -Status "Finished" -Completed

    Write-ToLogAndConsole -Message "Waiting for scripts to finish:  Done"
}


<#
.SYNOPSIS
Executes post pocessing script in a secure enclave.

.DESCRIPTION
Creates a temp directory in users \dev\ fodler and copies content of \_Script and \_Output folder into temp folder
It than executes python script using python 3.11 in temp \_Script folder. In that way it does not get blocked by any security softwarre installed monitoring scripts on a network drive.
After the python script is finished the content, processing oputputs,  of the temp \_Output folder gets copied back to the flow directory.

.PARAMETER flow_directory
The fully qualified directory of the flow

.PARAMETER python_file_path
The fully qualified file path of the pythonm version to be used to execute the python script.

.PARAMETER script_file_name
The file name only of the python script to be executed. It is assumed that this script is located in the \_Script directory.

.EXAMPLE
$flow_dir = "C:\flow directory path"
$standard_python_path = "C:\Program Files\Python311\python.exe"
$_post_step_one_script = "python_script.py"
$exit_code = start-PythonInSaveEnclave -flow_directory $flow_dir -python_file_path $standard_python_path -script_file_name $_post_step_one_script

.NOTES
General notes
#>
function start-PythonInSecureEnclave {
    param (
        [Parameter(Mandatory = $true)]
        [string]$flow_directory,
        [Parameter(Mandatory = $true)]
        [string]$python_file_path,
        [Parameter(Mandatory = $true)]
        [string]$script_file_name
    )
    # set up return value 
    $process_result = 0
    # get the user name
    $user_name = $env:USERNAME.ToLower()
    Write-ToLogAndConsole -Message "user: $user_name"
    # output user defined settings
    Write-ToLogAndConsole -Message "Flow directory: $flow_directory"
    Write-ToLogAndConsole -Message "Python file path: $python_file_path"
    Write-ToLogAndConsole -Message "Script file name: $script_file_name"

    # build secure enclave path
    $secure_enclave = "C:\Users\$user_name\dev"

    # build source directory names
    $script_folder_name = "_Script"
    $script_directory = Join-Path -Path $flow_directory  -ChildPath $script_folder_name
    $output_folder_name = "_Output"
    $out_directory = Join-Path -Path $flow_directory  -ChildPath $output_folder_name
    # build directory names to be created in secure enclave
    # get a GUID to be used as the temp directory name
    $temp_name = [System.Guid]::NewGuid()
    # Display the guid
    Write-ToLogAndConsole -Message "temp directory GUID: $temp_name"
    # set up the temp directory name
    $temp_dir = Join-Path $secure_enclave $temp_name
    # Display temp directory name
    Write-ToLogAndConsole -Message "temp directory : $temp_dir"
    # check if secure enclave exists
    if (Test-Path $secure_enclave -PathType Container) {
        # build temp script directory name
        $temp_dir_script = Join-Path -Path $temp_dir -ChildPath $script_folder_name
        # Display temp script directory name
        Write-ToLogAndConsole -Message "temp script directory: $temp_dir_script"
        # build temp output directory name
        $temp_dir_out = Join-Path -Path $temp_dir -ChildPath $output_folder_name
        # Display temp output directory name
        Write-ToLogAndConsole -Message "temp output directory: $temp_dir_out"
        # build file path of script to execute in secure enclave
        $script_file_path = Join-Path -Path $temp_dir_script -ChildPath $script_file_name
        # Display script full file name
        Write-ToLogAndConsole -Message "Script to execute file name: $script_file_path"

        # create a temp script directory ( added out -null to avoid having the path showing up in the return value!)
        New-Item -ItemType Directory -Path $temp_dir_script  | Out-Null
        if ($?) {
            Write-ToLogAndConsole -Message "Created temp script directory: $temp_dir_script"
            # create a temp output folder ( added out -null to avoid having the path showing up in the return value!)
            New-Item -ItemType Directory -Path $temp_dir_out  | Out-Null
            if ($?) {
                Write-ToLogAndConsole -Message "Created temp out directory: $temp_dir_out"
                # copy scipt files
                Copy-Item -Path $script_directory"\*" -Recurse -Destination $temp_dir_script
                if ($?) {
                    Write-ToLogAndConsole -Message "Copied files into temp dir: $temp_dir_script"
                    Write-ToLogAndConsole -Message "From: $script_directory\*"

                    # copy output files
                    Copy-Item -Path $out_directory"\*" -Destination $temp_dir_out
                    if ($?) {
                        Write-ToLogAndConsole -Message "Copied files into temp out dir: $temp_dir_out"
                        Write-ToLogAndConsole -Message "From: $out_directory\*"

                        # start python script
                        Write-ToLogAndConsole -Message "Starting script: $script_file_name"
                        $process_script = start-wrapper -path $python_file_path -arguments $script_file_path
                        $process_result = $process_script.ExitCode
                        # message user
                        Write-ToLogAndConsole -Message "Script finished with code: $process_result"
                        Write-ToLogAndConsole -Message "-"

                        # copy output back to source
                        Copy-Item -Path "$temp_dir_out\*" -Destination $out_directory -force
                        if ($?) {
                            Write-ToLogAndConsole -Message "Copied files from temp out dir: $temp_dir_out\*"
                            Write-ToLogAndConsole -Message "To origin: $out_directory"

                            # delete temp directory
                            Remove-Item -LiteralPath $temp_dir -Force -Recurse
                            if ($?) {
                                Write-ToLogAndConsole -Message "Deleted temp directory: $temp_dir"
                            }
                            else {
                                $process_result = 3
                                Write-ToLogAndConsole -Message "Aborting: Failed to delete temp directory: $temp_dir"
                            }
                            
                        }
                        else {
                            $process_result = 2
                            Write-ToLogAndConsole -Message "Aborting: Failed to copy data files back to $out_directory"
                        }
                        
                    }
                    else {
                        $process_result = 2
                        Write-ToLogAndConsole -Message "Aborting: Failed to copy data files from $out_directory\*"
                    }
                    
                }
                else {
                    $process_result = 2
                    Write-ToLogAndConsole -Message "Aborting: Failed to copy script files from: $script_directory\*"
                }
                
            }
            else {
                $process_result = 2
                Write-ToLogAndConsole -Message "Aborting: Failed to create directory $temp_dir_out"
            }
        }
        else {
            $process_result = 2
            Write-ToLogAndConsole -Message "Aborting: Failed to create directory $temp_dir_script"
        }

    }
    else {
        $process_result = 1
        Write-ToLogAndConsole -Message "Aborting: Secure enclave: $secure_enclave does not exist."
    }

    # check if temp directory need to be deleted after aborted command
    if ($process_result -eq 2) {
        Write-ToLogAndConsole -Message "Cleaning up after abort: $process_result"
        # delete temp directory ( added out -null to avoid having the path showing up in the return value!)
        Remove-Item -LiteralPath $temp_dir -Force -Recurse | Out-Null
        if ($?) {
            Write-ToLogAndConsole -Message "Deleted temp directory: $temp_dir"
        }
        else {
            $process_result = 3
            Write-ToLogAndConsole -Message "Aborting: Failed to delete temp directory: $temp_dir"
        }
    }

    Write-ToLogAndConsole -Message "exiting with: $process_result"
    return [int]$process_result
}

# global settings...


# set up the log file name
# get the script working directory
$log_dir = "$PWD\logs" 
# create a logs folder in the script's working directory if not exists already
if (!(Test-Path $log_dir)) {
    New-Item -ItemType Directory -Path $log_dir
}
$log_file_name = "Log_$(Get-Date -Format 'yyyy-MM-dd').log" # create log file name with current date
$log_file_path_ = Join-Path $log_dir $log_file_name   # join the log directory and filename
# and store it in a global variable
New-Variable -Name "log_file_path" -Value $log_file_path_ -Scope "Global"

# set console text to green, matrix style
$host.UI.RawUI.ForegroundColor = "Green"
