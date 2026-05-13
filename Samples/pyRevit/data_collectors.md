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

## Floors

Exports floor data from the current Revit model.

**Exported data includes:** Floor type, level, offset from level, area, design set/option membership, phasing, and all available floor instance and type parameters.

Use the exported data for floor finish schedules, quantity take-offs, or to cross-reference floor layouts against room data.

---

## Items

Exports placed family instance data (furniture, equipment, and similar items) from the current Revit model.

**Exported data includes:** Family type, instance parameters, level, offset from level derived from solid geometry, placement location (x/y/z in mm), facing direction (rotation matrix), room associations across all project phases, design set/option membership, and phasing.

By default the following categories are collected: Furniture, Furniture Systems, Mechanical Equipment, Electrical Equipment, Electrical Fixtures, Plumbing Fixtures, Specialty Equipment, and Generic Model.

Use the exported data for FF&E schedules, room content reports, or to verify item placement against a room data sheet.

---

## Notes

- All collectors write to a destination file you choose via a save dialog; ensure the destination folder exists and is writable.
- Export files are intended as point-in-time snapshots; re-run the collector to refresh the data after model changes.
- Exported data can be used as input for Revit Batch Processor workflows that process multiple models.
