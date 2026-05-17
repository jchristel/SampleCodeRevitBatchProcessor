# PushIt — drofus Data Source Guide

## Overview

The drofus data source pulls room data directly from your project's drofus database. After connecting, you choose which set of room attributes to work with and then map each drofus field to the corresponding Revit parameter. PushIt remembers your configuration between sessions, so you only need to set it up once per project.

---

## Opening the drofus Settings

1. In the main PushIt window, click **⚙ Settings** in the header banner.
2. In the **Data Source** dropdown, select **drofus**.
3. The drofus connection fields appear below the dropdown.

---

## Entering Your Connection Details

You need four pieces of information to connect. Ask your BIM manager or drofus administrator if you are unsure of any values.

| Field | What to enter | Example |
|---|---|---|
| Base URL | The web address of your organisation's drofus server | `https://api.hidd.health.nsw.gov.au` |
| Database | The drofus database name for your project | `hi-alburycr` |
| Project number | The project number within that database | `01` |
| API token | Your personal access token from drofus | *(see below)* |

**Finding your API token:** In drofus, open the Power Query credentials dialog. Copy the token shown there and paste it into the API token field in PushIt.

---

## Saving and Reloading Your Settings

Use the two buttons below the connection fields to save and share your configuration.

| Button | What it does |
|---|---|
| Save Settings | Saves all connection details, your attribute configuration choice, and all mappings to a file you can share with the team |
| Load Settings | Loads a settings file (for example, one shared by a colleague) to populate all the fields automatically |

Your settings are also saved automatically each time you close the PushIt window, so they are ready next time you open it.

---

## Connecting to drofus

Once all four connection fields are filled in, click **Connect**.

- While connecting, a *"Connecting…"* message is displayed.
- If the connection succeeds, a green message confirms it and shows how many rooms were found — for example, *"Connected — 142 rooms found."*
- If the connection fails, a red message explains the problem (wrong token, server unreachable, etc.). Check your connection details and try again.

Once connected, the **Attribute Configuration** selector and the **Property Mappings** list appear.

### If drofus Is Not Available

If PushIt cannot reach drofus when it opens — for example because you are working offline — any mappings you saved previously are still shown so you can review them. You cannot add, edit, or validate mappings until you successfully connect. Click **Connect** whenever the server becomes reachable again.

---

## Choosing an Attribute Configuration

drofus organises room data into **attribute configurations** — named groups of fields that are relevant to your project stage or use case. Selecting the right configuration ensures you only see and map the fields that apply to your work.

After a successful connection, a dropdown labelled **Attribute Configuration** appears above the mapping list. Select the configuration that matches your current workflow.

Your selection is remembered and restored automatically next time you open PushIt.

### Switching to a Different Configuration

If you change the configuration after you have already set up mappings, PushIt checks whether any of your existing mappings use fields that are not in the new configuration.

- If all your mappings are compatible, the switch happens immediately.
- If some mappings would be lost, a confirmation message appears telling you how many mappings will be **removed** and how many will be **kept**. You can confirm the switch or cancel and stay with your current configuration.

> Any mappings removed during a configuration switch cannot be recovered — you will need to add them again if you switch back.

---

## Setting Up Property Mappings

Property mappings tell PushIt which drofus field corresponds to which Revit parameter. You need at least one mapping, and exactly one of your mappings must be marked as the **unique identifier** — this is the field PushIt uses to match each drofus room to its corresponding mock room in Revit.

### The Mapping List

Each row in the mapping list shows one field-to-parameter link.

