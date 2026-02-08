
# version number for all dlls
$dllVersion=".25.0.0.3"

# Function to determine base path from script location
function Get-BasePathFromLocation {
    # Get the directory where this script is located
    $scriptPath = $PSScriptRoot
    Write-Host "Script is located at: $scriptPath" -ForegroundColor Cyan
    
    # Navigate up to find the repo root
    $currentDir = $scriptPath
    $repoRoot = $null
    
    # Look for the repo root by checking for specific patterns
    while ($currentDir -and $currentDir.Length -gt 10) {
        $dirName = Split-Path $currentDir -Leaf
        
        if ($dirName -match "SampleCodeRevitBatchProcessor") {
            $repoRoot = $currentDir
            break
        }
        
        # Move up one directory
        $currentDir = Split-Path $currentDir -Parent
    }
    
    if ($repoRoot) {
        Write-Host "Auto-detected repo root: $repoRoot" -ForegroundColor Green
        return $repoRoot
    } else {
        Write-Host "Could not auto-detect repo root from script location." -ForegroundColor Yellow
        Write-Host "Script path: $scriptPath" -ForegroundColor Yellow
        
        # Fallback: ask user to choose
        Write-Host "Please select the correct repo:" -ForegroundColor Yellow
        Write-Host "1. NET8 repo (SampleCodeRevitBatchProcessor-NET8)" -ForegroundColor Yellow
        Write-Host "2. NET48 repo (SampleCodeRevitBatchProcessor-NET48)" -ForegroundColor Yellow
        
        $choice = Read-Host "Enter 1 or 2"
        if ($choice -eq "1") {
            return "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8"
        } elseif ($choice -eq "2") {
            return "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET48"
        } else {
            Write-Host "Invalid choice. Defaulting to NET48" -ForegroundColor Yellow
            return "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET48"
        }
    }
}


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

# Determine base path from script location
$basePath = Get-BasePathFromLocation
Write-Host "Using base path: $basePath" -ForegroundColor Green

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
$pushItBasePath = "$basePath\VS\duHastRevitApplications\PushIt"
$atTheLibraryBasePath = "$basePath\VS\duHastRevitApplications\AtTheLibrary"
$uiPDFDWGExporterBasePath = "$basePath\VS\duHastUI\PDFDWGExporterUI"
$uiPDFDWGExporterSelectionBasePath = "$basePath\VS\duHastUI\PDFDWGExporterSelectionUI"
$uiFamilyReloaderBasePath = "$basePath\VS\duHastUI\FamilyReloaderUI"
$uiDocManagerSettingsBasePath = "$basePath\VS\duHastUI\DocManagerSettingsUI"

# Determine correct build paths using user-selected configuration
$pushItBuildPath = Get-BuildType $pushItBasePath $buildConfig
$atTheLibraryBuildPath = Get-BuildType $atTheLibraryBasePath $buildConfig
$uiPDFDWGExporterBuildPath = Get-BuildType $uiPDFDWGExporterBasePath $buildConfig
$uiPDFDWGExporterSelectionBuildPath = Get-BuildType $uiPDFDWGExporterSelectionBasePath $buildConfig
$uiFamilyReloaderBuildPath = Get-BuildType $uiFamilyReloaderBasePath $buildConfig
$uiDocManagerSettingsBuildPath = Get-BuildType $uiDocManagerSettingsBasePath $buildConfig


# Define source and destination paths for PushIt (using dynamic extension name)
$sourceFilePushIt = "$pushItBuildPath\PushIt$dllVersion.dll"
$destinationFilePushIt = "$basePath\VS\_References\duHast\PushIt$dllVersion.dll"

# Copy PushIt DLL
Copy-Item -Path $sourceFilePushIt -Destination $destinationFilePushIt -Force
Write-Output "File copied successfully from $sourceFilePushIt to $destinationFilePushIt"

# Define source and destination paths for AtTheLibrary (using dynamic extension name)
$sourceFileAtTheLibrary = "$atTheLibraryBuildPath\AtTheLibrary$dllVersion.dll"
$destinationAtTheLibrary = "$basePath\VS\_References\duHast\AtTheLibrary$dllVersion.dll"

# Copy AtTheLibrary DLL
Copy-Item -Path $sourceFileAtTheLibrary -Destination $destinationAtTheLibrary -Force
Write-Output "File copied successfully from $sourceFileAtTheLibrary to $destinationAtTheLibrary"

# copy Revit Async DLL to reference folder from where it will get copied to other locations
$sourceFileRevitAsync = "$pushItBuildPath\Revit.Async.dll"
$destinationFileRevitAsync = "$basePath\VS\_References\duHast\Revit.Async.dll"

# Copy Revit Async DLL
Copy-Item -Path $sourceFileRevitAsync -Destination $destinationFileRevitAsync -Force
Write-Output "File copied successfully from $sourceFileRevitAsync to $destinationFileRevitAsync"

# copy UI dlls
$sourceFileUI = "$uiPDFDWGExporterBuildPath\PDFDWGExporterUI$dllVersion.dll"
$destinationFileUI = "$basePath\VS\_References\duHast\PDFDWGExporterUI$dllVersion.dll"

Copy-Item -Path $sourceFileUI -Destination $destinationFileUI -Force
Write-Output "File copied successfully from $sourceFileUI to $destinationFileUI"

# copy UI dlls
$sourceFileUISelection = "$uiPDFDWGExporterSelectionBuildPath\PDFDWGExporterSelectionUI$dllVersion.dll"
$destinationFileUISelection = "$basePath\VS\_References\duHast\PDFDWGExporterSelectionUI$dllVersion.dll"

Copy-Item -Path $sourceFileUISelection -Destination $destinationFileUISelection -Force
Write-Output "File copied successfully from $sourceFileUISelection to $destinationFileUISelection"

# copy reloader UI dlls
$sourceFileFamilyReloaderUI = "$uiFamilyReloaderBuildPath\FamilyReloaderUI$dllVersion.dll"
$destinationFileFamilyReloaderUI = "$basePath\VS\_References\duHast\FamilyReloaderUI$dllVersion.dll"
# Copy Family Reloader UI DLL
Copy-Item -Path $sourceFileFamilyReloaderUI -Destination $destinationFileFamilyReloaderUI -Force
Write-Output "File copied successfully from $sourceFileFamilyReloaderUI to $destinationFileFamilyReloaderUI"

# copy doc manager settings UI dlls
$sourceFileDocManagerSettingsUI = "$uiDocManagerSettingsBuildPath\DocManagerSettingsUI$dllVersion.dll"
$destinationFileDocManagerSettingsUI = "$basePath\VS\_References\duHast\DocManagerSettingsUI$dllVersion.dll"
# Copy Doc Manager Settings UI DLL
Copy-Item -Path $sourceFileDocManagerSettingsUI -Destination $destinationFileDocManagerSettingsUI -Force
Write-Output "File copied successfully from $sourceFileDocManagerSettingsUI to $destinationFileDocManagerSettingsUI"

# lib directory
$sourceFolderLib="$basePath\VS\_References\duHast"
$destinationFolderLib_one="$basePath\Samples\pyRevit\Extensions\$pyRevitExtensionName\bin"
$destinationFolderLib_two="$basePath\src\duHast\lib"

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