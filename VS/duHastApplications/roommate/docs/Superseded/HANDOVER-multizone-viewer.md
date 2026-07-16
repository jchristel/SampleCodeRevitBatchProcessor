# Handover: Multi-Zone Linked Floor-Plan Viewer

**For:** Claude Desktop, working on the Roommate browser viewer (`index.html`).
**Scope:** Refactor the single-SVG viewer into N side-by-side zones, each
rendering an independent floor plan, with an option to link their zoom/pan so
they move together.

This is a **client-side-only** change. No server, contract, or MCP changes are
needed. Everything below concerns `index.html`.

---

## 1. Where the code stands today (ground truth)

The uploaded copy in the project chat was stale; this reflects the **actual**
current `index.html`. Read these before touching anything:

- **One canvas.** A single `<svg id="plan">` inside `<main>`. All rendering
  targets it directly via the module-level `const plan`.
- **One global view.** `let view = {x,y,w,h}` plus `let fitted = {...}` are
  module-level singletons. `setViewBox()` writes `view` onto `plan`'s
  `viewBox` attribute. There is exactly one of each.
- **Pan/zoom is bound to `plan` directly.** The `pointerdown/move/up`, `wheel`,
  and `dblclick` handlers (near the bottom, "--- pan & zoom ---") all mutate
  the single `view` and call `setViewBox()`.
- **Render entry point:** `renderLevel(payload, levelId, {refit})` does
  `plan.replaceChildren()`, computes `bounds()` over the level's rooms, sets
  `fitted`/`view` when `refit` is true, draws grid + room polygons (two-pass:
  all polygons, then all labels — SVG paint order = DOM order, so labels must
  come last), and that's it.
- **State singletons** near the top: `currentPayload`, `activeLevelId`,
  `currentProjectId`, `currentBuildingKey`, `currentMilestone`, plus the
  validation/error-highlight state (`showErrors`, `errorRoomIds`).
- **One polling loop.** `tick()` runs every 2s: `loadProjects()` then `poll()`.
  `poll()` fetches `roomsUrl()` (built from the current project/building/
  milestone selection), diffs the JSON string, and calls `ingest()` only on a
  real change. `ingest()` re-fits and rebuilds the level control.
- **Pure helpers already exist and are zone-agnostic:** `flip`, `bounds`,
  `loopBox`, `pointsAttr`, `centroid`, `levelsForPayload`, `roomsOnLevel`,
  `line`, `titleEl`. These take data and return data/elements — reuse as-is.

The blocker for multi-zone is simply that `plan`, `view`, `fitted`, and every
render/interaction function assume **one** of everything.

---

## 2. Target design

Replace the single canvas with a **zone model**. A zone is a self-contained
viewer: its own SVG element, its own `view`/`fitted`, its own scope selection
(project/building/milestone/level), its own poll cursor. Zones live in a CSS
grid inside `<main>`. A global toggle links their view transforms.

### 2.1 The `Zone` object

Model each zone as a plain object (or a small class). One instance per panel:

```
Zone = {
  id,                       // stable string, e.g. "zone-0"
  root,                     // the container <div> for this zone
  svg,                      // this zone's <svg> element
  view:   {x,y,w,h},        // was the global `view`
  fitted: {x,y,w,h},        // was the global `fitted`
  // scope selection (was the global currentProjectId etc.)
  projectId, buildingKey, milestone, activeLevelId,
  // per-zone poll bookkeeping (was the global lastPayloadJson etc.)
  currentPayload, lastPayloadJson,
  lastProjectIds, lastBuildingsSignature, lastMilestonesSignature,
  // per-zone validation/highlight state
  currentValidation, errorRoomIds, showErrors,
  // this zone's header controls (see 2.3)
  els: { projectSelect, buildingSelect, milestoneSelect, levelSelect,
         meta, validationToggle, ... }
}
```

The refactor is mechanically: **every module-level singleton that today
describes "the current view/scope/payload" becomes a field on `Zone`.** The
pure geometry helpers stay module-level and gain no state.

### 2.2 Function signatures change from implicit-global to explicit-zone

