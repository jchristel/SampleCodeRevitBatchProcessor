# DocManager Revit Add-in - Deployment Guide

## For IT Administrators

### Prerequisites

- Autodesk Revit 2020 or later installed
- Administrative access to deployment locations (for all-users deployment)
- .NET Framework 4.8 Runtime (usually included with Revit)

### Deployment Steps

#### Option 1: All Users (Recommended)

1. **Create Bundle Directory**
   ```
   C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\
   ```
   Replace `2024` with target Revit version

2. **Copy Files**
   Copy all files from build output:
   - duHastNet.DocManager.Revit.addin (manifest)
   - duHastNet.DocManager.Revit.dll
   - duHastNet.DocManager.Core.dll
   - duHastNet.DocManager.UI.Shared.dll
   - SQLite-net.dll
   - SQLitePCLRaw.*.dll (multiple files)
   - CommunityToolkit.Mvvm.dll
   - CsvHelper.dll
   - Any other dependencies

3. **Verify Structure**
   ```
   C:\ProgramData\Autodesk\Revit\Addins\2024\
   └── duHastNet.DocManager.bundle\
       └── Contents\
           ├── duHastNet.DocManager.Revit.addin
           ├── duHastNet.DocManager.Revit.dll
           └── (other DLLs)
   ```

4. **Set Permissions**
   - Users need READ access to bundle directory
   - Users need WRITE access to `%APPDATA%\DocManager\` for settings

5. **Test Installation**
   - Launch Revit as test user
   - Check Add-Ins tab for "DocManager" panel
   - Click "Launch DocManager" button
   - Verify window opens

#### Option 2: Per User

Deploy to user profile instead:
```
%APPDATA%\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\
```

Users can deploy themselves without admin rights.

### Multi-Version Deployment

To support multiple Revit versions simultaneously:

```batch
xcopy "C:\Deploy\DocManager\*" "C:\ProgramData\Autodesk\Revit\Addins\2020\duHastNet.DocManager.bundle\Contents\" /Y /I /E
xcopy "C:\Deploy\DocManager\*" "C:\ProgramData\Autodesk\Revit\Addins\2021\duHastNet.DocManager.bundle\Contents\" /Y /I /E
xcopy "C:\Deploy\DocManager\*" "C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\" /Y /I /E
xcopy "C:\Deploy\DocManager\*" "C:\ProgramData\Autodesk\Revit\Addins\2025\duHastNet.DocManager.bundle\Contents\" /Y /I /E
```

Same files work across all versions (no Revit API version dependencies).

### Network Deployment

#### Option A: Shared Add-in Location

Deploy to network share and use Revit's "Additional Addins Folders" registry setting:

```
HKEY_CURRENT_USER\Software\Autodesk\Revit\Autodesk Revit 2024
String Value: AdditionalAddInPaths
Data: \\server\share\RevitAddins
```

#### Option B: Login Script

Use Group Policy or login script to copy files:

```batch
@echo off
set SOURCE=\\server\share\DocManager
set DEST=%PROGRAMDATA%\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents

