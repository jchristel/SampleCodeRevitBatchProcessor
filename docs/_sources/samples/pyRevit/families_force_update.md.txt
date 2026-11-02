# Force Update

**Panel:** Families | **Button:** Force Update

<img src="Extensions/duHast-2025.extension/duHast.tab/Families.panel/ForceUpdate.pushbutton/Icon.png" width="40" alt="button icon">

Forces Revit to treat the open family as modified, so that projects using it will offer to
reload it.

## What it does

Operating on the family currently open in the Family Editor:

1. Creates a temporary new family type.
2. **Saves the family.**
3. Deletes the temporary type.
4. **Saves the family again.**

The type change between the two saves is what makes Revit register the family as changed.

## When to use this

Use this when a family file on disk has been altered — typically overwritten by a copy from
elsewhere — but Revit does not recognise it as different and will not offer to reload it into
a project.

## Requirements

- **The family must be open in the Family Editor and be the active document.** If it is not,
  the tool reports *"This is not a family document."* and exits. It does not operate on a
  family selected in the project browser.

## Notes

- Unlike **Change Category**, this tool **writes to disk** — it saves the family twice, over
  the file it was opened from. There is no prompt and no backup beyond Revit's own.
- The temporary type is created and removed automatically; no cleanup is needed.
- If either save fails the tool aborts and reports it, which can leave the temporary type in
  place. Check the family's type list before saving it yourself.
- Progress is reported in the output window.
