# Define paths
$solution1 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastUtils\duHastUtils.sln"
$solution2 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastRevitUtils\duHastRevitUtils.sln"
$solution3 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastRevitApplications\duHastRevitApplications.sln"
$solution4 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastApplications\duHastApplications.sln"
$solution5 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastUI\duHastUI.sln"
$solution6 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\duHastUICustomControls\duHastUICustomControls.sln"

$commonDir = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\_References\duHast"

$targetDirSolution5 = "C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\src\duHast\libs"

# Ask user for build configuration (Release or Debug)
$buildConfig = Read-Host "Enter build configuration (Release/Debug)"
if ($buildConfig -ne "Release" -and $buildConfig -ne "Debug") {
    Write-Host "Invalid configuration. Defaulting to Release."
    $buildConfig = "Release"
}

# Ensure MSBuild exists
$msbuildPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
if (!(Test-Path $msbuildPath)) {
    Write-Host "Error: MSBuild not found at $msbuildPath. Ensure Visual Studio is installed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Ensure target directories exist
$targetDirs = @($commonDir, $targetDirSolution5)
foreach ($dir in $targetDirs) {
    if (!(Test-Path $dir)) {
        Write-Host "Creating directory: $dir..."
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Clean up common directory
if (Test-Path $commonDir) {
    Write-Host "Removing contents of $commonDir..."
    Remove-Item "$commonDir\*" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2  # Small delay to ensure cleanup

    # Verify removal
    if ((Get-ChildItem -Path $commonDir).Count -eq 0) {
        Write-Host "✅ Successfully removed all contents from $commonDir."
    } else {
        Write-Host "⚠️ Warning: Some files may not have been removed from $commonDir."
    }
} else {
    Write-Host "Creating directory: $commonDir..."
    New-Item -ItemType Directory -Path $commonDir -Force | Out-Null

    # Verify creation
    if (Test-Path $commonDir) {
        Write-Host "Successfully created $commonDir."
    } else {
        Write-Host "Error: Failed to create $commonDir."
    }
}

# Function to extract solution directory
function Get-SolutionDir {
    param ($solutionPath)
    return Split-Path -Parent $solutionPath
}

# Function to find all project directories within a solution
function Get-ProjectDirs {
    param ($solutionPath)
    $solutionDir = Get-SolutionDir $solutionPath
    return Get-ChildItem -Path $solutionDir -Directory | Where-Object { Test-Path "$($_.FullName)\bin\x64\$buildConfig" }
}


# Function to build a solution
function Build-Solution {
    param ($solutionPath)
    Write-Host "Building $solutionPath in $buildConfig mode..."
    & "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" $solutionPath /p:Configuration=$buildConfig /p:Platform="x64"
}

# Function to copy DLLs to multiple destinations
function Copy-DLLs {
    param ($solutionPath, $destinationDirs)
    $projectDirs = Get-ProjectDirs $solutionPath

    foreach ($projectDir in $projectDirs) {
        $sourceDir = "$($projectDir.FullName)\bin\x64\$buildConfig"

        if (Test-Path $sourceDir) {
            foreach ($destDir in $destinationDirs) {
                Write-Host "Copying DLLs from $sourceDir to $destDir..."
                Copy-Item "$sourceDir\*.dll" -Destination $destDir -Force
            }
        } else {
            Write-Host "Warning: DLL directory not found for project $($projectDir.FullName)"
        }
    }
}

# Build and copy DLLs for Utils
Build-Solution $solution1
Copy-DLLs $solution1 @($commonDir)

# Build and copy DLLs for CustomControls
Build-Solution $solution6
Copy-DLLs $solution6 @($commonDir)

# Build and copy DLLs for RevitUtils
Build-Solution $solution2
Copy-DLLs $solution2 @($commonDir)

# Build Revit Applications only
Build-Solution $solution3

# Build duHastApplications only
Build-Solution $solution4

# Build and copy DLLs for UI → Target 3
Build-Solution $solution5
Copy-DLLs $solution5 @($targetDirSolution5)

Write-Host "Build and copy process completed!"
Read-Host "Press Enter to exit"
