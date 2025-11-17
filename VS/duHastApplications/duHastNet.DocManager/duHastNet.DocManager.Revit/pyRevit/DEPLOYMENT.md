# DocManager Revit Integration - Deployment Guide

## Project Structure

### Source Code Structure
```
YourSolution/
├── duHastNet.DocManager.Core/           # Core business logic
├── duHastNet.DocManager.UI.Shared/      # Shared UI components
│   ├── ViewModels/
│   ├── Views/
│   ├── Services/
│   │   ├── DialogService.cs
│   │   ├── SettingsService.cs
│   │   └── DocManagerBootstrapper.cs    # Bootstrapper lives here
│   └── ...
├── DocManager.Standalone/               # Standalone WPF app
│   └── App.xaml.cs                      # Updated to use bootstrapper
└── duHastNet.DocManager.Revit/          # Revit integration (minimal)
    └── PyRevit/
        └── DocManager.extension/        # PyRevit extension files
```

### PyRevit Extension Structure (Deployed)
```
DocManager.extension/
├── bundle.yaml                          # Extension metadata
├── README.md                            # User documentation
├── icon.png                             # Extension icon (optional)
├── DocManager.tab/                      # Creates "DocManager" tab in Revit
│   └── Launch.panel/                    # Creates "Launch" panel
│       └── Open DocManager.pushbutton/  # Creates button
│           ├── script.py                # Python launcher script
│           └── icon.png                 # Button icon (16x16 or 32x32)
└── lib/                                 # .NET assemblies
    ├── duHastNet.DocManager.Core.dll
    ├── duHastNet.DocManager.UI.Shared.dll
    ├── CommunityToolkit.Mvvm.dll
    ├── SQLite-net.dll
    ├── SQLitePCLRaw.core.dll
    ├── SQLitePCLRaw.provider.e_sqlite3.dll
    ├── SQLitePCLRaw.batteries_v2.dll
    └── (any other dependencies)
```

## Build and Deployment Steps

### Step 1: Build Solution
1. Build your entire solution in Release mode
2. This creates all DLLs in bin/Release folders

### Step 2: Create Extension Folder
Create the extension folder structure:
```powershell
# Create base structure
mkdir DocManager.extension
mkdir DocManager.extension\DocManager.tab
mkdir DocManager.extension\DocManager.tab\Launch.panel
mkdir DocManager.extension\DocManager.tab\Launch.panel\Open` DocManager.pushbutton
mkdir DocManager.extension\lib
```

### Step 3: Copy Files

**Copy Configuration Files:**
```powershell
# Copy to extension root
copy bundle.yaml DocManager.extension\
copy README.md DocManager.extension\
copy icon.png DocManager.extension\  # If you have one
```

**Copy Script Files:**
```powershell
# Copy to pushbutton folder
copy script.py "DocManager.extension\DocManager.tab\Launch.panel\Open DocManager.pushbutton\"
copy button-icon.png "DocManager.extension\DocManager.tab\Launch.panel\Open DocManager.pushbutton\icon.png"
```

**Copy DLL Files:**
```powershell
# Copy your assemblies
copy duHastNet.DocManager.Core\bin\Release\net8.0\duHastNet.DocManager.Core.dll DocManager.extension\lib\
copy duHastNet.DocManager.UI.Shared\bin\Release\net8.0-windows\duHastNet.DocManager.UI.Shared.dll DocManager.extension\lib\

# Copy dependencies (from any of the bin folders)
copy duHastNet.DocManager.UI.Shared\bin\Release\net8.0-windows\CommunityToolkit.Mvvm.dll DocManager.extension\lib\
copy duHastNet.DocManager.UI.Shared\bin\Release\net8.0-windows\SQLite-net.dll DocManager.extension\lib\
copy duHastNet.DocManager.UI.Shared\bin\Release\net8.0-windows\SQLitePCLRaw.*.dll DocManager.extension\lib\
# ... (copy all other dependencies)
```

### Step 4: Install Extension

**Manual Installation:**
```powershell
# Copy entire extension folder to pyRevit extensions directory
xcopy /E /I DocManager.extension "%APPDATA%\pyRevit\Extensions\DocManager.extension"
```

**Verify Installation:**
1. Open Revit
2. Go to pyRevit menu
3. Click "Reload"
4. Look for "DocManager" tab in ribbon

### Step 5: Test
1. Click "Open DocManager" button
2. Verify DocManager window opens
3. Test database connection
4. Verify all functionality works

## Automated Build Script

### PowerShell Build Script
Create `Deploy-PyRevitExtension.ps1`:
```powershell
# Configuration
$SolutionDir = "C:\Path\To\Your\Solution"
$OutputDir = "C:\Path\To\Output\DocManager.extension"
$PyRevitExtDir = "$env:APPDATA\pyRevit\Extensions\DocManager.extension"

