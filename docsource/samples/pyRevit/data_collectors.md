# Data Collectors

**Panel:** Data | **Menu:** Collectors

<img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Icon.png" width="40" alt="button icon">

Eight tools that extract element data from Revit models and write it to **JSON** files for
reporting, analysis or external workflows.

## How they work

All eight share the same shape:

1. **Pick the models** — a document picker lists the active document and every loaded Revit
   link, with multi-select. Data is collected from each chosen model in turn.
2. **Save per model** — one save dialog per selected document, titled with that document's
   name. Cancelling one save skips that model and continues with the next.
3. Output is **JSON only**, wrapped with model metadata and a data type key, with the elapsed
   time reported in the output window.

**Exception:** the **Sheets** collector has no document picker. It runs on the active
document only and asks for a single output file.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Rooms.pushbutton/Icon.png" width="24" alt="Rooms icon"> Rooms

Room data from the selected models.

Use the exported data to populate spreadsheets, feed room scheduling tools, or compare
against an external Schedule of Accommodation.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Spaces.pushbutton/Icon.png" width="24" alt="Spaces icon"> Spaces

MEP space data from the selected models. The space equivalent of the Rooms collector.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Sheets.pushbutton/Icon.png" width="24" alt="Sheets icon"> Sheets

Sheet data from the **active document only**.

Use it to build a document register or cross-reference against exported PDF/DWG filenames.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Ceilings.pushbutton/Icon.png" width="24" alt="Ceilings icon"> Ceilings

Ceiling data from the selected models. Use it for ceiling finish schedules or quantity
take-offs.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Floors.pushbutton/Icon.png" width="24" alt="Floors icon"> Floors

Floor data from the selected models, including design set/option membership and phasing.
Use it for floor finish schedules, take-offs, or to cross-reference floor layouts against
room data.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Doors.pushbutton/Icon.png" width="24" alt="Doors icon"> Doors

Door data from the selected models. Use it for door schedules and for checking door-to-room
relationships across linked architectural models.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Levels.pushbutton/Icon.png" width="24" alt="Levels icon"> Levels

Level data from the selected models. Use it to verify level setup against a project brief or
to populate external tools.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Data.panel/Collectors.pulldown/Items.pushbutton/Icon.png" width="24" alt="Items icon"> Items

Placed family instance data — furniture, equipment and similar.

**Exported data includes:** family type, instance parameters, level, offset from level
derived from solid geometry, placement location (x/y/z in mm), facing direction as a rotation
matrix, room associations across all project phases, design set/option membership, and
phasing.

Collected categories: Furniture, Furniture Systems, Mechanical Equipment, Electrical
Equipment, Electrical Fixtures, Plumbing Fixtures, Specialty Equipment, Generic Model.

Use it for FF&E schedules, room content reports, or to verify item placement against a room
data sheet.

---

## Notes

- Being able to collect from **linked models** is the main reason to use these over a Revit
  schedule export: one run over a federated model captures every discipline.
- Only instances with a point location are captured by the Items collector; line-based
  placements are skipped.
- Exports are point-in-time snapshots — re-run after model changes.
- The JSON output is the input format for downstream duHast data processing and for Revit
  Batch Processor workflows that process many models.
