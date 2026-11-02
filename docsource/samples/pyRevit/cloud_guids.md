# GUIDS

**Panel:** Cloud | **Button:** GUIDS

<img src="Extensions/duHast-2025.extension/duHast.tab/Cloud.panel/GUIDS.pushbutton/Icon.png" width="40" alt="button icon">

Collects the Autodesk cloud identifiers for the current model **and every Revit link in it**,
prints them to the output window, and saves them as a CSV.

## What it does

1. Reads the Revit version and the cloud project GUID, model GUID, file size and file name
   for the **active document**.
2. Walks all Revit link instances in the model and reads the same values for each linked
   document. File size for links is fetched from the cloud by model GUID.
3. Prints one comma-separated row per model:

   ```
   version, project guid, file guid, file size, file name
   ```

4. Opens a save dialog and writes all rows to a CSV file.

A link whose cloud data cannot be read is reported in the output window and skipped; the run
continues with the remaining links.

## When to use this

Use this when building a **Revit Batch Processor** task file that targets cloud models. The
CSV it produces contains exactly the identifiers the batch processor needs, for the host
model and its links in one pass — which is what makes it worth running on a federated model
rather than reading GUIDs one file at a time.

## Requirements

- The active document must be hosted on Autodesk Construction Cloud or BIM 360. Local files
  and local central files have no cloud GUIDs.
- Cloud access is needed for the link file sizes to resolve.

## Notes

- The CSV is written **without a header row** — the header shown above is printed to the
  output window only. Add it manually if your downstream process expects one.
- Cancelling the save dialog abandons the data; the values remain visible in the output
  window and can be copied from there.
- Links that are unloaded, or whose document cannot be opened, contribute no row.
