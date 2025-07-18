

# lib directory
$sourceFolderLib="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\src"
$destinationFolderLib_one="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\Samples\pyRevit\Extensions\duHast-2025.extension\lib"



# Function to clean and copy files
function CleanAndCopy($source, $destination) {
    # Ensure the destination directory exists
    if (Test-Path $destination) {
        Remove-Item -Path "$destination\*" -Force -Recurse
    } else {
        New-Item -ItemType Directory -Path $destination | Out-Null
    }

    # Copy files from source to destination
    Copy-Item -Path "$source\*" -Destination $destination -Force -Recurse

    Write-Output "Files copied successfully from $source to $destination"
}

# Execute the function for duHast in pyRevit sample
CleanAndCopy $sourceFolderLib $destinationFolderLib_one

Write-Host "Deploy process completed!"
Read-Host "Press Enter to exit"