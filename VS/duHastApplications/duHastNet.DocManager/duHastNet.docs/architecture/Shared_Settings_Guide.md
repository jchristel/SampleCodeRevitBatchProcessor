# Shared Settings Configuration Guide

## Overview

The DocManager application now supports using a custom directory for settings, allowing multiple users to share the same configuration. This is useful when:
- Multiple users need to use identical settings
- Settings should be centralized on a network location
- You want different shortcuts to use different setting profiles

## Implementation Details

### Modified Files

1. **ISettingsService.cs** - Updated interface documentation
2. **SettingsService.cs** - Added constructor overload to accept custom settings path
3. **DocManagerBootstrapper.cs** - Updated `InitializeAsync()` and `Initialize()` methods to accept custom settings path parameter

### How It Works

- **Default behavior**: If no custom path is provided, settings are stored in `%LocalAppData%\duHast`
- **Custom path**: If a custom path is provided, settings are stored directly in that path (no "duHast" subfolder is appended)

## Usage

### For Standalone WPF Application

If you have an application entry point (App.xaml.cs or Program.cs), modify it to parse command-line arguments:

```csharp
protected override async void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);
    
    // Parse command-line arguments
    string? customSettingsPath = null;
    if (e.Args.Length > 0 && e.Args[0].StartsWith("--settings="))
    {
        customSettingsPath = e.Args[0].Substring("--settings=".Length);
    }
    
    // Initialize with custom settings path
    var bootstrapper = new DocManagerBootstrapper();
    var mainWindow = await bootstrapper.InitializeAsync(customSettingsPath);
    mainWindow.Show();
}
```

### Creating Windows Shortcuts

#### Option 1: Single Argument Style

Create a shortcut with the following target:

```
"C:\Path\To\YourApp.exe" --settings="\\server\share\DocManagerSettings"
```

Or for a local path:

```
"C:\Path\To\YourApp.exe" --settings="C:\Shared\DocManagerSettings"
```

#### Option 2: Alternative Argument Style

You could also use a different argument format in your code:

```
"C:\Path\To\YourApp.exe" /settingspath:"\\server\share\DocManagerSettings"
```

Just update your argument parsing code accordingly.

### Creating the Shortcut

1. **Right-click** on your desktop or in a folder
2. Select **New > Shortcut**
3. In the location field, enter:
   ```
   "C:\Path\To\YourApp.exe" --settings="\\server\share\TeamSettings"
   ```
4. Click **Next**
5. Name your shortcut (e.g., "DocManager - Team Settings")
6. Click **Finish**

### Network Path Examples

For network shares, use UNC paths:
```
--settings="\\ServerName\ShareName\DocManagerSettings"
--settings="\\192.168.1.100\Shared\Settings"
```

For local paths:
```
--settings="C:\SharedSettings"
--settings="D:\TeamData\DocManagerConfig"
```

### Setting Up Shared Settings Directory

Before using a shared settings location:

1. **Create the directory** on the network location or shared drive
2. **Set appropriate permissions**:
   - Users need Read/Write access
   - Recommended: Create a dedicated folder like `\\server\share\DocManagerSettings`
3. **Test access**: Ensure users can create and modify files in the location

### Multiple Configuration Profiles

You can create multiple shortcuts for different configuration profiles:

- **Shortcut 1**: "DocManager - Project A"
  - Target: `"C:\Path\To\App.exe" --settings="\\server\ProjectA\Settings"`

- **Shortcut 2**: "DocManager - Project B"
  - Target: `"C:\Path\To\App.exe" --settings="\\server\ProjectB\Settings"`

- **Shortcut 3**: "DocManager - Personal"
  - Target: `"C:\Path\To\App.exe"` (uses default local settings)

## Settings Files

The following files will be stored in the custom settings directory:

- `DatabaseConnection.json` - Database connection settings
- `CurrentFolderManager.json` - Current folder manager settings  
- `CloudDocumentManager.json` - Cloud document manager settings
- Backup files (`.bak` extension)

