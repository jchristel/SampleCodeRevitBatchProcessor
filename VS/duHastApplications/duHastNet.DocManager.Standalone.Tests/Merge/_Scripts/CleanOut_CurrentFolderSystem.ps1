# Remove-FilesKeepFolders.ps1
# Deletes all files in a directory and its subdirectories while preserving the folder structure

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [switch]$WhatIf
)

# Check if path exists
if (-not (Test-Path -Path $Path)) {
    Write-Error "Path '$Path' does not exist."
    Read-Host "Press Enter to exit"
    exit 1
}

# Resolve to full path
$Path = Resolve-Path -Path $Path

Write-Host "Target directory: $Path" -ForegroundColor Cyan
Write-Host "Scanning for files..." -ForegroundColor Yellow

if ($WhatIf) {
    Write-Host "`n=== WHATIF MODE - No files will be deleted ===" -ForegroundColor Yellow
    Get-ChildItem -Path $Path -File -Recurse -Force | ForEach-Object {
        Write-Host "Would delete: $($_.FullName)" -ForegroundColor Gray
    }
    Read-Host "`nPress Enter to exit"
    exit 0
}

# Confirm deletion
#Write-Host "`nWARNING: This will delete ALL files in the directory and subdirectories!" -ForegroundColor Red
#$confirmation = Read-Host "Type 'DELETE' to confirm"

#if ($confirmation -ne 'DELETE') {
#    Write-Host "Operation cancelled." -ForegroundColor Yellow
#    Read-Host "Press Enter to exit"
#    exit 0
#}

Write-Host "`nDeleting files..." -ForegroundColor Yellow
$deletedCount = 0
$failedCount = 0

# Delete files as we find them (no pre-scan)
Get-ChildItem -Path $Path -File -Recurse -Force | ForEach-Object {
    try {
        $filePath = $_.FullName
        Remove-Item -LiteralPath $filePath -Force -ErrorAction Stop
        $deletedCount++
        Write-Host "$filePath" -ForegroundColor Green
    } catch {
        $failedCount++
        Write-Host "FAILED: $filePath" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Successfully deleted: $deletedCount file(s)" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "Failed to delete: $failedCount file(s)" -ForegroundColor Red
}
Write-Host "Folder structure preserved." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

#Read-Host "`nPress Enter to exit"