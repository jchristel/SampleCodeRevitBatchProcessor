# View Templates â€” Import and Export

**Panel:** View Templates | **Menu:** Import Export

Tools to transfer view template settings, view filters, and colour schemes between Revit projects using file-based import and export.

---

## Export View Templates

Exports the category override settings from selected view templates in the current project to a file.

- You choose which templates to export.
- Only graphic overrides (cut, projection, halftone, etc.) per category are exported; template-level settings such as view scale or discipline are not included.
- The exported file can be imported into another project to apply the same overrides to templates with matching names.

---

## Import View Templates

Imports category override settings from an exported file and applies them to view templates in the current project.

- Only templates whose names match entries in the import file are updated.
- Custom subcategories that exist in the source project but not in the target project are skipped.

**Use when:** You want to standardise graphic overrides across projects that share a common template set.

---

## Export View Filters

Exports the definitions of view filters (rules, categories, and graphic overrides) from the current project to a file.

---

## Import View Filters

Imports view filter definitions from an exported file and creates or updates the matching filters in the current project.

---

## Export Colour Schemes

Exports colour fill scheme definitions (room colour fills, space colour fills, etc.) from the current project to a file.

---

## Import Colour Schemes

Imports colour fill scheme definitions from an exported file and applies them to the current project.

---

## Notes

- Import operations match by **name**; ensure template, filter, and scheme names are consistent between source and target projects.
- Export files are JSON-based and can be committed to version control to track changes to project standards over time.
- These tools are designed for transferring settings between projects, not for creating templates from scratch.
