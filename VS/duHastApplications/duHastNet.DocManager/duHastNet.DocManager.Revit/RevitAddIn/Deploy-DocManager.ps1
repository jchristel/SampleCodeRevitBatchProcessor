# DocManager Revit Add-in Deployment Script
# 
# This script deploys the DocManager add-in to Revit's add-in directory
# Run with administrator privileges for all-users deployment
# Run as regular user for per-user deployment

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("2020","2021","2022","2023","2024","2025")]
    [string[]]$RevitVersions = @("2024"),
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("AllUsers","CurrentUser")]
    [string]$DeploymentScope = "AllUsers",
    
    [Parameter(Mandatory=$true)]
    [string]$SourcePath
)

# Color output functions
function Write-Success { param($Message) Write-Host $Message -ForegroundColor Green }
function Write-Info { param($Message) Write-Host $Message -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host $Message -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host $Message -ForegroundColor Red }

Write-Info "========================================"
Write-Info "DocManager Revit Add-in Deployment"
Write-Info "========================================"
Write-Host ""

# Validate source path
if (-not (Test-Path $SourcePath)) {
    Write-Error "Source path not found: $SourcePath"
    exit 1
}

Write-Info "Source: $SourcePath"
Write-Info "Scope: $DeploymentScope"
Write-Info "Revit Versions: $($RevitVersions -join ', ')"
Write-Host ""

# Determine base path based on deployment scope
$basePath = if ($DeploymentScope -eq "AllUsers") {
    "$env:ProgramData\Autodesk\Revit\Addins"
} else {
    "$env:APPDATA\Autodesk\Revit\Addins"
}

Write-Info "Target Base Path: $basePath"
Write-Host ""

# Check permissions
if ($DeploymentScope -eq "AllUsers") {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Warning "All-Users deployment requires administrator privileges."
        Write-Warning "Please run this script as administrator or use -DeploymentScope CurrentUser"
        exit 1
    }
}

# Deploy to each Revit version
$successCount = 0
$failCount = 0

foreach ($version in $RevitVersions) {
    Write-Info "Processing Revit $version..."
    
    $targetPath = Join-Path $basePath $version
    $bundlePath = Join-Path $targetPath "duHastNet.DocManager.bundle\Contents"
    
    try {
        # Create directory structure if it doesn't exist
        if (-not (Test-Path $bundlePath)) {
            Write-Info "  Creating directory: $bundlePath"
            New-Item -ItemType Directory -Path $bundlePath -Force | Out-Null
        }
        
        # Copy all files from source to target
        Write-Info "  Copying files..."
        Copy-Item -Path "$SourcePath\*" -Destination $bundlePath -Recurse -Force
        
        # Verify critical files
        $criticalFiles = @(
            "duHastNet.DocManager.Revit.addin",
            "duHastNet.DocManager.Revit.dll",
            "duHastNet.DocManager.Core.dll",
            "duHastNet.DocManager.UI.Shared.dll"
        )
        
        $allFilesPresent = $true
        foreach ($file in $criticalFiles) {
            $filePath = Join-Path $bundlePath $file
            if (-not (Test-Path $filePath)) {
                Write-Warning "  Missing critical file: $file"
                $allFilesPresent = $false
            }
        }
        
        if ($allFilesPresent) {
            Write-Success "  ✓ Revit $version deployment successful"
            $successCount++
        } else {
            Write-Warning "  ⚠ Revit $version deployment incomplete (missing files)"
            $failCount++
        }
    }
    catch {
        Write-Error "  ✗ Revit $version deployment failed: $($_.Exception.Message)"
        $failCount++
    }
    
    Write-Host ""
}

# Summary
Write-Info "========================================"
Write-Info "Deployment Summary"
Write-Info "========================================"
Write-Success "Successful: $successCount"
if ($failCount -gt 0) {
    Write-Error "Failed: $failCount"
}
Write-Host ""

if ($successCount -gt 0) {
    Write-Info "Next Steps:"
    Write-Info "1. Restart Revit if currently running"
    Write-Info "2. Look for 'DocManager' panel on Add-Ins tab"
    Write-Info "3. Click 'Launch DocManager' button to verify"
    Write-Host ""
}

if ($failCount -eq 0) {
    Write-Success "All deployments completed successfully!"
    exit 0
} else {
    Write-Warning "Some deployments failed. Please review the output above."
    exit 1
}
