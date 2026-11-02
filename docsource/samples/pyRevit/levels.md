# Levels

**Panel:** Grids And Levels | **Menu:** Levels

<img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/Icon.png" width="40" alt="button icon">

Tools for controlling level header visibility and level extents in the active view.

All of these act on the **active view** only, and on the levels visible in it. They are the
level counterparts of the [Grids](grids.md) tools and follow the same start/end convention —
but note there is no level equivalent of *Extend Grids* or *Propagate Grids*.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/All%200%20Headers%20On.pushbutton/Icon.png" width="24" alt="Show Headers Start icon"> Show Headers Start

Switches **on** the header at the start end (end 0) of every level visible in the active view.
It only turns headers on; it never turns one off.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/All%201%20Headers%20On.pushbutton/Icon.png" width="24" alt="Show Headers End icon"> Show Headers End

Switches **on** the header at the finish end (end 1) of every level visible in the active view.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/All%20Headers%20Off.pushbutton/Icon.png" width="24" alt="All Heads Off icon"> All Heads Off

Hides the headers at **both ends** of every level visible in the active view.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/All%202D.pushbutton/Icon.png" width="24" alt="All Levels to 2D icon"> All Levels to 2D

Sets both ends of every level visible in the active view to **2D**, so that extent and header
changes made in this view no longer affect other views.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/Toggle%200%20Headers%20By%20Selection.pushbutton/Icon.png" width="24" alt="Toggle Headers Start icon"> Toggle Headers Start

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Levels.pulldown/Toggle%201%20Headers%20By%20Selection.pushbutton/Icon.png" width="24" alt="Toggle Headers End icon"> Toggle Headers End

Toggles the header at end 0 (Start) or end 1 (End) for **levels you pick**.

Run the tool first — it starts a pick prompt ("Select levels") filtered to the Levels
category. Pick the levels, finish the selection, and their headers at that end are flipped.
There is no need to pre-select anything before launching.

---

## Notes

- Levels are visible in section and elevation views, so that is where these tools are
  normally used.
- Levels set to 3D share their extents across views. Run **All Levels to 2D** in a view first
  if you want changes there to stay local to it.
- If a tool reports no levels in the view, check the view's crop, extents and category
  visibility — the tools only see levels the view actually shows.
