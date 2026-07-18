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
  Building and level auto-hide when they have ≤1 option and auto-select when
  there's exactly one real choice, so the common single-building dev case
  shows no picker at all. **Project is the exception: it's shown whenever any
  project exists, single option included** (hidden only at zero, where there's
  no name to state). Which project you're looking at isn't a choice, it's the
  scope of everything on screen — and the ≤1 rule left that anonymous exactly
  when it's least obvious: several projects registered but only one holding
  rooms is the normal state while the others are onboarded, since `/projects`
  lists only projects with stored snapshots. The level picker lists floors
  highest-elevation-first (a
  `<select>` has no CSS-driven reversal the old button stack relied on, so
  it's sorted explicitly at render time). A building option the server flags
  `ambiguous` (another building shares its name — legitimate, since buildings
  are distinct by `(code, name)`) renders as "Name (CODE)" so the two options
  are distinguishable; a same-name entry with no code stays the bare name,
  its code-bearing twin carrying the visible distinction.
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
- **Milestone picker.** A header `<select>` sitting immediately after project,
  ahead of building: "Latest"
  (the default, no filter) plus one option per milestone from
  `GET /projects/{id}/milestones`, labelled `name (date)`. Refreshes on the
  same 2s cadence as the project/building pickers, gated by its own
  signature diff; hidden when the project defines no milestones — unlike the
  other pickers' `<=1` rule, "Latest" alone is not a choice worth a picker.
  Selecting one adds `milestone=` to the `/rooms` poll URL (only alongside
  its project — a milestone is a per-project name); a selected milestone
  that disappears (deleted/renamed in settings) falls back to Latest rather
  than keeping a filter the server would answer with nothing. The validation
  badge stays latest-based regardless of the milestone selection (see
  [Server](STRATEGY-SERVER.md)).
- **Colour plans: client-side room colouring, a picker + persisted config.**
  A fifth header `<select>` — "No colour" (flat, the default) plus one option
  per plan from the project's `settings.colour_plans` — lets the viewer colour
  rooms by a per-project, user-authored rule. **All colour math is client-side**
  (`colourForRoom` in `index.html`); the server stores `colour_plans` verbatim
  and computes nothing — the same "axum stays a pure JSON API" line that keeps
  CSV export and QA rendering out of the server. This is also *why* the viewer
  makes its one read of `/api/settings/projects/{id}` here (on project change,
  not every tick — re-fetching would fight the picker): colour plans have no
  other delivery channel, and reusing the settings read endpoint adds zero
  server surface. `ColourPlan.active` sets the picker's default; "No colour"
  always overrides, so it's a default, not a forced application. Palettes are a
  hand-picked JS constant of ColorBrewer schemes (no d3/npm — the page stays a
  zero-build vanilla layer), sampled piecewise-linearly. Fill is applied as an
  inline `style.fill` (a `fill` *presentation attribute* loses to the `.room`
  CSS rule; inline style wins), precedence selected-plan > error highlight >
  default `--fill`; "No colour" leaves the class fill untouched, preserving
  today's look and hover. A room the plan can't colour — missing/unparseable
  property, ratio-by-zero, a value in a gap between bands — renders a "no data"
  grey, never an error. **All three modes are wired:**
  - *property compare* — compare two room properties (`A op B`) → match /
    diverging / bands. The number→colour step (`Colouring`) is kept separate
    from the number-derivation step so a future milestone-compare mode (same
    property across two snapshots) reuses match/diverging/bands untouched.
  - *hierarchy* — categorical hue per parent tier, tint/shade per child. Reads
    each room's server-resolved `classification` path (already on the payload —
    no client re-derivation): `tiers[0]` → a distinct qualitative hue per value
    (Set2/Paired), `tiers[1]` → a lightened tint of it. An undefined parent
    tier → grey.
  - *date-range* — proximity of a date-typed property to `near_date`: after it
    → a fixed blue, at/before → green (near) to red (far), auto-scaled to the
    level's furthest past. Dates parse by an optional strftime `format` — the
    *same* pattern the dRofus date column uses, since Revit room dates originate
    from dRofus (the editor pre-fills it from the project's `date`-typed
    `drofus_fields`) — falling back to native ISO-8601 when omitted; an
    unparseable value → grey.
