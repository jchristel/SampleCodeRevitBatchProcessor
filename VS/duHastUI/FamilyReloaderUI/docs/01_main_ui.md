# FamilyReloaderUI — User Guide

## Overview

FamilyReloaderUI is a Revit add-in for batch reloading families. It lists all families in the open Revit document, searches a library directory for matching `.rfa` files, and lets you reload selected families — either updating existing types only or loading all types from the library files.

---

## Window Layout

The main window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and subtitle |
| Message banner | Displays status messages and validation errors |
| Families data grid | Lists all families in the open Revit document |
| Library path section | Specify and search the family library directory |
| Reload mode selector | Choose how types are handled during reload |
| Reload button | Execute the reload for all selected families |

---

## Header Banner

The blue banner at the top shows:

- **"Family Reloader"** — application title.
- **Reload families en-batch into your project or family** — subtitle.

---

## Message Banner

A status bar directly below the header displays informational and error messages. Error messages remain until dismissed. Informational messages auto-dismiss after a short interval.

---

## Families Data Grid

The central grid lists every family loaded in the open Revit document.

### Columns

| Column | Type | Editable | Description |
|---|---|---|---|
| Reload | Boolean (checkbox) | Yes | Tick to include this family in the reload operation |
| Family Name | Text | No | Name of the family in the Revit document |
| Family Category | Text | No | Revit category the family belongs to (e.g., Doors, Windows) |
| IsShared | Boolean | No | Whether the family is a shared family |
| Match Status | Text | No | Result of the library search: `SingleMatch`, `MultipleMatches`, or `NoMatch` |
| Family Last Updated | Date/Time | No | Last modification date of the matching library file |

### Match Status Values

| Status | Meaning |
|---|---|
| SingleMatch | Exactly one matching `.rfa` file was found in the library — this family can be reloaded |
| MultipleMatches | More than one matching file was found — the match is ambiguous and the family cannot be reloaded until resolved |
| NoMatch | No matching file was found in the library directory |

Only families with a **SingleMatch** status should be ticked for reload. Families with other statuses cannot be reloaded reliably.

### Selecting Families

The grid supports extended selection. The **Reload** checkbox is the only editable column — tick it on the rows you want to include in the batch reload.

---

## Library Path Section

This section specifies the directory to search for family files.

| Control | Description |
|---|---|
| Library Path text box | Full path to the folder containing your `.rfa` library files. Type or paste a path, or use Browse |
| Incl Sub Directories checkbox | When ticked, the search includes all subdirectories of the library path |
| Browse button | Opens a folder picker dialog to select the library directory |
| Update button | Searches the library directory and updates the Match Status and Family Last Updated columns for all families. Enabled only when a valid library path is entered |

### Validation

| Rule | Behaviour |
|---|---|
| Library path must not be empty | Error shown below the text box if blank |
| Library path must exist on disk | Error shown below the text box if the directory does not exist |

While any validation error is present, the **Reload Families** button remains disabled.

---

## Reload Mode Selector

Two mutually exclusive radio buttons control how family types are handled during the reload.

| Option | Behaviour |
|---|---|
| Import All Types On Reload | All types defined in the library `.rfa` file are loaded into the Revit document |
| Reload Existing Types Only | Only types that already exist in the document are updated; no new types are added |

---

## Reload Families Button

The large **Reload Families** button at the bottom executes the batch reload for all ticked families.

- Enabled only when a valid library path is entered (no validation errors).
- Saves all settings and grid column configuration before closing the window.
- The calling Revit command processes the selected families after the window closes.

---

## Settings Persistence

The following settings are saved automatically between sessions:

| Setting | Description |
|---|---|
| Library path | The last used library directory path |
| Include Sub Directories | The last state of the subdirectory checkbox |
| Reload mode | Whether Import All Types or Reload Existing Types was selected |
| Column configuration | Which columns are visible and their order |

Settings are stored in `%LocalAppData%\duHast\Reloader_settings.json`.

---

## Typical Workflow

1. Launch FamilyReloaderUI from the Revit ribbon with a document open.
2. The families grid populates with all families in the document.
3. Enter the path to your family library in the **Library Path** field, or click **Browse**.
4. Optionally tick **Incl Sub Directories** to search subdirectories.
5. Click **Update** to search the library and populate the Match Status and Last Updated columns.
6. Review the grid. Tick **Reload** on families with a `SingleMatch` status that you want to reload.
7. Select a reload mode: **Import All Types** or **Reload Existing Types Only**.
8. Click **Reload Families** to execute the batch reload and close the window.
