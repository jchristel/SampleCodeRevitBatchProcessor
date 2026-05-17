# PDFDWGExporterSelectionUI — Main UI Guide

## Overview

PDFDWGExporterSelectionUI is the sheet selection interface for Revit PDF and DWG batch exports. It lists all sheets in the open document, lets you filter by print set or schedule, select individual sheets for export, choose an export mode (PDF, DWG, or both), and specify the export destination folder.

---

## Window Layout

The main window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and subtitle |
| Message banner | Displays status messages and validation errors |
| Print Set section | Select and manage named print sets |
| Schedule section | Filter sheets by a Revit schedule |
| Sheet selection grid | Select individual sheets to export |
| Export path section | Specify the destination folder |
| Export mode selector | Choose PDF, DWG, or both |
| Export button | Execute the export and close |

---

## Header Banner

The blue banner at the top shows:

- **"Export PDF's and DWG's"** — application title.
- **Select sheets to export** — subtitle.

---

## Message Banner

Displays informational and error messages. Error messages remain until dismissed; informational messages auto-dismiss after a short interval.

---

## Print Set Section

A print set is a named, saved collection of sheets. Selecting a print set auto-ticks only the sheets belonging to that set in the grid below.

| Control | Description |
|---|---|
| Print Set dropdown | Lists all available print sets plus `<None>`. Selecting a set filters the Export checkboxes in the grid |
| Update button | Replaces the selected print set's sheet list with the sheets currently ticked in the grid |
| Duplicate button | Opens the [Print Set Name dialog](02_print_set_dialog_ui.md) to create a copy of the selected print set with a new name |
| Delete button | Marks the selected print set for deletion and resets the dropdown to `<None>` |

The **Update**, **Duplicate**, and **Delete** buttons are disabled when `<None>` is selected.

---

## Schedule Section

| Control | Description |
|---|---|
| Schedule dropdown | Lists all available Revit schedules plus `<None>`. Selecting a schedule auto-ticks only the sheets that appear in that schedule |

Selecting a schedule and selecting a print set are independent — either can be used to pre-populate the Export checkboxes.

---

## Sheet Selection Grid

The central grid lists every sheet in the open Revit document.

### Columns

| Column | Type | Editable | Description |
|---|---|---|---|
| Export | Boolean (checkbox) | Yes | Tick to include this sheet in the export |
| PDF Name | Text | No | Preview of the generated PDF filename based on the current PDF naming settings |
| DWG Name | Text | No | Preview of the generated DWG filename based on the current DWG naming settings |
| Sheet Number | Text | No | Revit sheet number |
| Sheet Name | Text | No | Revit sheet name |
| *(custom)* | Text | No | Additional sheet properties added dynamically from the data source |

### Grid Features

- **Extended multi-select** — Shift-click or Ctrl-click to select multiple rows.
- **Bulk selection** — a select-all control in the column header ticks or unticks all visible rows.
- **Column management** — columns can be shown or hidden via the column header menu.
- Column visibility preferences are saved and restored between sessions.

---

## Export Path Section

| Control | Description |
|---|---|
| Export Path text box | Full path to the folder where exported files will be saved. Type or paste a path, or use Browse |
| Browse button | Opens a folder picker dialog to select the export destination |

### Validation

| Rule | Behaviour |
|---|---|
| Path must not be empty | Error shown below the text box if blank |
| Path must exist on disk | Error shown below the text box if the folder does not exist |

While any validation error is present, the **Export** button remains disabled.

---

## Export Mode Selector (Three-Way Switch)

A three-position switch controls which file types are generated.

| Position | Label | Effect |
|---|---|---|
| Left | Export PDF(s) | Only PDF files are exported |
| Centre | Export DWG(s) | Only DWG files are exported |
| Right | Export PDF(s) and DWG(s) | Both PDF and DWG files are exported |

The Export button label updates to reflect the active mode.

---

## Export Button

The large button at the bottom executes the export for all ticked sheets.

- Enabled only when a valid export path is set.
- Saves all settings (selected print set, schedule, export path, mode, column configuration) before closing.
- The calling Revit command processes the export after the window closes.

---

## Settings Persistence

The following are saved automatically between sessions:

| Setting | Description |
|---|---|
| Last selected print set | The print set active when the window was closed |
| Last selected schedule | The schedule active when the window was closed |
| Export folder path | The last used export destination |
| Export mode | Whether PDF, DWG, or both was selected |
| Column configuration | Which columns are visible and their order |

Settings are stored in `%LocalAppData%\duHast\pdf_dwg_exporter_settings.json`.

---

## Typical Workflow

1. Open a Revit document and launch the PDF/DWG exporter.
2. Select a **Print Set** or **Schedule** to pre-tick a group of sheets, or tick sheets manually.
3. Review the **PDF Name** and **DWG Name** preview columns to confirm filenames look correct.
4. Click **Browse** to set the export destination folder, or type the path directly.
5. Select the export mode using the three-way switch.
6. Click the **Export** button to run the export and close the window.
