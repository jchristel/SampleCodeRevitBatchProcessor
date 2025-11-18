# DocManager Revit Add-in

## Overview

This Revit add-in provides a launcher for the DocManager application. Revit is used solely as a delivery mechanism to bypass executable restrictions in restricted environments. The DocManager application runs as a completely independent WPF window with no Revit API interaction.

## Architecture

- **LaunchDocManagerCommand.cs** - IExternalCommand that launches DocManager
- **DocManagerApplication.cs** - IExternalApplication that manages lifecycle and creates ribbon UI
- **duHastNet.DocManager.Revit.addin** - Manifest file that registers the add-in with Revit

## Key Features

- ✅ Independent window - DocManager runs separately from Revit
- ✅ Singleton pattern - Only one instance of DocManager can run at a time
- ✅ Clean lifecycle - Proper initialization and disposal
- ✅ No Revit dependencies - DocManager does not interact with Revit API
- ✅ Multi-version support - Works with any Revit version (2020+)

## Deployment

### Standard Deployment (All Users)

Copy the entire build output to Revit's add-in directory:

```
C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\
├── Contents\
│   ├── duHastNet.DocManager.Revit.addin
│   ├── duHastNet.DocManager.Revit.dll
│   ├── duHastNet.DocManager.Core.dll
│   ├── duHastNet.DocManager.UI.Shared.dll
│   ├── SQLite-net.dll
│   ├── SQLitePCLRaw.*.dll
│   ├── CommunityToolkit.Mvvm.dll
│   ├── CsvHelper.dll
│   └── Resources\
│       └── DocManager32.png (optional icon)
```

Replace `2024` with your target Revit version (2020, 2021, 2022, 2023, 2024, 2025, etc.)

### Per-User Deployment

Alternatively, deploy to user-specific directory:

```
%APPDATA%\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\
```

### Multi-Version Support

To support multiple Revit versions, copy the same bundle to each version's add-in directory:

```
C:\ProgramData\Autodesk\Revit\Addins\2020\duHastNet.DocManager.bundle\
C:\ProgramData\Autodesk\Revit\Addins\2021\duHastNet.DocManager.bundle\
C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\
```

## Usage

1. Start Revit
2. Look for "DocManager" panel on the Add-Ins ribbon tab
3. Click "Launch DocManager" button
4. DocManager window opens as independent application
5. Use DocManager normally (minimize Revit, work in other apps, etc.)
6. Close DocManager window when finished
7. Click button again to reopen (same instance)

## Build Configuration

### Required References

The Revit project must reference:

- **RevitAPI.dll** - From Revit installation (do NOT copy to output)
- **RevitAPIUI.dll** - From Revit installation (do NOT copy to output)
- **duHastNet.DocManager.Core** - Project reference
- **duHastNet.DocManager.UI.Shared** - Project reference

### NuGet Packages

- **sqlite-net-pcl** - For database operations
- **CommunityToolkit.Mvvm** - For MVVM pattern
- **CsvHelper** - For CSV file operations

### Build Output

Ensure all dependencies are copied to output directory **EXCEPT**:
- ❌ RevitAPI.dll (provided by Revit)
- ❌ RevitAPIUI.dll (provided by Revit)

### Post-Build Event (Optional)

Add post-build event to automatically copy files to Revit add-in directory:

```batch
xcopy "$(TargetDir)*.*" "C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.bundle\Contents\" /Y /I /E
```

## Troubleshooting

### Add-in Doesn't Appear

1. Check manifest file location: `C:\ProgramData\Autodesk\Revit\Addins\2024\duHastNet.DocManager.Revit.addin`
2. Verify assembly path in manifest matches actual DLL location
3. Check Revit version matches add-in directory
4. Restart Revit

### Window Doesn't Open

1. Check for error messages in Revit
2. Review exception details in Revit's Add-In Manager
3. Verify all dependencies are copied to output
4. Check SQLite native libraries are present

### Multiple Windows Opening

This shouldn't happen - the singleton pattern prevents it. If it does:
1. Check static fields in LaunchDocManagerCommand
2. Verify Window_Closed event is wired up correctly

### Settings Not Persisting

Settings are stored by SettingsService in default location:
- Typically `%APPDATA%\DocManager\` or application directory
- Check file system permissions
- Verify settings files are being created

### Database Connection Issues

1. Check user has read/write access to database file location
2. Verify SQLite native libraries are deployed
3. Test database file isn't locked by another process
4. Check network path accessibility (if using shared database)

## Version Compatibility

### Revit Versions

This add-in is compatible with Revit 2020 and later. The code uses basic Revit API features available in all modern versions.

### .NET Framework

Revit 2020-2024 use .NET Framework 4.8
Revit 2025+ may use .NET Core/6+

Target the appropriate framework version for your Revit version.

## Technical Notes

### No Revit Interaction

DocManager **does not** use Revit API for any functionality:
- No document access
- No element reading/writing
- No transaction handling
- No Revit events
- No Revit context

Revit is purely a launcher mechanism.

### Threading

DocManager runs on its own WPF UI thread, completely independent of Revit's UI thread. No marshaling or synchronization is needed.

### Window Behavior

- Window is NOT owned by Revit main window
- Can be minimized/maximized independently
- Survives Revit minimize/restore
- Closes independently of Revit
- Position persisted (if implemented in bootstrapper)

### Lifecycle

1. User clicks button → LaunchDocManagerCommand.Execute()
2. Check if window already exists → Activate existing window
3. If no window → Create bootstrapper → Initialize() → Show window
4. User closes window → Window_Closed event → Clean up references
5. Next click → Creates fresh instance

## License

BSD License - See individual source files for full license text.

Copyright 2025, Jan Christel

## Support

For issues or questions, contact your internal IT support or the development team.
