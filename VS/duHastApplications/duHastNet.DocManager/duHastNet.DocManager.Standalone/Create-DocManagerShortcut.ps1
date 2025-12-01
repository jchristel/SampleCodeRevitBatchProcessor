# Create-DocManagerShortcut.ps1
# PowerShell script to create DocManager shortcuts with custom settings paths
#
# Usage Examples:
#   .\Create-DocManagerShortcut.ps1 -AppPath "C:\Program Files\DocManager\DocManager.exe" -SettingsPath "\\FileServer\Share\Settings" -ShortcutName "DocManager - Team"
#   .\Create-DocManagerShortcut.ps1 -AppPath "C:\Program Files\DocManager\DocManager.exe" -ShortcutName "DocManager - Default"

param(
    [Parameter(Mandatory=$true, HelpMessage="Full path to the DocManager executable")]
    [string]$AppPath,
    
    [Parameter(Mandatory=$false, HelpMessage="Custom settings path (UNC or local path). If omitted, uses default settings location.")]
    [string]$SettingsPath,
    
    [Parameter(Mandatory=$true, HelpMessage="Name for the shortcut")]
    [string]$ShortcutName,
    
    [Parameter(Mandatory=$false, HelpMessage="Location to create the shortcut. Defaults to current user's Desktop.")]
    [string]$ShortcutLocation = "$env:USERPROFILE\Desktop"
)

# Function to validate the application path
function Test-AppPath {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        Write-Error "Application executable not found at: $Path"
        return $false
    }
    
    if ([System.IO.Path]::GetExtension($Path) -ne ".exe") {
        Write-Warning "The application path should point to an .exe file"
    }
    
    return $true
}

# Function to validate settings path (if provided)
function Test-SettingsPath {
    param([string]$Path)
    
    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $true  # Optional parameter
    }
    
    # Check if path is accessible
    if (-not (Test-Path $Path -IsValid)) {
        Write-Error "Settings path format is invalid: $Path"
        return $false
    }
    
    # Try to create directory if it doesn't exist
    if (-not (Test-Path $Path)) {
        Write-Host "Settings directory does not exist. Creating: $Path"
        try {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Host "✓ Directory created successfully" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to create settings directory: $_"
            return $false
        }
    }
    
    # Test write access
    $testFile = Join-Path $Path "test_write_access.tmp"
    try {
        [System.IO.File]::WriteAllText($testFile, "test")
        Remove-Item $testFile -Force
        Write-Host "✓ Write access confirmed" -ForegroundColor Green
    }
    catch {
        Write-Error "No write access to settings directory: $_"
        return $false
    }
    
    return $true
}

# Main script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "DocManager Shortcut Creator" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Validate application path
Write-Host "Validating application path..." -ForegroundColor Yellow
if (-not (Test-AppPath $AppPath)) {
    exit 1
}
Write-Host "✓ Application path valid" -ForegroundColor Green
Write-Host ""

# Validate settings path if provided
if (-not [string]::IsNullOrWhiteSpace($SettingsPath)) {
    Write-Host "Validating settings path..." -ForegroundColor Yellow
    if (-not (Test-SettingsPath $SettingsPath)) {
        exit 1
    }
}
else {
    Write-Host "No custom settings path provided - using default location" -ForegroundColor Yellow
    Write-Host "Default: %LocalAppData%\duHast" -ForegroundColor Gray
}
Write-Host ""

# Create the shortcut
$shortcutPath = Join-Path $ShortcutLocation "$ShortcutName.lnk"

Write-Host "Creating shortcut..." -ForegroundColor Yellow
Write-Host "Location: $shortcutPath" -ForegroundColor Gray

try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    
    # Set the target application
    $Shortcut.TargetPath = $AppPath
    
    # Set arguments if custom settings path provided
    if (-not [string]::IsNullOrWhiteSpace($SettingsPath)) {
        $Shortcut.Arguments = "--settings=`"$SettingsPath`""
        Write-Host "Settings Path: $SettingsPath" -ForegroundColor Gray
    }
    
    # Set working directory to app directory
    $Shortcut.WorkingDirectory = [System.IO.Path]::GetDirectoryName($AppPath)
    
    # Set description
    if (-not [string]::IsNullOrWhiteSpace($SettingsPath)) {
        $Shortcut.Description = "DocManager with settings at: $SettingsPath"
    }
    else {
        $Shortcut.Description = "DocManager with default settings location"
    }
    
    # Save the shortcut
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "✓ Shortcut created successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Shortcut Details:" -ForegroundColor Cyan
    Write-Host "  Name: $ShortcutName" -ForegroundColor White
    Write-Host "  Location: $shortcutPath" -ForegroundColor White
    Write-Host "  Application: $AppPath" -ForegroundColor White
    
    if (-not [string]::IsNullOrWhiteSpace($SettingsPath)) {
        Write-Host "  Settings: $SettingsPath" -ForegroundColor White
    }
    else {
        Write-Host "  Settings: Default (%LocalAppData%\duHast)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "You can now use this shortcut to launch DocManager." -ForegroundColor Green
}
catch {
    Write-Error "Failed to create shortcut: $_"
    exit 1
}

# Optional: Offer to create additional shortcuts
Write-Host ""
$response = Read-Host "Would you like to create another shortcut? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Run the script again with different parameters." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host '  .\Create-DocManagerShortcut.ps1 -AppPath "C:\Program Files\DocManager\DocManager.exe" -SettingsPath "\\FileServer\ProjectA\Settings" -ShortcutName "DocManager - Project A"' -ForegroundColor Gray
    Write-Host '  .\Create-DocManagerShortcut.ps1 -AppPath "C:\Program Files\DocManager\DocManager.exe" -SettingsPath "C:\SharedSettings" -ShortcutName "DocManager - Local Shared"' -ForegroundColor Gray
}