# Build solution
Write-Host "Building solution..." -ForegroundColor Green
dotnet build "$SolutionDir\YourSolution.sln" -c Release

# Create extension structure
Write-Host "Creating extension structure..." -ForegroundColor Green
if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Path "$OutputDir\DocManager.tab\Launch.panel\Open DocManager.pushbutton" -Force | Out-Null
New-Item -ItemType Directory -Path "$OutputDir\lib" | Out-Null

# Copy config files
Write-Host "Copying configuration files..." -ForegroundColor Green
Copy-Item "$SolutionDir\duHastNet.DocManager.Revit\PyRevit\bundle.yaml" "$OutputDir\"
Copy-Item "$SolutionDir\duHastNet.DocManager.Revit\PyRevit\README.md" "$OutputDir\"

# Copy script files
Write-Host "Copying script files..." -ForegroundColor Green
Copy-Item "$SolutionDir\duHastNet.DocManager.Revit\PyRevit\script.py" "$OutputDir\DocManager.tab\Launch.panel\Open DocManager.pushbutton\"

# Copy DLLs
Write-Host "Copying assemblies..." -ForegroundColor Green
$BinDir = "$SolutionDir\duHastNet.DocManager.UI.Shared\bin\Release\net8.0-windows"
Get-ChildItem "$BinDir\*.dll" | Copy-Item -Destination "$OutputDir\lib\"

# Install to pyRevit
Write-Host "Installing to pyRevit..." -ForegroundColor Green
if (Test-Path $PyRevitExtDir) { Remove-Item $PyRevitExtDir -Recurse -Force }
Copy-Item $OutputDir $PyRevitExtDir -Recurse

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Please reload pyRevit in Revit to see changes" -ForegroundColor Yellow
```

## MSBuild Post-Build Event

Add to `duHastNet.DocManager.Revit.csproj`:
```xml
<Target Name="PostBuild" AfterTargets="PostBuildEvent">
  <Exec Command="powershell -ExecutionPolicy Bypass -File &quot;$(ProjectDir)Deploy-PyRevitExtension.ps1&quot;" />
</Target>
```

## Troubleshooting Deployment

### Missing DLLs
Check bin/Release folder and ensure all dependencies are copied:
```powershell
# List all DLLs in bin folder
Get-ChildItem "bin\Release\net8.0-windows\*.dll" | Select-Object Name
```

### Wrong .NET Version
Ensure targeting net8.0-windows:
```xml
<TargetFramework>net8.0-windows</TargetFramework>
```

### pyRevit Can't Find Assemblies
Verify lib folder contents:
```powershell
Get-ChildItem "%APPDATA%\pyRevit\Extensions\DocManager.extension\lib\"
```

### Script Errors
Check pyRevit output window:
- pyRevit menu → Output Window
- Look for Python errors or stack traces

## Version Updates

When updating DocManager:
1. Build new version
2. Run deployment script
3. Reload pyRevit
4. Version number in bundle.yaml should be updated

## Distribution

### For Internal Use
Share the `DocManager.extension` folder via:
- Network share
- Internal Git repository
- Company software distribution

### For External Distribution
Create a zip file:
```powershell
Compress-Archive -Path DocManager.extension -DestinationPath DocManager-Extension-v1.0.0.zip
```

Users extract and copy to their pyRevit extensions folder.

## Notes

- No installer needed - simple folder copy
- Updates require replacing extension folder and reloading pyRevit
- Settings are stored in user AppData (persists across updates)
- Multiple users can share same extension installation

## File Locations

**Extension Location:**
```
%APPDATA%\pyRevit\Extensions\DocManager.extension\
```

**Settings Location (DocManager):**
```
%APPDATA%\DocManager\
├── DatabaseConnection.json
├── CurrentFolderManager.json
└── CloudDocumentManager.json
```

**Database Location:**
User-specified, typically:
```
C:\Users\<Username>\Documents\DocManager\
```
