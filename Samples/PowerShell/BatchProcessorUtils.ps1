# pads out any text marked as a header with asterisks
# makes test all upper case
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

# pipes output, the message past in, into a log file and console
function Write-ToLogAndConsole {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [bool]$IsHeader = $False
    )

    # check if message is a header, if so padd with asteriks 
    if($IsHeader){
        $Message = Add-Padding -InputString $Message.ToUpper() -Length 90
    }

    # get the current dated formatted
    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Message = $now + ' : ' + $Message
    $Message | Tee-Object -FilePath $log_file_path -Append
}

# Creates a temp file which receives the output from Start-Process and then pipes that output into the log file
# used for any python scripts which output to console
function start-wrapper{
    param (
        [Parameter(Mandatory=$true)]
        [string]$path,
        [Parameter(Mandatory=$true)]
        [string[]]$arguments
    )
    # create a temp file to capture output of the ui file selection script
    $tempFile = New-TemporaryFile
    # stat the process and wait for it to finish
    $process_result = Start-Process $path -ArgumentList $arguments -NoNewWindow -PassThru -RedirectStandardOutput $tempFile.FullName -Wait
    # Read the contents of the temporary file into a variable
    $output_temp_file = Get-Content $tempFile.FullName
    $output_temp_file | Tee-Object -FilePath $log_file_path -Append
    # Remove the temporary file
    Remove-Item $tempFile.FullName
    # return the process result object (checking for errors...)
    return $process_result
}

# a 60 second cont down with progress bar...
function wait-seconds(){
    $progressId = 2
    for ($i = 0; $i -le 60; $i++) {
        $timeLeft = 60 - $i
        $percentComplete = ($i / 60) * 100
        $status = "Time left: $($timeLeft)s"
        Write-Progress -Id $progressId -Activity "Countdown till next Revit session start" -Status $status -PercentComplete $percentComplete
        Start-Sleep 1
    }
    Write-Progress -Id $progressId -Activity "Countdown till next Revit session start" -Status "Finished" -Completed
}

# starts a number of batch processor scripts in a 60 seconds intervall and waits for them to finish
function start-batchProcessor{
    param (
        [Parameter(Mandatory=$true)]
        [string]$settings_directory,
        [Parameter(Mandatory=$true)]
        [string[]]$settings_file_names
    )

    # Define batch processor path
    $batch_processor_path = "$env:LOCALAPPDATA\RevitBatchProcessor\BatchRvt.exe"

    for ($i = 0; $i -lt $settings_file_names.Length; $i++) {
        $settings = $settings_file_names[$i]
        Write-ToLogAndConsole -Message "Starting Revit Batch Processor with settings: $settings_directory$settings"
        Start-Process $batch_processor_path -ArgumentList "--settings_file `"$settings_directory$settings`""
        if($i -ne $settings_file_names.Length) {
            #This won't execute on the final iteration
            wait-seconds
        }
    }

    # Wait for all scripts to finish and display an indeterminate progress bar 
    Write-ToLogAndConsole -Message "Waiting for all scripts to finish..." 
    $progress = 0 

    $progressId = 1
    # display a progress bar waiting for batch p to finish
    while ((Get-Process BatchRvt -ErrorAction SilentlyContinue | Where-Object {$_.HasExited -eq $false}).Count -gt 0) {
        Write-Progress -Id $progressId -Activity "Waiting for scripts to finish" -Status "Waiting" -PercentComplete $progress -CurrentOperation "Running Revit Batch Processor script(s)"
        $progress = ($progress + 10) % 100
        Start-Sleep -Seconds 2 
    } 

    # need this to make progress bar go away once finished
    Write-Progress -Id $progressId -Activity "Waiting for scripts to finish" -Status "Finished" -Completed

    Write-ToLogAndConsole -Message "Waiting for scripts to finish:  Done"
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