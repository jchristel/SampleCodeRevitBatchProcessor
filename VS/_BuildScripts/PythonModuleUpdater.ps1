# PythonModuleUpdater.ps1
# PowerShell module for updating Python files with version references
# Part of the cascading DLL version update system

# Function to determine Python directory based on branch and base path
function Get-PythonDirectoryPath {
    param(
        [string]$BasePath,
        [string]$BranchName
    )
    
    # Default relative path from base
    $relativePythonPath = "src\duHast\Revit\NetSupport"
    
    # Build the full path
    $pythonPath = Join-Path $BasePath $relativePythonPath
    
    # Verify the path exists
    if (Test-Path $pythonPath) {
        Write-Host "Found Python directory: $pythonPath" -ForegroundColor Cyan
        return $pythonPath
    } else {
        Write-Host "Warning: Python directory not found at: $pythonPath" -ForegroundColor Yellow
        
        # Try alternative common locations
        $alternativePaths = @(
            "$BasePath\src\duHast\Revit\NetSupport",
            "$BasePath\duHast\Revit\NetSupport", 
            "$BasePath\Samples\duHast\Revit\NetSupport"
        )
        
        foreach ($altPath in $alternativePaths) {
            if (Test-Path $altPath) {
                Write-Host "Found Python directory at alternative location: $altPath" -ForegroundColor Green
                return $altPath
            }
        }
        
        Write-Host "Could not locate Python directory automatically." -ForegroundColor Yellow
        $manualPath = Read-Host "Enter full path to Python directory (or press Enter to skip Python updates)"
        
        if ($manualPath -and (Test-Path $manualPath)) {
            return $manualPath
        } else {
            return $null
        }
    }
}

# Function to update Python files with version references
function Update-PythonFiles {
    param(
        [string]$PythonDirectory,
        [string]$OldVersion,
        [string]$NewVersion,
        [switch]$WhatIf
    )
    
    if (-not $PythonDirectory -or -not (Test-Path $PythonDirectory)) {
        Write-Host "Skipping Python updates - directory not found or not specified" -ForegroundColor Yellow
        return 0
    }
    
    $changesCount = 0
    Write-Host "Processing Python files in: $PythonDirectory" -ForegroundColor Yellow
    
    # Find all Python files recursively
    Get-ChildItem -Path $PythonDirectory -Recurse -Include "*.py", "*.pyw" | ForEach-Object {
        $filePath = $_.FullName
        $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
        $fileChanged = $false
        
        if ($content) {
            # Pattern 1: Direct DLL_VERSION assignment
            # Matches: DLL_VERSION = ".25.0.0.1" or DLL_VERSION = '.25.0.0.1'
            $dllVersionPattern = '(DLL_VERSION\s*=\s*["\x27])([^"\x27]*?)(\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(["\x27])'
            if ($content -match $dllVersionPattern) {
                $content = $content -replace $dllVersionPattern, "`$1`$2.$NewVersion`$4"
                $fileChanged = $true
                Write-Host "    Found DLL_VERSION assignment in $($_.Name)" -ForegroundColor Magenta
            }
            
            if ($fileChanged -and -not $WhatIf) {
                Set-Content -Path $filePath -Value $content -NoNewline
                $changesCount++
                Write-Host "    [PY] $($_.Name)" -ForegroundColor Cyan
            } elseif ($fileChanged) {
                $changesCount++
                Write-Host "    [PY] $($_.Name) (PREVIEW)" -ForegroundColor Cyan
            }
        }
    }
    
    if ($changesCount -eq 0) {
        Write-Host "    No Python files needed updating" -ForegroundColor Gray
    } else {
        Write-Host "    Updated $changesCount Python files" -ForegroundColor Green
    }
    
    return $changesCount
}

# Function to validate Python module structure and show current versions
function Test-PythonModuleVersions {
    param(
        [string]$PythonDirectory,
        [string]$ExpectedVersion
    )
    
    if (-not $PythonDirectory -or -not (Test-Path $PythonDirectory)) {
        Write-Host "Python directory not available for validation" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "`nValidating Python module versions in: $PythonDirectory" -ForegroundColor Cyan
    
    $foundVersions = @()
    $versionPattern = '\.([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'
    
    Get-ChildItem -Path $PythonDirectory -Recurse -Include "*.py", "*.pyw" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            # Look for DLL_VERSION assignments
            if ($content -match 'DLL_VERSION\s*=\s*["\x27]([^"\x27]+)["\x27]') {
                $version = $Matches[1]
                $foundVersions += @{
                    File = $_.Name
                    Version = $version
                    Type = "DLL_VERSION"
                }
            }
            
            # Look for direct version references in strings
            $versionMatches = [regex]::Matches($content, $versionPattern)
            foreach ($match in $versionMatches) {
                $version = $match.Groups[1].Value
                $foundVersions += @{
                    File = $_.Name
                    Version = ".$version"
                    Type = "Direct Reference"
                }
            }
        }
    }
    
    if ($foundVersions.Count -eq 0) {
        Write-Host "    No version references found in Python files" -ForegroundColor Gray
        return $true
    }
    
    # Group by version and show summary
    $versionGroups = $foundVersions | Group-Object Version
    foreach ($group in $versionGroups) {
        $version = $group.Name
        $count = $group.Count
        $isExpected = $version -eq $ExpectedVersion
        $color = if ($isExpected) { "Green" } else { "Yellow" }
        
        Write-Host "    Version $version`: $count references" -ForegroundColor $color
        if (-not $isExpected -and $ExpectedVersion) {
            Write-Host "      (Expected: $ExpectedVersion)" -ForegroundColor Gray
        }
        
        # Show first few files for each version
        $group.Group | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.File) ($($_.Type))" -ForegroundColor Gray
        }
        
        if ($group.Count -gt 3) {
            Write-Host "      ... and $($group.Count - 3) more" -ForegroundColor Gray
        }
    }
    
    return $true
}

# Enhanced function to update Python modules (integrates with main process)
function Update-PythonModules {
    param(
        [string]$BasePath,
        [string]$BranchName,
        [string]$OldVersion,
        [string]$NewVersion,
        [switch]$WhatIf
    )
    
    Write-Host "`n=== Processing Python Modules ===" -ForegroundColor Magenta
    
    # Get the Python directory path
    $pythonDir = Get-PythonDirectoryPath -BasePath $BasePath -BranchName $BranchName
    
    if (-not $pythonDir) {
        Write-Host "Skipping Python module updates" -ForegroundColor Yellow
        return 0
    }
    
    # Show current state before changes
    Write-Host "`nCurrent Python module state:" -ForegroundColor Yellow
    Test-PythonModuleVersions -PythonDirectory $pythonDir -ExpectedVersion $OldVersion
    
    # Update the Python files
    $changeCount = Update-PythonFiles -PythonDirectory $pythonDir -OldVersion $OldVersion -NewVersion $NewVersion -WhatIf:$WhatIf
    
    # Show state after changes (if not in preview mode)
    if (-not $WhatIf -and $changeCount -gt 0) {
        Write-Host "`nPython module state after update:" -ForegroundColor Yellow
        Test-PythonModuleVersions -PythonDirectory $pythonDir -ExpectedVersion $NewVersion
    }
    
    return $changeCount
}

# Export functions for use in other scripts
Export-ModuleMember -Function Get-PythonDirectoryPath, Update-PythonFiles, Test-PythonModuleVersions, Update-PythonModules