# Change Family Category

**Panel:** Families | **Button:** Change Family Category

Changes the Revit category assigned to a family directly from the project environment, without manually opening the family in the family editor.

## What it does

- Presents a list of available Revit categories to choose from.
- Reassigns the selected family to the chosen category.
- Saves the change back to the family.

## When to use this

Use this button when a family has been created or received with the wrong category assignment and needs to be corrected before it can be properly scheduled, filtered, or tagged in your project.

## Notes

- Changing a family's category may affect tags, schedules, filters, and visibility settings that reference the original category.
- Review downstream dependencies (schedules, view filters, tags) after changing the category.
- The family does not need to be open in the family editor; the tool operates on the loaded family in the project.
