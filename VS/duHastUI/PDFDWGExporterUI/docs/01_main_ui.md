# PDFDWGExporterUI — Settings Guide

## Overview

PDFDWGExporterUI is the settings interface for configuring how PDF and DWG exports are named. It lets you build a filename rule by combining Revit sheet properties (such as sheet number and sheet name) with optional prefixes, suffixes, and separators. Separate rules can be configured for PDF and DWG exports. Settings can be saved to and loaded from JSON files for reuse across projects.

---

## Window Layout

The settings window is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Shows the application title and subtitle |
| Message banner | Displays status and error messages |
| Document type selector | Choose between PDF and DWG settings |
| Parameter mapping area | Build the filename rule by selecting and ordering sheet properties |
| Export / Import buttons | Save or load the current configuration as a JSON file |
| Save button | Commit the settings back to the project and close |

---

## Header Banner

The blue banner at the top shows:

- **"Export PDF's and DWG's"** — application title.
- **Settings** — subtitle.

---

## Message Banner

Displays informational and error messages. Informational messages auto-dismiss after two seconds; error messages remain until dismissed.

---

## Document Type Selector

| Control | Description |
|---|---|
| Document type dropdown | Select **PDF** or **DWG** to switch which export's naming rule you are editing |
| DWG Export Scheme dropdown | Visible only when **DWG** is selected. Choose the DWG export scheme to use |

Switching between PDF and DWG reloads the parameter mapping area with that document type's current rule.

---

## Parameter Mapping Area

The central area is split into three columns.

### Available Sheet Properties (left grid)

Lists all Revit sheet properties available for use in the filename rule. Column header: **Sheet properties**.

- Single selection.
- Read-only — this is a reference list only.

### Add / Remove Buttons (centre)

| Button | Action |
|---|---|
| Add Parameter | Moves the selected sheet property from the available list into the filename rule grid on the right |
| Remove Parameter | Removes the selected row from the filename rule grid, returning it to the available list |

### Filename Rule Grid (right grid)

Shows the ordered list of sheet properties that make up the filename, along with their formatting options.

| Column | Editable | Description |
|---|---|---|
| Prefix | Yes | Text prepended to this property's value in the filename |
| Parameter | No | The sheet property name (e.g., Sheet Number, Sheet Name) |
| Suffix | Yes | Text appended to this property's value |
| Separator | Yes | Text inserted between this property and the next one in the filename |

Click any cell in the Prefix, Suffix, or Separator column to edit it directly.

**Up / Down buttons** below the grid reorder the selected row, controlling the order in which properties appear in the generated filename.

#### How the filename is built

For each row in the rule grid, the output is:

```
[Prefix][Property value][Suffix][Separator]
```

Rows are concatenated in order to produce the final filename.

**Example:** With two rows — Sheet Number (no prefix/suffix, separator `_`) and Sheet Name (no prefix/suffix) — the filename becomes `A101_Ground Floor Plan`.

---

## Export / Import Buttons

| Button | Action |
|---|---|
| Export | Opens a Save dialog to write the current PDF and DWG rules to a `.json` file |
| Import | Opens an Open dialog to load rules from a previously exported `.json` file. Both PDF and DWG rules are restored |

Importing updates both the filename rule grid and the DWG export scheme selection.

---

## Save To Project Button

The large **Save To Project** button commits the current naming rules for both PDF and DWG back to the calling Revit context and closes the window.

---

## Typical Workflow

1. The export tool opens the Settings window before running an export.
2. Select **PDF** in the document type dropdown.
3. From the **Sheet properties** list, select a property and click **Add Parameter** to add it to the rule.
4. Edit the **Prefix**, **Suffix**, and **Separator** cells as needed.
5. Use **Up** / **Down** to reorder properties.
6. Switch to **DWG** and repeat to configure the DWG naming rule.
7. Optionally click **Export** to save the configuration for reuse.
8. Click **Save To Project** to apply the settings and close.
