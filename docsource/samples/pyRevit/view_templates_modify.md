# View Templates â€” Modify

**Panel:** View Templates | **Menu:** Modify

Tools to propagate filter settings and graphic overrides across multiple view templates in the current project in a single operation.

---

## Apply Filter Overrides

Copies the graphic override settings of selected view filters from a source template to one or more target templates.

**Workflow:**
1. Run the tool.
2. Select the filters whose overrides you want to propagate.
3. Select the target view templates to update.
4. The tool applies the matching filter overrides to every selected target template.

- If a filter does not exist in a target template, it is skipped for that template (existing filters are not removed).
- Only the graphic overrides (colour, line weight, halftone, etc.) are copied; the filter rules themselves are not changed.

**Use when:** You have adjusted a filter override in one template and need the same change applied to many other templates.

---

## Add And Apply Filter Overrides

An extended version of **Apply Filter Overrides** that also adds the filter to target templates where it does not yet exist, in addition to applying the overrides.

**Use when:** You are rolling out a new filter standard and need to add the filter to all relevant templates as well as setting its overrides.

---

## Apply Graphic Overrides

Copies category-level graphic overrides (not filter-based) from a source template to one or more target templates.

- Useful for propagating changes to cut patterns, projection line weights, or category visibility settings that are defined directly on the template rather than through a filter.

---

## Delete Filters

Removes specified filters from one or more view templates in a single operation.

- You select which filters to delete and which templates to remove them from.
- The filter definitions themselves remain in the project; only the assignment to the selected templates is removed.

---

## Notes

- All tools act on **view templates** in the current project; they do not modify individual views directly.
- Test changes on a single target template before applying to all templates in large projects.
