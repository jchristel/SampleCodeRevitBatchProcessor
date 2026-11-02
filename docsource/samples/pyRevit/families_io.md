# Family IO — Load and Save

**Panel:** Families | **Menu:** IO

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/IO.pulldown/Icon.png" width="40" alt="button icon">

Tools to load families into the project in bulk, or save loaded families back out to disk.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/IO.pulldown/BulkLoad.pushbutton/Icon.png" width="24" alt="Load Them All icon"> Load Them All

Loads `.rfa` files from a directory into the current project.

**Workflow:**

1. Pick the source folder. The tool searches it **and all subfolders**.
2. Revit backup files (`*.0001.rfa` and similar) are filtered out.
3. A list of the files found is shown — **select the families to load**. This is a
   multi-select list, so despite the button name you are not obliged to load everything.
4. The selected families are loaded with a progress bar.

**Failure handling:** loading runs with rollback enabled for both warnings and errors. A
family that raises either is **rolled back** — it is not loaded — and the message is printed
to the output window. This is what happens when a family of the same name is already loaded.
So the effective behaviour is "already-loaded families are left alone", but the reason is a
rollback you will see reported, not a silent skip.

**Use when:** Populating a project from a library folder in one pass.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/IO.pulldown/SaveOut.pushbutton/Icon.png" width="24" alt="Save Out icon"> Save Out

Saves families from the current project to a folder.

**Workflow:**

1. Select the families to export from a list. Only families where Revit reports the family as
   editable are offered — in-place and system families are not.
2. Pick the destination folder.

Files are written as `.rfa` directly into that folder, and **existing files are overwritten**.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/IO.pulldown/SaveOutAdvanced.pushbutton/Icon.png" width="24" alt="Save Out Advanced icon"> Save Out Advanced

The same as **Save Out**, with a switch dialog after the folder pick offering two options:

| Switch | Effect when on |
|---|---|
| Save out to a single directory | All families go into the chosen folder |
| Overwrite existing families | Existing `.rfa` files at the destination are replaced |

Turning **Save out to a single directory** off is what produces a category-organised library:
subfolders named after each family's Revit category are created under the chosen folder and
each family is written into the matching one.

With **Overwrite existing families** off, a family whose file already exists at the
destination is skipped.

**Use when:** Building or refreshing a structured library.

---

## Notes

- Each family is opened and saved in its own operation, so one failure does not abort the
  batch — failures are reported per family in the output window.
- Ensure the destination folder exists and is writable before starting.
- **Save Out Advanced** with category subfolders is the better choice for library work; plain
  **Save Out** always uses a single folder and always overwrites.
