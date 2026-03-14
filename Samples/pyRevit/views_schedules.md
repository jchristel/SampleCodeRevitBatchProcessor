# Schedule Column Width Tools

**Panel:** Views | **Menu:** Schedules

Tools for managing the column widths of Revit schedules — exporting the current widths to a file, and restoring them from a saved file.

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

## Notes

- Column width tools act on the **schedule view**, not on placed schedule instances on sheets; changes propagate to all sheet instances of the same schedule.
- Export the column widths immediately after finalising a schedule layout to create a restoration point before sharing the template.
