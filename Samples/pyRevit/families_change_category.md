# Change Category

**Panel:** Families | **Button:** Change Category

Changes the Revit category of the family currently open in the Family Editor, preserving its
subcategories.

## What it does

- Checks that the active document is a **family document**. If it is not, the tool reports
  *"This is not a family document."* and exits.
- Presents a list of the categories available for the family's category type, so you can pick
  the new one.
- Reassigns the family to the selected category, recreating the family's subcategories under
  the new category and re-assigning elements to them so the family's graphical structure
  survives the change.

## When to use this

Use this when a family has been created or received with the wrong category and needs to be
corrected before it can be properly scheduled, filtered or tagged.

## Requirements

- **The family must be open in the Family Editor and be the active document.** This tool does
  not operate on families loaded in a project — open the family first (via Edit Family or by
  opening the `.rfa` directly).
- The target category must be valid for the family's template. Only categories matching the
  family's category type are offered.

## Notes

- The family is **not saved** by this tool. Review the result, then save the family yourself —
  or close without saving to discard the change.
- After saving, reload the family into any projects that use it for the change to take effect
  there.
- Changing a family's category affects tags, schedules, view filters and visibility settings
  that reference the original category. Review those downstream dependencies.
- Subcategories are carried across, but any host project overrides keyed to the old
  category's subcategories will not follow automatically.
