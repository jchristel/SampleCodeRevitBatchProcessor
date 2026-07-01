# Roommate — Architecture & Strategy

Notes capturing the design decisions behind the Revit → Rust → browser room
viewer, and the reasoning for where the project goes next. Written as a
reference to come back to, not a spec.

## What exists today

A three-part pipeline, decoupled across a process and a language boundary:

1. **Producer (IronPython / pyRevit).** Extracts room outlines and level data
   from a Revit model, translates them into a versioned JSON contract, and
   POSTs to the local server.
2. **Server (Rust / axum).** Receives the JSON, holds the latest payload in
   memory, and serves it back on request. Also serves the viewer page.
3. **Viewer (browser / SVG).** Fetches the payload, draws room outlines as a
   floor plan, with a level slider to switch floors. Polls every 2s so a fresh
   POST appears without a manual refresh.

The three are coupled only by the JSON contract over `localhost:5151`, not by
the build. Each can evolve independently.

## The core architectural principle: Revit extracts, Rust processes

The guiding split is that the Revit side does **only data extraction** and the
Rust side does **all processing**. The reasoning matters more than the rule:

- **Revit's API is the one thing that cannot be moved or parallelized.** It is
  single-threaded by design and must be called from Revit's main thread, via
  in-process IronPython (Python 2.7 on the CLR — interpreted, effectively no
  JIT for hot loops, no real threading). Whatever touches the live model is
  stuck on the slow side regardless of anything else.
- Therefore the win is to make that side do **as little as possible**: pull raw
  geometry and properties, serialize, hand off. Every piece of logic kept off
  the Revit side is logic that escapes the single-threaded, interpreted
  constraint.
- Rust is the place where the project is free: compiled, multicore (rayon makes
  data-parallel geometry near-trivial at scale), strongly typed, and decoupled
  from a Revit session. Processing server-side means geometry algorithms can run
  without Revit open, be unit-tested in isolation, and reprocess stored payloads
  without re-extracting.

### Disciplines that keep the split clean

- **Keep the extractor dumb on purpose.** Resist computing "just one thing" in
  IronPython because the data is right there. Every computed field there is
  logic in the slow language, untested, and duplicated if Rust needs it too.
  Extract raw inputs (loops, ids, level refs, raw properties); derive everything
  downstream.
- **The contract carries raw data, not interpreted data.** Send coordinates,
  not computed areas. Send level ids and elevations, not pre-sorted orderings.
  The more the JSON is primitives, the less the two sides are coupled to each
  other's assumptions.
- **Version the schema.** Already practised (v1 → v2 when levels became
  first-class). A mismatch then surfaces loudly (HTTP 422) instead of silently
  misrendering.

### A caveat to stay honest about

Moving computation to Rust only speeds up computation that is *in* Rust. The
current pipeline does almost no processing — it deserializes, stores, serves.
The likely real bottleneck on a large model is the Revit extraction itself,
which Rust's speed does nothing for. The Rust performance advantage is
**potential, not yet realised**; it becomes real only when actual heavy geometry
(adjacency graphs, polygon boolean ops, spatial indexing, room merging across
linked models, simplification) is pushed server-side.

**Before optimizing, measure where the seconds actually go** — Revit collection,
transport, or server processing. If extraction is 8 seconds, agonizing over a
50ms Rust algorithm is the wrong end.

Two related notes:

- "Old language" is not the real issue; *interpreted and CLR-hosted* is. The
  reason to reach for Rust is compiled performance plus real threads, not age.
- Parallelism has a threshold. Threading a few hundred rooms can be slower than
  a tight single-threaded loop once overhead is counted. Rayon pays off at scale
  (thousands of independent elements). Measure before parallelizing.

## Transport

Revit add-ins run in-process on .NET. Chosen transport is **HTTP POST to
localhost** — simplest, most debuggable, language-agnostic, and the same
`HttpClient` carries over to a future C# add-in. Alternatives considered:
WebSocket (only if the server needs to push updates back), named pipe (lowest
latency, more fiddly cross-language), file watch (crude but simple). HTTP is the
right default for on-demand room exports.

