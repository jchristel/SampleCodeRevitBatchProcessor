# PushIt Stats

**Panel:** PushIt | **Menu:** Stats

Two reporting tools covering the mock room families in the current model. Both print tables
to the pyRevit output window and change nothing in the model.

Both read the enabled categories and the unique-ID parameter from the current PushIt data
source configuration, and report on the family instances found in those categories.

---

## Stats

Prints three tables:

| Table | Columns |
|---|---|
| Basic Statistics of PushIt Elements | Family Name, Count |
| Creators of PushIt Elements | Creator, Count |
| Owners of PushIt Elements | Owner, Count |

The creator and owner figures come from Revit's worksharing tooltip information, so they are
only meaningful in a workshared model.

Before the tables, the output window lists the supported categories, the unique-ID parameter
name and GUID, and the total number of family instances found.

**Use when:** You want to know how many mock rooms exist, which families they use, and who
created or currently owns them.

---

## Stats By Design Set And Option

A data quality check, not a listing. It groups the mock rooms by their unique-ID parameter
value and reports only the values that appear in **more than one design set** — instances
that would be counted twice in any area or room schedule spanning design options.

| Column | Content |
|---|---|
| Unique Id | The unique-ID parameter value shared by the instances |
| Design Set | The design set the instances sit in |
| Family Instance ID | Element ids of the instances in that design set |

Each problematic unique ID produces one row, with the design set and instance ids repeated
across the row for every set the ID appears in.

When nothing is wrong the tool prints **"No problematic keys found."** and stops — an empty
result is the good outcome.

**Use when:** Before running area take-offs or exporting room data, to confirm no mock room
has been duplicated across design options.

---

## Notes

- Both tools require the PushIt data source to be configured; if it cannot be read they exit
  with *"Invalid data source or supported categories"*.
- Both require the unique-ID shared parameter to be present; if it is missing they exit with
  *"Invalid parameter name or guid"*.
- Both read the active document only. Sync a workshared model before running so the counts and
  ownership data are current.
