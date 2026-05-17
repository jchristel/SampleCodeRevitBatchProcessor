# AtTheLibrary — Main UI User Guide

## Overview

AtTheLibrary is a Revit add-in for browsing and managing a family library. It lets you load family data from an external Schedule of Accommodation (SoA) file, see how those families align with what is already loaded in your open Revit document, and load, edit, or open individual families directly from the interface.

---

## Window Layout

The main window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and subtitle |
| Message banner | Displays status messages and validation errors |
| Families data grid | Lists all families from your SoA data source |
| Action buttons | Quick operations on the Revit model or selected family |
| Data Admin panel | Data source configuration, load, and parameter filtering |

---

## Header Banner

The blue banner at the top shows:

- **"At The Library"** — application title.
- **Find your family** — subtitle.

---

## Message Banner

A status bar directly below the header displays informational and error messages. Messages auto-dismiss after a short interval. Error messages remain until dismissed. If a validation problem prevents an action, the relevant error is shown here.

---

## Families Data Grid

The central grid lists every family entry loaded from your SoA data source.

### Columns

| Column | Type | Description |
|---|---|---|
| Id | Text | Unique identifier for each family entry |
| Count | Number | Number of matching family types already loaded in the open Revit document |
| Family Name | Text | Name of the family |
| Family Category | Text | Revit category the family belongs to |
| Family Type Name | Text | Type name within the family |
| Has Type Catalogue File | Boolean | Whether the family has an associated type catalogue file |
| *(custom)* | Various | Additional columns added dynamically from pre-selected parameters (see [02_parameters_selection_ui.md](02_parameters_selection_ui.md)) |

### Row Colour Coding

| Row colour | Meaning |
|---|---|
| Red background | More than one matching family type exists in the Revit document (ambiguous match) |
| Light grey background | Exactly one matching family type exists in the document (expected state) |
| White background | No matching family type exists in the document |

### Grid Filter Indicator

Column filters can be applied via column headers. When a filter is active, not all families are visible — scroll or clear the filter to see all rows.

### Grid Disabled State

While AtTheLibrary is waiting for a Revit command to complete, the grid is disabled and cannot be interacted with. It re-enables automatically when the command finishes.

### Selecting a Family

Click any row to select it. Only one family can be selected at a time. The selected family is the target for the Load, Edit Type Catalogue, and Edit Family actions.

---

## Action Buttons

Four buttons appear below the grid for direct model interaction.

| Button | Action |
|---|---|
| Refresh families from model | Re-reads all loaded family types from the open Revit document and updates the Count column |
| Load family into model | Loads the selected family's `.rfa` file into the open Revit document |
| Edit Type Catalogue | Opens the type catalogue editor for the selected family (enabled only when the family has a type catalogue file — see [03_type_catalogue_editor_ui.md](03_type_catalogue_editor_ui.md)) |
| Edit family | Opens the selected family's `.rfa` file in the Revit family editor |

---

## Data Admin Panel

The **Data Admin** section is an expandable panel. Click the header to expand or collapse it. It contains two sub-sections.

### Data Source Configuration

This sub-section lets you specify the SoA file to load family data from.

| Control | Description |
|---|---|
| Path to SoA | Text box showing the currently selected file path. You can type or paste a path directly, or use the Browse button |
| Browse | Opens a file picker dialog to select your SoA data file |
| Load | Loads (or reloads) family data from the selected file into the grid. Disabled until a valid file path is entered |

#### Entering a File Path

**Option A — Browse:**
1. Click **Browse**.
2. Navigate to your SoA file in the file picker dialog.
3. Select the file and click **Open**.
4. The file path populates automatically in the text box.

**Option B — Type directly:**
1. Click in the file path text box.
2. Type or paste the full path to your SoA file (e.g., `C:\Projects\Hospital\Families.csv`).

The path is validated in real time. Validation errors appear as red text below the text box.

#### Validation Rules

| Rule | Behaviour |
|---|---|
| Field must not be empty | Error shown if the field is blank |
| File must exist at the specified path | Error shown if the path points to a non-existent file |

While any validation error is present, the **Load** button remains disabled.

### Parameter Filtering

A separate bordered section below the file path contains a single button.

| Button | Action |
|---|---|
| Filter Available Parameters | Opens the Parameters Selection view, where you can choose which family parameters appear as additional columns in the families grid (see [02_parameters_selection_ui.md](02_parameters_selection_ui.md)) |

---

## Typical Workflow

1. Launch AtTheLibrary from the Revit ribbon with a document open.
2. Expand the **Data Admin** panel.
3. Click **Browse** and select your SoA data file, or type the path directly.
4. Click **Load** to populate the families grid.
5. Optionally, click **Filter Available Parameters** to choose which parameter columns appear in the grid.
6. Review the grid. Red rows indicate families already loaded more than once; light grey rows are already loaded once; white rows are not yet in the document.
7. Select a family row and use the action buttons:
   - **Load family into model** — loads the `.rfa` into the current document.
   - **Edit Type Catalogue** — opens the type catalogue editor if the family has one.
   - **Edit family** — opens the `.rfa` in the Revit family editor.
8. Click **Refresh families from model** at any time to resync the Count column with the current state of the document.
