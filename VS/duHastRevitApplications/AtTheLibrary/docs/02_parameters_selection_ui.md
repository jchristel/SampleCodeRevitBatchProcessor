# AtTheLibrary — Parameters Selection Guide

## Overview

The Parameters Selection view lets you choose which family parameters appear as additional columns in the main families grid. Because families can expose many parameters, you pre-select only the ones relevant to your current task to keep the grid usable.

> **Note:** Selecting more than 10 parameters may make the families grid difficult to use due to the number of columns.

---

## Accessing the Parameters Selection View

1. In the main AtTheLibrary window, expand the **Data Admin** panel.
2. Click **Filter Available Parameters**.
3. The view switches to the Parameters Selection screen.

---

## Window Layout

| Section | Purpose |
|---|---|
| Header | Title and instructions |
| Message banner | Status and validation messages |
| Parameters data grid | Lists all parameters found across the loaded family data |
| Apply button | Confirms the selection and returns to the families grid |

---

## Header

The header shows:

- **"At the library"** — application title.
- Instruction text: *"Pre-select any parameters here which you want to be able to see in the families selection."*

---

## Message Banner

Displays informational and error messages, consistent with the main view.

---

## Parameters Data Grid

The grid lists every parameter found across all families in the loaded data source.

### Columns

| Column | Type | Editable | Description |
|---|---|---|---|
| Is Selected | Boolean (checkbox) | Yes | Tick to include this parameter as a column in the families grid |
| Parameter Name | Text | No | Name of the parameter |
| Occurence Count | Number | No | Number of families in the data source that have this parameter |

### Grid Behaviour

- **Extended selection** — multiple rows can be selected simultaneously using Shift-click or Ctrl-click.
- **Bulk selection** — a select-all control is available in the column header to tick or untick all rows at once.
- The **Is Selected** checkbox is the only editable field. All other columns are read-only.

### Choosing Parameters

Tick the **Is Selected** checkbox for each parameter you want to appear as a column in the families grid. Untick parameters you do not need. The **Occurence Count** column helps you identify parameters that are present across most families versus ones that appear in only a few.

---

## Apply Button

Click **Apply** to confirm your parameter selection and return to the families grid.

- The families grid immediately reflects the new column selection — ticked parameters appear as additional columns.
- Your parameter selection is saved automatically between sessions.

---

## Typical Parameters Selection Workflow

1. From the main window, expand **Data Admin** and click **Filter Available Parameters**.
2. Review the parameter list. Use **Occurence Count** to identify the most widely shared parameters.
3. Tick **Is Selected** for each parameter you want to display (aim for 10 or fewer).
4. Click **Apply** to return to the families grid with the updated columns.
