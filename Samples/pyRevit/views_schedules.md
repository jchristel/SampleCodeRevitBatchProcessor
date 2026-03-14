# Schedule Tools

**Panel:** Views | **Menu:** Schedules

Tools for managing Revit schedules — column widths, sheet placement overlaps, and room number filter values.

---

## Export Column Width

Saves the current column widths of a selected schedule to a file.

- You select the schedule to export.
- Column widths are written to a JSON or CSV file you specify.
- Use this as a snapshot before changes, or as a template to apply to other schedules.

---

## Resize Column Width From Export

Restores column widths to a schedule from a previously saved export file.

- You select the target schedule and the export file.
- Column widths are applied in the order defined in the file.
- Columns that exist in the file but not in the schedule are skipped.

**Use when:** A schedule's column widths have been reset (e.g., after upgrading a template) and you need to restore them to a known-good state.

---

## Resize Column Width By Name And Value

Sets schedule column widths by specifying column names and target widths directly, without needing a previously exported file.

- Useful for applying a standard width to a named set of columns across multiple schedules.

---

## Report Schedules Overlaps

Checks selected sheets for schedule segments that are incorrectly positioned and saves a CSV report for each overlap type found.

- You select the sheets to check.
- You choose an output folder for the reports.
- Three checks are performed:
  - Schedule segments overlapping each other on the same sheet.
  - Schedule segments placed outside the title block boundary.
  - Schedule segments overlapping viewports on the sheet.
- A separate CSV file is written for each overlap type that has findings.

**Use when:** You need to audit sheet layouts before issue, or after a template change has caused schedule instances to shift.

---

## Fix Schedule Segments Overlaps

Automatically resolves overlapping schedule segments on sheets by moving them horizontally until no overlaps remain.

- You select the split schedules to fix.
- The tool adjusts the position of each schedule sheet instance in the horizontal direction until segments no longer overlap.
- Schedules that do not have overlapping segments are left unchanged.

**Use when:** Split schedules (schedules broken into multiple segments across a sheet) have shifted and are overlapping each other after a template upgrade or sheet reorganisation.

---

## Export Room Number Filter Value

Exports the **Room: Number** filter value currently set on each selected schedule to a CSV file.

- You select the schedules to export.
- The exported CSV contains: Schedule Name, Schedule Id, Field Index, Filter Index, and Room Filter Value.
- Only the first Room: Number filter per schedule is exported.

**Use when:** You want to snapshot which room number each schedule is currently filtered to — for example, before bulk-updating schedules or as part of a handover audit.

---

## Extract Room Number Filter Value From Schedule Name

Reads each selected schedule's name, extracts the room number from it using a prefix you specify, and updates that schedule's **Room: Number** filter value to match.

- You select the schedules to update.
- You provide a prefix string (e.g. `"Room "`) — the text immediately after the prefix in the schedule name is used as the room number.
- The Room: Number filter on each schedule is updated in a Revit transaction.
- Schedules where no room number can be extracted from the name are skipped and reported.

**Use when:** Schedules have been renamed to include a room number in their name (e.g. `"Room 1.01 - Door Schedule"`) and you need the schedule's Room: Number filter to be kept in sync with that name.

---

## Import Room Number Filter Value

Reads a previously exported Room Number filter CSV file and applies the saved filter values back to the matching schedules.

- You select the CSV file produced by **Export Room Number Filter Value**.
- Schedules are matched by their Revit Element Id (from the CSV).
- The Room: Number filter on each matched schedule is updated to the value stored in the CSV.

**Use when:** You need to restore or bulk-apply room filter values to schedules — for example, after a model was detached and schedules lost their filter settings, or when applying a filter snapshot from another model.

---

## Notes

- Column width tools act on the **schedule view**, not on placed schedule instances on sheets; changes propagate to all sheet instances of the same schedule.
- Export column widths immediately after finalising a schedule layout to create a restoration point before sharing the template.
- The overlap report and fix tools operate on **schedule instances on sheets**, not on the schedule view definition.
- The Room: Number filter tools work with schedules that have a filter on the built-in `Room: Number` field; schedules without that filter are skipped.
