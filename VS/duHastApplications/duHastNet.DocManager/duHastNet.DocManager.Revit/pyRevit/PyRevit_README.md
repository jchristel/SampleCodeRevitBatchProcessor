# DocManager PyRevit Extension

## Overview
This PyRevit extension provides a launcher button for the DocManager document management application within Autodesk Revit.

**Important:** This extension does NOT interact with Revit documents or data. It simply provides a convenient way to launch the standalone DocManager application from within the Revit environment, useful for bypassing certain file system restrictions.

## Features
- Single button to launch DocManager
- Runs independently of Revit
- Can remain open while working in Revit
- Full access to DocManager functionality

## Installation

### Method 1: Manual Installation
1. Download or clone the extension
2. Copy the `DocManager.extension` folder to your pyRevit extensions directory:
   - Windows: `%APPDATA%\pyRevit\Extensions\`
   - Or use the pyRevit extensions directory shown in pyRevit settings
3. Reload pyRevit (pyRevit menu → Reload)
4. The DocManager tab should appear in the Revit ribbon

### Method 2: pyRevit Package Manager
*(If/when available in pyRevit package manager)*
1. Open pyRevit menu
2. Click "Extensions"
3. Search for "DocManager"
4. Click Install

## Structure
```
DocManager.extension/
├── bundle.yaml                          # Extension metadata
├── README.md                            # This file
├── DocManager.tab/                      # Ribbon tab
│   └── Launch.panel/                    # Ribbon panel
│       └── Open DocManager.pushbutton/  # Launch button
│           ├── script.py                # Python launch script
│           └── icon.png                 # Button icon
└── lib/                                 # .NET assemblies
    ├── duHastNet.DocManager.Revit.dll
    ├── duHastNet.DocManager.Core.dll
    ├── duHastNet.DocManager.UI.Shared.dll
    └── (other dependencies)
```

## Usage
1. Open Revit (any project or family)
2. Click the "DocManager" tab in the ribbon
3. Click "Open DocManager" button
4. The DocManager window will open
5. Use DocManager normally
6. Close DocManager window when done

## Requirements
- Autodesk Revit 2025 or later
- pyRevit 4.8 or later
- .NET 8.0 runtime (installed with Revit 2025)

## Troubleshooting

### Button doesn't appear
- Verify extension is in correct directory
- Reload pyRevit
- Check pyRevit output window for errors

### Error launching DocManager
- Check lib folder contains all required DLLs
- Verify .NET 8.0 is installed
- Check pyRevit output window for detailed error

### Window doesn't open
- Check if DocManager opened behind Revit window
- Try Alt+Tab to switch windows
- Check Windows taskbar

## Notes
- DocManager runs independently of Revit
- You can open multiple DocManager windows
- Closing DocManager does not affect Revit
- No Revit document interaction occurs

## Support
For issues or questions:
- GitHub: https://github.com/jchristel/SampleCodeRevitBatchProcessor
- Open an issue on the repository

## License
BSD License - See main project for details
