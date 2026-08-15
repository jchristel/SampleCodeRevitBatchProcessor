# Solve Warnings

**Panel:** Warnings | **Menu:** Solve Warnings

Automated fixes for four common Revit warning types. Each tool collects the warnings of its
type from the **whole document**, then works through them with a cancellable progress bar.
None of them is view-scoped, and none requires a selection.

If the model holds no warnings of the relevant type, the tool reports so and exits.

---

## Room tags outside of room

Moves room tags that Revit reports as sitting outside their room back onto the room.

For each affected tag it:

1. **Unpins** the tag if it is pinned,
2. **removes the tag's leader**, and
3. moves the tag to the room's location point.

**Note:** the leader removal is a visible change and is not undone by the tool. If your
documentation relies on tag leaders, review the affected tags afterwards.

---

## Duplicate Marks

Resolves **Duplicate Mark** warnings by clearing the Mark parameter.

- Every element named in each warning has its Mark set to an empty value — including the
  first one. The tool does not keep one instance's mark and clear the rest.
- Warnings about duplicate **Type Mark** are recognised and deliberately skipped; they are
  listed in the output as ignored.

**Use when:** A model carries many duplicate mark warnings and the mark values are not
relied upon.

---

## Area Lines Overlap Long / Room Lines Overlap Long

Resolves overlapping area or room separation line warnings by **lengthening**:

> The longer of the two overlapping lines is extended so it completely covers the shorter
> one, and the shorter line is then deleted.

The result is a single continuous line.

---

## Area Lines Overlap Short / Room Lines Overlap Short

Resolves the same warnings by **shortening**:

> The overlap is trimmed away so the two lines no longer cover each other.

Both lines survive, meeting end to end.

---

## Choosing Long or Short

Long and Short are **geometric strategies, not speed or search settings**. Pick on the
outcome you want:

| | Result | Line count |
|---|---|---|
| **Long** | One continuous line spanning both originals | Reduced — the shorter line is deleted |
| **Short** | Two abutting lines with the overlap removed | Unchanged |

Use **Long** to tidy up fragmented boundaries into single runs. Use **Short** where the
individual line segments carry meaning you want to keep — for example where they were drawn
per design area.

---

## Notes

- Warnings are matched by their Revit warning GUID, so only the exact warning type each tool
  targets is addressed. Other warning types are untouched.
- Changes are made with failure handling that does not roll back on warnings, so a fix that
  triggers a further warning still commits. Review the output window.
- Check the Revit warnings dialog after running to confirm the warnings have cleared; some
  overlaps resolve into new warnings that need a second pass.
- These tools modify the model. Save or make a backup first — there is no built-in undo
  beyond Revit's own.
