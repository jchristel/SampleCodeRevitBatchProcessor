# PushIt — CSV Data Source Guide

## Overview

The CSV data source lets you load room data from a comma-separated values (`.csv`) file stored on your local machine or a network path. This is the simplest data source option and requires no credentials or network connection beyond file access.

---

## Accessing the CSV Configuration

1. In the main PushIt window, click **⚙ Settings** in the header banner.
2. The Settings view opens. In the **Data Source** dropdown, select **CSV**.
3. The CSV configuration panel appears below the dropdown.

---

## CSV Configuration Panel

The panel contains a single file path field.

| Control | Description |
|---|---|
| Path to SoA label | Identifies the field as the path to your Schedule of Accommodation CSV file |
| File path text box | Displays the currently selected file path. You can type or paste a path directly, or use the Browse button |
| Browse button | Opens a file picker dialog filtered to `.csv` files |

### Entering a File Path

**Option A — Browse:**
1. Click **Browse**.
2. Navigate to your CSV file in the file picker dialog.
3. Select the file and click **Open**.
4. The file path populates automatically in the text box.

**Option B — Type directly:**
1. Click in the file path text box.
2. Type or paste the full path to your CSV file (e.g., `C:\Projects\Hospital\SoA.csv`).

The path is validated in real time as you type.

---

## Validation

The file path field enforces three rules:

| Rule | Error message behaviour |
|---|---|
| Field must not be empty | Error shown if the field is blank |
| File must exist at the specified path | Error shown if the path points to a non-existent location |
| File must have a `.csv` extension | Error shown if a different file type is selected |

Validation errors appear as red text directly below the file path field. While any error is present, the **Load Data** button in the Settings view remains disabled.

---

## CSV File Requirements

PushIt reads column headers from the first row of the CSV. Each header becomes a column in the mock rooms grid. Ensure your file meets the following requirements:

- The file must be saved with a `.csv` extension.
- The first row must contain column headers.
- One column must contain the room ID values that correspond to mock room identifiers in your Revit model.
- The file must be accessible (not locked by another application such as Microsoft Excel).

> **Tip:** If the file is open in Excel, close it before clicking **Load Data** to avoid file-locking errors.

---

## Loading Data

Once a valid file path is entered:

1. Click **Load Data** at the bottom of the Settings view.
2. PushIt reads the CSV, populates the mock rooms grid with one row per data row in the file, and returns to the main window.
3. Column headers from the CSV are added as dynamic columns in the grid.

The file path setting is saved automatically when the PushIt window is closed, so the same file is pre-selected the next time you open PushIt.

---

## Typical CSV Setup Workflow

1. Click **⚙ Settings** in the main window header.
2. Select **CSV** in the Data Source dropdown.
3. Click **Browse** and select your Schedule of Accommodation CSV file, or type the path directly into the text box.
4. Confirm that no validation errors appear below the path field.
5. Click **Load Data** at the bottom of the Settings view.
6. Review the mock rooms grid — each row from the CSV appears as an entry with the Count column reflecting matches in the current Revit document.