The cost the split adds is **serialization overhead** — extract, JSON-encode,
send, decode. Almost always worth it for the decoupling, but it is the thing to
measure on a huge model.

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
  selected, full detail on one room for a properties panel.

This also means the processing layer and the endpoint that exposes it tend to
arrive in the same move: add the algorithm, add the endpoint.

## Data model: project → model → snapshot → {levels, rooms}

The moment the server *stores* data rather than relaying it, "the latest
payload" stops being meaningful — latest *for what?* Stored data needs a key
saying which thing each snapshot is a version of. This is the general form of
the multi-document overwrite bug: without identity, two buildings POSTed to the
same server overwrite each other.

The committed hierarchy is **project → model → snapshot(timestamped) →
{levels, rooms}**. Each level earns its place; collapsing two of them forces a
later migration.

- **Project** — the human-meaningful container ("the hospital job"). Stable,
  long-lived, mostly identity + display metadata (name, number, client). Groups
  models that belong together. The level a user thinks in.
- **Model** — a single Revit file. One project routinely has several:
  architectural, structural, linked consultant models, each POSTing
  independently. This is exactly the `pick_document` multi-select case — each
  selected document is a *model* under one *project*. Collapsing model into
  project reintroduces the overwrite bug. The stable Revit identity (model GUID)
  lives here, since a GUID identifies a *file*, not a job.
- **Snapshot** — one timestamped push of one model. This is what makes it a
  *store* rather than a relay. Every export creates a snapshot; the model
  accumulates them. Keeping all (full history) vs. latest-only is a retention
  choice deferrable to later — but snapshot being its own level is what makes
  "this floor as it was last Tuesday" or "what changed since last push"
  *possible* without restructuring.
- **{levels, rooms}** — payload content scoped to a snapshot. Stays together for
  the fetch-lifecycle reason above; the hierarchy over it is about identity and
  versioning, this layer is the geometry.

### Identity

Each level needs its own key, keying downward:

- **Project id** — stable, user-assigned or generated.
- **Model id** — lean on the **Revit model GUID**: stable across renames,
  unique per file. Prefer it over file name (which forks the record on rename).
- **Snapshot id** — a timestamp is the natural key; source it from the export's
  existing `"date processed"` field so it reflects when the model was *read*,
  not when the server received it.
- **Room identity is really *(model, room id)*** — raw Revit room ids are only
  unique within a model, so the same id can appear in two linked models. The
  hierarchy disambiguates them.

Keep **identity** (immutable, machine-chosen — e.g. the GUID) separate from
**display metadata** (mutable — name, number). Tie storage to the id, not the
name, so renaming in Revit does not fork the record.

**Project ids should be globally unique** (a GUID-like key, not "project 1" /
"project 2" scoped to nothing). Globally unique ids let a project be addressed,
compared, or later re-parented under an owning entity without collision or
renumbering — the flexibility is free, so take it even before it is needed.

### Cross-project operations, and whether a top level is needed

Comparing or moving data *between* projects does **not** require a container
above project. Those are *operations across peers*, not evidence of a shared
parent — modelling the verb (compare, move) as a noun (a new level) is the
wrong instinct. A container is justified only when things share a lifecycle or
ownership; "compare A to B" implies neither.

What cross-project operations actually need:

- **Stable, addressable identity per project** — already provided by the project
  id. Comparison and move are functions over two ids:
  `compare(projectA, projectB)`, or a move sourcing from one project id and
  writing to another. Peers reached by id, no nesting.
- **A common coordinate frame, for geometry.** The real subtlety, and *not* a
  hierarchy problem. Each project's rooms sit in their own Revit model space
  (own origin, own rotation). Comparing footprints or moving a room across
  projects is meaningless until they share a datum — a shared survey point or an
  explicit alignment transform between them. No amount of nesting solves this;
  it is a geometry problem that bites anyone assuming "same structure ⇒
  comparable."

**When a top level *is* justified:** a real owning entity emerges — a portfolio,
organization, or client that groups many projects, controls access, or is the
unit queried at ("all rooms across the hospital network"). That is a genuine
container with its own identity and metadata, driven by *organizational* need
(multi-tenancy, access control, rollups), not by the compare/move operations.
Absent that need, the level is dead weight.

