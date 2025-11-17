# DocManager Architecture - Final Summary

## Overview

The DocManager application has been restructured to support both Standalone and Revit-hosted deployments using a shared bootstrapper pattern.

## Key Principle

**The bootstrapper lives in UI.Shared, not in the Revit project.**

This ensures:
- Clean separation of concerns
- No unnecessary dependencies
- True code reuse between Standalone and Revit versions
- The Revit project is minimal (just deployment files)

## Project Structure

```
Solution/
├── duHastNet.DocManager.Core/
│   ├── Models/
│   ├── Services/
│   │   └── Api/
│   │       └── DocManagerApi.cs            # Main API for external integration
│   └── Interfaces/
│
├── duHastNet.DocManager.UI.Shared/
│   ├── ViewModels/
│   │   ├── NavigationHostViewModel.cs
│   │   ├── SettingsViewModel.cs
│   │   └── MergeViewModel.cs
│   ├── Views/
│   │   ├── NavigationHostView.xaml         # UserControl (not Window)
│   │   ├── SettingsView.xaml
│   │   └── MergeView.xaml
│   ├── Services/
│   │   ├── DocManagerBootstrapper.cs       # ⭐ THE KEY CLASS
│   │   ├── DialogService.cs
│   │   └── SettingsService.cs
│   └── Stores/
│       ├── NavigationStore.cs
│       └── MessageStore.cs
│
├── DocManager.Standalone/                   # Standalone WPF Application
│   ├── App.xaml
│   └── App.xaml.cs                         # Calls bootstrapper
│
└── duHastNet.DocManager.Revit/              # Revit Integration (minimal)
    └── PyRevit/
        └── DocManager.extension/           # PyRevit extension files
            ├── bundle.yaml
            ├── README.md
            └── DocManager.tab/
                └── Launch.panel/
                    └── Open DocManager.pushbutton/
                        ├── script.py       # Calls bootstrapper
                        └── icon.png
```

## The Bootstrapper Pattern

### What is DocManagerBootstrapper?

A class that:
1. **Initializes all services** (API, Manager, MessageStore, etc.)
2. **Loads settings** from JSON files
3. **Connects to database** if previously configured
4. **Creates the main window** with proper ViewModel wiring
5. **Returns a Window** ready to display

### Why in UI.Shared?

**Location:** `duHastNet.DocManager.UI.Shared/Services/DocManagerBootstrapper.cs`

**Namespace:** `duHastNet.DocManager.UI.Shared.Services`

**Reasons:**
- ✅ It creates UI components (ViewModels, Views)
- ✅ Both Standalone and Revit need it
- ✅ No Revit-specific code
- ✅ Keeps Revit project minimal
- ✅ Standalone doesn't depend on Revit project
- ✅ Logical grouping with other services (DialogService, SettingsService)

## Usage Patterns

### From Standalone WPF App

```csharp
// App.xaml.cs
using duHastNet.DocManager.UI.Shared.Services;

public partial class App : Application
{
    private DocManagerBootstrapper? _bootstrapper;

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        
        _bootstrapper = new DocManagerBootstrapper();
        MainWindow = await _bootstrapper.InitializeAsync();
        MainWindow.Show();
    }
}
```

### From PyRevit (IronPython)

```python
# script.py
import clr
clr.AddReference("duHastNet.DocManager.Core")
clr.AddReference("duHastNet.DocManager.UI.Shared")

from duHastNet.DocManager.UI.Shared.Services import DocManagerBootstrapper

bootstrapper = DocManagerBootstrapper()
window = bootstrapper.Initialize()  # Synchronous version
window.Show()
```

### Future: From Revit Add-in (C#)

```csharp
// DocManagerCommand.cs
using duHastNet.DocManager.UI.Shared.Services;

public class DocManagerCommand : IExternalCommand
{
    public Result Execute(ExternalCommandData commandData, 
        ref string message, ElementSet elements)
    {
        var bootstrapper = new DocManagerBootstrapper();
        var window = bootstrapper.Initialize();
        window.Show();
        return Result.Succeeded;
    }
}
```

## Window Structure

The bootstrapper creates this structure:

```
Window (System.Windows.Window)
└── Content = NavigationHostView (UserControl)
    └── DataContext = NavigationHostViewModel
        ├── CurrentViewModel (changes based on navigation)
        │   ├── SettingsViewModel → SettingsView
        │   └── MergeViewModel → MergeView
        └── Services (API, Manager, MessageStore, etc.)
```

**Why this structure?**
- `NavigationHostView` is a `UserControl` (for flexibility)
- Bootstrapper wraps it in a `Window` (required for display)
- ViewModel handles navigation between different views
- Clean MVVM pattern throughout

## Dependency Flow

