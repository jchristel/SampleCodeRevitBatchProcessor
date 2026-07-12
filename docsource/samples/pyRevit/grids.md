# Grids

**Panel:** Grids and Levels | **Menu:** Grids

Tools for controlling grid bubble visibility and grid display mode in the active Revit view.

---

## All 0 Bubbles On

Shows the grid bubble at the **start end** (end 0) of every grid in the active view.

---

## All 1 Bubbles On

Shows the grid bubble at the **finish end** (end 1) of every grid in the active view.

---

## All Bubbles Off

Hides grid bubbles at **both ends** of every grid in the active view.

---

## All 2D

Switches every grid in the active view to **2D** mode, so that changes to grid extents and bubble visibility in this view do not affect other views.

---

## Propagate Grids

Copies grid bubble visibility, extent overrides, and bubble-end settings from the **active view** to one or more selected target views.

**Workflow:**
1. Set up grid display exactly as required in the source plan view.
2. Run **Propagate Grids**.
3. Select the target views to apply the same settings to.

**Use when:** You want all floor plan views in a project to share consistent grid display without adjusting each view manually.

---

## Extend Grids

Extends the visible length of grids in the active view to match a defined boundary or extent.

---

## Toggle 0 Bubbles By Selection

Toggles the bubble at **end 0** of only the grids you have selected before running the tool. Runs on the active view.

---

## Toggle 1 Bubbles By Selection

Toggles the bubble at **end 1** of only the grids you have selected before running the tool. Runs on the active view.

---

## Notes

- All tools act on the **active view** only unless stated otherwise.
- Grid changes made in 3D mode affect all views; switch to 2D mode first with **All 2D** if you need view-specific control.
- **Propagate Grids** is the most efficient way to apply a consistent grid layout across many views at once.