The committed structure blocks neither path: cross-project operations can be
added without a new level, and an owning level can be added above project later
without disturbing anything below it — additive, like snapshot history.

### Contract shape (v3)

A pushed payload declares where it sits; the server reads project + model to
find the slot and creates a snapshot under it.

```json
{
  "schema_version": 3,
  "project":  { "id": "...", "name": "Hospital Job" },
  "model":    { "id": "<revit-guid>", "name": "Project1-ARCH" },
  "snapshot": { "taken_at": "2026-05-09T11:13:34Z" },
  "levels": [ ... ],
  "rooms":  [ ... ]
}
```

### Storage shape follows the hierarchy

In-memory first: `Map<ProjectId, Project>` → `Map<ModelId, Model>` → ordered
snapshots. Endpoints address into it (`/projects`,
`/projects/{id}/models`, `/projects/{p}/models/{m}/snapshots/latest`), which is
where "endpoints follow fetch lifecycle" pays off — the hierarchy gives the URL
structure for free. This is also where the in-memory `Mutex<Option<Payload>>`
becomes a keyed map, and later a real datastore if persistence across restarts
is wanted.

### Commit to the shape, implement incrementally

The *structure* is the decision now; the *machinery* can lag. Sensible first
step: project + model keying with snapshot = latest-only (one payload per model,
overwritten). That immediately fixes multi-model overwrite and matches where
`pick_document` already is. Full snapshot history (keep the list, query by time)
is added when history is actually wanted — and because snapshot is already its
own level, that addition is additive, not a migration. **Persistence** (a
database, retention, surviving restarts) is a bigger, separate step than keying
by project; add it only when a snapshot must outlive the process. Let the
live-model testing indicate whether it is needed.

## Open items / things to watch

- **Extraction is the dominant cost (measured).** ~840 rooms exported in ~11s
  (~13ms/room) — normal-to-good for Revit boundary extraction, and almost
  entirely Revit API time: single-threaded on Revit's main thread because it
  must be. Serialization, POST, and server storage are milliseconds against
  this. Confirms the "measure where the seconds go" principle: the seconds are
  in extraction, which Rust's speed does **not** touch. Freeing consequence:
  server-side processing can be written for clarity, not speed — it runs against
  an 11s baseline it cannot move. The real optimization axis for the slow side
  is **extracting less or incrementally** (fewer params, skip unneeded rooms,
  pull only changed rooms since the last snapshot — which the snapshot hierarchy
  leaves the door open for), *not* server-side speed or language choice. Only
  worth attacking if near-live updates while modeling are wanted.
- **Multi-document overwrite.** The server stores only the latest POST
  (last-write-wins, in-memory). Selecting several models in `pick_document`
  leaves only the last one visible. Fine for the POC; merging instead of
  replacing is a deliberate server-side change if multiple linked models should
  be viewed together.
- **Payload size and the 2s poll on large models.** The viewer re-stringifies
  the whole payload every 2s to detect change. On a big building that diff plus
  re-render may feel sluggish; cheap fixes are a longer interval or a small
  fingerprint (room count + hash) instead of full stringify.
- **Room ↔ level join.** Each room's `level.id` must match an `id` in the level
  export. A mismatch surfaces as rooms landing on a fallback level named by raw
  id — a useful signal that the two collectors saw different model state.
- **Level ordering source.** The slider orders by the level export's
  `elevation` field (real elevations, in mm), not by `offset_from_level` (the
  room's offset from its level, which was always 0.0 and useless for ordering).
- **Coordinates and units.** Revit internal units are decimal feet, Y-up; SVG
  is Y-down — handled by flipping Y when building geometry. Absolute units do
  not matter while the viewer auto-fits, but they will once dimensions, a scale
  bar, or north-alignment are added.

## Current contract (v2)

```json
{
  "schema_version": 2,
  "levels": [
    { "id": "311", "name": "Level 0", "elevation": 0.0 }
  ],
  "rooms": [
    {
      "id": "324772",
      "name": "Room 1",
      "level_id": "311",
      "loops": [
        { "points": [ { "x": 0.0, "y": 0.0 } ] }
      ]
    }
  ]
}
```

Convention: `loops[0]` is the outer boundary, `loops[1..]` are holes.
