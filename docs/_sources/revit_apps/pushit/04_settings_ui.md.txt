# PushIt — Settings View Guide

## Overview

The Settings view is where you configure the data source (CSV or drofus) and specify which Revit categories PushIt should target when searching for mock room families. Changes made here take effect when you click **Load Data** to return to the main window.

---

## Accessing Settings

Click the **⚙ Settings** button in the top-right corner of the main window header. The window content switches to the Settings view.

---

## Window Layout

The Settings view is divided into the following sections from top to bottom:

| Section | Purpose |
|---|---|
| Header banner | Blue banner showing "Settings" |
| Message banner | Status and validation messages |
| Data Source section | Choose and configure the active data source |
| Supported Categories section | Enable or disable Revit categories that PushIt searches for mock rooms |
| Bottom buttons | Cancel (discard changes) or Load Data (apply and return) |

---

## Data Source Section

The Data Source section lets you choose where room data is loaded from and configure the connection details.

1. **Data Source** dropdown — select either **CSV** or **drofus**. Selecting a source reveals its configuration controls below the dropdown.
2. Provider-specific configuration panel — appears immediately below the dropdown once a source is selected.

For full configuration details, refer to the relevant guide:
- [03_csv_data_source_ui.md](03_csv_data_source_ui.md) — CSV file configuration
- [02_drofus_data_source_ui.md](02_drofus_data_source_ui.md) — drofus API connection and property mappings

---

## Supported Categories Section

The Supported Categories grid lists the Revit family categories that PushIt will search when looking for mock room families in the model.

| Column | Description |
|---|---|
| IsEnabled | Checkbox — tick to include this category in PushIt operations |
| CategoryName | Name of the Revit category (read-only) |

Changes to the checkboxes are applied automatically — no separate Apply button is required.

> **Note:** Enabling only the categories that contain your mock room families improves performance and reduces false matches.

---

## Bottom Buttons

| Button | Action |
|---|---|
| Cancel | Discards all changes made in this session and returns to the main window without loading data |
| Load Data | Saves the current settings, loads data from the configured source, and returns to the main window with the mock rooms grid populated |

The **Load Data** button is disabled if the selected data source has unresolved validation errors (e.g., invalid file path or missing drofus connection).

---

## Typical Settings Workflow

1. Click **⚙ Settings** in the main window header.
2. Select your data source (**CSV** or **drofus**) in the Data Source dropdown.
3. Configure the data source (see the relevant guide linked above).
4. In the Supported Categories section, tick the categories that contain your mock room families; untick any that do not apply.
5. Click **Load Data** to apply settings, populate the grid, and return to the main window.
6. Click **Cancel** at any time to discard changes and return without reloading data.
