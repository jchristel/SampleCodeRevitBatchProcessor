# DocManagerSettingsUI — User Guide

## Overview

DocManagerSettingsUI is the settings interface for configuring document numbering rules used by the Document Manager Revit integration. It lets you build a document number by combining Revit sheet properties (such as sheet number or custom parameters) with optional prefixes, suffixes, and separators. Settings can be exported to and imported from JSON files for reuse.

---

## Window Layout

The settings window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and subtitle |
| Message banner | Displays status and error messages |
| Database path | Select the CSV data source file |
| Parameter mapping area | Build the document number rule by selecting and ordering sheet properties |
| Export / Import buttons | Save or load the current configuration as a JSON file |
| Save button | Commit the settings back to the project and close |

---

## Header Banner

The blue banner at the top shows:

- **"Document Manager - Revit Integration"** — application title.
- **Document number settings** — subtitle.

---

## Message Banner

Displays informational and error messages. Informational messages auto-dismiss after two seconds; error messages remain until dismissed.

---

## Database Path

| Control | Description |
|---|---|
| Database Path text box | Read-only display of the currently selected CSV data source file path |
| Browse button | Opens a file picker filtered to `.csv` files to select the data source |

The selected CSV file provides the list of available sheet properties used to populate the parameter list.

---

## Parameter Mapping Area

The central area is split into three columns.

### Available Sheet Properties (left grid)

Lists all Revit sheet properties available for use in the document number rule. Column header: **Sheet properties**.

- Single selection.
- Read-only — this is a reference list only.

### Add / Remove Buttons (centre)

| Button | Action |
|---|---|
| Add Parameter | Moves the selected sheet property from the available list into the document number rule grid on the right |
| Remove Parameter | Removes the selected row from the rule grid, returning it to the available list |

### Document Number Rule Grid (right grid)

Shows the ordered list of sheet properties that make up the document number, along with their formatting options.

| Column | Editable | Description |
|---|---|---|
| Prefix | Yes | Text prepended to this property's value |
| Parameter | No | The sheet property name (e.g., Sheet Number, Sheet Name) |
| Suffix | Yes | Text appended to this property's value |
| Separator | Yes | Text inserted between this property and the next one |

Click any cell in the Prefix, Suffix, or Separator column to edit it directly.

**Up / Down buttons** below the grid reorder the selected row, controlling the order in which properties appear in the generated document number.

#### How the document number is built

For each row in the rule grid, the output is:

```
[Prefix][Property value][Suffix][Separator]
```

Rows are concatenated in order to produce the final document number.

**Example:** With two rows — Sheet Number (no prefix/suffix, separator `-`) and Sheet Name (no prefix/suffix) — the result becomes `A101-Ground Floor Plan`.

---

## Export / Import Buttons

| Button | Action |
|---|---|
| Export | Opens a Save dialog to write the current document number rule to a `.json` file |
| Import | Opens an Open dialog to restore a rule from a previously exported `.json` file |

---

## Save To Project Button

The large **Save To Project** button commits the current document number rule back to the calling Revit context and closes the window.

---

## Typical Workflow

1. The Document Manager opens the Settings window.
2. Click **Browse** and select the CSV file containing your sheet properties.
3. Select a property from the **Sheet properties** list and click **Add Parameter**.
4. Edit **Prefix**, **Suffix**, and **Separator** cells to format each component.
5. Use **Up** / **Down** to reorder properties.
6. Repeat until the document number rule is complete.
7. Optionally click **Export** to save the rule for reuse on other projects.
8. Click **Save To Project** to apply the settings and close.