Rewrite the render/interaction functions to take a `zone`:

- `setViewBox(zone)` → writes `zone.view` onto `zone.svg`.
- `renderLevel(zone, payload, levelId, {refit})` → all `plan.*` become
  `zone.svg.*`; all `view`/`fitted` become `zone.view`/`zone.fitted`;
  `showErrors`/`errorRoomIds` read from `zone`.
- `addLabel(zone, room, baseFont)` → appends to `zone.svg`.
- `ingest(zone, payload)`, `updateMeta(zone)`, `selectLevel(zone, levelId)`,
  `buildLevelControl(zone, ...)`, `roomsUrl(zone)`, `poll(zone)` — same
  pattern.

`bounds`, `loopBox`, `pointsAttr`, `centroid`, `line`, `titleEl`,
`flip`, `levelsForPayload`, `roomsOnLevel` are **unchanged** — they never
touched globals.

### 2.3 Per-zone header vs. global header

Today all pickers live in the one top `<header>`. With N zones each needing its
own project/building/milestone/level selection, move those pickers into a
**per-zone toolbar** (a strip at the top of each zone's container). Keep a
slim **global header** for app-wide controls: the title, an "Add zone" /
"Remove zone" control, the layout selector, and the **Link views** toggle.

If you want to keep scope simple for a first cut: let every zone default to the
same project/building the first zone resolves, and let the user change each
zone's level independently. Independent project selection per zone is the fully
general version and falls straight out of the model above.

### 2.4 Layout

`<main>` becomes a CSS grid of zone containers:

```css
main { display: grid; gap: 1px; background: var(--ink); /* gap = hairline rule */ }
main.cols-1 { grid-template-columns: 1fr; }
main.cols-2 { grid-template-columns: 1fr 1fr; }
main.cols-3 { grid-template-columns: 1fr 1fr 1fr; }
.zone { position: relative; overflow: hidden; background: var(--paper);
        display: grid; grid-template-rows: auto 1fr; }
.zone-toolbar { display: flex; gap: .5rem; padding: .4rem .6rem;
                border-bottom: 1px solid var(--ink); }
.zone svg { width: 100%; height: 100%; display: block; cursor: grab; }
```

The `gap` with a dark `background` gives you the hairline divider between zones
for free. Set `main.className` from the zone count (or an explicit layout
picker).

---

## 3. The linking mechanism (the actual point)

A global flag plus a broadcast. When **linked**, an interaction in any zone
writes the resulting transform to every zone; when **unlinked**, it writes only
to its own.

```js
let linkViews = false;   // global toggle, driven by the header button

// Apply a view to a zone and repaint its viewBox.
function applyView(zone, v) {
  zone.view = { ...v };
  setViewBox(zone);
}

// After a zone computes its new view from a gesture, route it:
// linked -> every zone gets the SAME view; unlinked -> just this one.
function commitView(originZone, v) {
  if (linkViews) {
    for (const z of zones) applyView(z, v);
  } else {
    applyView(originZone, v);
  }
}
```

### 3.1 Same coordinate space assumption

Broadcasting a raw `{x,y,w,h}` viewBox across zones only "lines up" if the zones
share a world coordinate system — true when they show **different levels of the
same building** (all levels share the model origin) or the **same plan** twice.
For different buildings/projects the origins differ, so a raw copy will pan them
in lockstep but not to a meaningful shared datum. That is acceptable and often
still useful (synchronized relative pan/zoom). If you later want true datum
alignment across buildings, offset each zone's broadcast by
`(zone.fitted - originZone.fitted)` — note it as a future refinement, don't
build it now.

### 3.2 Rebind the gesture handlers per zone

Today's handlers are attached once to `plan`. Attach them per zone in a
`wireInteractions(zone)` called at zone creation. Each handler computes the new
transform against **that zone's** `view`/`svg`, then calls `commitView(zone, v)`
instead of mutating a global and calling `setViewBox()` directly. Sketch:

```js
function wireInteractions(zone) {
  const svg = zone.svg;
  let dragging = false, last = null;

  svg.addEventListener("pointerdown", e => {
    dragging = true; last = { x: e.clientX, y: e.clientY };
    svg.setPointerCapture(e.pointerId);
  });
  svg.addEventListener("pointerup", () => { dragging = false; });

  svg.addEventListener("pointermove", e => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const v = { ...zone.view };
    v.x -= (e.clientX - last.x) / rect.width  * v.w;
    v.y -= (e.clientY - last.y) / rect.height * v.h;
    last = { x: e.clientX, y: e.clientY };
    commitView(zone, v);           // <- linked? broadcast. else just this zone.
  });

  svg.addEventListener("wheel", e => {
    e.preventDefault();
    const rect = svg.getBoundingClientRect();
    const v = { ...zone.view };
    const mx = v.x + (e.clientX - rect.left) / rect.width  * v.w;
    const my = v.y + (e.clientY - rect.top)  / rect.height * v.h;
    const k = e.deltaY > 0 ? 1.1 : 0.9;
    v.x = mx - (mx - v.x) * k;
    v.y = my - (my - v.y) * k;
    v.w *= k; v.h *= k;
    commitView(zone, v);
  }, { passive: false });

  svg.addEventListener("dblclick", () => commitView(zone, zone.fitted));
}
```

### 3.3 One subtlety: linked wheel-zoom anchor

When linked, each zone zooms around the **origin zone's** cursor point (because
`commitView` copies one `v` to all). That's the correct and expected behavior —
the plans stay locked together. Do **not** recompute the anchor per zone in
linked mode; that would desync them. Only the origin zone's gesture defines the
transform.

