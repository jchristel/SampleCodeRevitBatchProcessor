# Custom Settings Path Implementation - Summary

## Overview

The DocManager application has been enhanced to support custom settings directory paths, enabling multiple users to share the same configuration by pointing to a network location or shared drive.

## Files Modified

### 1. ISettingsService.cs
- **Change**: Updated XML documentation for `SettingsDirectory` property
- **Impact**: Documentation now reflects that the path can be customized via constructor

### 2. SettingsService.cs
- **Changes**:
  - Added new constructor: `SettingsService(string? customSettingsPath)`
  - Modified default constructor to call new constructor with null parameter
  - Added logic to use custom path when provided, or default to `%LocalAppData%\duHast`
- **Behavior**:
  - If `customSettingsPath` is null/empty → Uses default location
  - If `customSettingsPath` is provided → Uses that path directly (no "duHast" subfolder appended)
  - Directory is automatically created if it doesn't exist

### 3. DocManagerBootstrapper.cs
- **Changes**:
  - `InitializeAsync()` method: Added optional `customSettingsPath` parameter
  - `Initialize()` method: Added optional `customSettingsPath` parameter and passes it through to `InitializeAsync()`
  - Updated instantiation: `new SettingsService(customSettingsPath)`
- **Behavior**: 
  - Maintains backward compatibility (parameter is optional)
  - Passes custom path to SettingsService during initialization

## New Files Created

### 1. App.xaml.cs (Example Implementation)
- Complete example showing how to:
  - Parse command-line arguments
  - Extract custom settings path
  - Initialize DocManagerBootstrapper with custom path
  - Handle startup errors gracefully

### 2. SharedSettingsGuide.md
- Comprehensive documentation covering:
  - Implementation details
  - Usage instructions
  - Creating Windows shortcuts
  - Network path examples
  - Multiple configuration profiles
  - Troubleshooting guide
  - Security considerations
  - Best practices
  - Example deployment scenarios

### 3. ShortcutQuickReference.md
- Quick reference card with:
  - Step-by-step shortcut creation
  - Target path examples
  - Network path format guidelines
  - Testing procedures
  - Permission requirements
  - Troubleshooting table

### 4. Create-DocManagerShortcut.ps1
- PowerShell automation script that:
  - Validates application and settings paths
  - Tests write access to settings directory
  - Creates shortcuts automatically
  - Provides detailed feedback
  - Includes usage examples

## Key Features

### ✅ Backward Compatible
- Existing code continues to work without modifications
- Default constructor still uses `%LocalAppData%\duHast`

### ✅ Flexible
- Supports UNC network paths (e.g., `\\server\share\folder`)
- Supports local paths (e.g., `C:\SharedSettings`)
- Supports multiple configuration profiles via different shortcuts

### ✅ Automatic Setup
- Settings directory is created automatically if it doesn't exist
- No manual setup required

### ✅ Safe
- Maintains backup file strategy (`.bak` files)
- Uses temporary files during save (`.tmp` files)
- Graceful error handling

## Usage Scenarios

### Scenario 1: Default Behavior (No Changes Required)
```csharp
var bootstrapper = new DocManagerBootstrapper();
var window = await bootstrapper.InitializeAsync();
```
Result: Settings in `%LocalAppData%\duHast`

### Scenario 2: Shared Network Settings
```csharp
var bootstrapper = new DocManagerBootstrapper();
var window = await bootstrapper.InitializeAsync(@"\\FileServer\Shared\DocManagerSettings");
```
Result: Settings in `\\FileServer\Shared\DocManagerSettings`

### Scenario 3: Local Shared Settings
```csharp
var bootstrapper = new DocManagerBootstrapper();
var window = await bootstrapper.InitializeAsync(@"C:\SharedData\DocManager");
```
Result: Settings in `C:\SharedData\DocManager`

### Scenario 4: Command-Line Driven (Shortcut)
Shortcut target:
```
"C:\Program Files\DocManager\DocManager.exe" --settings="\\FileServer\TeamSettings"
```

App.xaml.cs parses `--settings=` argument and passes to bootstrapper.

## Settings Files

The following files are stored in the settings directory:

| File | Purpose |
|------|---------|
| `DatabaseConnection.json` | Database connection settings |
| `CurrentFolderManager.json` | Current folder manager configuration |
| `CloudDocumentManager.json` | Cloud document manager settings |
| `*.bak` | Backup files (automatic) |
| `*.tmp` | Temporary files during save (automatic cleanup) |

## Integration Steps

To integrate into your standalone application:

1. **Copy the modified files** to your project:
   - `ISettingsService.cs`
   - `SettingsService.cs`
   - `DocManagerBootstrapper.cs`

2. **Update your application entry point** (App.xaml.cs or Program.cs):
   - Add command-line argument parsing (see App.xaml.cs example)
   - Pass custom path to `InitializeAsync()`

3. **Create shortcuts** for users:
   - Use PowerShell script for automated creation
   - Or manually create shortcuts with `--settings=` argument

4. **Setup shared location** (if using network path):
   - Create directory on network share
   - Set appropriate permissions (Read/Write for users)
   - Test access from each user machine

## Testing Checklist

- [ ] Default behavior works (no custom path)
- [ ] Local custom path works
- [ ] Network UNC path works
- [ ] Settings are saved to correct location
- [ ] Settings persist across application restarts
- [ ] Multiple users can access shared settings
- [ ] Backup files (`.bak`) are created
- [ ] Permissions are correctly set on shared folder
- [ ] Error handling works for invalid paths
- [ ] Command-line argument parsing works

## Important Considerations

### 🔒 Security
- Settings files may contain sensitive information (database passwords, paths)
- Use appropriate network permissions
- Consider encrypting sensitive fields in settings files

### 👥 Concurrent Access
- Multiple users can access settings simultaneously
- **Last write wins** - no merge or conflict resolution
- Consider implementing file locking if needed

### 💾 Backup Strategy
- Automatic `.bak` files provide one level of backup
- Consider additional backup strategy for critical deployments
- Network shares should have backup/restore capabilities

### 📝 Documentation
- Document the settings path for your team
- Keep inventory of shared settings locations
- Provide users with appropriate shortcuts

## Support

For issues or questions:

1. Check `SharedSettingsGuide.md` for comprehensive documentation
2. Review `ShortcutQuickReference.md` for quick answers
3. Use PowerShell script for automated shortcut creation
4. Test with local paths before deploying to network

## Version Compatibility

This implementation maintains full backward compatibility:
- ✅ Existing code requires no changes
- ✅ Default behavior unchanged
- ✅ Optional parameters used throughout
- ✅ No breaking changes to public APIs
