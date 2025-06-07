

# Ask user for build configuration (Release or Debug)
$buildConfig = Read-Host "Enter build configuration (Release/Debug)"
if ($buildConfig -ne "Release" -and $buildConfig -ne "Debug") {
    Write-Host "Invalid configuration. Defaulting to Release."
    $buildConfig = "Release"
}
# Function to determine build type based on user input
function Get-BuildType($basePath, $config) {
    $buildPath = "$basePath\bin\x64\$config"

    if (Test-Path $buildPath) {
        return $buildPath
    } else {
        Write-Output "Error: $config folder not found for $basePath!"
        exit 1
    }
}

# Define base paths for PushIt and AtTheLibrary
$pushItBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastRevitApplications\PushIt"
$atTheLibraryBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastRevitApplications\AtTheLibrary"
$uiPDFDWGExporterBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastUI\PDFDWGExporterUI"
$uiPDFDWGExporterSelectionBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastUI\PDFDWGExporterSelectionUI"


# Determine correct build paths using user-selected configuration
$pushItBuildPath = Get-BuildType $pushItBasePath $buildConfig
$atTheLibraryBuildPath = Get-BuildType $atTheLibraryBasePath $buildConfig
$uiPDFDWGExporterBuildPath = Get-BuildType $uiPDFDWGExporterBasePath $buildConfig
$uiPDFDWGExporterSelectionBuildPath = Get-BuildType $uiPDFDWGExporterSelectionBasePath $buildConfig

# Define source and destination paths for PushIt
$sourceFilePushIt = "$pushItBuildPath\PushIt.dll"
$destinationFilePushIt = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\pyRevit\Extensions\duHast.extension\duHast.tab\PushIt.panel\bin\PushIt.dll"

# Copy PushIt DLL
Copy-Item -Path $sourceFilePushIt -Destination $destinationFilePushIt -Force
Write-Output "File copied successfully from $sourceFilePushIt to $destinationFilePushIt"

# Define source and destination paths for AtTheLibrary
$sourceFileAtTheLibrary = "$atTheLibraryBuildPath\AtTheLibrary.dll"
$destinationAtTheLibrary = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\pyRevit\Extensions\duHast.extension\duHast.tab\Families.panel\bin\AtTheLibrary.dll"

# Copy AtTheLibrary DLL
Copy-Item -Path $sourceFileAtTheLibrary -Destination $destinationAtTheLibrary -Force
Write-Output "File copied successfully from $sourceFileAtTheLibrary to $destinationAtTheLibrary"

# copy Revit Async DLL to reference folder from where it will get copied to other locations
$sourceFileRevitAsync = "$pushItBuildPath\Revit.Async.dll"
$destinationFileRevitAsync = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\_References\duHast\Revit.Async.dll"

# Copy Revit Async DLL
Copy-Item -Path $sourceFileRevitAsync -Destination $destinationFileRevitAsync -Force
Write-Output "File copied successfully from $sourceFileRevitAsync to $destinationFileRevitAsync"


# copy UI dlls
$sourceFileUI = "$uiPDFDWGExporterBuildPath\PDFDWGExporterUI.dll"
$destinationFileUI = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\_References\duHast\PDFDWGExporterUI.dll"

Copy-Item -Path $sourceFileUI -Destination $destinationFileUI -Force
Write-Output "File copied successfully from $sourceFileUI to $destinationFileUI"

# copy UI dlls
$sourceFileUISelection = "$uiPDFDWGExporterSelectionBuildPath\PDFDWGExporterSelectionUI.dll"
$destinationFileUISelection = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\_References\duHast\PDFDWGExporterSelectionUI.dll"

Copy-Item -Path $sourceFileUISelection -Destination $destinationFileUISelection -Force
Write-Output "File copied successfully from $sourceFileUISelection to $destinationFileUISelection"


# lib directory
$sourceFolderLib="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\_References\duHast"
$destinationFolderLib_one="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\pyRevit\Extensions\duHast.extension\bin"
$destinationFolderLib_two="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\src\duHast\lib"

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

# Execute the function for both destinations
CleanAndCopy $sourceFolderLib $destinationFolderLib_one
CleanAndCopy $sourceFolderLib $destinationFolderLib_two

Write-Host "Deploy process completed!"
Read-Host "Press Enter to exit"