

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

# Function to stamp the deployed copy with the commit it was taken from.
#
# A copy in an extension's lib folder is not in git, so without this nothing on
# a machine says WHICH duHast is installed there -- and duHast decides what an
# export means (an item's level, a door's footprint, whether a hole in a floor
# is a hole), so "duHast is present" is not the question anyone needs answered
# when an export looks wrong. The file is written into the DEPLOYED copy only;
# src\duHast is deliberately left unstamped, so a copy carrying no
# _build_info.py is simply one nobody deployed and reports as "unknown".
#
# Pure ASCII and both python 2 and 3, because pyRevit runs this under
# IronPython 2.7, which refuses to parse a non-ASCII source file at all.
function Write-BuildInfo($destination, $repoRoot, $branchName) {
    $commit = "unknown"
    $dirty = $false

    Push-Location $repoRoot
    try {
        $sha = git rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0 -and $sha) {
            $commit = $sha.Trim()
            # Scoped to src\duHast: an edit elsewhere in this repo does not
            # make the python that was copied any less the committed python.
            $changes = git status --porcelain -- src/duHast 2>$null
            $dirty = [bool]$changes
        }
    } catch {
        Write-Host "Warning: could not read the commit, stamping it as unknown." -ForegroundColor Yellow
    } finally {
        Pop-Location
        # A failed git probe is an expected outcome here, not the script's
        # result -- without this reset a machine with no git ends the whole
        # deploy on git's exit code, having deployed perfectly well.
        $global:LASTEXITCODE = 0
    }

    $template = @'
"""Records which duHast this copy is, and what deployed it.

Written into the copy, never into the source tree: a duHast with no
_build_info.py is one nobody deployed, which reads as "unknown" rather than
as an error. Read it through describe() so every caller words it the same.
"""

COMMIT = "__COMMIT__"
DIRTY = __DIRTY__
BRANCH = "__BRANCH__"
BUILT_AT = "__BUILT_AT__"
BUILT_BY = "__BUILT_BY__"


def describe():
    """One line naming this copy, for a log or a tool's own output.

    DIRTY matters as much as the commit: a deploy from an edited working tree
    is not the commit it names, and saying so here is cheaper than working it
    out later from an export that disagrees with the code.
    """
    if not COMMIT or COMMIT == "unknown":
        return "unknown"
    text = COMMIT[:8]
    if DIRTY:
        text += "-dirty"
    if BRANCH and BRANCH != "unknown":
        text += " (" + BRANCH + ")"
    return text
'@

    if (-not $branchName) { $branchName = "unknown" }

    $content = $template.
        Replace("__COMMIT__", $commit).
        Replace("__DIRTY__", $(if ($dirty) { "True" } else { "False" })).
        Replace("__BRANCH__", $branchName).
        Replace("__BUILT_AT__", (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")).
        Replace("__BUILT_BY__", "updateDuHastInPyRevitSample.ps1")

    # LF and no BOM: IronPython is happy either way, but a BOM is a non-ASCII
    # byte in a file whose whole point is to be importable.
    $content = $content.Replace("`r`n", "`n") + "`n"
    $path = Join-Path $destination "_build_info.py"
    [System.IO.File]::WriteAllText($path, $content, (New-Object System.Text.UTF8Encoding($false)))

    $suffix = ""
    if ($dirty) { $suffix = "-dirty" }
    Write-Host "Stamped duHast as $($commit.Substring(0, [Math]::Min(8, $commit.Length)))$suffix ($branchName)" -ForegroundColor Green
}

# Execute the function for duHast in pyRevit sample
CleanAndCopy $sourceFolderLib $destinationFolderLib_one

# Stamp AFTER the copy: CleanAndCopy empties the destination first, so a file
# written before it would not survive.
Write-BuildInfo "$destinationFolderLib_one\duHast" $basePath $currentBranch

Write-Host "Deploy process completed!"
Read-Host "Press Enter to exit"