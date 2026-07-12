# Solve Warnings

**Panel:** Warnings | **Menu:** Solve Warnings

Automated tools for resolving common Revit model warnings without manual intervention.

---

## Room Tags Outside Room

Moves room tags that Revit is warning are positioned outside their associated room back inside the room boundary.

- Automatically repositions each affected tag to the room's internal reference point.
- No manual selection required; the tool processes all relevant warnings in the active document.

---

## Duplicate Marks

Resolves **Duplicate Mark** warnings by clearing the mark value on the affected element instances.

- Identifies all elements generating duplicate mark warnings.
- Clears (empties) the Mark parameter on the duplicate instances.
- The mark on the first instance is left intact; subsequent duplicates are cleared.

**Use when:** A model contains many duplicate mark warnings that are slowing down workflows or preventing export.

---

## Area Separation Lines Long

Resolves **Overlapping Area Separation Lines** warnings using an extended search radius to find and remove duplicate or overlapping line segments.

- Scans all area separation lines in the model.
- Removes the redundant overlapping segment where two lines occupy the same location.

**Long** = wider search radius, catches more overlaps but takes longer on large models.

---

## Area Separation Lines Short

Same as **Area Separation Lines Long** but uses a smaller search radius for faster processing on models where overlaps are known to be close together.

---

## Room Separation Lines Long

Resolves **Overlapping Room Separation Lines** warnings using an extended search radius.

---

## Room Separation Lines Short

Resolves **Overlapping Room Separation Lines** warnings using a smaller, faster search radius.

---

## Notes

- Run **Refresh** (or sync the model) after using any solve tool to confirm warnings have been cleared.
- **Long** variants are more thorough but slower; use **Short** first on large models and fall back to **Long** if any warnings remain.
- These tools only address the specific warning type they are named for; other warning types must be resolved separately.