```
┌──────────────────────────────────┐
│  duHastNet.DocManager.Core       │
│  - DocManagerApi                 │
│  - Manager, Document, Revision   │
│  - Database services             │
└────────────┬─────────────────────┘
             │
             │ Referenced by
             ↓
┌──────────────────────────────────┐
│  duHastNet.DocManager.UI.Shared  │
│  - DocManagerBootstrapper ⭐     │
│  - ViewModels, Views             │
│  - Services, Stores              │
└────────────┬─────────────────────┘
             │
             │ Referenced by
       ┌─────┴──────┐
       ↓            ↓
┌──────────┐  ┌──────────┐
│Standalone│  │  Revit   │
│(WPF App) │  │(PyRevit) │
└──────────┘  └──────────┘
```

## Benefits of This Architecture

### 1. Code Reuse
- Single bootstrapper used by all hosts
- Same initialization logic everywhere
- Bug fixes benefit all versions

### 2. Clean Separation
- Core = Business logic (no UI)
- UI.Shared = UI + Initialization (no host-specific code)
- Standalone = WPF app hosting
- Revit = Revit-specific hosting

### 3. Testability
- Bootstrapper can be unit tested
- No Application dependencies required
- Can mock services easily

### 4. Maintainability
- Changes to initialization in one place
- Clear dependencies between projects
- No circular references

### 5. Flexibility
- Easy to add new hosts (Windows Service, Console App, etc.)
- Can create multiple instances if needed
- Host-agnostic design

## File Locations

### Source Code
```
duHastNet.DocManager.UI.Shared/
└── Services/
    └── DocManagerBootstrapper.cs
```

### Standalone App
```
DocManager.Standalone/
└── App.xaml.cs                      (uses bootstrapper)
```

### PyRevit Extension (Deployed)
```
%APPDATA%\pyRevit\Extensions\DocManager.extension/
├── bundle.yaml
├── README.md
├── DocManager.tab/
│   └── Launch.panel/
│       └── Open DocManager.pushbutton/
│           └── script.py            (uses bootstrapper)
└── lib/
    ├── duHastNet.DocManager.Core.dll
    ├── duHastNet.DocManager.UI.Shared.dll  (contains bootstrapper)
    └── (dependencies)
```

## Key Classes

### DocManagerBootstrapper
**Purpose:** Initialize and wire up the entire application

**Key Methods:**
- `InitializeAsync()` - Async initialization, returns Window
- `Initialize()` - Sync wrapper for IronPython
- `Shutdown()` - Cleanup resources

**Creates:**
- All services (API, Manager, MessageStore, etc.)
- Loads settings from JSON
- Connects to database
- Creates Window with NavigationHostView
- Wires up ViewModels

### NavigationHostViewModel
**Purpose:** Manage navigation between views

**Responsibilities:**
- Host current ViewModel
- Switch between Settings and Merge views
- Provide ViewModels with services they need

### DocManagerApi
**Purpose:** External integration API

**Used By:**
- ViewModels (for database operations)
- Import/Export services
- Any external caller

## Settings and Data

### Settings Files (JSON)
```
%APPDATA%\DocManager\
├── DatabaseConnection.json
├── CurrentFolderManager.json
└── CloudDocumentManager.json
```

### Database
```
User-specified location, e.g.:
C:\Users\<Username>\Documents\DocManager\project.db
```

## Revit Integration Notes

### What Revit Does
- Hosts the application (runs the Python script)
- Provides environment to bypass file restrictions
- **Does NOT interact with Revit documents**
- **Does NOT use Revit API**

### What Revit Does NOT Do
- Does not read/write Revit parameters
- Does not modify Revit documents
- Does not export from Revit
- Does not sync with Revit data

### Why Use Revit?
- Convenient launcher at work
- Bypass certain file system restrictions
- Always available when working on Revit projects
- Can keep DocManager open alongside Revit

## Future Extensions

### Easy to Add
1. **Revit Add-in** (native .addin bundle)
2. **Console Application** (for automation)
3. **Windows Service** (background processing)
4. **Web API Host** (expose DocManager via REST)

All would use the same `DocManagerBootstrapper` class.

### Would Require Changes
- Different UI framework (WinForms, Avalonia, etc.)
  - Would need new bootstrapper, but Core stays same
- Cloud-based hosting
  - Would need different database backend

## Summary

**The Pattern:**
```
Bootstrapper (in UI.Shared)
    ↓
Creates Window + ViewModels
    ↓
Host (Standalone/Revit) Shows Window
    ↓
User Interacts with DocManager
```

**The Key Insight:**
By placing the bootstrapper in UI.Shared, we achieve true code reuse without creating unwanted dependencies between Standalone and Revit projects.

**The Result:**
- Clean architecture
- Minimal code duplication
- Easy to test
- Easy to extend
- Clear separation of concerns
