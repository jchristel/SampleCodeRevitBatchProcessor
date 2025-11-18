# Quick Start Guide - DocManager Revit Add-in

## For Developers (5 Minutes)

### 1. Add Files to Project
Copy all files from `RevitAddIn` folder into your `duHastNet.DocManager.Revit` project under a `RevitAddIn` folder.

### 2. Add References
Add to your project:
- `RevitAPI.dll` (from Revit installation)
- `RevitAPIUI.dll` (from Revit installation)

Set **Copy Local = False** for both Revit DLLs.

### 3. Build
Build the project in Release mode.

### 4. Quick Deploy (Testing)
Double-click `Deploy-DocManager.bat` from your build output folder, or run:
```powershell
.\Deploy-DocManager.ps1 -SourcePath "C:\path\to\bin\Release" -RevitVersions @("2024")
```

### 5. Test
1. Start Revit 2024
2. Go to Add-Ins tab
3. Click "Launch DocManager"
4. Verify window opens

Done! ✅

---

## For IT Teams (10 Minutes)

### Option A: Interactive Batch File
1. Copy all DLLs to a folder
2. Copy `Deploy-DocManager.bat` to same folder
3. Double-click the batch file
4. Follow prompts
5. Done!

### Option B: PowerShell Script
```powershell
# For single version (Revit 2024)
.\Deploy-DocManager.ps1 -SourcePath ".\DLLs" -RevitVersions @("2024") -DeploymentScope AllUsers

# For multiple versions
.\Deploy-DocManager.ps1 -SourcePath ".\DLLs" -RevitVersions @("2023","2024","2025") -DeploymentScope AllUsers
```

Run PowerShell **as Administrator** for AllUsers deployment.

### Verification
```powershell
# Check installation
Get-ChildItem "C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle"
```

---

## For End Users (1 Minute)

### First Use
1. Open Revit
2. Look for **Add-Ins** tab at top
3. Find **DocManager** panel
4. Click **Launch DocManager** button
5. Window opens - start using!

### Daily Use
1. Open Revit (any project or no project)
2. Click the DocManager button
3. Work in DocManager
4. Close window when done
5. Close Revit

**Tip**: You can minimize Revit and keep working in DocManager!

---

## Common Commands

### Deploy to Revit 2024 (Current User)
```powershell
.\Deploy-DocManager.ps1 -SourcePath ".\bin\Release" -RevitVersions @("2024") -DeploymentScope CurrentUser
```

### Deploy to All Versions (All Users)
```powershell
.\Deploy-DocManager.ps1 -SourcePath ".\bin\Release" -RevitVersions @("2020","2021","2022","2023","2024","2025") -DeploymentScope AllUsers
```

### Uninstall from Revit 2024
```powershell
.\Uninstall-DocManager.ps1 -RevitVersion "2024" -UninstallScope AllUsers
```

### Uninstall from All Versions (with settings removal)
```powershell
.\Uninstall-DocManager.ps1 -RevitVersion "All" -UninstallScope Both -RemoveSettings
```

---

## File Locations

### Installation
```
C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\
```

### Settings (User-specific)
```
%APPDATA%\DocManager\
```

### Manifest
```
C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.Revit.addin
```

---

## Quick Troubleshooting

**Button not visible?**
→ Restart Revit

**Window doesn't open?**
→ Check Add-In Manager (Manage tab → Add-Ins)

**Missing dependencies?**
→ Verify all DLLs copied to bundle folder

**Settings not saving?**
→ Check %APPDATA%\DocManager\ folder exists and is writable

---

## Support Files

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment instructions |
| `IMPLEMENTATION_SUMMARY.md` | Technical implementation details |
| `PROJECT_INFO.txt` | GUIDs, versions, configuration |
| `Deploy-DocManager.ps1` | PowerShell deployment script |
| `Deploy-DocManager.bat` | Batch deployment script |
| `Uninstall-DocManager.ps1` | PowerShell uninstall script |

---

## Need More Help?

1. Check `README.md` for detailed information
2. Review `DEPLOYMENT_GUIDE.md` for specific scenarios
3. See `IMPLEMENTATION_SUMMARY.md` for technical details
4. Contact IT support or development team

---

## Version Info

- **Add-in Version**: 1.0.0
- **Supported Revit**: 2020 - 2025
- **Target Framework**: .NET Framework 4.8
- **Platform**: x64

---

**That's it! You're ready to use DocManager via Revit.** 🚀
