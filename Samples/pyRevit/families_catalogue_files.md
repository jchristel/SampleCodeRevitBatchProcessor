# Catalogue Files

**Panel:** Families | **Menu:** Catalogue Files

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/CatalogueFiles.pulldown/Icon.png" width="40" alt="button icon">

Tools for creating, cleaning, and configuring type catalogue files (`.txt`) for Revit
families.

**All three tools run on the family currently open in the Family Editor**, not on a project.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/CatalogueFiles.pulldown/ExportCatalogueFile.pushbutton/Icon.png" width="24" alt="Export File icon"> Export File

Exports the type data of the open family to a type catalogue file.

- Asks you to select an output directory.
- Writes `<family name>.txt` into that directory, using the open family's file name.
- **Any existing file of that name in the target directory is overwritten without warning.**

**Use when:** A family has its types defined internally and you need to produce a catalogue
file so users can choose which types to load.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/CatalogueFiles.pulldown/DeleteParametersFromCatalogueFile.pushbutton/Icon.png" width="24" alt="Clean Catalogue File icon"> Clean Catalogue File

Cleans an existing catalogue file by removing parameters that should not appear there.

- Removes **instance parameters** (catalogue files only support type parameters).
- Removes **formula-driven type parameters** (their values are calculated, not user-defined).
- Sorts the remaining parameters: explicitly defined parameters first, then the rest in
  alphabetical order.
- Lists the parameters (columns) being removed, then shows the revised file as a table in the
  pyRevit output window.
- Saves the result alongside the original with a `__` suffix appended to the file name, so
  the original is preserved.

**Workflow:**

1. Export the catalogue file from Revit using **Export Family Types**, or use **Export File**
   above.
2. With the family open, run this tool and select the catalogue file.
3. Review the listed removals and the resulting table.
4. Rename the `__` file over the original once you are satisfied.

**Use when:** A catalogue file contains redundant or invalid parameters that cause problems
when loading the family.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/CatalogueFiles.pulldown/DefaultCatalogueFileType.pushbutton/Icon.png" width="24" alt="Default Catalogue File Type icon"> Default Catalogue File Type

> **Warning — this tool deletes family types.** It does not configure a pre-selected type in
> a catalogue file. Read the steps below before running it, and work on a copy of the family
> if you are unsure.

Replaces every type in the open family with a single placeholder type, so that the family
relies entirely on its catalogue file for type definitions.

**What it does:**

1. Shows a confirmation prompt — *"Do you really want to delete all types in this family?"* —
   with a red **Yes** and a green **Oh No, Get me out of here!**. Anything other than Yes
   aborts.
2. Creates a new family type named **`Refer To Catalog File`**.
3. **Deletes every other type in the family.**
4. Resets the parameters listed in `PARAMETERS_TO_RESET` to the value `Refer To Catalog File`.

**Use when:** A family's types are supplied by a catalogue file and the internal types are
redundant, so that a user loading the family is presented with the catalogue file's types
rather than a stale internal list.

**Before running:**

- Export the catalogue file first — once the types are deleted they cannot be recovered from
  the family.
- The family is **not** saved by this tool. If the result is not what you expected, close the
  family without saving.

**Configuration:** `PARAMETERS_TO_RESET` in
`Extensions/duHast-2025.extension/duHast.tab/lib/families/defaultCatalogueFileType.py` is
currently an **empty list**, so step 4 does nothing as shipped. Add the parameter names your
families use to have them stamped with the placeholder value.

---

## Notes

- Catalogue files must have the same name as their associated `.rfa` file and must be in the
  same directory for Revit to offer them on load.
- Use **At The Library** (Families panel) to edit catalogue file contents interactively in a
  table editor.
