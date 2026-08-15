# Purge Unused

**Panel:** Purge Unused | **Menu:** Purge

<img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Icon.png" width="40" alt="button icon">

Tools to remove unused graphic styles, patterns, parameters, views and templates from the
current model.

**Every tool in this menu asks you what to remove before it deletes anything.** None of them
runs unattended. What differs is *how* they decide what to offer you.

## Two families of tool

**Try-and-delete tools** — Line Styles, Line Patterns, Fill Patterns, Shared Parameters.
These attempt to delete each candidate and keep only the deletions Revit accepts; anything
still in use is rejected and survives. Each has a plain button that sweeps everything of that
kind, and a **By Selection** twin that runs the same sweep restricted to items you pick.

**List-and-choose tools** — Filters, Unplaced Legends, Unplaced Schedules, Templates,
Unplaced Views. These work out the unused items up front and present that list for you to
choose from. There is no By Selection twin because the selection *is* the tool.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Line%20Styles.pushbutton/Icon.png" width="24" alt="Line Styles icon"> <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Line%20Styles%20By%20Selection.pushbutton/Icon.png" width="24" alt="Line Styles By selection icon"> Line Styles / Line Styles By selection

Removes line styles not referenced by any element.

The **By Selection** variant lists **every** line style in the model, not just the unused
ones — the try-and-delete pass still refuses to remove any that are in use, so a selection
that includes used styles is safe, it simply won't remove them.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Fill%20Patterns.pushbutton/Icon.png" width="24" alt="Fill Patterns icon"> <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Fill%20Patterns%20By%20Selection.pushbutton/Icon.png" width="24" alt="Fill Patterns By Selection icon"> Fill Patterns / Fill Patterns By Selection

Removes fill patterns not used by any material, surface pattern or element override. Same
selection behaviour as line styles.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Line%20Patterns.pushbutton/Icon.png" width="24" alt="Line Patterns icon"> <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Line%20Patterns%20By%20Selection.pushbutton/Icon.png" width="24" alt="Line Patterns By Selection icon"> Line Patterns / Line Patterns By Selection

Removes line patterns not used by any line style, grid, level or other element. Same
selection behaviour as line styles.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Shared%20Parameters.pushbutton/Icon.png" width="24" alt="Shared Parameters icon"> <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Shared%20Parameters%20By%20Selection.pushbutton/Icon.png" width="24" alt="Shared Parameters by Selection icon"> Shared Parameters / Shared Parameters by Selection

Removes shared parameter definitions not bound to any category in the project. Same
selection behaviour as line styles.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Unused%20Filters.pushbutton/Icon.png" width="24" alt="Filters icon"> Filters

Collects view filters not assigned to any view or view template, then asks which of them to
purge.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Unused%20Legends.pushbutton/Icon.png" width="24" alt="Unplaced Legends icon"> Unplaced Legends

Collects legend views not placed on any sheet, then asks which to purge.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Unused%20Schedules.pushbutton/Icon.png" width="24" alt="Unplaced Schedules icon"> Unplaced Schedules

Collects schedule views not placed on any sheet, then asks which to purge.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Unused%20Templates.pushbutton/Icon.png" width="24" alt="Templates icon"> Templates

Collects view templates not applied to any view, then asks which to purge.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Purge%20Unused.panel/Purge.pulldown/Purge%20Unplaced%20Views.pushbutton/Icon.png" width="24" alt="Unplaced Views icon"> Unplaced Views

Collects views not placed on any sheet — floor plans, sections, elevations, 3D views — then
asks which to purge.

---

## Notes

- Save or back up the model before purging. Deletions cannot be undone once the file is saved.
- The list-and-choose tools show nothing to select when there is nothing unused of that kind;
  they report so and exit.
- Running Revit's built-in **Purge Unused** afterwards can free up further items these tools
  do not target.
- These tools cover specific element types. They are not a substitute for a full model audit.
