# Schedules

**Panel:** Views | **Menu:** Schedules

<img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Icon.png" width="40" alt="button icon">

Tools for managing Revit schedules — column widths, sheet placement overlaps, and room number filter values.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Export%20Column%20Width.pushbutton/Icon.png" width="24" alt="Export Column Width icon"> Export Column Width

Saves schedule column widths to a **CSV** file.

- You select the schedules to export — this is a **multi-select** list, not one schedule.
- A second dialog asks whether to export **all fields** or only **specific fields**.
- A save dialog asks where to write the `.csv` file.

Use this as a snapshot before changes, or as a source to apply to other schedules.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Resize%20Column%20Width%20From%20Export.pushbutton/Icon.png" width="24" alt="Resize Column Width From Export icon"> Resize Column Width From Export

Applies column widths to schedules from a previously saved CSV.

**Workflow:**

1. Select the **CSV file** first.
2. Select which **schedules** to update, chosen from those named in the file.
3. The widths are applied with a progress bar.

- Matching is by **schedule name and field name**, not by column order.
- Schedules that do not contain a field named in the file are skipped, and listed at the end
  of the run.

**Use when:** A schedule's column widths have been reset (for example after a template
upgrade) and you need to restore them to a known-good state.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Resize%20Column%20Width%20By%20Name%20And%20Value.pushbutton/Icon.png" width="24" alt="Resize Column Width By Name And Value icon"> Resize Column Width By Name And Value

Sets one column's width across many schedules, without needing an export file.

**Workflow:**

1. Select the **schedules** to modify.
2. Select the **single field** whose width you want to set.
3. Enter the width **in millimetres** in the dialog.

Schedules that do not contain that field are skipped and listed at the end of the run.

**Use when:** Applying a standard width to one named column across a set of schedules.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Report%20Schedules%20Overlaps.pushbutton/Icon.png" width="24" alt="Report Overlaps icon"> Report Overlaps

Checks selected sheets for schedule segments that are incorrectly positioned and saves a CSV report for each overlap type found.

- You select the sheets to check.
- You choose an output folder for the reports.
- Three checks are performed:
  - Schedule segments overlapping each other on the same sheet.
  - Schedule segments placed outside the title block boundary.
  - Schedule segments overlapping viewports on the sheet.
- A separate CSV file is written for each overlap type that has findings, named after the
  model:
  - `<model title>_schedule_segments_overlap.csv`
  - `<model title>_schedule_overlaps_title_block.csv`
  - `<model title>_schedule_overlaps_viewports.csv`

**Use when:** You need to audit sheet layouts before issue, or after a template change has caused schedule instances to shift.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Fix%20Schedule%20Segments%20Overlaps.pushbutton/Icon.png" width="24" alt="Fix Segment Overlaps icon"> Fix Segment Overlaps

Automatically resolves overlapping schedule segments on sheets by moving them horizontally until no overlaps remain.

- You select the split schedules to fix.
- The tool adjusts the position of each schedule sheet instance in the horizontal direction until segments no longer overlap.
- Schedules that do not have overlapping segments are left unchanged.

**Use when:** Split schedules (schedules broken into multiple segments across a sheet) have shifted and are overlapping each other after a template upgrade or sheet reorganisation.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Export%20Room%20Number%20Filter%20Value.pushbutton/Icon.png" width="24" alt="Export Room Number Filter Value icon"> Export Room Number Filter Value

Exports the **Room: Number** filter value currently set on each selected schedule to a CSV file.

- You select the schedules to export.
- The exported CSV contains: Schedule Name, Schedule Id, Field Index, Filter Index, and Room Filter Value.
- Only the first Room: Number filter per schedule is exported.

**Use when:** You want to snapshot which room number each schedule is currently filtered to — for example, before bulk-updating schedules or as part of a handover audit.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Extract%20Room%20Number%20Filter%20Value%20From%20Schedule%20Name.pushbutton/Icon.png" width="24" alt="Extract Room Number Filter Value icon"> Extract Room Number Filter Value

Reads each selected schedule's name, extracts the room number from it using a prefix you specify, and updates that schedule's **Room: Number** filter value to match.

- You select the schedules to update.
- You provide a prefix string (e.g. `"Room "`) — the text immediately after the prefix in the schedule name is used as the room number.
- The Room: Number filter on each schedule is updated in a Revit transaction.
- Schedules where no room number can be extracted from the name are skipped and reported.

**Use when:** Schedules have been renamed to include a room number in their name (e.g. `"Room 1.01 - Door Schedule"`) and you need the schedule's Room: Number filter to be kept in sync with that name.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Views.panel/Schedules.pulldown/Import%20Room%20Number%20Filter%20Value.pushbutton/Icon.png" width="24" alt="Import Room Number Filter Value icon"> Import Room Number Filter Value

Reads a previously exported Room Number filter CSV file and applies the saved filter values back to the matching schedules.

- You select the CSV file produced by **Export Room Number Filter Value**.
- Schedules are matched by their Revit Element Id (from the CSV).
- The Room: Number filter on each matched schedule is updated to the value stored in the CSV.

**Use when:** You need to restore or bulk-apply room filter values to schedules — for example, after a model was detached and schedules lost their filter settings, or when applying a filter snapshot from another model.

---

## Notes

- Column width tools act on the **schedule view**, not on placed schedule instances on sheets; changes propagate to all sheet instances of the same schedule.
- Column widths are handled in **millimetres** throughout; the exported CSV carries the same units.
- Export column widths immediately after finalising a schedule layout to create a restoration point before sharing the template.
- The overlap report and fix tools operate on **schedule instances on sheets**, not on the schedule view definition.
- The Room: Number filter tools work with schedules that have a filter on the built-in `Room: Number` field; schedules without that filter are skipped.
