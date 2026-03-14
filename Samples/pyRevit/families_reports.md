# Family Reports

**Panel:** Families | **Menu:** Reports

Reporting tools for auditing and comparing family libraries and project family data.

---

## Report Library

Generates a comprehensive CSV report of all families found in a selected library directory.

**Report data includes:** Family name, all type names, Revit category, and all type parameter names and values for every type.

- Results are shown in the pyRevit output window.
- The report can be saved to a CSV file.

**Use when:** You need a complete inventory of a family library for documentation or QA purposes.

---

## Compare Project vs Library

Compares the families loaded in the current Revit project against the families available in a library directory.

- Only differences are reported (families or parameter values that differ between project and library).
- Output includes family names, type names, categories, and the specific parameters that differ.
- Report can be saved to CSV.

**Use when:** You want to identify which project families are out of date compared to the library, or to check whether library updates have been applied to a project.

---

## Compare Library vs Library

Compares families across two or more library directories.

- Produces a report per library showing parameter values side by side.
- Where a family or parameter is absent from one library, the value is shown as `N/A`.
- Report can be saved to CSV.

**Use when:** You maintain multiple versions of a library (e.g., per project or per year) and need to identify what has changed between them.

---

## Create XML Report Library

Generates XML part atom exports for family files in a library directory. These XML files are used as input by other reporting and comparison tools.

---

## Report Project A / Report Project B

Generate project-specific family reports saved to predefined output locations. Used to capture a snapshot of family data at a point in time for later comparison.

---

## Clean XML Files

Removes temporary or outdated XML export files from a directory after they are no longer needed.

---

## Notes

- **Create XML Report Library** must be run before **Compare Library vs Library** and **Compare Project vs Library**, as those tools read the XML exports rather than the `.rfa` files directly.
- Large libraries may take several minutes to process; progress is shown in the pyRevit output window.
