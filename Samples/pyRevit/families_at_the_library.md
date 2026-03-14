# At The Library

**Panel:** Families | **Button:** At The Library

Opens the **AtTheLibrary** WPF application — an interactive library browser that lets you view, filter, load, and edit families from a Schedule of Accommodation (SoA) data source without leaving Revit.

## What it does

- Loads family data from a CSV-based SoA file and displays it in a filterable grid.
- Shows how many instances of each family are currently loaded in the open Revit document (the **Count** column).
- Lets you select individual families and:
  - **Load** the `.rfa` file directly into the current document.
  - **Edit** the family by opening its `.rfa` in the Revit family editor.
  - **Edit Type Catalogue** to modify the family's type catalogue file using an inline table editor.
- Supports optional parameter column filtering so you can display only the SoA parameters relevant to your task.

## When to use this

Use this button when you need to browse a family library, check what is already loaded in a project, or load and edit specific families in an organised, data-driven way — rather than using the Revit Load Family dialog.

## Notes

- The SoA CSV file path is configured within the AtTheLibrary window (browse or type the path, then click Load Data).
- See the [AtTheLibrary user guide](../../VS/duHastRevitApplications/AtTheLibrary/docs/01_main_ui.md) for full documentation of the interface.
