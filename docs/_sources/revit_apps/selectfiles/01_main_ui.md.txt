# SelectFiles — User Guide

## Overview

SelectFiles is an IronPython/WPF tool for choosing which Revit (`.rvt`) files to include in a batch processing run. It presents a filterable list of files found in a source directory and returns the user's selection to the calling batch process.

---

## Window Layout

The window is divided into three sections from top to bottom:

| Section | Purpose |
|---|---|
| Settings expander | Configure the source directory and search options |
| Files section | Browse, filter, and select Revit files |
| Action buttons | Confirm or cancel the selection |

---

## Settings Expander

The **Settings** expander is collapsed by default. Click the header to expand it and reveal the path and search configuration fields.

| Field | Editable | Description |
|---|---|---|
| Source Path | Yes | Directory to search for Revit files. Type a path directly or update via the calling script |
| Destination Path | No | Output directory for batch task files — set by the calling process |
| File Type | No | File extension being searched (e.g., `.rvt`) — set by the calling process |
| Number of Files | No | Number of task files to generate — set by the calling process |
| Incl Sub Dirs | Yes (checkbox) | When ticked, the search includes all subdirectories of the source path |

> **Note:** Destination Path, File Type, and Number of Files are read-only and are passed in by the launching script (`startUI.ps1` or equivalent). Only Source Path and the subdirectory checkbox are user-editable.

---

## Files Section

The files section is always expanded and shows the results of the directory search.

### File Name Filter

A text box at the top of the section lets you narrow the list by file name.

| Control | Description |
|---|---|
| File Name Filter text box | Type one or more terms to filter the file list |
| AND radio button | All terms must be present in the file name |
| OR radio button | Any term is sufficient for a match |

Terms are space-separated. For example, entering `hospital level` with **AND** shows only files whose names contain both words; with **OR** it shows files containing either word.

### File List

The data grid below the filter shows all files matching the current filter.

| Column | Description |
|---|---|
| File | File name of the Revit file found in the source directory |

- **Multi-select** — hold Shift or Ctrl and click to select multiple files.
- Rows are highlighted when selected. The selection is reflected in the `is_selected` binding on each row.
- Alternating rows use a light background to aid readability.

---

## Action Buttons

| Button | Action |
|---|---|
| OK | Confirms the selection and closes the window. The selected files are passed back to the calling process |
| Cancel | Closes the window without making a selection. The calling process receives no files |

---

## Typical Workflow

1. The batch processing script launches SelectFiles, passing the source directory, destination, file type, and task file count as arguments.
2. The window opens with the **Files** section expanded showing all `.rvt` files found.
3. Optionally expand **Settings** and tick **Incl Sub Dirs** to include files from subdirectories.
4. Type in the **File Name Filter** box to narrow the list. Use **AND** / **OR** to control how multiple terms are combined.
5. Select one or more files in the list (Ctrl-click or Shift-click for multiple).
6. Click **OK** to confirm. The selected files are returned to the batch process.
