# Grids

**Panel:** Grids And Levels | **Menu:** Grids

<img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Icon.png" width="40" alt="button icon">

Tools for controlling grid bubble visibility and grid extents in the active view.

All of these act on the **active view** only, and on the grids visible in it.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/All%200%20Bubbles%20On.pushbutton/Icon.png" width="24" alt="Show Bubbles Start icon"> Show Bubbles Start

Switches **on** the bubble at the start end (end 0) of every grid visible in the active view.
It only turns bubbles on; it never turns one off.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/All%201%20Bubbles%20On.pushbutton/Icon.png" width="24" alt="Show Bubbles End icon"> Show Bubbles End

Switches **on** the bubble at the finish end (end 1) of every grid visible in the active view.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/All%20Bubbles%20Off.pushbutton/Icon.png" width="24" alt="All Bubbles Off icon"> All Bubbles Off

Hides the bubbles at **both ends** of every grid visible in the active view.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/All%202D.pushbutton/Icon.png" width="24" alt="All Grids to 2D icon"> All Grids to 2D

Sets both ends of every grid visible in the active view to **2D**, so that extent and bubble
changes made in this view no longer affect other views.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Toggle%200%20Bubbles%20By%20Selection.pushbutton/Icon.png" width="24" alt="Toggle Bubbles Start icon"> Toggle Bubbles Start

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Toggle%201%20Bubbles%20By%20Selection.pushbutton/Icon.png" width="24" alt="Toggle Bubbles End icon"> Toggle Bubbles End

Toggles the bubble at end 0 (Start) or end 1 (End) for **grids you pick**.

Run the tool first — it starts a pick prompt ("Select Grids") filtered to the Grids category.
Pick the grids, finish the selection, and their bubbles at that end are flipped: on becomes
off, off becomes on. There is no need to pre-select anything before launching.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Extend%20Grids.pushbutton/Icon.png" width="24" alt="Extend Grids icon"> Extend Grids

Extends linear grids in the active view out to the **view's crop box**.

**Requirements:**

- The active view must be a **Floor Plan, Ceiling Plan or Area Plan**.
- The view's **crop box must be enabled** — the crop region is what the grids are extended to.
- Only linear grids are handled; arc grids are left alone.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/Grids%20And%20Levels.panel/Grids.pulldown/Propagate%20Grids.pushbutton/Icon.png" width="24" alt="Propagate Grids icon"> Propagate Grids

Copies grid bubble visibility and grid extents from the **active view** to views you select.

**Workflow:**

1. Set the grid display up exactly as you want it in the source view.
2. Run **Propagate Grids**.
3. Select the target views from the list — entries are shown as `view name (view type)`.

**Requirements:**

- The **active view** must be a Floor Plan, Ceiling Plan or Area Plan; the tool exits with an
  "Unsupported active view type" message otherwise.
- Only Floor Plans, Ceiling Plans and Area Plans are offered as targets. Sections, elevations
  and 3D views cannot be targeted.

Progress is shown in a cancellable progress bar.

---

## Notes

- Grids set to 3D share their extents across views. Run **All Grids to 2D** in a view first if
  you want changes there to stay local to it.
- **Propagate Grids** is the efficient way to apply one grid setup across many plan views;
  the per-view tools above are for setting up that one source view.
- If a tool reports "No grids visible in view", check the view's crop, view range and category
  visibility — the tools only see grids the view actually shows.
