# PDFDWGExporterSelectionUI — Print Set Name Dialog Guide

## Overview

The Print Set Name dialog appears when duplicating an existing print set. It prompts you to enter a unique name for the new print set before it is created.

---

## Accessing the Dialog

1. In the main export window, select an existing print set from the **Print Set** dropdown (not `<None>`).
2. Click **Duplicate**.
3. The Print Set Name dialog opens, centred on the main window.

---

## Dialog Layout

| Control | Description |
|---|---|
| Print set name label | "Print set name:" — identifies the input field |
| Name text box | Enter the name for the new print set. Validated in real time |
| Create button | Confirms the name and creates the new print set. Disabled until a valid name is entered. Also triggered by pressing Enter |
| Cancel button | Closes the dialog without creating a print set. Also triggered by pressing Escape |

---

## Validation Rules

The name field enforces the following rules in real time. Errors appear as red text below the text box.

| Rule | Error condition |
|---|---|
| Name must not be empty | Error shown if the field is blank or contains only whitespace |
| Name must be unique | Error shown if a print set with the same name already exists (case-insensitive) |
| Maximum 100 characters | Error shown if the name exceeds 100 characters |
| No invalid file name characters | Error shown if the name contains any of: `/ \ : * ? " < > |` |

The **Create** button is disabled until all validation rules pass.

---

## Outcome

- **Create clicked (or Enter pressed):** The new print set is created as a copy of the original, containing the same sheets. The main window's Print Set dropdown updates and automatically selects the new set.
- **Cancel clicked (or Escape pressed):** No print set is created and the dialog closes.

---

## Typical Usage

1. Select a print set to copy in the main window.
2. Click **Duplicate** to open this dialog.
3. Type a unique name for the new print set.
4. Confirm no validation errors appear below the field.
5. Click **Create** (or press Enter) to create the copy.
