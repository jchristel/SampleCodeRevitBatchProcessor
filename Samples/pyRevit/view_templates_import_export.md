# View Templates — Import and Export

**Panel:** View Templates | **Menu:** Import Export

<img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Icon.png" width="40" alt="button icon">

Tools to move view template overrides, view filters and colour fill scheme values between
projects through files.

Note the file formats differ: view overrides and view filters use **JSON**; colour fill
scheme values use **CSV**.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Export%20View%20Templates.pushbutton/Icon.png" width="24" alt="Export View Overrides icon"> Export View Overrides

Exports the graphic overrides of selected view templates to a **JSON** file.

- You select which templates to export.
- Both **category overrides** and **filter overrides** are exported for each template —
  despite the button name, this is not limited to category settings.
- Template-level properties such as view scale, detail level or discipline are **not**
  included.
- A save dialog asks where to write the `.json` file.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Import%20View%20Templates.pushbutton/Icon.png" width="24" alt="Import View Overrides icon"> Import View Overrides

Applies overrides from an exported JSON file to the templates in the current project.

- You select the export file.
- Templates are matched **by name**. Templates in the file with no name match in the target
  project are skipped.
- Custom subcategories that exist in the source project but not in the target are skipped.

**Use when:** Standardising graphic overrides across projects that share a template set.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Export%20View%20Filters.pushbutton/Icon.png" width="24" alt="Export View Filters icon"> Export View Filters

Exports the definitions of **view filters** — rules and categories — to a **JSON** file.

- You select which filters to export from a list of the filters in the project.
- A save dialog asks where to write the `.json` file.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Import%20View%20Filters.pushbutton/Icon.png" width="24" alt="Import View Filters icon"> Import View Filters

Creates or updates view filters in the current project from an exported JSON file.

- You select the file; the filters it contains are applied to the current document.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Export%20Colour%20Schemes.pushbutton/Icon.png" width="24" alt="Export Colour Fill Scheme Values icon"> Export Colour Fill Scheme Values

Exports the **entries** of one or more colour fill schemes — the values and their colours —
to a **CSV** file.

- You select which colour fill schemes to export.
- Schemes with no entries are reported and skipped.
- A save dialog asks where to write the `.csv` file.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Import%20Export.pulldown/Import%20Colour%20Schemes.pushbutton/Icon.png" width="24" alt="Import Colour Fill Scheme Values icon"> Import Colour Fill Scheme Values

Applies colour fill scheme values from a CSV file to a scheme in the current project. This is
a four-step wizard, not a single file pick:

1. Select the **CSV file** to read.
2. Select which **scheme in the file** to import.
3. Select which **scheme in the current model** to modify.
4. Select the **update mode**:
   - **update existing values only** — colours are updated for entries that already exist in
     the target scheme; nothing is added;
   - **add new and update existing** — missing entries are created as well.

Because source and target schemes are chosen separately, the two do not need to share a name.

---

## Notes

- Import matches templates and filters **by name**; keep naming consistent between source and
  target projects.
- The JSON exports are text and can be committed to version control to track project
  standards over time. The colour scheme CSV can be edited in a spreadsheet before importing.
- These tools transfer settings between existing objects. They do not create templates from
  scratch.
