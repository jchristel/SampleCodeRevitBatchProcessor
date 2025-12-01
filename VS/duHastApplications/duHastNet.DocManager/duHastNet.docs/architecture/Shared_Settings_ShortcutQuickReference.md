# Quick Reference: Creating Shortcuts for Shared Settings

## Shortcut Creation Steps

1. Right-click on Desktop or in a folder
2. Select **New > Shortcut**
3. Enter target path (see examples below)
4. Click **Next**
5. Name your shortcut
6. Click **Finish**

## Shortcut Target Examples

### Default Settings (Local User)
```
"C:\Program Files\DocManager\DocManager.exe"
```
*Uses: %LocalAppData%\duHast*

### Network Share (UNC Path)
```
"C:\Program Files\DocManager\DocManager.exe" --settings="\\FileServer\Share\DocManagerSettings"
```

### Local Shared Folder
```
"C:\Program Files\DocManager\DocManager.exe" --settings="C:\SharedData\DocManagerSettings"
```

### Multiple Projects Example

**Project A Shortcut:**
```
"C:\Program Files\DocManager\DocManager.exe" --settings="\\FileServer\ProjectA\Settings"
```
Name: "DocManager - Project A"

**Project B Shortcut:**
```
"C:\Program Files\DocManager\DocManager.exe" --settings="\\FileServer\ProjectB\Settings"
```
Name: "DocManager - Project B"

## Network Path Format

✅ **Correct UNC Paths:**
- `\\ServerName\ShareName\FolderName`
- `\\192.168.1.100\Shared\DocManager`
- `\\FILESERVER\Departments\Engineering\DocManagerSettings`

❌ **Incorrect Paths:**
- `\\ServerName\ShareName\FolderName\` (trailing backslash - optional but can cause issues)
- `ServerName\ShareName` (missing leading \\)
- `\\Server Name\Share` (spaces in server name without proper escaping)

## Testing Your Shortcut

After creating the shortcut:

1. Double-click to launch the application
2. Navigate to Settings view
3. Verify settings are loading from correct location
4. Make a test change and save
5. Check the settings directory to confirm files are being written

## Permission Requirements

Users need:
- ✅ Read access to the settings directory
- ✅ Write access to the settings directory
- ✅ Create files permission
- ✅ Delete files permission (for .tmp and .bak files)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Access Denied" | Check folder permissions |
| "Path not found" | Verify UNC path is correct |
| Settings not persisting | Ensure write permissions are granted |
| Application won't start | Check path doesn't contain invalid characters |

## Best Practices

1. **Test locally first** - Use a local path like `C:\TestSettings` before deploying to network
2. **Document the path** - Keep a record of the shared settings location
3. **Consistent naming** - Use clear shortcut names like "DocManager - Team Settings"
4. **Backup settings** - Periodically backup the shared settings folder

## Example Deployment

For a team of 5 users sharing settings on a network drive:

1. **Create shared folder:**
   ```
   \\FileServer\Shared\DocManager\TeamSettings
   ```

2. **Set permissions:**
   - Add user group with Read/Write access
   - Test access by each user

3. **Create shortcut on each user's desktop:**
   ```
   "C:\Program Files\DocManager\DocManager.exe" --settings="\\FileServer\Shared\DocManager\TeamSettings"
   ```

4. **Name the shortcut:**
   ```
   DocManager - Team Settings
   ```

5. **Test:**
   - First user launches and configures settings
   - Second user launches and verifies settings match
   - Both users save settings to confirm no conflicts

## Important Notes

⚠️ **All users sharing settings will see:**
- Same database connection
- Same folder paths
- Same cloud document settings
- All other application settings

⚠️ **Last write wins:**
If two users save settings simultaneously, the last one to save will overwrite the other's changes.

⚠️ **Security:**
Settings files contain database connection strings and paths - ensure appropriate access controls.
