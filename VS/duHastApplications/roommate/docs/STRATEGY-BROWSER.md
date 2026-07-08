# Roommate — Browser

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Sources](STRATEGY-SOURCES.md) · [Server](STRATEGY-SERVER.md) ·
[MCP](STRATEGY-MCP.md)

The SVG viewer: how it renders, how it's expected to grow, and how the fetch
side should shape future server endpoints.

## Implemented

- **SVG floor-plan rendering.** Draws room outlines per level from the
  `/rooms` payload.
- **Header scope pickers: project, building, level.** Three `<select>`s in the
  header row, right of "Room Plan" — project and building (see
  [Server](STRATEGY-SERVER.md)'s `/projects`/`/projects/{id}/buildings`), and
  the level picker moved here from its former floating panel over the canvas.
  Each auto-hides when it has ≤1 option and auto-selects when there's exactly
  one real choice, so the common single-project/single-building dev case shows
  no pickers at all. The level picker lists floors highest-elevation-first (a
  `<select>` has no CSS-driven reversal the old button stack relied on, so
  it's sorted explicitly at render time).
- **Scoped polling.** `poll()` builds `/rooms`'s URL from the current
  project/building selection every tick; project/building pickers themselves
  refresh on the same 2s cadence (gated by a shallow id-list diff so they
  don't fight an in-progress selection), which is also how a newly-pushed
  project or building shows up without a page reload.
- **Room labels: configurable, always-rendered, correctly layered.** `addLabel`
  renders `room.label` (the server-resolved, ordered field list — see
  [Server](STRATEGY-SERVER.md)'s `room_label` setting) instead of hardcoding
  `room.name`/`room.id`; the first field is the large primary line, any
  further fields stack below as smaller accent-colored lines, generalizing
  the old fixed two-line layout to however many fields are configured. Two
  bugs fixed alongside this: (1) labels no longer silently disappear on small
  rooms — the old `fontSize < baseFont * 0.25` cutoff (a floor-wide threshold
  that dropped a label outright rather than just shrinking it) is gone; a
  label now always renders clamped to fit its own room, however small, and
  zoom can't recover a dropped label anyway since panning/zooming never
  re-invokes rendering. (2) `renderLevel` now appends every room's polygons
  in one pass, then every room's labels in a second pass — SVG has no
  reliable z-index (paint order is DOM order, full stop), so the old
  per-room interleaved loop let a later room's opaque polygon paint over an
  earlier room's label whenever their screen-space boxes were anywhere
  close, which got worse on bigger plans with more rooms.
- **Data validation panel: badge, highlighting, CSV export.** A header badge
  (`⚠ N`, `✓`, or hidden when dRofus isn't configured) toggles a right-anchored
  side panel listing [Server](STRATEGY-SERVER.md)'s six dRofus health checks
  (missing/duplicate link values, unmatched-in-dRofus, property mismatches,
  and the two Revit-side presence checks, `fields_absent_in_revit` /
  `fields_empty_in_revit`), plus an always-shown, non-error **field
  coverage** section (which dRofus columns this pass actually checks, and
  against which Revit property). Coverage is built and rendered separately
  from the issue sections specifically so it survives the "No issues found"
  collapse instead of disappearing with it, and it stays out of the badge
  count — it's a config reference, not a data-quality problem. Fetched only
  when the project selection changes or via the panel's own Refresh button —
  deliberately not on the 2s room poll, since this is an on-demand check, not
  something to watch update live. Two things layered on top, both entirely
  client-side: (1) rooms with any issue (across all six checks) get a
  distinct fill (`.room.error`, a new `--error` CSS variable) *only while the
  panel is open* — `showErrors` toggles with the panel's visibility and
  triggers a `refit: false` re-render, so opening/closing it never disturbs
  the current pan/zoom. (2) A "Download CSV" button builds a `room_id,error`
  CSV directly from the already-fetched report (one row per issue, so a room
  with several issues appears several times) and triggers a browser download
  — no server endpoint for this, matching "keep axum a pure JSON API": a CSV
  is just a presentation reshuffle of data the browser already has.

## Rendering: SVG today, and when to move

SVG is the current choice and is likely right for a long time.

- **SVG stays correct** for more vector primitives — annotations, dimension
  lines, tags, highlighted adjacencies, overlays, clickable/hoverable regions —
  in the hundreds to low thousands of elements. Every element is a real DOM
  node, so hit-testing, hover, click, CSS styling, and accessibility come for
  free. This is why labels and tooltips were trivial to add.
- **The wall is the DOM**, not the feature set. Performance degrades somewhere
  in the low tens of thousands of elements (layout/repaint of a huge DOM).
  SVG also has no render loop — it is retained-mode, so continuous animation
  (dragging, live cursor feedback) fights the model.

The escalation tiers, if ever needed:

- **Canvas 2D** — immediate-mode, handles far more shapes, natural for
  draw-on-top with a render loop. Cost: lose DOM-given interactivity; rebuild
  hit-testing (point-in-polygon), hover, styling by hand.
- **WebGL / GPU** (PixiJS, regl, deck.gl-style) — hundreds of thousands of
  elements at 60fps. Real complexity; overkill unless genuinely at that scale.

The trigger to move is **not** "draw shapes on top" (well within SVG's comfort
zone) but **element count on screen** or **a need for continuous animation**.
Because the server emits geometry as data, the renderer is swappable without
touching the server or extractor — so this decision can be deferred until real
usage demands it. For many architectural-plan cases it never does.

## UI growth: toward a richer browser tool

Goal is a richer browser tool run locally (not a desktop app). The strategy:

- **Keep axum as a pure JSON API. This is the load-bearing decision.** The
  server emits data over HTTP, never HTML, and never assumes what the UI looks
  like. Holding this line keeps every later choice reversible and local.
- **Grow the vanilla JS until it actually hurts** — and that takes longer than
  expected. More endpoints, a properties panel on click, filters, search,
  synchronized views can all be plain DOM against the current setup. The real
  signal to adopt a framework is not a feature but a feeling: manually writing
  the same state into several DOM places and watching them drift. Adopting one
  earlier is toolchain overhead for no payoff.
- **When it hurts, the fork is JS framework vs. Rust+WASM.** Behind axum, either
  a JS framework (Svelte gentlest, React most-supported) or a Rust+WASM one
  (Leptos / Dioxus). The project tilts toward **Leptos / Dioxus**: the Rust
  `Room` / `Level` / processed-geometry structs can be reused directly in the
  UI, eliminating the recurring friction of re-describing a carefully versioned
  contract in TypeScript. The trade is a smaller ecosystem and fewer ready-made
  components — a fair deal for a single-developer tool valuing one language and
  shared types end to end.

### Endpoints follow fetch lifecycle, not data type

As capabilities are added, give each its own **purpose-shaped endpoint** rather
than overloading `/rooms`. When processing arrives, `/rooms` stays raw geometry
and new endpoints (`/adjacencies`, `/levels/{id}/analysis`, etc.) carry the
derived data. Small endpoints mean any future frontend composes them freely, and
no presentation assumption gets baked into the data layer.

The principle is **not** "one endpoint per data type" — it is "one endpoint per
thing fetched independently, on its own schedule, by its own consumer." The
test: *would this ever be fetched on a different trigger, or be expensive enough
that it shouldn't sit in the default payload?*

- **No → keep it in the snapshot.** Levels are a worked example: the viewer needs
  levels and rooms *together*, in the same render pass, from the same POST. They
  share a lifecycle (one export, one payload, one fetch). Splitting them would
  mean two requests that always travel together, recombined client-side, with a
  race between them — cost, no benefit. Levels stay inside the payload.
- **Yes → own endpoint.** Derived/computed data that is recomputed on a
  different trigger, sized differently, or consumed by a different part of the
  UI: an adjacency graph, per-level analysis fetched only when a level is
  selected, full detail on one room for a properties panel. `/projects` and
  `/projects/{id}/buildings` are a shipped example: they're fetched on a
  different schedule (a picker changing) than the room render, by a different
  consumer (the header, not the SVG canvas) — so they earned their own
  endpoints rather than riding inside `/rooms`.

This also means the processing layer and the endpoint that exposes it tend to
arrive in the same move: add the algorithm, add the endpoint. dRofus and
classification (see [Server](STRATEGY-SERVER.md) and
[Sources](STRATEGY-SOURCES.md)) are worked examples of the "no" branch that
already shipped: both are joined/resolved at `/rooms` response assembly rather
than given their own endpoint, because today they still share the viewer's
render pass. Each is a candidate for its own endpoint (`/drofus`, `/hierarchy`)
the moment it starts refreshing on a different trigger (a live dRofus poll) or
serving a different consumer (a hierarchy browser) than the room render.

## Open items / things to watch

- **Payload size and the 2s poll on large models.** The viewer re-stringifies
  the whole payload every 2s to detect change. On a big building that diff plus
  re-render may feel sluggish; cheap fixes are a longer interval or a small
  fingerprint (room count + hash) instead of full stringify.
- **Coordinates and units.** Revit internal units are decimal feet, Y-up; SVG
  is Y-down — handled by flipping Y when building geometry. Absolute units do
  not matter while the viewer auto-fits, but they will once dimensions, a scale
  bar, or north-alignment are added.