| Column | What it shows |
|---|---|
| ⚠ | An orange warning icon appears if PushIt cannot find the drofus field or the Revit parameter. See [Mapping Warnings](#mapping-warnings). |
| 🔑 | A key icon marks the mapping that is used as the unique room identifier |
| drofus Field | The name of the drofus room field (hover over it to see the underlying field code) |
| Revit Parameter | The Revit shared parameter that will receive the data |
| Direction | Which way the data flows (currently always *drofus → Revit*) |
| Revit Precedence | A checkbox that controls what happens on repeated pushes to split rooms — see [Revit Precedence](#revit-precedence) |

### Adding a Mapping

1. Click **Add**.
2. In the dialog that opens, choose a drofus field and a Revit parameter (see [Mapping Dialog](#mapping-dialog)).
3. Click **OK**. The new mapping appears in the list.

The **Add** button is disabled when all available fields in the current configuration have already been mapped.

### Editing a Mapping

1. Click the mapping row you want to change to select it.
2. Click **Edit**.
3. Adjust the settings in the dialog and click **OK**.

### Removing a Mapping

1. Click the mapping row you want to delete to select it.
2. Click **Remove**. The mapping is deleted immediately.

---

## Mapping Dialog

When you add or edit a mapping, a dialog opens with the following fields.

| Field | Description |
|---|---|
| drofus Field | Choose the drofus room field from the dropdown. Only fields in your selected attribute configuration that have not already been mapped are shown. |
| Revit Parameter | Choose the Revit shared parameter from the dropdown. Only parameters that exist in the current document and have not already been mapped are shown. |
| GUID | Filled in automatically when you select a Revit parameter. You do not need to change this. |
| Direction | The direction data flows. Pre-filled based on how the field is configured in drofus. Currently only *drofus → Revit* is active. |
| Is unique identifier | Tick this box to mark the mapping as the unique room match key. Only one mapping can have this ticked at a time. |

Click **OK** to save the mapping or **Cancel** to discard it.

---

## Mapping Warnings

If the orange ⚠ icon appears next to a mapping, one of the following has happened:

- **drofus field missing** — the field no longer exists in the current attribute configuration (it may have been renamed or removed in drofus).
- **Revit parameter missing** — the shared parameter does not exist in the currently open Revit document.

A yellow **"Some mappings have validation warnings"** banner also appears above the mapping list when any warning is present. Resolve all warnings before loading data — PushIt cannot push data for a mapping it cannot validate.

**To fix a missing drofus field:** Edit the mapping and choose the replacement field, or remove the mapping if the field is no longer needed.

**To fix a missing Revit parameter:** Ensure the correct shared parameter file is loaded in the Revit document, then reconnect so PushIt can recheck the parameters.

---

## Revit Precedence

The **Revit Precedence** checkbox on each mapping row controls what PushIt does when it pushes data to a **split room** more than once.

| Checkbox state | Behaviour |
|---|---|
| Unchecked (default) | Every push overwrites the Revit parameter with the current value from drofus. Manual changes made in Revit are overwritten. |
| Checked | The first push writes the drofus value into Revit as usual. After that, PushIt leaves the Revit value untouched — it will not be overwritten by drofus data on any future push. |

Use **Revit Precedence** for parameters you expect to be fine-tuned in Revit after the initial layout is established — for example, where the net area of a split room has been manually adjusted. Leave it unchecked for parameters that should always reflect the current drofus data.

Changes to the Revit Precedence checkboxes are saved automatically when you close the Settings view or click **Save Settings**.

---

## Loading Data

Once you have connected, chosen a configuration, and set up your mappings:

1. Click **Load Data** at the bottom of the Settings view.
2. PushIt retrieves the room data from drofus, populates the rooms grid in the main window, and returns you to the main view.

If the Load Data button is greyed out, check that:
- All four connection fields are filled in.
- You have successfully connected (green status message showing).
- At least one mapping exists and has no warnings.

---

## Typical First-Time Setup

1. Click **⚙ Settings** in the main window.
2. Choose **drofus** from the Data Source dropdown.
3. Enter your Base URL, Database, Project number, and API token.
4. Click **Connect** and wait for the green confirmation message.
5. Choose your project's **Attribute Configuration** from the dropdown.
6. Click **Add** and create your first mapping — make sure to tick *Is unique identifier* on the field that links drofus rooms to Revit rooms.
7. Click **Add** again for each additional parameter you want to push.
8. For any parameter that should not be overwritten after its first split-room push, tick **Revit Precedence** in the mapping list.
9. Check that no ⚠ warnings are shown.
10. Click **Save Settings** to store the configuration for the team.
11. Click **Load Data** to populate the rooms grid.
