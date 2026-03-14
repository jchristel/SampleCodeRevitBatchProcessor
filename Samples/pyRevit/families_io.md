# Family IO — Bulk Load and Save

**Panel:** Families | **Menu:** IO

Tools to load families into the project in bulk or save families from the project back to disk.

---

## Load Them All

Loads every `.rfa` file found in a selected directory (and its subdirectories) into the current Revit project in a single operation.

- A folder picker lets you choose the source directory.
- Warnings and errors that would normally interrupt a manual load are suppressed.
- Families that are already loaded with the same name are skipped.

**Use when:** You want to populate a project with a large set of families from a library in one step.

---

## Save Out

Saves selected families from the current project to a chosen directory on disk.

- A UI lets you pick which loaded families to export.
- Files are written as `.rfa` files.
- Existing files in the destination folder are overwritten.

---

## Save Out Advanced

An extended version of **Save Out** with additional organisation options.

- **Organise by category:** Creates subdirectories named after Revit family categories and places each `.rfa` in the matching subdirectory.
- **Overwrite existing files:** Controls whether existing files at the destination are replaced.

**Use when:** You want to export families to a structured library layout organised by category.

---

## Notes

- Ensure the destination folder exists and you have write permissions before saving.
- **Save Out Advanced** with category organisation is the recommended approach when building or refreshing a library.
