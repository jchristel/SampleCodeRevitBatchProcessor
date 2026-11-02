# Family Reports

**Panel:** Families | **Menu:** Reports

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/Icon.png" width="40" alt="button icon">

Reporting tools for auditing family libraries and project family data.

## XML part atom exports come first

Three of these tools do **not** read `.rfa` files. They read **XML part atom exports** —
metadata files Revit can produce for a family without opening it. Run
**Create XML Files Of Families** over a library before running:

- Report Library Families
- Compare Library vs Library Families
- Compare Project vs Library Families

Without the XML files those tools find nothing to report.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/CreateXMLReportLibrary.pushbutton/Icon.png" width="24" alt="Create XML Files Of Families icon"> Create XML Files Of Families

Generates XML part atom exports for the family files in a library directory. These are the
input for the report and compare tools above.

An optional `xml_path_mapper.NETWORK_PATH_MAPPER` module, if importable from the extension's
lib folder, is used to map network paths — useful where the library is reached by different
paths from different machines.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/CleanXMLFiles.pushbutton/Icon.png" width="24" alt="Delete orphaned XML files icon"> Delete orphaned XML files

Deletes XML part atom exports in a library location that no longer have a matching family
file. Run it after families have been renamed or removed from the library so the reports do
not carry stale entries.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/ReportLibrary.pushbutton/Icon.png" width="24" alt="Report Library Families icon"> Report Library Families

Reports on the families in one or more library directories, from their XML exports.

- You select the library directories to process — **multiple directories** can be chosen.
- Results are printed as a table in the output window, then a save dialog writes a CSV.
- If more than 10,000 rows are produced, the tool warns that saving may take a while.

**Report data includes:** family name, type names, category, and type parameter names and
values.

**Optional filtering:** if a module named `settings_xml_library_writer` exposing a
`filter_data(data)` function is importable, it is applied to the rows before they are
reported. Use it to trim large libraries down to what you care about.

**Use when:** You need an inventory of a library for documentation or QA.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/CompareProjectvsLibrary.pushbutton/Icon.png" width="24" alt="Compare Project vs Library Families icon"> Compare Project vs Library Families

Compares the families loaded in the current project against a library, reporting **only the
differences**.

- Output includes family names, type names, categories and the specific parameters that
  differ.
- Results are printed as a table, then a save dialog writes a CSV.

**Use when:** Identifying which project families have fallen behind the library.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/CompareLibraryVsLibrary.pushbutton/Icon.png" width="24" alt="Compare Library vs Library Families icon"> Compare Library vs Library Families

Compares families across two or more libraries.

- One column per library, showing each parameter's value in that library.
- Where a family, type or parameter is absent from a library, the value is shown as `N/A`.
- Results are printed as a table, then a save dialog writes a CSV.

**Use when:** Maintaining several versions of a library and needing to see what has diverged.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/ReportProjectA.pushbutton/Icon.png" width="24" alt="Report Placed Families icon"> Report Placed Families

Reports on the families placed in the current project, including instance counts by type.

> **Configure before first use.** This report only covers the parameters listed in
> `FAMILY_PARAMETERS_TO_REPORT` in
> `Extensions/duHast-2025.extension/duHast.tab/lib/families/report.py`. That list currently
> holds placeholders — `"Sample Parameter One"`, `"Sample Parameter Two"`,
> `"Sample Parameter Three"` — so as shipped the report returns no useful parameter columns.
> Replace them with your project's parameter names.

Results are printed as a table, then a save dialog writes a CSV.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/Reports.pulldown/ReportProjectB.pushbutton/Icon.png" width="24" alt="Report Loaded Families icon"> Report Loaded Families

Reports on the families loaded in the current project via XML part atom export of the
project's families — a different mechanism to **Report Placed Families**, which reads the
families directly.

**Report data includes:** family name, type name, category, and type parameters and values.

Results are printed as a table, then a save dialog writes a CSV.

---

## Notes

- Neither project report writes to a fixed location; both ask where to save.
- Large libraries take several minutes; progress is shown in a cancellable progress bar.
- The two optional hook modules (`settings_xml_library_writer`, `xml_path_mapper`) are looked
  up on import and ignored if absent — no error is raised if you do not use them.
