# Export PDF and DWG

**Panel:** Export | **Button:** PDF and DWG / Settings (split button)

Batch-export sheets from the current Revit project to PDF and/or DWG files, following a configured naming standard.

---

## PDF and DWG (main button)

Runs the sheet export for all sheets you have selected, producing PDF and DWG output files in the configured destination folder.

- Opens the [PDFDWGExporterSelectionUI](../../VS/duHastUI/PDFDWGExporterSelectionUI/docs/01_main_ui.md) sheet-selection window.
- You choose which sheets to export by ticking them individually, selecting a saved **Print Set**, or filtering by a Revit **Schedule**.
- Preview columns show the generated PDF and DWG filenames before you commit.
- A three-way switch lets you export **PDF only**, **DWG only**, or **both**.
- Click **Export** to produce the files and close the window.

---

## Settings

Configures the naming rules used to generate PDF and DWG filenames.

- Opens the [PDFDWGExporterUI](../../VS/duHastUI/PDFDWGExporterUI/docs/01_main_ui.md) settings window.
- You select which Revit sheet properties (sheet number, name, revision, etc.) to include in the filename, and set a prefix, suffix, and separator for each component.
- Settings are saved to the project so they persist between sessions.
- DWG-specific: choose an export scheme to control which DWG version and layer standards are applied.

**Run Settings before your first export** to ensure filenames match your project's naming convention.

---

## Notes

- Print sets created in the selection window are saved to the project and can be reused on subsequent exports.
- DWG export uses the scheme configured in Settings; make sure a compatible DWG export scheme exists in the project.
