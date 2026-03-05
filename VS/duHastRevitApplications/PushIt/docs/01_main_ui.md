# PushIt — Main UI User Guide

## Overview

PushIt is a Revit add-in for rapid room layout development. It lets you load room data from an external source (CSV file or drofus API), view how that data aligns with rooms in your open Revit document, and push the data into the model room by room or all at once.

---

## Window Layout

The main window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and the current Revit document name |
| Message banner | Displays status messages and validation errors |
| Rooms data grid | Lists all rooms from your data source |
| Model action buttons | Quick operations on the Revit model |
| Data Admin panel | Data source configuration, load, and bulk operations |
| Push It buttons | Select push mode and execute the push on the selected room |

---

## Header Banner

The blue banner at the top shows:

- **"Push It...Real Good!"** — application title.
- **Rapid layout development in Revit** — subtitle.
- **Document name** — the title of the currently open Revit document. Long titles wrap automatically.

---

## Message Banner

A status bar directly below the header displays informational and error messages. Messages auto-dismiss after a short interval. If a validation problem prevents an action, the relevant error is shown here.

---

## Rooms Data Grid

The central grid lists every room loaded from your active data source.

### Columns

| Column | Type | Description |
|---|---|---|
| RoomId | Text | Unique identifier for each room entry |
| Count | Number | Number of Revit room instances in the model that match this room ID |
| Split | Number | Number of split Revit rooms associated with this room ID |
| *(custom)* | Various | Additional columns are added dynamically from the data source (e.g., parameter values from CSV headers or drofus field mappings) |

### Row Colour Coding

| Row colour | Meaning |
|---|---|
| Red background | More than one Revit room matches this room ID (ambiguous match) |
| Light grey background | Exactly one Revit room matches (expected state) |
| White background | No Revit rooms match this room ID |

### Grid Filter Indicator

When a column filter is active, the border around the grid turns **red** as a reminder that not all rooms are visible.

### Grid Disabled State

While PushIt is waiting for a Revit command to complete, the grid is disabled and cannot be interacted with. It re-enables automatically when the command finishes.

### Selecting a Room

Click any row to select it. Only one room can be selected at a time. The selected room is the target for the Push It, Wipe, and Highlight actions.

---

## Model Action Buttons

Four buttons appear below the grid for direct model interaction.

| Button | Action |
|---|---|
| Refresh rooms from model | Re-reads all Revit rooms from the open document and updates the Count and Split columns |
| Wipe selected rooms in model | Removes PushIt-managed parameter data from the Revit rooms that match the currently selected grid row |
| Highlight rooms in model | Selects and highlights the Revit rooms that match the currently selected grid row in the active Revit view |
| *(info display)* | Shows the **Active Design Set** and **Active Design Option** names to the right of the buttons |

---

## Data Admin Panel

The **Data Admin** section is an expandable panel. Click the header to expand or collapse it. It contains three sub-sections.

### Admin Action Buttons

| Button | Action |
|---|---|
| Update rooms in model | Pushes data from **all** grid rows to their matched Revit rooms simultaneously |
| Wipe stale data from rooms in model | Scans the Revit model for rooms that were previously managed by PushIt but no longer have a match in the current data, and removes their managed parameters |
| Save room data | Opens a file picker to save the current grid contents as a CSV file |

### Data Source Configuration

This sub-section lets you choose where room data is loaded from and trigger a load.

1. **Data Source** dropdown — select either **CSV** or **drofus**. Selecting a source reveals its configuration controls (see the separate guides for each).
2. **Load** button — loads (or reloads) data from the configured source into the grid. This button is disabled until the selected data source is fully configured and valid.

### Settings (Categories)

An inner **Settings** expander shows a list of Revit categories.

| Column | Description |
|---|---|
| IsEnabled | Checkbox — tick to include this category in PushIt operations |
| CategoryName | Name of the Revit category (read-only) |

After changing category checkboxes, click **Apply** to save the selection to the model configuration.

---

## Push It Buttons

The bottom section contains the mode selector and the main action button.

### Mode Selector (Three-Way Switch)

| Position | Label | Mode |
|---|---|---|
| Left | Push It | Push data from the selected grid row into the matched Revit room |
| Centre | Split It | Split the matched Revit room and push data |
| Right | New Room | Create a new Revit room and push data |

Click the desired label to activate that mode. The large action button label updates to reflect the active mode.

### Main Action Button

The large button (labelled **Push It**, **Split It**, or **Create New** depending on the mode) executes the push operation on the currently selected grid row.

- The button is enabled only when a room is selected in the grid.
- The button is disabled while a Revit command is in progress.

---

## Typical Workflow

1. Open a Revit document.
2. Launch PushIt from the Revit ribbon.
3. The grid populates with rooms currently in the model (if any).
4. Expand **Data Admin**, choose a data source (**CSV** or **drofus**), and configure it (see the relevant guide).
5. Click **Load** to populate the grid with your room data.
6. Review the grid. Red rows indicate ambiguous matches that need attention in Revit before pushing.
7. Select a row, choose a push mode, and click the main action button to push one room at a time.
8. Use **Update rooms in model** to push all rooms at once after reviewing.
9. Use **Wipe stale data from rooms in model** after reorganising the data source to clean up orphaned parameter values.
10. Click **Refresh rooms from model** at any time to resync the Count and Split columns with the current state of the Revit document.