if not exist "%DEST%" mkdir "%DEST%"
xcopy "%SOURCE%\*" "%DEST%\" /Y /I /E /Q
```

### Security Considerations

#### File Restrictions

This add-in is designed specifically to bypass EXE restrictions:
- Uses Revit as launcher (allowed application)
- DocManager runs as DLL loaded by Revit
- No standalone EXE required

#### Code Signing

Consider code-signing assemblies for additional trust:
- Sign duHastNet.DocManager.Revit.dll
- Sign all DocManager DLLs
- Helps with AV/whitelisting

#### Application Whitelisting

If using AppLocker or similar:
- Whitelist Revit.exe (usually already whitelisted)
- Add-in DLLs inherit Revit's permissions
- No additional rules needed

### Monitoring and Logging

DocManager logs to:
- User settings: `%APPDATA%\DocManager\`
- Check for error logs if issues reported

Monitor for:
- Failed launches (check Revit Add-In Manager)
- Database connection issues
- File permission problems

### Updates

To update existing installation:

1. **Stop Revit** (all users)
2. **Backup Settings** (optional)
   ```
   xcopy "%APPDATA%\DocManager\*" "C:\Backup\DocManager\" /Y /I /E
   ```
3. **Replace Files** in bundle directory
4. **Restart Revit**
5. **Verify** update succeeded

Settings and databases are preserved (not in bundle directory).

## For End Users

### Getting Started

1. **Open Revit**
   - Any version 2020 or later

2. **Find DocManager**
   - Go to **Add-Ins** tab on ribbon
   - Look for **DocManager** panel
   - Click **Launch DocManager** button

3. **First Launch**
   - Window opens (may take a few seconds)
   - Configure database connection
   - Set up folders and settings

4. **Using DocManager**
   - DocManager window is independent
   - You can minimize Revit and keep working in DocManager
   - DocManager stays open even if you switch projects in Revit

5. **Closing**
   - Close DocManager window when done
   - Revit continues running normally

### Tips

- **Single Instance**: Clicking the button multiple times brings the same window to front (doesn't create multiple windows)
- **Settings Persist**: Your settings are saved automatically
- **Independent**: DocManager doesn't interact with your Revit model
- **Background Work**: Can run DocManager while Revit is minimized

### Common Questions

**Q: Can I use DocManager without opening a Revit model?**
A: Yes! Just open Revit to the start screen and launch DocManager.

**Q: Does DocManager affect my Revit model?**
A: No, DocManager doesn't access or modify Revit models in any way.

**Q: Can I close Revit while DocManager is open?**
A: No, DocManager requires Revit to be running. Close DocManager first, then close Revit.

**Q: Where are my settings stored?**
A: Settings are stored in `%APPDATA%\DocManager\` folder.

**Q: Can I use a network database?**
A: Yes, you can select a database on a network share (subject to network permissions).

### Troubleshooting

**Problem: DocManager button doesn't appear**
- Solution: Restart Revit
- Check with IT if add-in is installed

**Problem: Button does nothing when clicked**
- Solution: Check for error messages in Revit
- Contact IT support

**Problem: Settings don't save**
- Solution: Check you have write permissions to `%APPDATA%\DocManager\`
- Contact IT support

**Problem: Database connection fails**
- Solution: Verify database file path is accessible
- Check network connectivity if using network database
- Ensure file isn't locked by another user

## For Developers

### Building from Source

1. **Prerequisites**
   - Visual Studio 2022 or later
   - Revit 2020+ installed (for API references)
   - .NET Framework 4.8 SDK

2. **Project Setup**
   - Add references to RevitAPI.dll and RevitAPIUI.dll
   - Set "Copy Local" to False for Revit assemblies
   - Install NuGet packages

3. **Build Configuration**
   ```xml
   <PropertyGroup>
     <Configuration>Debug|Release</Configuration>
     <Platform>x64</Platform>
     <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
   </PropertyGroup>
   ```

4. **Post-Build Event**
   ```batch
   xcopy "$(TargetDir)*.*" "C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\" /Y /I /E /EXCLUDE:$(ProjectDir)ExcludeList.txt
   ```

   ExcludeList.txt:
   ```
   RevitAPI.dll
   RevitAPIUI.dll
   *.pdb
   ```

5. **Debug Configuration**
   - Set Start Action to external program: `C:\Program Files\Autodesk\Revit 2024\Revit.exe`
   - Attach debugger after Revit starts
   - Breakpoints work normally

### Version-Specific Builds

Create separate build configurations for different Revit versions:

```xml
<PropertyGroup Condition="'$(Configuration)' == 'Debug_R2024'">
  <DefineConstants>DEBUG;REVIT2024</DefineConstants>
  <HintPath>C:\Program Files\Autodesk\Revit 2024\RevitAPI.dll</HintPath>
</PropertyGroup>
```

### Testing

1. **Unit Tests**: Test bootstrapper and services independently
2. **Integration Tests**: Test command execution
3. **Manual Testing**: Test in actual Revit environment

### Packaging

Create deployment package:

```
DocManager_Revit_v1.0.0.zip
├── duHastNet.DocManager.bundle\
│   └── Contents\
│       ├── (all DLLs)
│       └── duHastNet.DocManager.Revit.addin
├── README.md
├── DEPLOYMENT_GUIDE.md
└── LICENSE.txt
```

## Support

For technical issues:
- Check README.md for common solutions
- Review Revit Add-In Manager for errors
- Contact development team

For deployment issues:
- Contact IT support
- Verify file permissions
- Check Revit version compatibility
