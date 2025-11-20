# DocManager MSI Installer Setup Guide

## Prerequisites

### 1. Install Visual Studio Installer Projects Extension

1. Open Visual Studio 2022
2. Go to **Extensions → Manage Extensions**
3. Select **Online** tab
4. Search for "Microsoft Visual Studio Installer Projects"
5. Download and install the extension
6. **Restart Visual Studio** to complete installation

## Step 1: Add Setup Project to Solution

1. Open your DocManager solution in Visual Studio
2. Right-click on the **Solution** in Solution Explorer
3. Select **Add → New Project**
4. In the template search box, type "setup"
5. Select **Setup Project** template
6. Name it: `DocManager.Setup`
7. Click **Create**

## Step 2: Configure Installer Properties

1. Right-click on `DocManager.Setup` project in Solution Explorer
2. Select **Properties**
3. Configure the following properties:

### Basic Properties
| Property | Value |
|----------|-------|
| **Author** | duHast |
| **Manufacturer** | duHast |
| **ProductName** | DocManager |
| **Title** | DocManager Setup |
| **Version** | 1.0.0 |
| **Description** | Document Manager for tracking and managing project documentation |

### Installation Behavior Properties
| Property | Value | Notes |
|----------|-------|-------|
| **InstallAllUsers** | `TRUE` | Default to per-machine install |
| **InstallAllUsersVisible** | `TRUE` | **CRITICAL**: Allows user to choose "Only Me" or "Everyone" |
| **RequiresElevation** | `TRUE` | Requests admin rights for per-machine install |

### Location Properties
| Property | Value |
|----------|-------|
| **DefaultLocation** | `[ProgramFilesFolder][Manufacturer]\[ProductName]` |

## Step 3: Add Application Files

### 3.1 Add Primary Output

1. Right-click on `DocManager.Setup` in Solution Explorer
2. Select **View → File System**
3. In the File System editor, right-click **Application Folder**
4. Select **Add → Project Output...**
5. In the dialog:
   - **Project**: Select your standalone WPF project (e.g., `DocManager.Standalone`)
   - **Output**: Select `Primary output`
   - Click **OK**

### 3.2 Add Content Files (if any)

If you have additional files (README, documentation, etc.):
1. Right-click **Application Folder**
2. Select **Add → File...**
3. Browse and select the files
4. Click **OK**

## Step 4: Configure Installation Folders

The File System editor has three main folders:

### Application Folder
- **Location**: `[ProgramFilesFolder][Manufacturer]\[ProductName]`
- **Contains**: All application binaries and DLLs
- This is where your application executable and dependencies will be installed

### User's Desktop
- Add shortcuts here if you want desktop icons

### User's Programs Menu
- Add shortcuts here for Start Menu entries

## Step 5: Create Application Shortcuts

### 5.1 Create Desktop Shortcut (Optional)

1. In File System editor, locate `Primary output from [YourProject]` under **Application Folder**
2. Right-click on `Primary output` → **Create Shortcut**
3. Rename the shortcut to: `DocManager`
4. **Drag** this shortcut to **User's Desktop** folder
5. Right-click the shortcut and select **Properties**
6. Set the following:
   - **Icon**: Select your application icon (if you have one)
   - **Description**: `Document Manager Application`

### 5.2 Create Start Menu Shortcut

1. Right-click **User's Programs Menu** folder
2. Select **Add → Folder**
3. Rename the folder to: `duHast`
4. In File System editor, locate `Primary output` under **Application Folder**
5. Right-click → **Create Shortcut**
6. Rename to: `DocManager`
7. **Drag** this shortcut to the `duHast` folder you created under **User's Programs Menu**
8. Configure shortcut properties as above

## Step 6: Configure Prerequisites

### 6.1 Add .NET Runtime Prerequisite

1. Right-click on `DocManager.Setup` project
2. Select **Properties**
3. Click the **Prerequisites** button
4. In the Prerequisites dialog, check:
   - ✓ **.NET Desktop Runtime 8.0** (or your target .NET version)
   - ✓ **Create setup program to install prerequisite components**
5. Select download location:
   - ⦿ **Download prerequisites from the component vendor's web site** (recommended)
6. Click **OK**

### 6.2 Verify NuGet Dependencies

The following dependencies should be automatically included via Primary Output:
- ✓ SQLite-net-pcl
- ✓ CsvHelper
- ✓ MVVM Community Toolkit
- ✓ Newtonsoft.Json
- ✓ All WPF framework assemblies

**No additional action needed** - these are bundled automatically.

## Step 7: Configure User Data Locations

