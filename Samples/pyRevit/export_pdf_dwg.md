# PDF and DWG

**Panel:** Export | **Button:** PDF and DWG / Settings (split button)

<img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/PDF_DWG.splitbutton/Icon.png" width="40" alt="button icon">

Batch-export sheets from the current Revit project to PDF and/or DWG files, following a configured naming standard.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/PDF_DWG.splitbutton/PDF_DWG.pushbutton/Icon.png" width="24" alt="PDF and DWG icon"> PDF and DWG (main button)

Runs the sheet export for all sheets you have selected, producing PDF and DWG output files in the configured destination folder.

- Opens the [PDFDWGExporterSelectionUI](../../VS/duHastUI/PDFDWGExporterSelectionUI/docs/01_main_ui.md) sheet-selection window.
- You choose which sheets to export by ticking them individually, selecting a saved **Print Set**, or filtering by a Revit **Schedule**.
- Preview columns show the generated PDF and DWG filenames before you commit.
- A three-way switch lets you export **PDF only**, **DWG only**, or **both**.
- The **export directory** is set in this window, not in Settings.
- Click **Export** to produce the files and close the window.

Any print sets you create or edit in the selection window are **written back to the model**
before the export runs.

**Run Settings first.** If no export settings are stored in the model this button exits with
*"Cant find any settings for this file. Please run the settings add-in first."*

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Export.panel/PDF_DWG.splitbutton/Settings.pushbutton/Icon.png" width="24" alt="Settings icon"> Settings

Configures the naming rules used to generate PDF and DWG filenames.

- Opens the [PDFDWGExporterUI](../../VS/duHastUI/PDFDWGExporterUI/docs/01_main_ui.md) settings window.
- You select which Revit sheet properties (sheet number, name, revision, etc.) to include in the filename, and set a prefix, suffix, and separator for each component. Any parameter present on sheets in this model can be used.
- Settings are stored in an **extensible schema in the model** — separate JSON strings for the PDF rule, the DWG rule and the DWG export scheme name — so they travel with the file.
- DWG-specific: choose an export scheme to control which DWG version and layer standards are applied. The list offered comes from the **predefined DWG export setups in the model**.

**Run Settings before your first export** to ensure filenames match your project's naming convention.

---

## Notes

- Print sets created in the selection window are saved to the project and can be reused on subsequent exports.
- DWG export uses the scheme configured in Settings; create the DWG export setup in Revit first, otherwise there is nothing to choose.
- Both buttons load .NET UI assemblies from the extension's `bin` folder at run time. If that folder is missing or incomplete, the button fails immediately with a message about the bin directory.
