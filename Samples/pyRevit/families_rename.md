# Rename Families

**Panel:** Families | **Menu:** Rename

A pulldown containing tools to rename families and family types — both within the current Revit project and on disk in a library folder.

---

## Rename Loaded Families

Renames families that are already loaded in the open Revit project.

**CSV input columns:** Current family name, File path, Family category, New family name.

The first row of the CSV is treated as a header and is ignored.

---

## Rename Loaded Family Types

Renames specific types within families loaded in the open Revit project.

**CSV input columns:** Current family name, Old type name, File path, Family category, New type name.

---

## Rename Families in Folder

Renames `.rfa` files on disk in a library directory without opening Revit.

**CSV input columns:** Current family name, File path, Family category, New family name.

The original files are renamed in place.

---

## Copy and Rename Families in Folder

Creates copies of `.rfa` files with new names and optionally places them in a different target directory.

**CSV input columns:** Current family name, File path, Family category, New family name, Target directory.

The originals are left untouched; only the copies are renamed.

---

## Notes

- All operations use a CSV file as the instruction source; prepare the CSV before running the tool.
- Renaming on disk does not automatically update families already loaded in any open projects — use **Reload Families** afterwards if needed.
