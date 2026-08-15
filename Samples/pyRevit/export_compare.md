# Compare

**Panel:** Export | **Button:** Compare

Compares the sheets listed in a Revit schedule against the PDF files in a folder, and
reports which sheets have no matching file and which have more than one.

## What it does

1. Asks you to select a **schedule** from the model by name.
2. Asks you to select a **folder** containing the PDF files to check against.
3. Exports all sheet schedules and reads the selected schedule's content back.
4. Builds a sheet number for each row by concatenating the **first two columns** of that row
   (see *Schedule setup* below). Rows with fewer than two columns are skipped.
5. Finds every `.pdf` in the folder and all its subfolders.
6. Matches each sheet number against the file names using a **starts with** test.
7. Reports, sorted by sheet number:
   - sheet numbers with **no matching file**;
   - sheet numbers with **more than one matching file**.

Matched sheets are printed as they are found. If every sheet matches exactly one file the
tool reports that all files matched successfully.

## When to use this

Use this after an issue to confirm that every sheet on the drawing register has been
exported, and that no sheet has produced duplicate files.

## Schedule setup

The sheet number is built as `row[0] + row[1]` — the first two columns of the schedule,
concatenated with no separator. This suits a schedule whose first two fields together form
the full sheet number (for example a discipline prefix column followed by a number column).

If your schedule holds the whole sheet number in a single first column, the second column's
value will be appended to it and nothing will match. Adjust the schedule fields, or the
`get_full_sheet_number_from_data` function in
`Extensions/duHast-2025.extension/duHast.tab/lib/export/CompareRevitToFolder/compare_revit_schedule_to_folder.py`,
accordingly.

## Requirements

- A schedule in the model listing the sheets to check.
- A folder of exported PDFs, named so that each file name **begins with** the sheet number.

## Notes

- Only `.pdf` files are considered. DWG exports are not checked by this tool.
- The comparison is on file names only. File contents, dates and sizes are not examined, so
  this will not tell you whether a PDF is out of date — only whether one exists.
- The search walks subfolders, so a sheet found in two different subfolders is reported as
  a multiple match.
- A schedule that filters out sheets will cause those sheets to be absent from the check;
  the tool reports on what the schedule contains, not on every sheet in the model.
