# Rename Families

**Panel:** Families | **Menu:** Rename

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/Icon.png" width="40" alt="button icon">

Tools to rename families and family types, in the open project or on disk in a library folder.

Each tool asks for a **single CSV file**. The first row is treated as a header and ignored.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/RenameLoadedFamilies.pushbutton/Icon.png" width="24" alt="Rename Loaded Families icon"> Rename Loaded Families

Renames families already loaded in the open project.

**CSV columns:** Current family name, File path, Family category, New family name.

Family names are without the `.rfa` extension. File path may be left blank when renaming
families inside a project.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/RenameLoadedFamilyTypes.pushbutton/Icon.png" width="24" alt="Rename Loaded Family Types icon"> Rename Loaded Family Types

Renames types within families loaded in the open project.

**CSV columns:** Current family name, Old type name, File path, Family category, New type name.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/RenameFamiliesInFolder.pushbutton/Icon.png" width="24" alt="Rename Families In Folder icon"> Rename Families In Folder

Renames `.rfa` files on disk in a library directory, and the family inside each file.

**CSV columns:** Current family name, File path, Family category, New family name.

Family category may be left blank when only renaming files.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Rename.pulldown/CopyAndRenameFamiliesInFolder.pushbutton/Icon.png" width="24" alt="Copy And Rename Families in Folder icon"> Copy And Rename Families in Folder

> **Not currently available — unfinished, not merely unwired.** The button prints a greeting
> and does nothing, and the library function behind it
> (`lib/families/rename/copy_and_rename_families_in_folder.py`) stops part way through: it
> asks for the CSV file and then ends without copying or renaming anything. Connecting the
> button would not make it work.
>
> Use **Rename Families In Folder** on a copy of the library in the meantime.

Intended behaviour: create renamed **copies** of `.rfa` files, optionally into a different
target directory, leaving the originals untouched.

**Intended CSV columns:** Current family name, File path, Family category, New family name,
Target directory. Target directory may be left blank to copy into the same directory.

---

## Notes

- Prepare the CSV before running — all four tools are driven entirely by the file.
- Renaming files on disk does not update families already loaded in any open project. Use
  **Reload** afterwards where needed.
- The duHast library also recognises directive files named `RenameDirective*.csv` and
  `TypeRenameDirective*.csv` when reading a whole folder; these buttons take one file at a
  time, so the file name does not matter here.
