# Highlight Warnings

**Panel:** Warnings | **Menu:** Highlight Warnings

Six tools for finding area and room separation lines that carry warnings — two that report
them model-wide as tables, two that colour them in the active view, and two that clear the
colouring again.

---

## Report Area Lines with Warnings

Prints a table of every area separation line in the **model** that has a warning attached,
so you can find them. Nothing is selected, zoomed to or overridden.

Table: *Area lines with warnings by scheme and level*

| Column | Content |
|---|---|
| Area Scheme | Area scheme the lines belong to |
| Level | Level the lines are placed on |
| Ids of Area lines with warnings | Element ids, semicolon separated |
| Area Views | Names of the area views on that scheme and level |

The Area Views column tells you which view to open to reach the lines listed on that row.

---

## Report Room Lines with Warnings

The same idea for room separation lines, grouped more finely.

Table: *Room separation lines with warnings by design set / option, level and phase created*

| Column | Content |
|---|---|
| Design Set & Option | Design set and option the lines sit in |
| Level | Level the lines are placed on |
| Phase Created | Phase the lines were created in |
| Ids of Room separation lines with warnings | Element ids, semicolon separated |

---

## Highlight Area Lines with Warnings

Overrides the area separation lines that have warnings in the **active view**, setting their
projection line colour to **red**.

**Requires the active view to be an Area Plan.** The tool exits with *"Active view is not an
area plan view."* otherwise. Only lines belonging to that view's **area scheme** and **level**
are considered.

---

## Highlight Room Lines with Warnings

The room separation line equivalent, also overriding to **red** in the active view.

**Requires the active view to be a Floor Plan.** The tool exits with *"Active view is not an
floor plan view."* otherwise. The lines considered are narrowed to:

- the view's **level**,
- the **active design option** — or the main model if no option is active, and
- the view's **phase** plus all earlier phases; lines created in a later phase are ignored.

The phases being considered are printed to the output window before the override is applied,
which is worth reading if fewer lines light up than you expected.

---

## Remove Highlight from Area Lines without Warnings

## Remove Highlight from Room Lines without Warnings

These do **not** clear every highlight. They remove the override from the lines that **no
longer have warnings**, deliberately leaving the still-warning lines coloured.

That makes them a progress check rather than a cleanup: run a solve tool, then run the
matching Remove Highlight, and whatever is still red is what still needs attention.

The same active view type restrictions apply — Area Plan for area lines, Floor Plan for room
lines.

---

## Suggested workflow

1. **Report** the lines with warnings to see the full scope across the model, and which views
   to work in.
2. Open one of those views and **Highlight** to see them in context.
3. Fix them, either by hand or with the [Solve Warnings](warnings_solve.md) tools.
4. **Remove Highlight** — anything still red is still carrying a warning.
5. Repeat from step 3 until nothing is highlighted.

## Notes

- The overrides are per-view graphic overrides on the active view only; other views are not
  affected.
- Because Remove Highlight only clears lines without warnings, a line whose override you want
  gone while it still has a warning must be reset manually in the view.
- The report tools cover the whole model regardless of the active view, so use them first —
  the highlight tools will only ever show you what is in the view you are standing in.
