# Get A Room

**Panel:** PushIt | **Button:** Get A Room! / Settings (split button)

Tools for creating mock room families from filled regions drawn in the Revit model.

---

## Get A Room! (main button)

Converts filled regions in the current Revit model into mock room family instances.

- Reads each filled region's geometry and position.
- Places a mock room family instance at the corresponding location, sized and oriented to match the region.
- The resulting mock rooms can then be targeted by the PushIt tool to receive room data.

**Workflow:**
1. Draw filled regions in a plan view to represent your room layout (or import them from a design tool).
2. Run **Get A Room!** to convert them to mock room family instances.
3. Use **PushIt** to push room data into the created instances.

---

## Settings

Configures the parameters used by **Get A Room!** when creating mock room families.

- Select which family and type to use for the mock rooms.
- Set default parameter values applied to newly created instances.
- Configure how the tool interprets the filled region geometry (e.g., which dimension maps to width vs depth).

**Run Settings before your first use** of Get A Room! to ensure the correct family type is selected.

---

## Notes

- Filled regions must be in a plan view; regions in other view types are not processed.
- Each filled region becomes one mock room family instance; complex or irregular shapes are approximated by the family's boundary.
