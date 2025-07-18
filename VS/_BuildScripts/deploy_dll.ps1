# Function to get current Git branch
function Get-CurrentBranch {
    try {
        $branch = git rev-parse --abbrev-ref HEAD
        if ($LASTEXITCODE -eq 0) {
            return $branch.Trim()
        } else {
            Write-Host "Error: Unable to determine Git branch. Make sure you're in a Git repository." -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Error: Git command failed. Make sure Git is installed and accessible." -ForegroundColor Red
        exit 1
    }
}

# Function to determine pyRevit extension name based on branch
function Get-PyRevitExtensionName {
    param ($branchName)
    
    # Check if branch starts with net8 or contains net8
    if ($branchName -match "^net8" -or $branchName -match "net8") {
        return "duHast-2025.extension"
    }
    # Check if branch starts with net48 or contains net48
    elseif ($branchName -match "^net48" -or $branchName -match "net48") {
        return "duHast-2024.extension"
    }
    # Default fallback - you can customize this logic
    else {
        Write-Host "Warning: Branch '$branchName' doesn't match expected patterns (net8*/net48*)." -ForegroundColor Yellow
        Write-Host "Available options:" -ForegroundColor Yellow
        Write-Host "1. duHast-2025.extension (net8)" -ForegroundColor Yellow
        Write-Host "2. duHast-2024.extension (net48)" -ForegroundColor Yellow
        
        $choice = Read-Host "Enter 1 or 2 to select extension manually"
        if ($choice -eq "1") {
            return "duHast-2025.extension"
        } elseif ($choice -eq "2") {
            return "duHast-2024.extension"
        } else {
            Write-Host "Invalid choice. Defaulting to duHast-2024.extension" -ForegroundColor Yellow
            return "duHast-2024.extension"
        }
    }
}

# Get current branch
$currentBranch = Get-CurrentBranch
Write-Host "Current Git branch: $currentBranch" -ForegroundColor Green

# Determine pyRevit extension name
$pyRevitExtensionName = Get-PyRevitExtensionName $currentBranch
Write-Host "Using pyRevit extension: $pyRevitExtensionName" -ForegroundColor Green

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
$pushItBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastRevitApplications\PushIt"
$atTheLibraryBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastRevitApplications\AtTheLibrary"
$uiPDFDWGExporterBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUI\PDFDWGExporterUI"
$uiPDFDWGExporterSelectionBasePath = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastUI\PDFDWGExporterSelectionUI"

# Determine correct build paths using user-selected configuration
$pushItBuildPath = Get-BuildType $pushItBasePath $buildConfig
$atTheLibraryBuildPath = Get-BuildType $atTheLibraryBasePath $buildConfig
$uiPDFDWGExporterBuildPath = Get-BuildType $uiPDFDWGExporterBasePath $buildConfig
$uiPDFDWGExporterSelectionBuildPath = Get-BuildType $uiPDFDWGExporterSelectionBasePath $buildConfig

# Define source and destination paths for PushIt (using dynamic extension name)
$sourceFilePushIt = "$pushItBuildPath\PushIt.dll"
$destinationFilePushIt = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\Samples\pyRevit\Extensions\$pyRevitExtensionName\duHast.tab\PushIt.panel\bin\PushIt.dll"

# Copy PushIt DLL
Copy-Item -Path $sourceFilePushIt -Destination $destinationFilePushIt -Force
Write-Output "File copied successfully from $sourceFilePushIt to $destinationFilePushIt"

# Define source and destination paths for AtTheLibrary (using dynamic extension name)
$sourceFileAtTheLibrary = "$atTheLibraryBuildPath\AtTheLibrary.dll"
$destinationAtTheLibrary = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\Samples\pyRevit\Extensions\$pyRevitExtensionName\duHast.tab\Families.panel\bin\AtTheLibrary.dll"

# Copy AtTheLibrary DLL
Copy-Item -Path $sourceFileAtTheLibrary -Destination $destinationAtTheLibrary -Force
Write-Output "File copied successfully from $sourceFileAtTheLibrary to $destinationAtTheLibrary"

# copy Revit Async DLL to reference folder from where it will get copied to other locations
$sourceFileRevitAsync = "$pushItBuildPath\Revit.Async.dll"
$destinationFileRevitAsync = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\_References\duHast\Revit.Async.dll"

# Copy Revit Async DLL
Copy-Item -Path $sourceFileRevitAsync -Destination $destinationFileRevitAsync -Force
Write-Output "File copied successfully from $sourceFileRevitAsync to $destinationFileRevitAsync"

# copy UI dlls
$sourceFileUI = "$uiPDFDWGExporterBuildPath\PDFDWGExporterUI.dll"
$destinationFileUI = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\_References\duHast\PDFDWGExporterUI.dll"

Copy-Item -Path $sourceFileUI -Destination $destinationFileUI -Force
Write-Output "File copied successfully from $sourceFileUI to $destinationFileUI"

# copy UI dlls
$sourceFileUISelection = "$uiPDFDWGExporterSelectionBuildPath\PDFDWGExporterSelectionUI.dll"
$destinationFileUISelection = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\_References\duHast\PDFDWGExporterSelectionUI.dll"

Copy-Item -Path $sourceFileUISelection -Destination $destinationFileUISelection -Force
Write-Output "File copied successfully from $sourceFileUISelection to $destinationFileUISelection"

# lib directory
$sourceFolderLib="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\_References\duHast"
$destinationFolderLib_one="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\Samples\pyRevit\Extensions\$pyRevitExtensionName\duHast.tab\bin"
$destinationFolderLib_two="C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\src\duHast\lib"

# Function to clean and copy files
function CleanAndCopy($source, $destination) {
    # Ensure the destination directory exists
    if (Test-Path $destination) {
        Remove-Item -Path "$destination\*" -Force -Recurse
    } else {
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
    }

    # Copy files from source to destination
    Copy-Item -Path "$source\*" -Destination $destination -Force -Recurse

    Write-Output "Files copied successfully from $source to $destination"
}

# Execute the function for both destinations
CleanAndCopy $sourceFolderLib $destinationFolderLib_one
CleanAndCopy $sourceFolderLib $destinationFolderLib_two

Write-Host "Deploy process completed for branch: $currentBranch using extension: $pyRevitExtensionName!" -ForegroundColor Green
Read-Host "Press Enter to exit"