---

## 4. Recommended build order

1. **Extract the Zone struct without changing behavior.** Wrap today's single
   canvas in one `Zone` instance; thread `zone` through `renderLevel`,
   `setViewBox`, `ingest`, `poll`, etc. Verify the app behaves exactly as
   before with `zones = [theOneZone]`. This is the bulk of the work and is
   pure mechanical de-globalization.
2. **Make `zones` an array + render N containers.** Add "Add/Remove zone" and
   the `main.cols-N` layout switch. Give each zone its own toolbar + poll loop.
   `tick()` becomes `for (const z of zones) await pollZone(z)` (plus the shared
   `loadProjects` per zone, or once globally if scope is shared).
3. **Add the link toggle + `commitView` broadcast.** Wire the header button to
   `linkViews`; route all gesture handlers through `commitView`.
4. **Polish:** per-zone meta line, per-zone validation panel (or keep
   validation global and target the active zone), sensible default scope for a
   newly-added zone (clone the last zone's project/building, bump the level).

Ship after step 3; step 4 is refinement.

---

## 5. Gotchas carried over from the current code

- **Two-pass rendering must stay.** In `renderLevel`, all room polygons are
  appended before any label because SVG z-order is DOM order. Keep this per
  zone — don't collapse it back into one loop.
- **`refit: false` on highlight toggles.** The validation panel re-renders with
  `refit:false` so opening it doesn't disturb pan/zoom. Preserve this per zone;
  a re-render must never silently reset `zone.view`.
- **Poll diffing is by JSON string.** `lastPayloadJson` gates `ingest`. This
  must become per-zone (`zone.lastPayloadJson`) or zones sharing one scope will
  stomp each other's change detection.
- **Picker auto-hide/auto-select logic** (≤1 option hides; exactly one real
  choice auto-selects) lives in the populate/load functions — carry it per zone
  so a single-project dev setup still shows a clean UI in every zone.
- **`vector-effect: non-scaling-stroke`** on rooms/grid keeps line weights
  constant under zoom; it's per-element CSS, so it survives the refactor
  untouched — just don't drop it from the copied styles.

---

## 6. Out of scope for this task (mention only)

- Colour-fill-by-attribute mode (department/net-area/dRofus status) is a
  separate, smaller change that layers on `renderLevel`'s polygon class
  assignment — same pattern as the existing `.room.error` highlight. Not part
  of this handover; do multi-zone first since it's the structural change.
- Server-side datum alignment across buildings (see 3.1) — future refinement.
