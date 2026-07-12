# Catalogue Files

**Panel:** Families | **Menu:** Catalogue Files

Tools for creating, cleaning, and configuring type catalogue files (`.txt`) for Revit families.

---

## Export Catalogue File

Generates a new type catalogue file for a family based on an XML atom export.

- Reads the family's parameter data from an XML part atom export.
- Writes a properly formatted type catalogue file that Revit can use when loading the family.

**Use when:** A family has types defined internally and you need to produce a catalogue file so users can select which types to load.

---

## Delete Parameters from Catalogue File

Cleans an existing catalogue file by removing parameters that should not appear there.

- Removes **instance parameters** (catalogue files only support type parameters).
- Removes **formula-driven type parameters** (their values are calculated, not user-defined).
- Sorts the remaining parameters: explicitly defined parameters first, then the rest in alphabetical order.
- Saves the result with a `__` suffix appended to the original filename so the original is preserved.

**Use when:** A catalogue file contains redundant or invalid parameters that cause issues when loading the family.

---

## Default Catalogue File Type

Sets the default selected type in a family's catalogue file. When a user loads the family, this type is pre-selected in the type chooser dialog.

---

## Notes

- Catalogue files must have the same name as their associated `.rfa` file and must be in the same directory.
- Use the **AtTheLibrary** or **Type Catalogue Editor** (in the AtTheLibrary WPF tool) to edit catalogue file contents interactively.
