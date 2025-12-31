# Copy-AllFiles.ps1
# Copies all files from a source folder to a destination folder

param(
    [Parameter(Mandatory=$true)]
    [string]$Source,
    
    [Parameter(Mandatory=$true)]
    [string]$Destination,
    
    [switch]$IncludeSubfolders,
    
    [switch]$WhatIf
)

# Check if source exists
if (-not (Test-Path -Path $Source)) {
    Write-Error "Source path '$Source' does not exist."
    Read-Host "Press Enter to exit"
    exit 1
}

# Resolve to full paths
$Source = Resolve-Path -Path $Source
Write-Host "Source: $Source" -ForegroundColor Cyan
Write-Host "Destination: $Destination" -ForegroundColor Cyan

# Create destination folder if it doesn't exist
if (-not (Test-Path -Path $Destination)) {
    Write-Host "Destination folder does not exist. Creating it..." -ForegroundColor Yellow
    if (-not $WhatIf) {
        New-Item -Path $Destination -ItemType Directory -Force | Out-Null
    }
}

Write-Host "Scanning for files..." -ForegroundColor Yellow

# Get files based on whether we want subdirectories
if ($IncludeSubfolders) {
    $files = Get-ChildItem -Path $Source -File -Recurse -Force
    Write-Host "Mode: Copying files from all subdirectories (flattened)" -ForegroundColor Cyan
} else {
    $files = Get-ChildItem -Path $Source -File -Force
    Write-Host "Mode: Copying files from root folder only" -ForegroundColor Cyan
}

if ($files.Count -eq 0) {
    Write-Host "No files found to copy." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "Found $($files.Count) file(s) to copy.`n" -ForegroundColor Cyan

if ($WhatIf) {
    Write-Host "=== WHATIF MODE - No files will be copied ===" -ForegroundColor Yellow
    $files | ForEach-Object {
        $destFile = Join-Path -Path $Destination -ChildPath $_.Name
        Write-Host "Would copy: $($_.FullName)" -ForegroundColor Gray
        Write-Host "        to: $destFile" -ForegroundColor Gray
    }
    Read-Host "`nPress Enter to exit"
    exit 0
}

# Confirm copy
#$confirmation = Read-Host "Copy $($files.Count) file(s) to $Destination? Type 'COPY' to confirm"

#if ($confirmation -ne 'COPY') {
#    Write-Host "Operation cancelled." -ForegroundColor Yellow
#    Read-Host "Press Enter to exit"
#    exit 0
#}

Write-Host "`nCopying files..." -ForegroundColor Yellow
$copiedCount = 0
$skippedCount = 0
$failedCount = 0

foreach ($file in $files) {
    try {
        $destFile = Join-Path -Path $Destination -ChildPath $file.Name
        
        # Check if file already exists at destination
        if (Test-Path -Path $destFile) {
            Write-Host "Skipped (already exists): $($file.Name)" -ForegroundColor Yellow
            $skippedCount++
        } else {
            Copy-Item -LiteralPath $file.FullName -Destination $destFile -Force -ErrorAction Stop
            $copiedCount++
            Write-Host "$($file.Name)" -ForegroundColor Green
        }
    } catch {
        $failedCount++
        Write-Host "FAILED: $($file.Name)" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Successfully copied: $copiedCount file(s)" -ForegroundColor Green
if ($skippedCount -gt 0) {
    Write-Host "Skipped (already exist): $skippedCount file(s)" -ForegroundColor Yellow
}
if ($failedCount -gt 0) {
    Write-Host "Failed to copy: $failedCount file(s)" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

#Read-Host "`nPress Enter to exit"
