# Get A Room!

**Panel:** PushIt | **Button:** Get A Room! / Settings (split button)

<img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/GetARoom.splitbutton/Icon.png" width="40" alt="button icon">

Builds new mock room families from filled regions drawn in the model, then loads and places
them.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/GetARoom.splitbutton/GetARoom.pushbutton/Icon.png" width="24" alt="Get A Room! icon"> Get A Room! (main button)

This tool **authors Revit family files on disk**. It does not place instances of an existing
mock room family — it creates a new set of family files for every filled region you select.

**What it does**, for each selected filled region:

1. Verifies the region: it must have **one or two** curve loops, and if there are two they
   must be nested (an outer boundary with an inner void). Regions that fail are reported and
   skipped.
2. Moves a copy of the region's curve loops so the bounding box centre sits on the origin.
3. Creates **three family files** from the templates shipped with the extension:
   - a **wall hosted host family**, containing
   - a **nested generic model family** for Medium and Fine detail levels, and
   - a **nested generic model family** for Coarse detail level.

   One loop produces a **Bay** family; two loops produce a **Room** family.
4. Saves the families into the configured output directory.
5. Loads the host family into the model and places an instance at the filled region's
   bounding box centre.
6. Asks what to do with the source filled region — *delete just this one*, *delete all*,
   *keep this one*, or *keep all*. The "all" answers are remembered for the rest of the run.

**Workflow:**

1. Run **Settings** once per model to set the family output directory.
2. Draw filled regions in a floor plan or area plan to represent your room layout.
3. Open that view, run **Get A Room!** and pick the filled regions.
4. Answer the prompt about deleting the source regions.
5. Use **Push It!** to push room data into the created instances.

**Requirements:**

- The **active view must be a Floor Plan or an Area Plan**. The tool exits if it is not.
- The Get A Room settings schema must exist in the model — see **Settings** below. Without it
  the tool exits with *"Extensible schema does not exist. Please run the settings add-in
  first."*
- The output directory must be writable; three `.rfa` files are written per filled region.

---

## <img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/GetARoom.splitbutton/Settings.pushbutton/Icon.png" width="24" alt="Settings icon"> Settings

Stores **one value** in the model: the directory the generated family files are written to.

- The value is saved to the model in an extensible schema, so it travels with the file and
  only needs setting once per model.
- If the schema exists but holds no usable directory, **Get A Room!** falls back to asking you
  to pick one for that run.

Settings does **not** select a mock room family or type, and does not set default parameter
values — the families are generated from the bundled templates, and the geometry comes from
the filled region.

---

## Notes

- Family templates live in
  `Extensions/duHast-2025.extension/duHast.tab/lib/pushIt_associated/get_a_room/templates/`.
  The generated families derive their width, depth, height and designed area from the
  `duHast_*` parameters shared with the rest of the PushIt toolset.
- One filled region produces one mock room. Shapes with more than two loops are rejected
  rather than approximated.
- Files are written straight to the output directory. Re-running over the same regions will
  produce families with the same names — check the directory before a second pass.
- Deleting the source filled region is optional and is asked per run, not per session.
