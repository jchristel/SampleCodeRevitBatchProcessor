# PushIt Stats

**Panel:** PushIt | **Menu:** Stats

Reporting tools that provide a summary of the mock room families in the current Revit model.

---

## Stats Simple

Displays a basic statistical summary of all PushIt mock room elements in the project.

- Total count of mock room instances.
- Breakdown by design set and design option.
- Summary of area totals per design option.

Results are shown in the pyRevit output window and can be copied from there.

**Use when:** You want a quick overview of how many mock rooms exist in the model and what area they collectively represent.

---

## IDs By Design Set and Option

Lists the Revit element IDs of all mock room instances, organised by design set and design option.

- Useful for scripting or batch processing workflows where you need to reference specific elements by ID.
- Output is shown in the pyRevit output window.

**Use when:** You need a structured list of element IDs — for example, to feed into a Revit Batch Processor task or to audit which rooms belong to which design option.

---

## Notes

- Both tools read data from the active document; workshared models must be synced before running to ensure the data is current.