## Troubleshooting

### Issue: Settings not loading from custom path

**Check:**
1. Path is accessible (try opening in Windows Explorer)
2. User has read/write permissions
3. Path doesn't contain invalid characters
4. Network path is properly formatted (UNC path: `\\server\share\folder`)

### Issue: Permission denied errors

**Solution:**
- Verify the user has write permissions to the directory
- Check that no files are locked by other users
- Ensure antivirus isn't blocking file access

### Issue: Settings reverting to default

**Possible cause:**
- Command-line argument not being parsed correctly
- Check the shortcut target is exactly as documented
- Verify no extra spaces in the argument

## Code Example: Parsing Arguments

Here's a complete example of parsing command-line arguments in your application:

```csharp
using System;
using System.Linq;
using System.Windows;
using duHastNet.DocManager.UI.Shared.Services;

namespace YourApp
{
    public partial class App : Application
    {
        protected override async void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            
            try
            {
                // Parse custom settings path from command line
                string? customSettingsPath = ParseSettingsPath(e.Args);
                
                // Log the path being used (optional)
                if (!string.IsNullOrEmpty(customSettingsPath))
                {
                    System.Diagnostics.Debug.WriteLine($"Using custom settings path: {customSettingsPath}");
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine("Using default settings location");
                }
                
                // Initialize DocManager with optional custom path
                var bootstrapper = new DocManagerBootstrapper();
                var mainWindow = await bootstrapper.InitializeAsync(customSettingsPath);
                mainWindow.Show();
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Failed to initialize application: {ex.Message}",
                    "Startup Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
                Shutdown(1);
            }
        }
        
        private string? ParseSettingsPath(string[] args)
        {
            if (args == null || args.Length == 0)
                return null;
                
            // Look for --settings= argument
            var settingsArg = args.FirstOrDefault(arg => 
                arg.StartsWith("--settings=", StringComparison.OrdinalIgnoreCase));
                
            if (settingsArg != null)
            {
                return settingsArg.Substring("--settings=".Length).Trim('"');
            }
            
            // Alternative: Look for /settingspath: argument
            var altSettingsArg = args.FirstOrDefault(arg => 
                arg.StartsWith("/settingspath:", StringComparison.OrdinalIgnoreCase));
                
            if (altSettingsArg != null)
            {
                return altSettingsArg.Substring("/settingspath:".Length).Trim('"');
            }
            
            return null;
        }
    }
}
```

## Security Considerations

When using network-based shared settings:

1. **Sensitive Data**: Database connection strings and other sensitive data will be accessible to all users with access to the shared folder
2. **Concurrent Access**: Multiple users can modify settings simultaneously - last write wins
3. **Backup Strategy**: Consider implementing a backup strategy for shared settings
4. **Access Control**: Use appropriate network permissions to control who can read/write settings

## Best Practices

1. **Document the path**: Keep a record of where shared settings are stored
2. **Version control**: Consider backing up settings files periodically
3. **Test first**: Test with a local path before deploying to network location
4. **User training**: Ensure all users understand they're sharing settings
5. **Naming convention**: Use descriptive folder names (e.g., `DocManagerSettings_ProjectX`)

## Example Deployment Scenarios

### Scenario 1: Small Team on Network Share

- Create folder: `\\FileServer\Shared\DocManager\TeamSettings`
- Create shortcut on each user's desktop pointing to this location
- All users share: database connection, folder paths, cloud settings

### Scenario 2: Multiple Projects

- Create folders:
  - `\\FileServer\Projects\ProjectA\DocManagerSettings`
  - `\\FileServer\Projects\ProjectB\DocManagerSettings`
- Create separate shortcuts for each project
- Users can work on different projects with different configurations

### Scenario 3: Development vs Production

- Create folders:
  - `C:\DocManager\Dev` - Development settings (local)
  - `\\FileServer\DocManager\Prod` - Production settings (shared)
- Developers use local settings for testing
- Production users use shared network settings
