# duHastNet.DocManager.Revit Project

## Purpose

This project contains **only** the Revit-specific integration files for DocManager. It is intentionally minimal.

## What's Here

```
duHastNet.DocManager.Revit/
└── PyRevit/
    └── DocManager.extension/
        ├── bundle.yaml
        ├── README.md
        └── DocManager.tab/
            └── Launch.panel/
                └── Open DocManager.pushbutton/
                    ├── script.py
                    └── icon.png
```

## What's NOT Here

**The bootstrapper is NOT in this project!**

The `DocManagerBootstrapper` class lives in `duHastNet.DocManager.UI.Shared/Services/` because:
- It's shared code used by both Standalone and Revit versions
- It has no Revit-specific code
- It belongs with the UI components it initializes
- Keeps dependencies clean (Standalone doesn't need to reference Revit project)

## Project Dependencies

This project references:
- `duHastNet.DocManager.Core` (for models/API)
- `duHastNet.DocManager.UI.Shared` (for bootstrapper and UI)

This project does NOT need a separate assembly. It only contains resource files (Python scripts, YAML, etc.) that are deployed as a pyRevit extension.

## Architecture

```
┌─────────────────────────────────────────┐
│  duHastNet.DocManager.Core              │
│  (Business Logic, Database, API)        │
└─────────────────┬───────────────────────┘
                  │
                  │ References
                  ↓
┌─────────────────────────────────────────┐
│  duHastNet.DocManager.UI.Shared         │
│  (Views, ViewModels, Bootstrapper)      │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ↓                   ↓
┌───────────────┐   ┌───────────────┐
│  Standalone   │   │  Revit        │
│  (WPF App)    │   │  (PyRevit)    │
└───────────────┘   └───────────────┘
```

## Building

**Important:** This project does NOT build a DLL. 

It's a content-only project that:
1. Contains the pyRevit extension files
2. Gets packaged for distribution
3. References other assemblies that DO build

## Deployment

See `DEPLOYMENT.md` for complete deployment instructions.

Quick summary:
1. Build the solution (builds Core and UI.Shared DLLs)
2. Copy DLLs from UI.Shared\bin\Release to extension\lib folder
3. Copy extension folder to pyRevit extensions directory
4. Reload pyRevit

## Future Additions

If you want to add a Revit Add-in (not just pyRevit), you could add:
```
duHastNet.DocManager.Revit/
└── AddIn/
    ├── DocManagerAddIn.cs          # IExternalApplication
    ├── DocManagerCommand.cs        # IExternalCommand
    └── DocManager.addin            # Manifest file
```

But for now, pyRevit is sufficient and simpler.

## Testing

To test the pyRevit extension:
1. Install extension to pyRevit extensions folder
2. Open Revit 2025
3. Reload pyRevit
4. Click "Open DocManager" button in DocManager tab
5. DocManager window should open independently

## Notes

- No Revit API code is needed (DocManager doesn't interact with Revit)
- Revit is just a host environment to bypass file restrictions
- DocManager runs completely independently of Revit
- The same bootstrapper code works for both Standalone and Revit versions
