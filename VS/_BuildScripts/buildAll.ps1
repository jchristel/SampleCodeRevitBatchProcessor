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

# Function to get current Git branch (optional, for display purposes)
function Get-CurrentBranch {
    try {
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $branch.Trim()
        } else {
            return "unknown"
        }
    } catch {
        return "unknown"
    }
}

# Determine base path from script location
$basePath = Get-BasePathFromLocation
Write-Host "Using base path: $basePath" -ForegroundColor Green

# Get current branch (for display only)
$currentBranch = Get-CurrentBranch
if ($currentBranch -ne "unknown") {
    Write-Host "Current Git branch: $currentBranch" -ForegroundColor Green
}

# Define paths using dynamic base path
$solution1 = "$basePath\VS\duHastUtils\duHastUtils.sln"
$solution2 = "$basePath\VS\duHastRevitUtils\duHastRevitUtils.sln"
$solution3 = "$basePath\VS\duHastRevitApplications\duHastRevitApplications.sln"
$solution4 = "$basePath\VS\duHastApplications\duHastApplications.sln"
$solution5 = "$basePath\VS\duHastUI\duHastUI.sln"
$solution6 = "$basePath\VS\duHastUICustomControls\duHastUICustomControls.sln"

$commonDir = "$basePath\VS\_References\duHast"
$targetDirSolution5 = "$basePath\src\duHast\lib"

# Verify that solutions exist
$solutions = @($solution1, $solution2, $solution3, $solution4, $solution5, $solution6)
foreach ($sol in $solutions) {
    if (!(Test-Path $sol)) {
        Write-Host "Warning: Solution not found: $sol" -ForegroundColor Yellow
    }
}

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
        Write-Host "Successfully removed all contents from $commonDir."
    } else {
        Write-Host "Warning: Some files may not have been removed from $commonDir."
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

# Function to restore packages
function Restore-Packages {
    param ($solutionPath)
    Write-Host "Restoring packages for $solutionPath..." -ForegroundColor Yellow
    
    & dotnet restore $solutionPath --force --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Package restore failed for $solutionPath" -ForegroundColor Red
        exit 1
    }
}

# Function to build a solution
function Build-Solution {
    param ($solutionPath)
    
    if (!(Test-Path $solutionPath)) {
        Write-Host "Warning: Solution not found: $solutionPath" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Building $solutionPath in $buildConfig mode..."
    
    # Restore packages first
    Restore-Packages $solutionPath
    
    # Clean first
    & $msbuildPath $solutionPath /t:Clean /p:Configuration=$buildConfig /p:Platform="x64"
    
    # Then build
    & $msbuildPath $solutionPath /p:Configuration=$buildConfig /p:Platform="x64"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed for $solutionPath" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Function to copy DLLs to multiple destinations
function Copy-DLLs {
    param ($solutionPath, $destinationDirs)
    
    if (!(Test-Path $solutionPath)) {
        Write-Host "Warning: Solution not found for DLL copy: $solutionPath" -ForegroundColor Yellow
        return
    }
    
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

Write-Host "Build and copy process completed for branch: $currentBranch!" -ForegroundColor Green
Write-Host "Base path used: $basePath" -ForegroundColor Green
Read-Host "Press Enter to exit"