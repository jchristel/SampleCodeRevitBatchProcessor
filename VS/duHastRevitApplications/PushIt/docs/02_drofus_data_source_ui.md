# PushIt — drofus Data Source Guide

## Overview

The drofus data source connects PushIt directly to a drofus REST API to retrieve room data. Once connected, you define **property mappings** that tell PushIt which drofus field maps to which Revit shared parameter. These mappings persist between sessions so you only need to configure them once per project.

---

## Accessing the drofus Configuration

1. In the main PushIt window, expand the **Data Admin** panel.
2. In the **Data Source** dropdown, select **drofus**.
3. The drofus configuration panel appears below the dropdown.

---

## Connection Fields

Fill in all four fields before connecting.

| Field | Description | Example |
|---|---|---|
| Base URL | Root URL of the drofus API server for your organisation | `https://api.hidd.health.nsw.gov.au` |
| Database | Name of the drofus database for the project | `hi-alburycr` |
| Project number | Project number within the database | `01` |
| API token | Your personal API token from the drofus Power Query credentials dialog | *(paste from drofus)* |

> **Where to find your API token:** In drofus, open the Power Query credentials dialog. Copy the token and paste it into the API token field.

---

## Saving and Loading Settings

Your connection settings can be saved to a file so you do not have to re-enter them each session.

| Button | Action |
|---|---|
| Save Settings | Writes the current Base URL, Database, Project number, and API token to a settings file |
| Load Settings | Reads a previously saved settings file and populates the four fields |

Settings are also saved automatically when the PushIt window is closed.

---

## Connecting to drofus

Once all four fields are filled in, click **Connect**.

- A "Connecting…" status message appears while the request is in progress.
- On success: a green message confirms the connection and shows how many rooms were found (e.g., *"Connected — 142 rooms found."*).
- On failure: a red error message describes the problem (e.g., invalid token, unreachable server).

The **Property Mappings** section becomes visible only after a successful connection.

---

## Property Mappings

Property mappings define the relationship between drofus room data fields and Revit shared parameters. At least one mapping must be designated as the **unique identifier** so PushIt can match drofus rooms to Revit rooms.

### Mapping List Columns

| Column | Description |
|---|---|
| ⚠ | Warning indicator — appears in orange when a mapped drofus field or Revit parameter cannot be found |
| Key icon | Marks the mapping that is used as the unique identifier |
| drofus Field | The JSON field name from the drofus API room response |
| Revit Parameter | The Revit shared parameter name that receives the data |
| Direction | Data flow: currently always **drofus → Revit** |

### Warning Badge

If any mapping has a validation issue, a yellow **"Some mappings have validation warnings"** badge appears above the list. This typically means:

- A drofus field in the mapping was not found in the latest API response (the field may have been renamed or removed).
- A Revit shared parameter in the mapping does not exist in the current document.

Resolve these before loading data.

### Adding a Mapping

1. Click **Add**. The Add Mapping dialog opens.
2. Fill in the dialog fields (see [Mapping Dialog](#mapping-dialog) below).
3. Click **OK**. The new mapping appears in the list.

The **Add** button is disabled if there are no more available drofus fields to map.

### Editing a Mapping

1. Select the mapping row you want to change.
2. Click **Edit**. The dialog opens pre-populated with the current values.
3. Adjust the fields as needed.
4. Click **OK** to save changes.

### Removing a Mapping

1. Select the mapping row you want to delete.
2. Click **Remove**. The mapping is deleted immediately.

---

## Mapping Dialog

The Add / Edit Mapping dialog has the following fields.

| Field | Description |
|---|---|
| drofus Field | Dropdown of available drofus room fields retrieved from the API. Fields already mapped are excluded when adding. |
| Revit Parameter | Dropdown of available Revit shared parameters in the current document. Parameters already mapped are excluded when adding. |
| GUID | Read-only. Auto-populated from the selected Revit shared parameter. No action required. |
| Direction | Dropdown — select the data flow direction. Currently only **drofus → Revit** is active; *Revit → drofus* is reserved for future use. |
| Is unique identifier | Checkbox — tick to nominate this mapping as the unique match key between drofus rooms and Revit rooms. Only one mapping in the list may be the unique identifier. |

Click **OK** to save or **Cancel** to discard changes.

---

## Loading Data

After configuring and connecting:

1. Return to the main Data Admin panel.
2. Click **Load**.
3. PushIt queries the drofus API, retrieves room data, and populates the rooms grid using the configured mappings.

If there are validation errors (e.g., missing mappings or connection fields), the Load button remains disabled until the issues are resolved.

---

## Typical drofus Setup Workflow

1. Select **drofus** in the Data Source dropdown.
2. Enter Base URL, Database, Project number, and API token.
3. Click **Save Settings** to persist the credentials.
4. Click **Connect** and confirm the success message.
5. Click **Add** to create at least one mapping, designating one as the unique identifier.
6. Add further mappings for each parameter you want to push into Revit.
7. Review the mapping list for any ⚠ warnings and resolve them.
8. Click **Load** in the Data Admin panel to populate the rooms grid.