**Important**: Your application already stores user settings correctly:
- Settings Path: `%LocalAppData%\duHast\`
- Files created:
  - `DatabaseConnection.json`
  - `CurrentFolderManager.json`
  - `CloudDocumentManager.json`

**No installer configuration needed** - this is handled by your `SettingsService` class at runtime.

### How It Works Per Installation Type:

#### Per-Machine Install (All Users):
- **Program Files**: `C:\Program Files\duHast\DocManager\` (shared, read-only)
- **User Settings**: `C:\Users\[Username]\AppData\Local\duHast\` (per-user, writable)

#### Per-User Install (Only Me):
- **Program Files**: `C:\Users\[Username]\AppData\Local\Programs\duHast\DocManager\` (user-specific)
- **User Settings**: `C:\Users\[Username]\AppData\Local\duHast\` (same location)

## Step 8: Configure Launch Conditions

1. Right-click `DocManager.Setup` → **View → Launch Conditions**
2. Review the default conditions:
   - **Search for .NET Desktop Runtime** (already configured via Prerequisites)
3. Add custom conditions if needed (optional):
   - Right-click **Launch Conditions** → **Add Windows Version Condition**
   - Example: Require Windows 10 or later

## Step 9: Configure User Interface

1. Right-click `DocManager.Setup` → **View → User Interface**
2. You'll see two install flows:
   - **Install** (normal installation)
   - **Administrative Install** (network deployment)

### Customize Install Flow (Optional)

Under **Install → Start**:
- `Welcome` - Introduction screen
- `Installation Folder` - **This is where InstallAllUsersVisible matters!**
  - When `InstallAllUsersVisible = TRUE`, users see "Install for all users" checkbox
- `Confirm Installation` - Final confirmation

You can add custom dialogs here if needed (Checkboxes, RadioButtons, Textboxes).

## Step 10: Build Configuration

### 10.1 Set Build Configuration

1. Right-click `DocManager.Setup` project
2. Select **Properties**
3. In **Configuration** dropdown, ensure it matches your application:
   - `Release` (recommended for distribution)
   - `Debug` (for testing)

### 10.2 Output Settings

1. In Properties window, locate:
   - **Output file name**: `DocManager.msi` (default is fine)
   - **Package files**: `As loose uncompressed files` or `In cabinet file(s)` (compressed, recommended)
   - **Compression**: `Optimized for size` (recommended)

## Step 11: Build the MSI

1. Right-click `DocManager.Setup` project
2. Select **Build**
3. Watch the Output window for build progress
4. Build output location:
   - **Debug**: `[SolutionDir]\DocManager.Setup\Debug\DocManager.msi`
   - **Release**: `[SolutionDir]\DocManager.Setup\Release\DocManager.msi`

### Build Also Creates:
- `setup.exe` - Bootstrap installer that checks prerequisites
- `DocManager.msi` - Main installer package

## Step 12: Test the Installer

### 12.1 Test Per-Machine Install (All Users)

1. Locate `setup.exe` in the build output folder
2. **Right-click** → **Run as administrator**
3. In the Installation Folder dialog, select **"Install for all users"** (checkbox)
4. Complete installation
5. Verify:
   - ✓ Program installed in `C:\Program Files\duHast\DocManager\`
   - ✓ Start Menu shortcut exists
   - ✓ Desktop shortcut exists (if configured)
6. Run the application
7. Verify settings created in `%LocalAppData%\duHast\`
8. Uninstall via **Add/Remove Programs**

### 12.2 Test Per-User Install (Only Me)

1. Locate `setup.exe` in the build output folder
2. **Double-click** to run (no admin rights)
3. In the Installation Folder dialog, **uncheck** "Install for all users"
4. Complete installation
5. Verify:
   - ✓ Program installed in `C:\Users\[You]\AppData\Local\Programs\duHast\DocManager\`
   - ✓ Start Menu shortcut exists for your user only
   - ✓ Desktop shortcut exists for your user only
6. Run the application
7. Verify settings created in `%LocalAppData%\duHast\`
8. Uninstall via **Add/Remove Programs**

### 12.3 Test Upgrade Scenario

1. Install version 1.0.0
2. Create some test settings (connect to a database, configure folders)
3. Increment version to 1.0.1 in installer properties
4. Change `ProductCode` (right-click project → Properties → generate new GUID)
5. **Keep** `UpgradeCode` the same (critical!)
6. Rebuild installer
7. Run new installer
8. Verify:
   - ✓ Old version removed automatically
   - ✓ New version installed
   - ✓ Settings preserved in `%LocalAppData%\duHast\`

## Step 13: Distribution

### What to Distribute:

**Option 1: Setup.exe + MSI (Recommended)**
- Distribute both files together
- Users run `setup.exe`
- Automatically installs prerequisites (.NET Runtime)

**Option 2: MSI Only**
- For environments where .NET Runtime is already installed
- Users run `DocManager.msi` directly
- Smaller file size

### File Locations:
```
[BuildOutput]\
├── setup.exe                    (Bootstrap installer)
├── DocManager.msi              (Main installer)
└── [PrerequisiteFiles]\        (If prerequisites embedded)
```

## Common Configurations Summary

| Scenario | InstallAllUsers | InstallAllUsersVisible | RequiresElevation | Result |
|----------|----------------|----------------------|-------------------|--------|
| **Flexible (Recommended)** | TRUE | TRUE | TRUE | User chooses at install time |
| **Force Per-Machine** | TRUE | FALSE | TRUE | Always installs for all users |
| **Force Per-User** | FALSE | FALSE | FALSE | Always installs for current user only |

## Troubleshooting

### Issue: "Product code" or "Upgrade code" errors
**Solution**: 
- Each new version needs a new `ProductCode` (regenerate GUID)
- Keep `UpgradeCode` the same across all versions
- Right-click project → Properties → Click `{...}` button to generate new GUID

### Issue: Installer asks for admin rights even for per-user install
**Solution**: 
- Ensure `RequiresElevation = TRUE` only if `InstallAllUsers = TRUE`
- For per-user only installs, set `RequiresElevation = FALSE`

### Issue: Application files not included
**Solution**: 
- Ensure you added **Primary output** not individual files
- Check your standalone project builds successfully first
- Verify `Primary output` appears under Application Folder in File System view

### Issue: Missing DLLs at runtime
**Solution**: 
- NuGet packages should be included automatically via Primary output
- If missing, manually add them: File System → Application Folder → Add → File
- Check `CopyLocal = True` on project references

### Issue: Settings not persisting
**Solution**: 
- Your `SettingsService` correctly uses `%LocalAppData%\duHast\`
- No installer changes needed
- Verify folder permissions if issues persist

### Issue: Can't uninstall
**Solution**: 
- Check Windows Event Log for errors
- Ensure no application instances are running
- Use `msiexec /x {ProductCode}` from command line

## Version Management

### For Each New Release:

1. **Update Version Number**:
   - Right-click `DocManager.Setup` → Properties
   - Increment **Version** (e.g., 1.0.0 → 1.0.1)

2. **Generate New Product Code**:
   - Properties → **ProductCode** → Click `{...}` button → New GUID
   - **This is required for upgrades to work!**

3. **Keep Upgrade Code**:
   - Properties → **UpgradeCode** → **DO NOT CHANGE**
   - Same UpgradeCode links all versions as upgradeable

4. **Set RemovePreviousVersions**:
   - Properties → **RemovePreviousVersions** = `True`
   - Automatically uninstalls old version before installing new

5. **Rebuild**:
   - Build the Setup project
   - Test upgrade scenario

## Advanced Options (Future Enhancements)

### Code Signing (Recommended for Production)
1. Obtain code signing certificate
2. Right-click project → Properties
3. Under **Signing**, import your certificate
4. Or use `signtool.exe` post-build

### Custom Actions (If Needed)
1. View → Custom Actions
2. Add custom executables or scripts for:
   - Install phase
   - Commit phase
   - Rollback phase
   - Uninstall phase

### Registry Entries (Optional)
1. View → Registry
2. Add keys for:
   - File associations
   - Application settings
   - Uninstall information

### File Associations (Optional)
1. View → File Types
2. Add associations for:
   - `.db` files (DocManager database files)
   - Custom file extensions

## Recommended Final Configuration

```
Project Properties:
├── Author: duHast
├── Manufacturer: duHast
├── ProductName: DocManager
├── Version: 1.0.0
├── InstallAllUsers: TRUE
├── InstallAllUsersVisible: TRUE
├── RequiresElevation: TRUE
├── RemovePreviousVersions: TRUE
└── DefaultLocation: [ProgramFilesFolder][Manufacturer]\[ProductName]

