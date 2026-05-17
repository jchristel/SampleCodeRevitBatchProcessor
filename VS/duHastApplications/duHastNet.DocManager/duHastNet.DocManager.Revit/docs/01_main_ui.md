# DocManager Revit Integration — User Guide

## Overview

The DocManager Revit Integration is a Revit add-in that synchronises sheets and revisions from a Revit model to a Document Manager database. It reads sheet properties from the open model, builds document numbers according to a configurable rule, and lets you import new sheets and record revision history against database entries. The window shows two panels — Sheets and Revisions — that can be toggled with a navigation button.

---

## Window Layout

The window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header strip | Shows the application name, connected database path, and connection status |
| Message banner | Displays status and error messages |
| Navigation toggle | Switches between the Sheets panel and the Revisions panel |
| Content area | Shows either the Sheets panel or the Revisions panel |

---

## Header Strip

The header strip at the top shows:

- **Application name** — identifies the add-in.
- **Database path** — the path of the connected Document Manager database.
- **Connection status** — indicates whether the database connection is active.

---

## Message Banner

Displays informational and error messages. Informational messages auto-dismiss after two seconds; error messages remain until dismissed.

---

## Navigation Toggle

The toggle button switches the content area between the two panels:

| State | Panel shown |
|---|---|
| Sheets | Lists all sheets in the Revit model and their database status |
| Revisions | Lists sheets with revisions and their revision sync status |

---

## Sheets Panel

The Sheets panel shows all sheets in the Revit model as rows in a grid. Row background colour indicates the status of each sheet relative to the database:

| Row colour | Meaning |
|---|---|
| Red | Sheet is not yet in the database — needs importing |
| Yellow | Sheet is in the database but its name has changed — needs updating |
| Green | Sheet is up to date in the database |

### Sheets Grid Columns

| Column | Description |
|---|---|
| Sheet Number | The Revit sheet number |
| Sheet Name | The Revit sheet name |
| Document Number | The document number built from the configured numbering rule |
| Database Name | The sheet name currently stored in the database (if present) |

### Updating Sheets

1. Select one or more red or yellow rows in the grid.
2. Click **Update**.
3. If the database has custom field definitions, the [Sheet Custom Properties dialog](#sheet-custom-properties-dialog) opens to collect per-sheet values before the import proceeds.
4. If a sheet's document number has changed and a matching entry already exists in the database, the [Update Existing Document dialog](#update-existing-document-dialog) opens to confirm the link.
5. On completion the grid refreshes and successfully processed rows turn green.

---

## Revisions Panel

The Revisions panel shows sheets that have matching database documents, along with the status of their revision history. Row background colour indicates sync status:

| Row colour | Meaning |
|---|---|
| Grey | One or more revision dates could not be parsed — manual review required |
| Red | Revisions exist on the sheet that are missing from the database entirely |
| Yellow | Revisions are in the database but have not yet been recorded in the revision indicator history |
| Green | All revisions are valid and fully synchronised |

### Updating Revisions

1. Select one or more rows in the grid.
2. Click **Update**.
3. Any revisions missing from the database are created first.
4. Revision history for the selected sheets is then synchronised to the database.
5. On completion the grid refreshes and successfully processed rows turn green.

---

## Sheet Custom Properties Dialog

This modal dialog appears during a sheet import when the database has custom field definitions configured. It presents one input field per custom field for the sheet being imported.

| Control | Description |
|---|---|
| Custom field inputs | One text field per defined custom property, labelled with the field name |
| Confirm button | Submits the entered values and continues the import |
| Cancel button | Cancels the import for the current sheet |

---

## Update Existing Document Dialog

This modal dialog appears when a sheet's document number has changed and a matching entry already exists in the database. It allows you to link the changed sheet to its existing database record rather than creating a duplicate.

| Control | Description |
|---|---|
| Existing document list | Shows the candidate database entry to link to |
| Confirm button | Links the sheet to the selected existing entry and continues |
| Cancel button | Skips this sheet and continues with the remaining selection |

---

## Typical Workflow — Importing Sheets

1. Open the Revit model and launch the Document Manager Revit Integration from the add-in ribbon.
2. The window opens on the **Sheets** panel. Red rows indicate sheets not yet in the database.
3. Select all red rows (or a specific subset) and click **Update**.
4. If prompted, fill in any custom field values in the **Sheet Custom Properties** dialog and confirm.
5. The grid refreshes — successfully imported sheets turn green.
6. Repeat for any yellow rows where sheet names have changed.

---

## Typical Workflow — Synchronising Revisions

1. Switch to the **Revisions** panel using the navigation toggle.
2. Grey rows indicate sheets with unparseable revision dates — review these manually before proceeding.
3. Select red or yellow rows and click **Update**.
4. The add-in creates any missing revision records in the database, then records the revision history for each selected sheet.
5. The grid refreshes — successfully synchronised sheets turn green.
