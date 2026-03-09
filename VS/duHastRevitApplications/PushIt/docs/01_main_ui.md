# PushIt — Main UI User Guide

## Overview

PushIt is a Revit add-in for rapid layout development. It lets you load room data from an external source (CSV file or drofus API), view how that data aligns with **mock rooms** in your open Revit document, and push the data into the model one entry at a time or all at once.

**Mock rooms** are Revit families that visually resemble rooms (with or without walls) but are generic model families — they are not native Revit rooms. PushIt targets these mock room families rather than the built-in Revit room tool.

---

## Window Layout

The main window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title, the current Revit document name, and the Settings navigation button |
| Message banner | Displays status messages and validation errors |
| Mock rooms data grid | Lists all entries from your data source and their match status in the model |
| Model action buttons | Quick operations on the Revit model |
| Data Admin panel | Bulk data operations (update all, wipe stale, save) |
| Push It buttons | Select push mode and execute the push on the selected entry |

---

## Header Banner

The blue banner at the top shows:

- **"Push It...Real Good!"** — application title.
- **Rapid layout development in Revit** — subtitle.
- **Document name** — the title of the currently open Revit document.
- **⚙ Settings** button (top-right) — opens the Settings view to configure the data source and supported Revit categories. See [04_settings_ui.md](04_settings_ui.md).

---

## Message Banner

A status bar directly below the header displays informational and error messages. Messages auto-dismiss after a short interval. If a validation problem prevents an action, the relevant error is shown here.

---

## Mock Rooms Data Grid

The central grid lists every entry loaded from your active data source, showing how each entry matches against mock room families in the Revit model.

### Columns

| Column | Type | Description |
|---|---|---|
| RoomId | Text | Unique identifier for each data source entry |
| Count | Number | Number of mock room family instances in the model that match this room ID |
| Split | Number | Number of split mock rooms associated with this room ID |
| *(custom)* | Various | Additional columns added dynamically from the data source (e.g., parameter values from CSV headers or drofus field mappings) |

### Row Colour Coding

| Row colour | Meaning |
|---|---|
| Red background | More than one mock room in the model matches this room ID (ambiguous match — resolve in Revit before pushing) |
| Light grey background | Exactly one mock room matches (expected state) |
| White background | No mock rooms match this room ID |
| Light green background | Entry is marked as a new mock room (pending creation in the model) |
| Amber background | Entry is marked as a split mock room |

### Grid Filter Indicator

When a column filter is active, the border around the grid turns **red** as a reminder that not all entries are visible.

### Grid Disabled State

While PushIt is waiting for a Revit command to complete, the grid is disabled and cannot be interacted with. It re-enables automatically when the command finishes.

### Selecting an Entry

Click any row to select it. Only one entry can be selected at a time. The selected entry is the target for the Push It, Wipe, and Highlight actions.

---

## Model Action Buttons

Four controls appear below the grid for direct model interaction.

| Control | Action |
|---|---|
| Refresh rooms from model | Re-reads all mock room families from the open document and updates the Count and Split columns |
| Wipe selected rooms in model | Removes PushIt-managed parameter data from the mock rooms that match the currently selected grid row |
| Highlight rooms in model | Selects and highlights the mock room families that match the currently selected grid row in the active Revit view |
| *(info display)* | Shows the **Active Design Set** and **Active Design Option** names to the right of the buttons |

---

## Data Admin Panel

The **Data Admin** section is an expandable panel. Click the header to expand or collapse it. It contains bulk administrative operations.

### Admin Action Buttons

| Button | Action |
|---|---|
| Update rooms in model | Pushes data from **all** grid rows to their matched mock rooms simultaneously |
| Wipe stale data from rooms in model | Scans the Revit model for mock rooms that were previously managed by PushIt but no longer have a match in the current data, and removes their managed parameters |
| Save room data | Opens a file picker to save the current grid contents as a CSV file |

> **Data source and category settings** are configured in the **Settings** view. Click **⚙ Settings** in the header to open it.

---

## Push It Buttons

The bottom section contains the mode selector and the main action button.

### Mode Selector (Three-Way Switch)

| Position | Label | Mode |
|---|---|---|
| Left | Push It | Push data from the selected grid row into the matched mock room |
| Centre | Split It | Split the matched mock room and push data |
| Right | New Room | Create a new mock room and push data |

Click the desired label to activate that mode. The large action button label updates to reflect the active mode.

### Main Action Button

The large button executes the push operation on the currently selected grid row. Its label changes to match the active mode (**Push It**, **Split It**, or **New Room**).

- The button is enabled only when an entry is selected in the grid.
- The button is disabled while a Revit command is in progress.

---

## Typical Workflow

1. Open a Revit document containing mock room families.
2. Launch PushIt from the Revit ribbon.
3. Click **⚙ Settings** in the header to configure your data source (CSV or drofus) and enabled Revit categories.
4. Click **Load Data** in the Settings view to populate the grid and return to the main window.
5. Review the grid. Red rows indicate ambiguous matches; light green rows are new entries pending creation; amber rows are splits.
6. Click **Refresh rooms from model** at any time to resync the Count and Split columns with the current state of the Revit document.
7. Select a row, choose a push mode, and click the main action button to push one entry at a time.
8. Use **Update rooms in model** in the Data Admin panel to push all entries at once after reviewing.
9. Use **Wipe stale data from rooms in model** after reorganising the data source to clean up orphaned parameter values.