File System:
├── Application Folder
│   ├── Primary output from [Standalone Project]
│   └── [Content Files]
├── User's Desktop
│   └── Shortcut to Primary output
└── User's Programs Menu
    └── duHast
        └── Shortcut to Primary output

Prerequisites:
└── .NET Desktop Runtime 8.0 (or target version)
```

## Notes

1. **Settings Location**: Your application correctly stores settings in `%LocalAppData%\duHast\` which is perfect because:
   - Works for both per-machine and per-user installs
   - Each user gets their own settings
   - No admin rights needed to write settings
   - Settings survive uninstall/reinstall

2. **Database Files**: Users will specify database location via your application UI, so no installer configuration needed.

3. **Flexible Installation**: With `InstallAllUsersVisible = TRUE`, you've created a single MSI that works for:
   - Enterprise deployments (IT admins choose "All Users")
   - Individual users (choose "Only Me")
   - Testing both scenarios with one installer

4. **Future-Proof**: This setup supports:
   - Silent installs via `msiexec`
   - Group Policy deployment
   - SCCM/Intune deployment
   - Manual user installation

## Next Steps After Initial Setup

1. Build and test both installation scenarios
2. Verify settings persistence
3. Test uninstall/reinstall
4. Test upgrade scenario
5. Share installer with client for feedback
6. Lock down configuration once client chooses preferred installation type (if they want)

---

**Created for**: DocManager Standalone Application  
**Author**: duHast  
**Date**: 2025  
**Visual Studio**: 2022 (compatible with 2019, 2017)
