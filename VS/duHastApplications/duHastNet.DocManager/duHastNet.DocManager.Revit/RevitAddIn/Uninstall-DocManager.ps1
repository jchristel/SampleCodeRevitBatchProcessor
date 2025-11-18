# DocManager Revit Add-in Uninstall Script
# 
# This script removes the DocManager add-in from Revit's add-in directory
# Run with administrator privileges for all-users uninstall
# Run as regular user for per-user uninstall

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("2020","2021","2022","2023","2024","2025","All")]
    [string]$RevitVersion = "All",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("AllUsers","CurrentUser","Both")]
    [string]$UninstallScope = "AllUsers",
    
    [Parameter(Mandatory=$false)]
    [switch]$RemoveSettings = $false
)

# Color output functions
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

Write-Info "========================================"
Write-Info "DocManager Revit Add-in Uninstall"
Write-Info "========================================"
Write-Host ""

# Determine versions to process
$versions = if ($RevitVersion -eq "All") {
    @("2020","2021","2022","2023","2024","2025")
} else {
    @($RevitVersion)
}

# Determine scopes to process
$scopes = switch ($UninstallScope) {
    "AllUsers" { @(@{Name="AllUsers"; Path="$env:ProgramData\Autodesk\Revit\Addins"}) }
    "CurrentUser" { @(@{Name="CurrentUser"; Path="$env:APPDATA\Autodesk\Revit\Addins"}) }
    "Both" { 
        @(
            @{Name="AllUsers"; Path="$env:ProgramData\Autodesk\Revit\Addins"},
            @{Name="CurrentUser"; Path="$env:APPDATA\Autodesk\Revit\Addins"}
        )
    }
}

Write-Info "Scope: $UninstallScope"
Write-Info "Versions: $($versions -join ', ')"
if ($RemoveSettings) {
    Write-Warning "Settings will be removed"
}
Write-Host ""

# Check permissions for AllUsers scope
if ($UninstallScope -in @("AllUsers","Both")) {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Warning "All-Users uninstall requires administrator privileges."
        Write-Warning "Please run this script as administrator or use -UninstallScope CurrentUser"
        exit 1
    }
}

$removedCount = 0
$notFoundCount = 0

# Process each scope and version
foreach ($scope in $scopes) {
    Write-Info "Processing $($scope.Name) scope..."
    
    foreach ($version in $versions) {
        $bundlePath = Join-Path $scope.Path "$version\duHastNet.DocManager.bundle"
        
        if (Test-Path $bundlePath) {
            try {
                Write-Info "  Removing from Revit $version..."
                Remove-Item -Path $bundlePath -Recurse -Force
                Write-Success "  ✓ Removed from Revit $version"
                $removedCount++
            }
            catch {
                Write-Error "  ✗ Failed to remove from Revit $version`: $($_.Exception.Message)"
            }
        } else {
            Write-Info "  Not found in Revit $version (skipping)"
            $notFoundCount++
        }
    }
    Write-Host ""
}

# Remove user settings if requested
if ($RemoveSettings) {
    Write-Info "Removing user settings..."
    $settingsPath = "$env:APPDATA\DocManager"
    
    if (Test-Path $settingsPath) {
        try {
            # Create backup first
            $backupPath = "$env:TEMP\DocManager_Settings_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Write-Info "  Creating backup: $backupPath"
            Copy-Item -Path $settingsPath -Destination $backupPath -Recurse -Force
            
            # Remove settings
            Remove-Item -Path $settingsPath -Recurse -Force
            Write-Success "  ✓ Settings removed (backup created)"
        }
        catch {
            Write-Error "  ✗ Failed to remove settings: $($_.Exception.Message)"
        }
    } else {
        Write-Info "  No settings found (skipping)"
    }
    Write-Host ""
}

# Summary
Write-Info "========================================"
Write-Info "Uninstall Summary"
Write-Info "========================================"
Write-Success "Removed: $removedCount"
Write-Info "Not Found: $notFoundCount"
Write-Host ""

if ($removedCount -gt 0) {
    Write-Info "Next Steps:"
    Write-Info "1. Restart Revit if currently running"
    Write-Info "2. Verify DocManager panel is gone from Add-Ins tab"
    Write-Host ""
    Write-Success "Uninstall completed successfully!"
} else {
    Write-Warning "No installations found to remove."
}

exit 0
