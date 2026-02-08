

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

# lib directory
$sourceFolderLib="$basePath\src"
$destinationFolderLib_one="$basePath\Samples\pyRevit\Extensions\$pyRevitExtensionName\lib"



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