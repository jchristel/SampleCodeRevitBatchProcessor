# View Templates — Modify

**Panel:** View Templates | **Menu:** Modify

<img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Icon.png" width="40" alt="button icon">

Tools to propagate filter and category overrides from one view template to many others in the
current project.

Three of the four tools work **from a source template**. That source selection is the first
thing they ask for, and it is easy to miss:

> **source template → target templates → what to propagate → apply**

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Apply%20Filter%20Overrides.pushbutton/Icon.png" width="24" alt="Apply Filter Overrides icon"> Apply Filter Overrides

Copies the graphic overrides of selected view filters from a source template to target
templates.

**Workflow:**

1. Select the **source view template** — the one whose overrides are correct.
2. Select the **target view templates** to update.
3. Select the **filters** whose overrides you want to propagate. Only filters present in the
   source template are offered.
4. The overrides are applied.

- A filter that does not exist in a target template is **skipped** for that template.
- Only the graphic overrides are copied. The filter rules themselves are untouched.

**Use when:** You have corrected a filter override in one template and need the same
correction in many others.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Add%20And%20Apply%20Filter%20Overrides.pushbutton/Icon.png" width="24" alt="Add & Apply Filter Overrides icon"> Add & Apply Filter Overrides

Identical to **Apply Filter Overrides**, except that a filter missing from a target template
is **added** to it before its overrides are applied.

**Use when:** Rolling out a new filter standard, where the filter needs to reach templates
that do not yet have it.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Apply%20Graphic%20Overrides.pushbutton/Icon.png" width="24" alt="Apply Graphic Overrides icon"> Apply Graphic Overrides

Copies **category** overrides and visibility settings from a source template to target
templates.

**Workflow:**

1. Select the **source view template**.
2. Select the **target view templates**.
3. Select the **categories** to propagate.
4. The settings are applied.

**Use when:** Propagating cut patterns, projection line weights or category visibility that
are set directly on the template rather than through a filter.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/View%20Templates.panel/Modify.pulldown/Delete%20Filters.pushbutton/Icon.png" width="24" alt="Delete Filters icon"> Delete Filters

Removes filters from view templates. This one has **no source template** — the order is
reversed:

1. Select the **filters** to remove.
2. Select the **view templates** to remove them from.

The filter definitions remain in the project; only their assignment to the selected templates
is removed. Progress is printed per template to the output window.

---

## Notes

- These tools act on **view templates**, not on individual views. Views using those templates
  pick the changes up through the template.
- Test on a single target template before applying across a large project — there is no
  built-in undo beyond Revit's own.
- If a tool reports that no filters or categories are available, check the source template
  actually carries the overrides you expect.
