# Purge Unused

**Panel:** Purge Unused | **Menu:** Purge

Tools to remove unused graphic styles, patterns, parameters, views, and templates from the current Revit model, reducing file size and improving model cleanliness.

Each tool comes in two variants: a **standard** version that processes everything automatically, and a **By Selection** version that shows a list and lets you choose which items to remove.

---

## Purge Line Styles

Removes all line styles that are not referenced by any element in the model.

Uses a try-and-rollback method: it attempts to delete each style and confirms whether Revit allows the deletion (used styles are rejected). Only confirmed unused styles are permanently removed.

**By Selection variant:** Presents a list of candidate line styles so you can choose which ones to remove.

---

## Purge Fill Patterns

Removes all fill patterns not used by any material, surface pattern, or element override in the model.

**By Selection variant:** Presents a list so you can choose which fill patterns to remove.

---

## Purge Line Patterns

Removes all line patterns not used by any line style, grid, level, or other element in the model.

**By Selection variant:** Presents a list so you can choose which line patterns to remove.

---

## Purge Shared Parameters

Removes shared parameter definitions that are not bound to any element category in the current project.

**By Selection variant:** Presents a list so you can choose which shared parameters to remove.

---

## Purge Unused Filters

Removes view filters that are not assigned to any view or view template in the model.

---

## Purge Unused Legends

Removes legend views that are not placed on any sheet.

---

## Purge Unused Schedules

Removes schedule views that are not placed on any sheet.

---

## Purge Unused Templates

Removes view templates that are not applied to any view in the model.

---

## Purge Unplaced Views

Removes all views (floor plans, sections, elevations, 3D views, etc.) that are not placed on any sheet.

---

## Notes

- Always save or create a model backup before running purge operations — deletions cannot be undone after saving.
- **By Selection** variants are recommended when you are unsure which items are safe to remove.
- Running Revit's built-in **Purge Unused** command after these tools can further reduce file size.
- These tools target specific element types; they do not replace a full model audit.
