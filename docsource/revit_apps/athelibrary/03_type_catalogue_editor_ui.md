# AtTheLibrary — Type Catalogue Editor Guide

## Overview

The Type Catalogue Editor lets you view and edit the type catalogue file (`.txt`) associated with a selected family directly within AtTheLibrary. Type catalogue files define the available types for a family — each row is a type, and each column is a parameter value for that type. Changes are saved back to the file on disk.

---

## Accessing the Type Catalogue Editor

1. In the main AtTheLibrary window, select a family row in the families grid.
2. The **Edit Type Catalogue** button is enabled only when the selected family has an associated type catalogue file (indicated by a tick in the **Has Type Catalogue File** column).
3. Click **Edit Type Catalogue**. The view switches to the Type Catalogue Editor.

---

## Window Layout

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and editor subtitle |
| Message banner | Status and error messages |
| Cell editor | Inline table editor for type catalogue data |
| Action buttons | Close (return to families) or Save (write changes to file) |

---

## Header Banner

The blue banner at the top shows:

- **"At The Library"** — application title.
- **Type catalogue file editor** — subtitle indicating the active view.

---

## Message Banner

Displays informational and error messages, consistent with the rest of the application.

---

## Cell Editor

The cell editor displays the type catalogue data as a table with full inline editing support.

### Columns

| Column | Editable | Description |
|---|---|---|
| Family Type Name | No (read-only) | The name of the type. This is the first column of every type catalogue file and cannot be changed here |
| *(parameter columns)* | Yes | One column per parameter defined in the type catalogue. Values are edited directly in the cell |

### Editing Values

Click any editable cell to enter edit mode. Type the new value and press **Enter** or click away to confirm. The cell editor validates types where possible — for example, a numeric column will not accept text.

### Adding a Row (New Type)

Click the **Add row** control at the bottom of the table to append a new type row. All cells in the new row start empty and must be filled in manually.

### Duplicating a Row

Select an existing row and use the **Duplicate row** control to create a copy of it. This is useful when creating a new type that differs only slightly from an existing one.

### Deleting a Row

Select the row you want to remove and use the **Delete row** control. The row is removed immediately from the editor; the deletion is written to disk only when you click **Save**.

---

## Action Buttons

| Button | Action |
|---|---|
| Close | Discards any unsaved changes and returns to the main families grid |
| Save | Writes all current changes in the cell editor back to the type catalogue file on disk, then remains in the editor |

> **Important:** Closing without saving discards all edits made in the current session. Always click **Save** before clicking **Close** if you want to keep your changes.

---

## Typical Type Catalogue Editing Workflow

1. In the families grid, select a family with a tick in the **Has Type Catalogue File** column.
2. Click **Edit Type Catalogue**.
3. Review the existing types in the cell editor.
4. Edit cell values directly by clicking on them.
5. Add new types with **Add row**, or duplicate a similar type with **Duplicate row**.
6. Remove unwanted types with **Delete row**.
7. Click **Save** to write the changes to the type catalogue file.
8. Click **Close** to return to the families grid.
