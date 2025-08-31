# Cascading DLL Version Update Script
# Updates version numbers in dependency order: builds each solution after updating its references

param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion,
    [string]$OldVersion,
    [switch]$WhatIf,
    [int]$StartFromSolution = 1, # Which solution to start from (1-6)
    [string]$BuildConfig = "Release"
)

# Function to determine base path from script location
function Get-BasePathFromLocation {
    $scriptPath = $PSScriptRoot
    Write-Host "Script is located at: $scriptPath" -ForegroundColor Cyan
    
    $currentDir = $scriptPath
    $repoRoot = $null
    
    while ($currentDir -and $currentDir.Length -gt 10) {
        $dirName = Split-Path $currentDir -Leaf
        if ($dirName -match "SampleCodeRevitBatchProcessor") {
            $repoRoot = $currentDir
            break
        }
        $currentDir = Split-Path $currentDir -Parent
    }
    
    if ($repoRoot) {
        Write-Host "Auto-detected repo root: $repoRoot" -ForegroundColor Green
        return $repoRoot
    } else {
        Write-Host "Could not auto-detect repo root from script location." -ForegroundColor Yellow
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

# Function to get current DLL version
function Get-CurrentDllVersion {
    param(
        [string]$BasePath,
        [string]$BuildConfig = "Release"
    )
    
    $commonDir = "$BasePath\VS\_References\duHast"
    
    if (Test-Path $commonDir) {
        $dllFiles = Get-ChildItem -Path $commonDir -Filter "*.dll" | 
                   Where-Object { $_.Name -match "duHast.*(\d+\.\d+\.\d+\.\d+)\.dll" } |
                   Sort-Object Name -Descending |
                   Select-Object -First 1
        
        if ($dllFiles -and $dllFiles.Name -match "(\d+\.\d+\.\d+\.\d+)") {
            return $Matches[1]
        }
    }
    
    return $null
}

# Function to update version in a specific solution
function Update-SolutionVersion {
    param(
        [string]$SolutionPath,
        [string]$OldVersion,
        [string]$NewVersion,
        [switch]$WhatIf
    )
    
    $changesCount = 0
    $solutionName = Split-Path $SolutionPath -Leaf
    
    Write-Host "Processing solution: $solutionName" -ForegroundColor Yellow
    
    if (-not (Test-Path $SolutionPath)) {
        Write-Host "Warning: Solution path not found: $SolutionPath" -ForegroundColor Yellow
        return 0
    }
    
    $solutionDir = Split-Path $SolutionPath -Parent
    
    # Update .csproj files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.csproj" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "  [CSPROJ] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update App.config files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "App.config" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "  [CONFIG] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update XAML files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.xaml" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "  [XAML] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update C# and AssemblyInfo files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.cs" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "  [CS] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    return $changesCount
}

# Function to build a solution (from original script)
function Build-Solution {
    param ($solutionPath)
    
    if (!(Test-Path $solutionPath)) {
        Write-Host "Warning: Solution not found: $solutionPath" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "Building $solutionPath in $BuildConfig mode..." -ForegroundColor Yellow
    
    # Ensure MSBuild exists
    $msbuildPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    if (!(Test-Path $msbuildPath)) {
        Write-Host "Error: MSBuild not found at $msbuildPath" -ForegroundColor Red
        return $false
    }
    
    # Restore packages
    & dotnet restore $solutionPath --force --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Package restore failed for $solutionPath" -ForegroundColor Red
        return $false
    }
    
    # Clean and build
    & $msbuildPath $solutionPath /t:Clean /p:Configuration=$BuildConfig /p:Platform="x64"
    & $msbuildPath $solutionPath /p:Configuration=$BuildConfig /p:Platform="x64"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed for $solutionPath" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to copy DLLs (from original script)
function Copy-DLLs {
    param ($solutionPath, $destinationDirs)
    
    if (!(Test-Path $solutionPath)) {
        return
    }
    
    $solutionDir = Split-Path -Parent $solutionPath
    $projectDirs = Get-ChildItem -Path $solutionDir -Directory | 
                  Where-Object { Test-Path "$($_.FullName)\bin\x64\$BuildConfig" }
    
    foreach ($projectDir in $projectDirs) {
        $sourceDir = "$($projectDir.FullName)\bin\x64\$BuildConfig"
        if (Test-Path $sourceDir) {
            foreach ($destDir in $destinationDirs) {
                Write-Host "Copying DLLs from $sourceDir to $destDir..." -ForegroundColor Cyan
                Copy-Item "$sourceDir\*.dll" -Destination $destDir -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Function to update pyRevit YAML files
function Update-PyRevitYamlFiles {
    param(
        [string]$BasePath,
        [string]$OldVersion,
        [string]$NewVersion,
        [switch]$WhatIf
    )
    
    $pyRevitYamlFiles = @(
        "$BasePath\Samples\pyRevit\Extensions\duHast-2024.extension\duHast.tab\Families.panel\AtTheLibrary.invokebutton\bundle.yaml",
        "$BasePath\Samples\pyRevit\Extensions\duHast-2024.extension\duHast.tab\PushIt.panel\PushIt.invokebutton\bundle.yaml"
    )
    
    $changesCount = 0
    Write-Host "`nProcessing pyRevit YAML files:" -ForegroundColor Yellow
    
    foreach ($yamlFile in $pyRevitYamlFiles) {
        if (Test-Path $yamlFile) {
            $content = Get-Content $yamlFile -Raw -ErrorAction SilentlyContinue
            if ($content -and $content -match $OldVersion) {
                if (-not $WhatIf) {
                    $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                    Set-Content -Path $yamlFile -Value $newContent -NoNewline
                }
                $fileName = Split-Path $yamlFile -Leaf
                $parentDir = Split-Path (Split-Path $yamlFile -Parent) -Leaf
                Write-Host "  [YAML] $parentDir\$fileName" -ForegroundColor Cyan
                $changesCount++
            }
        } else {
            Write-Host "  Warning: pyRevit YAML file not found: $yamlFile" -ForegroundColor Yellow
        }
    }
    
    return $changesCount
}

# Function to save version change history
function Save-VersionChange {
    param(
        [string]$OldVersion,
        [string]$NewVersion,
        [string]$BasePath,
        [string]$ChangeLog = "version_changes.json"
    )
    
    $changeLogPath = Join-Path $BasePath $ChangeLog
    
    $change = @{
        DateTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        FromVersion = $OldVersion
        ToVersion = $NewVersion
        Branch = git rev-parse --abbrev-ref HEAD 2>$null
        BasePath = $BasePath
    }
    
    $history = @()
    if (Test-Path $changeLogPath) {
        try {
            $history = Get-Content $changeLogPath | ConvertFrom-Json
        } catch {
            $history = @()
        }
    }
    
    $history += $change
    $history | ConvertTo-Json -Depth 3 | Set-Content $changeLogPath
    Write-Host "Version change logged to $changeLogPath" -ForegroundColor Green
}

# Function to process solutions in cascading order
function Invoke-CascadingVersionUpdate {
    param(
        [string]$BasePath,
        [string]$OldVersion,
        [string]$NewVersion,
        [int]$StartFromSolution = 1,
        [switch]$WhatIf
    )
    
    # Define solutions in dependency order
    $solutions = @(
        @{ 
            Name = "duHastUtils"
            Path = "$BasePath\VS\duHastUtils\duHastUtils.sln"
            CopyTo = @("$BasePath\VS\_References\duHast")
            Description = "Base utilities (no dependencies)"
        },
        @{ 
            Name = "duHastUICustomControls"
            Path = "$BasePath\VS\duHastUICustomControls\duHastUICustomControls.sln"
            CopyTo = @("$BasePath\VS\_References\duHast")
            Description = "Custom controls (depends on Utils)"
        },
        @{ 
            Name = "duHastRevitUtils"
            Path = "$BasePath\VS\duHastRevitUtils\duHastRevitUtils.sln"
            CopyTo = @("$BasePath\VS\_References\duHast")
            Description = "Revit utilities (depends on Utils + CustomControls)"
        },
        @{ 
            Name = "duHastRevitApplications"
            Path = "$BasePath\VS\duHastRevitApplications\duHastRevitApplications.sln"
            CopyTo = @()
            Description = "Revit applications (depends on RevitUtils)"
        },
        @{ 
            Name = "duHastApplications"
            Path = "$BasePath\VS\duHastApplications\duHastApplications.sln"
            CopyTo = @()
            Description = "General applications (depends on Utils)"
        },
        @{ 
            Name = "duHastUI"
            Path = "$BasePath\VS\duHastUI\duHastUI.sln"
            CopyTo = @("$BasePath\src\duHast\lib")
            Description = "UI components (depends on most others)"
        }
    )
    
    # Ensure target directories exist
    $commonDir = "$BasePath\VS\_References\duHast"
    $targetDirSolution5 = "$BasePath\src\duHast\lib"
    
    @($commonDir, $targetDirSolution5) | ForEach-Object {
        if (!(Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }
    
    # Clean common directory before starting
    if (Test-Path $commonDir) {
        Write-Host "Cleaning reference directory: $commonDir" -ForegroundColor Yellow
        if (-not $WhatIf) {
            Remove-Item "$commonDir\*" -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "`n=== Cascading Version Update Process ===" -ForegroundColor Magenta
    Write-Host "Starting from solution $StartFromSolution" -ForegroundColor Cyan
    
    for ($i = $StartFromSolution - 1; $i -lt $solutions.Count; $i++) {
        $solution = $solutions[$i]
        $stepNumber = $i + 1
        
        Write-Host "`n--- Step $stepNumber`: $($solution.Name) ---" -ForegroundColor Magenta
        Write-Host $solution.Description -ForegroundColor Gray
        
        # Step 1: Update version references in this solution
        Write-Host "`n1. Updating version references..." -ForegroundColor Yellow
        $changeCount = Update-SolutionVersion -SolutionPath $solution.Path -OldVersion $OldVersion -NewVersion $NewVersion -WhatIf:$WhatIf
        
        if ($changeCount -eq 0) {
            Write-Host "   No version references to update in this solution" -ForegroundColor Gray
        }
        
        # Step 2: Build the solution
        if (-not $WhatIf) {
            Write-Host "`n2. Building solution..." -ForegroundColor Yellow
            $buildResult = Build-Solution -SolutionPath $solution.Path
            if (-not $buildResult) {
                Write-Host "Build failed for $($solution.Name)! Stopping cascade." -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "`n2. [PREVIEW] Would build solution..." -ForegroundColor Yellow
        }
        
        # Step 3: Copy DLLs to reference directories
        if ($solution.CopyTo.Count -gt 0) {
            Write-Host "`n3. Copying DLLs to reference directories..." -ForegroundColor Yellow
            if (-not $WhatIf) {
                Copy-DLLs -SolutionPath $solution.Path -DestinationDirs $solution.CopyTo
            } else {
                Write-Host "   [PREVIEW] Would copy DLLs to: $($solution.CopyTo -join ', ')" -ForegroundColor Gray
            }
        } else {
            Write-Host "`n3. No DLL copying needed for this solution" -ForegroundColor Gray
        }
        
        Write-Host "step $stepNumber completed" -ForegroundColor Green
    }
    
    return $true
}

# Function to update version in a specific solution (same as before)
function Update-SolutionVersion {
    param(
        [string]$SolutionPath,
        [string]$OldVersion, 
        [string]$NewVersion,
        [switch]$WhatIf
    )
    
    $changesCount = 0
    
    if (-not (Test-Path $SolutionPath)) {
        return 0
    }
    
    $solutionDir = Split-Path $SolutionPath -Parent
    
    # Update .csproj files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.csproj" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "    [CSPROJ] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update App.config files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "App.config" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "    [CONFIG] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update XAML files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.xaml" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "    [XAML] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    # Update C# and AssemblyInfo files
    Get-ChildItem -Path $solutionDir -Recurse -Filter "*.cs" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match $OldVersion) {
            if (-not $WhatIf) {
                $newContent = $content -replace [regex]::Escape($OldVersion), $NewVersion
                Set-Content -Path $_.FullName -Value $newContent -NoNewline
            }
            Write-Host "    [CS] $($_.Name)" -ForegroundColor Cyan
            $changesCount++
        }
    }
    
    return $changesCount
}

# Main execution
Write-Host "=== Cascading DLL Version Update Process ===" -ForegroundColor Magenta

# Determine base path
$basePath = Get-BasePathFromLocation
Write-Host "Using base path: $basePath" -ForegroundColor Green

# Auto-detect old version if not provided
if (-not $OldVersion) {
    $detectedVersion = Get-CurrentDllVersion -BasePath $basePath -BuildConfig $BuildConfig
    if ($detectedVersion) {
        $OldVersion = $detectedVersion
        Write-Host "Auto-detected current version: $OldVersion" -ForegroundColor Green
    } else {
        $OldVersion = Read-Host "Could not auto-detect current version. Please enter current version"
    }
}

# Validate versions
if ($OldVersion -eq $NewVersion) {
    Write-Error "Old version and new version are the same: $OldVersion"
    exit 1
}

Write-Host "`nUpdate Details:" -ForegroundColor Cyan
Write-Host "  From Version: $OldVersion" -ForegroundColor Yellow
Write-Host "  To Version: $NewVersion" -ForegroundColor Yellow
Write-Host "  Build Config: $BuildConfig" -ForegroundColor Yellow
Write-Host "  Starting from: Solution $StartFromSolution" -ForegroundColor Yellow

# Preview the cascading process
if ($WhatIf) {
    Write-Host "`n=== Preview Mode ===" -ForegroundColor Magenta
    $result = Invoke-CascadingVersionUpdate -BasePath $basePath -OldVersion $OldVersion -NewVersion $NewVersion -StartFromSolution $StartFromSolution -WhatIf
    
    # Preview pyRevit YAML updates
    $yamlChanges = Update-PyRevitYamlFiles -BasePath $basePath -OldVersion $OldVersion -NewVersion $NewVersion -WhatIf
    if ($yamlChanges -gt 0) {
        Write-Host "`nWould also update $yamlChanges pyRevit YAML files" -ForegroundColor Yellow
    }
    
    Write-Host "`nPreview complete. Run without -WhatIf to apply changes." -ForegroundColor Yellow
    exit 0
}

# Confirm before proceeding
Write-Host "`nThis will:" -ForegroundColor Yellow
Write-Host "- Update each solutions version references in dependency order" -ForegroundColor Yellow
Write-Host "- Build each solution after updating its references" -ForegroundColor Yellow  
Write-Host "- Copy built DLLs to reference directories" -ForegroundColor Yellow
Write-Host "- Update pyRevit YAML files at the end" -ForegroundColor Yellow

$confirmation = Read-Host "`nProceed with cascading version update? (y/N)"
if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "Operation cancelled." -ForegroundColor Red
    exit 0
}

# Execute the cascading update
Write-Host "`n=== Executing Cascading Update ===" -ForegroundColor Magenta
$result = Invoke-CascadingVersionUpdate -BasePath $basePath -OldVersion $OldVersion -NewVersion $NewVersion -StartFromSolution $StartFromSolution

if (-not $result) {
    Write-Host "`nCascading update failed!" -ForegroundColor Red
    exit 1
}

# Update pyRevit YAML files at the end
Write-Host "`n=== Updating pyRevit YAML Files ===" -ForegroundColor Magenta
$yamlChanges = Update-PyRevitYamlFiles -BasePath $basePath -OldVersion $OldVersion -NewVersion $NewVersion

if ($yamlChanges -eq 0) {
    Write-Host "No pyRevit YAML files needed updating" -ForegroundColor Gray
}

# Save change history
Save-VersionChange -OldVersion $OldVersion -NewVersion $NewVersion -BasePath $basePath

Write-Host "`n=== Cascading Update Complete ===" -ForegroundColor Green
Write-Host "Successfully updated entire dependency chain from $OldVersion to $NewVersion" -ForegroundColor Green
Write-Host "All solutions built and DLLs copied to reference directories" -ForegroundColor Green
Write-Host "PyRevit YAML files updated" -ForegroundColor Green

Read-Host "`nPress Enter to exit"