- **SVG export (per-zone, one file per level).** An "Export SVGs" button on each
  zone's toolbar saves that zone's whole building — one standalone `.svg` per
  level — with no server endpoint, the same "presentation reshuffle of data the
  browser already has" line that kept CSV export and QA/colour rendering
  client-side: the browser already holds the rendered SVG, so exporting is just
  serializing DOM. A second consumer of the render path — `renderLevel` was split
  into a pure `paintLevel(svg, rooms, fitted, …)` painter (reads no zone/global
  state) plus the on-screen `renderLevel` wrapper, so the export and the live view
  can't drift. Each file is fully self-contained: framed to that level's *fitted*
  bounds (not the user's pan/zoom), an embedded `<style>` whose colours are read
  live from the resolved `:root` custom properties (so it never diverges from the
  page and needs no `tokens.css`), an opaque paper background `<rect>`, `xmlns`,
  and an explicit `viewBox`/`width`/`height` — it opens correctly in a bare
  browser tab and in Illustrator/Inkscape. Error highlighting follows the
  validation panel (`showErrors`), which is only on once validation is loaded, so
  an exported "errors" file is never a silent empty highlight; coloured rooms
  carry their resolved fill inline and survive serialization. Filenames are
  self-describing (`roomplan_<project>_<level>[_<milestone>][_errors].svg`). One
  click emits N downloads (browsers prompt once to allow multiple), staggered to
  avoid throttling. All-levels-in-one-file and raster (PNG/PDF) export remain out
  of scope.
- **Hierarchy areas overlay + summary.** A per-zone "Areas" toggle draws the
  server's dissolved gross-area footprints (`GET /projects/{id}/areas`, see
  [Server](STRATEGY-SERVER.md)) on top of the current level, rooms ghosted
  beneath, with a tier picker (Building / Department / …) to choose which tier's
  footprints show. The overlay reuses the render path's transforms and the
  categorical `Set2` palette; footprints are hole-free, so each group is a plain
  `<polygon>` per island (no even-odd path) — a small simplification the
  "discard holes" server decision buys the front end. A Case-A excluded group
  (`counted_upward: false`) reads dashed + faint rather than vanishing. A summary
  panel puts each group's dissolved **footprint** area beside its summed **net**
  room area (computed client-side by shoelace over each room's loops) and their
  **Δ** = wall zones + filled voids, with a per-level total and a cross-level
  total for the tier — the two numbers answer different questions, and their
  difference is itself legible. All client-side, the same "axum stays a pure JSON
  API" line as the colour maths and CSV export: the server ships coordinates and
  areas, the browser draws and tabulates. Fetched **on demand** (on toggle, and
  refreshed when new room data arrives) rather than on the 2s room poll, since
  areas are derived and heavier than a room fetch — the endpoint-vs-poll lifecycle
  call the "Endpoints follow fetch lifecycle" section describes.
- **Settings page (`settings.html`).** A sibling static page, linked from the
  viewer's header, over [Server](STRATEGY-SERVER.md)'s `/api/settings` routes:
  a project-file list on the left (a file that fails to parse still gets a
  row showing its error), a form editor for identity / dRofus source /
  hierarchy / builtin properties / room label / milestones / QA fields /
  colour plans, a dRofus "check" button that dry-runs the CSV path
  server-side, and saves that go through the exact startup validation before
  landing (see Server).
  The dRofus section is a three-way source selector (`none` / `file` /
  `upload`): `file` keeps the path input + check button; `upload` shows a
  drag-and-drop zone (with a file-picker fallback) that POSTs the dropped
  CSV as a raw `text/csv` body to `/projects/{id}/drofus` — deliberately not
  `FormData`/multipart, matching the server's raw-body ingest — plus the
  stored upload history from `GET .../drofus/snapshots` with the live latest
  marked. A success refreshes the QA label dropdowns from the response's
  `labels` (no second call); the upload-mode counterpart of "check" is
  `GET .../drofus/latest`, run on editor open, where a 404 renders as a
  neutral "no upload yet" hint rather than an error. The zone is disabled
  with a "save the project first" hint while the project is unsaved, since
  the endpoint rejects unregistered projects.
  The milestones section edits name/date rows plus per-model pin dropdowns
  whose options are the snapshot ids the server actually stores
  (`GET /projects/{id}/snapshots`); a pin referencing a model or snapshot
  the store no longer has renders visibly as missing rather than being
  silently dropped — removing it is the user's call. Each milestone also
  gets a single **dRofus pin** dropdown (`— current dRofus —` plus one option
  per uploaded dRofus snapshot from `GET /projects/{id}/drofus/snapshots`),
  shown only when the project actually has uploaded dRofus snapshots to
  choose from — a `file`-sourced or upload-less project has nothing to pin,
  so the control is simply absent. The **colour plans** section edits all three
  modes: a name, an active *radio* (the browser enforces the one-active rule the
  server also validates), a mode selector, and mode-specific controls —
  *property compare*: A/B property inputs (datalist of the project's real room
  keys from `/rooms`), op, and colouring sub-mode (match tolerance / diverging
  scheme / add-remove band rows); *hierarchy*: an ordered checklist of the
  project's own hierarchy tiers (parent first) + a qualitative scheme;
  *date-range*: a date-property input, a near-date picker, a scheme, and a
  strftime format input pre-filled from the project's `date`-typed
  `drofus_fields` (blank = native ISO). A plan of a genuinely unknown mode
  (forward-compat) is shown read-only and round-trips unchanged rather than
  being clobbered on save. Same visual
  language as the viewer — once a third sibling page (`comparison.html`) appeared,
  the shared `:root` palette tokens were extracted to `static/tokens.css`
  (`<link>`ed by all three pages), and the two identical settings-API fetch
  helpers (`apiGet`/`apiSend`, used by `settings.html` and `comparison.html`) to
  `static/common.js` — which also now carries the selection-persistence helpers
  (`seedProjectId`/`persistSelection`, loaded by all three pages including the
  viewer; see "Selection persistence" below). Both are served by the same
  `ServeDir`, so it stays a zero-build vanilla layer; page-specific CSS/JS stays
  inline per page.
- **Selection persistence (URL + localStorage).** The three pages are separate
  static documents linked by plain `<a href>`, so a navigation drops all
  in-memory state; previously each reseeded to `projects[0]`, so viewer → settings
  → back reset the user's project. Now the scope pick survives navigation,
  reloads, and bookmarks via two stores with a deliberate precedence, in
  `common.js`'s `seedProjectId` (read) / `persistSelection` (write): **the URL
  query wins** (a bookmarked/deep-linked `?project=…` is authoritative),
  **localStorage is the cross-page fallback seed** (one shared key,
  `roommate.project`, so a pick on any page seeds the others), and the page's own
  `projects[0]` default is the last resort. A restored id is always **validated
  against the live `/projects` list** first — a stale id falls through to the
  default, never a bad fetch. Writes use `history.replaceState` (a selection is
  not a navigation, so it adds no Back-button history). localStorage stores
  **only the project id** (the one selection every page shares); the viewer's
  building/milestone are viewer-specific and per-project, so they ride the **URL
  only** and never seed the other pages. The viewer persists only its **first
  zone** (`zones[0]`) — restoring N independent zone scopes from one URL isn't
  worth the complexity — and its restore also seeds localStorage (parity with the
  editors, whose restore persists via `selectProject`), so a bookmarked viewer
  link carries the project onward. Deliberately kept a small URL/localStorage fix,
  not a router or framework — the STRATEGY trigger for that ("writing the same
  state into several DOM places and watching them drift") isn't met.

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

- **2s-poll re-render cost — resolved.** The viewer used to re-stringify the
  whole payload every 2s to detect change. It now compares a single
  server-computed content `revision` (see [Server](STRATEGY-SERVER.md)), so a
  quiet system triggers no re-render between real pushes; the per-zone tick also
  fetches `/projects` once and runs zones concurrently. Kept here as a pointer
  since earlier notes flagged this as a risk.
- **Viewport culling on pan/zoom — implemented.** SVG clips but does not cull, so
  every room element used to cost per frame regardless of zoom. `paintLevel` now
  records each room's precomputed (Y-flipped) bbox + its nodes as a "cull unit";
  `setViewBox` schedules a `requestAnimationFrame`-throttled `cullZone` that hides
  rooms whose bbox is outside the current view (plus a 20%-of-view margin) and
  shows them again on re-entry, toggling a unit's `display` only when its on/off
  state actually changes. bboxes come from the loop points, never `getBBox` (which
  would force layout). The SVG export deliberately passes no cull-unit array — an
  exported file needs every room. Measured on the 10k-room `big-plate` fixture
  (5,046 rooms/level): a deep zoomed-in pan went from **~595 ms/frame (~2 fps)** to
  **4–15 ms/frame** (only the ~12–40 on-screen rooms drawn), verified to restore
  every room on zoom-out and to leave the export at full room count.
- **Fitted-view cost at very high room counts — still open.** Culling helps only
  when geometry is off-screen; a *fitted* view of a 5,000-room level still paints
  everything (~0.5 s+/frame), so the remaining lever there is level-of-detail
  (drop labels / merge rooms when the whole plate is on screen), not culling. The
  grid is also not yet capped to the visible region — minor next to the rooms, but
  the same idea. Both deferred pending need.
- **Coordinates and units.** Revit internal units are decimal feet, Y-up; SVG
  is Y-down — handled by flipping Y when building geometry. Absolute units do
  not matter while the viewer auto-fits, but they will once dimensions, a scale
  bar, or north-alignment are added. The **placement** half of that is already
  on the wire: a model may carry a `model_to_shared` affine on its envelope (see
  [Index](STRATEGY.md) "The upload envelope") mapping its room points into the
  project's shared/real-world frame. The renderer ignores it today (auto-fit
  needs no absolute placement), but north-alignment, a real-world scale bar, and
  the georeferencing map underlay (Phase 3 — `docs/HANDOVER-georeferencing.md`)
  are exactly the features that consume it. Composing it correctly is a
  browser-side job — the existing Y-flip *plus* the `model_to_shared` matrix
  *plus* (for the underlay) a reprojection into the tile frame — and the server
  stays out of it: it emits the transform as data, the renderer composes the
  picture, consistent with "the server emits geometry as data, the renderer is
  swappable."
