# Force Update

**Panel:** Families | **Button:** Force Update

Forces Revit to recognise and apply changes to a family that it has already loaded, bypassing the normal "family is up to date" cache.

## What it does

1. Opens the selected family in the family editor.
2. Creates a temporary new family type.
3. Saves the family.
4. Deletes the temporary type.
5. Saves the family again.

This double-save with a type change tricks Revit into treating the family as modified, which causes it to prompt for reload when the family is next encountered in a project.

## When to use this

Use this button when you have edited a family file on disk but Revit is not detecting the change and refusing to reload it — typically because the file timestamp or internal checksum has not changed in a way Revit recognises.

## Notes

- The family must be open in Revit (or you must select it from the project browser) before running this tool.
- The temporary type is created and deleted automatically; no manual cleanup is required.
