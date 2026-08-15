# Push It!

**Panel:** PushIt | **Button:** Push It!

<img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/PushIt.pushbutton/Icon.png" width="40" alt="button icon">

Opens the **PushIt** WPF application — the main interface for loading room data from an external source (CSV or drofus API) and pushing parameter values into mock room families in the open Revit document.

## What it does

- Loads a room schedule (Schedule of Accommodation) from a CSV file or drofus API connection.
- Displays each room entry alongside the number of matching mock room family instances found in the current Revit model.
- Lets you push data from a single selected row into its matching mock room, split a mock room, or create a new mock room.
- Provides bulk operations (update all, wipe stale data) and data export.

## Mock rooms

Mock rooms are Revit families that visually resemble rooms (with or without walls) but are generic model families — not native Revit rooms. PushIt targets these mock room families to carry room data.

## When to use this

Use this button as the primary PushIt workflow tool whenever you need to synchronise room data from an external source into a Revit layout model.

## Notes

- Configure your data source (CSV path or drofus credentials) via **⚙ Settings** inside the PushIt window before loading data.
- The window is a .NET UI loaded from the extension's `bin` folder at run time. If that folder is missing or incomplete the button fails immediately with a message about the bin directory.
- See the [PushIt user guide](../../VS/duHastRevitApplications/PushIt/docs/01_main_ui.md) for full interface documentation.
