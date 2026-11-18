# DocManager installer

An MSI built with [WiX Toolset v5](https://wixtoolset.org/) (pinned to 5.0.2). It builds with `dotnet build`, so GitHub Actions can build it
and Visual Studio is not needed. It replaces the two Visual Studio Installer Projects (`DocManager.Setup`, `DocManager.Setup.PerUser`).

## Build

```
dotnet build VS/duHastApplications/duHastNet.DocManager/DocManager.Installer -c Release
```

The build publishes the Standalone app (framework dependent, win-x64) into `obj\publish` and packages the published files (no pdb files).
The MSI is written to `bin\Release\DocManager-<version>-x64.msi`.

The version is the `Version` of `duHastNet.DocManager.Standalone.csproj`; the published app gets the same version. To build another
version: `-p:InstallerVersion=1.2.3` (numbers only, major.minor.build).

> The previous installers were version 1.1.0. Windows Installer refuses to replace an installed product with a package of a lower or
> equal version (it counts as a downgrade), so keep the version above 1.1.0. The build warns if it is not.

## What the installer does

- One setup for both kinds of install: the dialogs ask *Install just for you* or *Install for all users* (the two Visual Studio projects were
  one each).
  - all users: `C:\Program Files\duHast\DocManager` (needs administrator rights)
  - just for you: `%LocalAppData%\Programs\duHast\DocManager`
- Start menu entry *duHast > DocManager*.
- Needs the **.NET 8 Desktop Runtime (x64)**: the setup stops with a message and the download link when it is missing.
- Same `UpgradeCode` as the previous installers, so installing a newer version replaces the installed one (all users replaces all users, just for you
  replaces just for you: Windows Installer does not upgrade across the two).
- Settings are not touched: the app keeps them in `%LocalAppData%\duHast`, they stay when the app is uninstalled or upgraded.

## Silent install

```
msiexec /i DocManager-1.2.0-x64.msi /qn                          (all users, needs admin rights)
msiexec /i DocManager-1.2.0-x64.msi /qn MSIINSTALLPERUSER=1      (just for the current user)
msiexec /i DocManager-1.2.0-x64.msi /qn APPLICATIONFOLDER="D:\Tools\DocManager"
```

## Release

`.github/workflows/build_docmanager_installer.yml` builds the MSI on every pull request touching this folder (kept as a workflow
artifact) and attaches it to a release when `build_and_publish.yml` runs for one.

The MSI is not code signed.

## Files

| File | |
|---|---|
| `DocManager.Installer.wixproj` | project: version, publish step, WiX extensions |
| `Package.wxs` | the package: files, shortcut, runtime check, dialogs |
| `License.rtf` | the licence dialog (the repository LICENSE) |
