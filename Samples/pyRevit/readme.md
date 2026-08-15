# duHast pyRevit Extension

A pyRevit toolbar extension for Revit, providing automation tools for BIM workflows across family management, export, view management, model maintenance, and more.

---

## Toolbar Panels

### Families

Tools for loading, saving, renaming, swapping, and reporting on Revit families and type catalogue files.

| Button Group | Description |
|---|---|
| [Reload](families_reload.md) | Reload families from a library folder, with match-status filtering |
| [Rename](families_rename.md) | Rename loaded families and types, or rename files in a library folder |
| [Load / Save](families_io.md) | Bulk-load families into the project, or save families out to a folder |
| [Catalogue Files](families_catalogue_files.md) | Export and clean type catalogue files; strip a family back to a single catalogue placeholder type |
| [Force Update](families_force_update.md) | Force Revit to detect a family as changed when source files have been overwritten |
| [Change Category](families_change_category.md) | Reassign the open family to a different Revit category, preserving subcategories |
| [Swap](families_swap.md) | Replace family instances with a different family, by CSV directive or interactive selection |
| [Reports](families_reports.md) | Generate, compare, and export reports on family libraries and projects |
| [At The Library](families_at_the_library.md) | Open the AtTheLibrary tool for managing shared type catalogue parameters |

---

### Export

Tools for exporting sheets to PDF and DWG, comparing export sets, and managing document metadata.

| Button Group | Description |
|---|---|
| [PDF / DWG Export](export_pdf_dwg.md) | Export sheets to PDF and/or DWG with configurable naming rules and print sets |
| [Compare](export_compare.md) | Check the sheets in a Revit schedule against the PDF files in a folder |
| [DocManager](export_docmanager.md) | Manage document properties and revision data for export records |

---

### Grids

Tools for controlling grid bubble visibility and 2D/3D extent behaviour.

| Button Group | Description |
|---|---|
| [Grids](grids.md) | Toggle grid bubbles on/off at ends 0 and 1, switch to 2D, propagate and extend grids |

---

### Levels

Tools for controlling level header visibility and 2D/3D extent behaviour.

| Button Group | Description |
|---|---|
| [Levels](levels.md) | Toggle level headers on/off at ends 0 and 1, switch to 2D |

---

### Warnings

Tools for resolving and highlighting common Revit warnings related to rooms, areas, and annotation.

| Button Group | Description |
|---|---|
| [Solve Warnings](warnings_solve.md) | Fix room tags outside rooms, duplicate marks, and overlapping separation lines |
| [Highlight Warnings](warnings_highlight.md) | Report area and room separation lines carrying warnings, and colour-highlight them in the active view |

---

### View Templates

Tools for importing, exporting, and applying view templates, filters, and graphic overrides.

| Button Group | Description |
|---|---|
| [Import / Export](view_templates_import_export.md) | Export and import view templates, view filters, and colour schemes to/from JSON |
| [Modify](view_templates_modify.md) | Apply filter overrides and graphic overrides to view templates in bulk |

---

### PushIt

Tools for managing mock rooms (room-like generic model families) and their associated data.

| Button Group | Description |
|---|---|
| [PushIt](pushit_main.md) | Open the PushIt application for managing mock room data |
| [Get A Room!](pushit_get_a_room.md) | Build mock room families from filled regions; set the family output directory |
| [Swap Dimensions](pushit_swap_dimensions.md) | Swap the Width and Depth parameter values on selected mock rooms |
| [Stats](pushit_stats.md) | Report mock room counts by family, creator and owner; flag IDs duplicated across design sets |
| [Place Revit Rooms](pushit_place_revit_rooms.md) | Create native Revit rooms at the locations of mock rooms |
| [Verify Push It Area](pushit_area_by_room.md) | Measure mock rooms with temporary Revit rooms and write the area back onto them |

---

### Purge

Tools for purging unused elements from the model to reduce file size and improve performance.

| Button Group | Description |
|---|---|
| [Purge Unused](purge_unused.md) | Purge unused line styles, fill patterns, line patterns, shared parameters, filters, legends, schedules, view templates, and unplaced views — with or without pre-selection |

---

### Data Collectors

Scripts for exporting model data to file for reporting and audit purposes.

| Button Group | Description |
|---|---|
| [Data Collectors](data_collectors.md) | Collect and export rooms, sheets, ceilings, and levels data to file |

---

### Ceilings

Tools for generating ceiling elements from room boundaries.

| Button Group | Description |
|---|---|
| [Ceilings By Rooms](ceilings_by_rooms.md) | Automatically create ceiling elements for every room in the model |

---

### Walls

Tools that relate walls and facade openings back to the rooms they bound.

| Button Group | Description |
|---|---|
| [Walls By Room](walls_by_rooms.md) | Write the room number onto the walls bounding each selected room |
| [Facade Opening To Room](walls_facade_opening.md) | Report external wall and window opening areas per room to CSV |

---

### Cloud

Tools for working with cloud-hosted Revit models.

| Button Group | Description |
|---|---|
| [Cloud GUIDs](cloud_guids.md) | Retrieve the cloud project and model GUIDs for use in Revit Batch Processor task files |

---

### Views — Schedules

Tools for managing Revit schedules on sheets and in views.

| Button Group | Description |
|---|---|
| [Schedules](views_schedules.md) | Manage column widths; report and fix schedule segment overlaps on sheets; export, extract, and import Room: Number filter values |

---

## Getting Started

1. Install [pyRevit](https://github.com/pyrevitlabs/pyRevit) if not already installed.
2. Copy the extension folder to your pyRevit extensions directory, or add it via pyRevit settings.
3. Restart Revit — the **duHast** tab will appear in the ribbon.
4. Refer to individual button docs (linked above) for prerequisites and configuration steps before first use.

## Requirements

- Revit (version compatible with your pyRevit installation)
- pyRevit (latest stable version recommended)
- duHast Python library (bundled in the extension)
- .NET 8 WPF components for tools that open a UI window (PushIt, AtTheLibrary, PDF/DWG Export, DocManager)
