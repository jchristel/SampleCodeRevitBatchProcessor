# duHast pyRevit Extension

A pyRevit toolbar extension for Revit, providing automation tools for BIM workflows across
family management, export, view management, model maintenance, and more.

---

## Toolbar Panels

Panels and button groups are listed in **ribbon order**, matching the extension's bundle
layouts. Names are the labels shown in Revit.

### About

Reference links. Neither button touches the model.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/About.panel/About.pulldown/Icon.png" width="20" alt=""> | [About](about.md) | Open the extension licence on GitHub, or the Icons8 site the icons come from |

---

### Cloud

Tools for working with cloud-hosted Revit models.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Cloud.panel/GUIDS.pushbutton/Icon.png" width="20" alt=""> | [GUIDS](cloud_guids.md) | Retrieve cloud project and model GUIDs for the model and all its links, for Revit Batch Processor task files |

---

### Grids And Levels

Tools for controlling grid bubble and level header visibility, and 2D/3D extent behaviour, in
the active view.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Icon.png" width="20" alt=""> | [Grids](grids.md) | Show or toggle grid bubbles at either end, switch grids to 2D, extend grids to the view crop, propagate grid setup to other plan views |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/Icon.png" width="20" alt=""> | [Levels](levels.md) | Show or toggle level headers at either end, switch levels to 2D |

---

### View Templates

Tools for propagating and transferring view template settings, filters and colour schemes.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Icon.png" width="20" alt=""> | [Modify](view_templates_modify.md) | Propagate filter and category overrides from a source view template to many others; delete filters from templates |
| <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Icon.png" width="20" alt=""> | [Import Export](view_templates_import_export.md) | Export and import view template overrides and view filters as JSON, and colour fill scheme values as CSV |

---

### Views

Tools for managing Revit schedules on sheets and in views.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Icon.png" width="20" alt=""> | [Schedules](views_schedules.md) | Manage column widths; report and fix schedule segment overlaps on sheets; export, extract and import Room: Number filter values |

---

### Purge Unused

Tools to remove unused elements from the model. Every tool asks what to remove before
deleting anything.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Icon.png" width="20" alt=""> | [Purge](purge_unused.md) | Purge unused line styles, fill patterns, line patterns, shared parameters, filters, legends, schedules, view templates and unplaced views |

---

### Warnings

Tools for resolving and locating common Revit warnings on rooms, areas and annotation.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Warnings.panel/Solve%20Warnings.pulldown/Icon.png" width="20" alt=""> | [Solve Warnings](warnings_solve.md) | Fix room tags outside rooms, duplicate marks, and overlapping area or room separation lines |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Warnings.panel/Highlight%20Warnings.pulldown/Icon.png" width="20" alt=""> | [Highlight Warnings](warnings_highlight.md) | Report area and room separation lines carrying warnings, and colour-highlight them in the active view |

---

### Families

Tools for loading, saving, renaming, swapping and reporting on Revit families and type
catalogue files.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reload.pushbutton/Icon.png" width="20" alt=""> | [Reload](families_reload.md) | Reload families from a library folder, with match-status filtering |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/Icon.png" width="20" alt=""> | [Rename](families_rename.md) | Rename loaded families and types, or rename `.rfa` files in a library folder, from a CSV |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/IO.pulldown/Icon.png" width="20" alt=""> | [IO](families_io.md) | Load families from a folder into the project, or save loaded families out to a folder |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/CatalogueFiles.pulldown/Icon.png" width="20" alt=""> | [CatalogueFiles](families_catalogue_files.md) | Export and clean type catalogue files; strip a family back to a single catalogue placeholder type |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/ForceUpdate.pushbutton/Icon.png" width="20" alt=""> | [Force Update](families_force_update.md) | Force Revit to detect a family as changed when source files have been overwritten |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/ChangeFamilyCategory.pushbutton/Icon.png" width="20" alt=""> | [Change Category](families_change_category.md) | Reassign the open family to a different Revit category, preserving subcategories |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/Icon.png" width="20" alt=""> | [Reports](families_reports.md) | Report on and compare family libraries and projects, via XML part atom exports |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/SwapFamilies.pulldown/Icon.png" width="20" alt=""> | [SwapFamilies](families_swap.md) | Replace family instances with a different type, by CSV directive folder, selection or picking |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/AtTheLibrary.pushbutton/Icon.png" width="20" alt=""> | [At The Library](families_at_the_library.md) | Open the AtTheLibrary tool for managing shared type catalogue parameters |

---

### Ceilings

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Ceilings.panel/CeilingsByRooms.pushbutton/Icon.png" width="20" alt=""> | [Ceilings By Room](ceilings_by_rooms.md) | Create a ceiling matching the boundary of each selected room |

---

### Walls

