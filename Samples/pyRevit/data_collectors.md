# Data Collectors

**Panel:** Data | **Menu:** Collectors

Tools that extract element data from the current Revit model and export it to structured files for use in reporting, analysis, or external workflows.

---

## Rooms

Exports room data from the current Revit model.

**Exported data includes:** Room name, number, department, level, area, and all available room parameters.

Output is saved to a CSV or JSON file you specify. Use the exported data to populate spreadsheets, feed into room scheduling tools, or compare against an external Schedule of Accommodation.

---

## Sheets

Exports sheet data from the current Revit model.

**Exported data includes:** Sheet number, sheet name, revision data, view names placed on the sheet, and all available sheet parameters.

Use the exported data to build a document register or cross-reference with exported PDF/DWG filenames.

---

## Ceilings

Exports ceiling data from the current Revit model.

**Exported data includes:** Ceiling type, level, area, room association, and all available ceiling parameters.

Use the exported data for ceiling finish schedules or quantity take-offs.

---

## Levels

Exports level data from the current Revit model.

**Exported data includes:** Level name, elevation, and associated parameters.

Use the exported data to verify level setup against a project brief or to populate external tools.

---

## Notes

- All collectors write to a destination file you choose via a save dialog; ensure the destination folder exists and is writable.
- Export files are intended as point-in-time snapshots; re-run the collector to refresh the data after model changes.
- Exported data can be used as input for Revit Batch Processor workflows that process multiple models.