Tools that relate walls and facade openings back to the rooms they bound.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Walls.panel/WallsByRooms.pushbutton/Icon.png" width="20" alt=""> | [Walls By Room](walls_by_rooms.md) | Write the room number onto the walls bounding each selected room |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Walls.panel/FacadeOpeningToRoom.pushbutton/Icon.png" width="20" alt=""> | [Facade Opening To Room](walls_facade_opening.md) | Report external wall and window opening areas per room to CSV |

---

### PushIt

Tools for managing mock rooms — room-like families that carry room data — and the data pushed
into them.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/PushIt.pushbutton/Icon.png" width="20" alt=""> | [Push It!](pushit_main.md) | Open the PushIt application for loading room data and pushing it into mock rooms |
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/GetARoom.splitbutton/Icon.png" width="20" alt=""> | [Get A Room!](pushit_get_a_room.md) | Build mock room families from filled regions; set the family output directory |
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/SwapWidthAndDepth.pushbutton/Icon.png" width="20" alt=""> | [Swap Width And Depth](pushit_swap_dimensions.md) | Swap the width and depth values on picked mock rooms and rotate them 90 degrees |
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/Stats.pulldown/Icon.png" width="20" alt=""> | [Stats](pushit_stats.md) | Report mock room counts by family, creator and owner; flag IDs duplicated across design sets |
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/PlaceRevitRooms.pushbutton/Icon.png" width="20" alt=""> | [Place Revit Rooms](pushit_place_revit_rooms.md) | Create native Revit rooms at the locations of mock rooms, read from this model or a link |
| <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/Area%20By%20Room.pushbutton/Icon.png" width="20" alt=""> | [Verify Push It Area](pushit_area_by_room.md) | Measure mock rooms with temporary Revit rooms and write the area back onto them |

---

### Export

Tools for exporting sheets, checking exports, and syncing document data.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/PDF_DWG.splitbutton/Icon.png" width="20" alt=""> | [PDF and DWG](export_pdf_dwg.md) | Export sheets to PDF and/or DWG with configurable naming rules and print sets |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/Compare.pushbutton/Icon.png" width="20" alt=""> | [Compare](export_compare.md) | Check the sheets in a Revit schedule against the PDF files in a folder |
| <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/docManager.pulldown/Icon.png" width="20" alt=""> | [docManager](export_docmanager.md) | Sync sheets and revisions from the model to a Document Manager database; configure document numbering |

---

### Data

Scripts for exporting model data to file for reporting and audit purposes.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Icon.png" width="20" alt=""> | [Collectors](data_collectors.md) | Export rooms, spaces, sheets, ceilings, floors, doors, levels and placed items to JSON — from the active model and its Revit links |

---

### RoomMate

Integration with a local RoomMate server.

|  | Button Group | Description |
|:-:|---|---|
| <img src="Extensions/duHast-2025.extension/duHast.tab/RoomMate.panel/RoomMateRooms.pushbutton/Icon.png" width="20" alt=""> | [Export](roommate.md) | Push room and door data from the model and its links to a local RoomMate server |

---

## Getting Started

1. Install [pyRevit](https://github.com/pyrevitlabs/pyRevit) if not already installed.
2. Copy the extension folder to your pyRevit extensions directory, or add it via pyRevit
   settings.
3. Restart Revit — the **duHast** tab will appear in the ribbon.
4. Refer to the individual docs linked above for prerequisites and configuration before first
   use.

## Before you run a tool

Three things decide whether a button will work at all. Each doc repeats the ones that apply
to it, but they are worth knowing up front.

**Some tools only run on a family open in the Family Editor.** They exit with "This is not a
family document." if run from a project: [Change Category](families_change_category.md),
[Force Update](families_force_update.md) and all three
[Catalogue Files](families_catalogue_files.md) tools.

**Some tools store their settings in the Revit model** and refuse to start until a Settings
button has been run on that model: [PDF/DWG Export](export_pdf_dwg.md),
[docManager](export_docmanager.md) and [Get A Room!](pushit_get_a_room.md). Settings are held
in an extensible schema, so they travel with the file but do not travel between files.

**Some tools open a .NET window** loaded from the extension's `bin` folder at run time. If
that folder is missing or incomplete the button fails immediately with a message about the
bin directory. This applies to [Push It!](pushit_main.md),
[At The Library](families_at_the_library.md), [Reload](families_reload.md),
[PDF/DWG Export](export_pdf_dwg.md) and [docManager](export_docmanager.md).

A few tools are also driven by constants edited in the extension's `lib` folder rather than by
a dialog — see [Facade Opening To Room](walls_facade_opening.md),
[Ceilings By Room](ceilings_by_rooms.md) and [Reports](families_reports.md).

## Requirements

- **Revit 2025 or later** — the extension declares `min_revit_ver: 2025`, with engines
  configured for 2025 and 2026.
- pyRevit (latest stable version recommended).
- duHast Python library — bundled in the extension under `lib/duHast`.
- The extension's `bin` folder, for the tools that open a .NET window.
