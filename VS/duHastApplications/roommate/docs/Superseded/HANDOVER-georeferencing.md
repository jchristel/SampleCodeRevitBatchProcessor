# HANDOVER — Georeferencing & Map Underlay

Adds the ability to place a project's rooms in a real-world coordinate frame,
and (as a later, purely visual phase) to draw a mapping-service image behind the
room plan as an underlay.

This is a **separate** track from HANDOVER-units. It shares the `geo_reference`
field that units work introduces on the envelope, but nothing here blocks the
units work shipping first. Read HANDOVER-units for the envelope/schema
conventions; this doc only adds to them.

The headline: because of two facts confirmed about how these projects are
actually built (below), the map underlay goes from "contingent and fiddly" to "a
straightforward later phase resting on a transform we want anyway." **Do not
start by building the underlay.** Build the transform (phase 1); it earns its
place on cross-model comparison grounds alone, and the underlay (phase 3) rests
on it.

> **Status (2026-07-19): Phase 1 has landed.** ✅ The `model_to_shared` transform
> is on the envelope end-to-end (server + producer), tested and shipped. Phases 2
> and 3 remain as described. Two things worked out differently from the sketch
> below once the actual exporter was read — both noted inline in the Phase 1
> section: (a) the transform is read **once per model** directly from the
> document's `ProjectLocation`, so the per-room-equality ingest guard proved
> unnecessary; (b) the affine's row/column mapping was pinned down from source
> (rotation is stored as basis-vector rows). See `docs/STRATEGY.md` "The upload
> envelope" for the shipped contract and the plan file for the full record.

---

## The two facts everything here depends on

Both were confirmed against how these Revit models are actually produced. They
are **load-bearing assumptions** — write them into the contract as explicit,
opt-in declarations, never infer them, because a project that violates them
still produces perfectly self-consistent (but wrong) geometry with no error
anywhere.

**Fact 1 — the model→shared transform is constant per Revit model.** Each room
polygon currently carries a translation+rotation matrix mapping its points into
the project's *shared coordinate system*. That relationship (model space →
shared space) is one-per-model; the per-room matrix is the *same* matrix
repeated on every room. So it is really a **model-level fact**, and belongs on
the envelope, not smeared across rooms (see "Phase 1").

**Fact 2 — shared coordinates are usually survey-registered to a real CRS.**
These projects are usually set up from a survey, and the survey declares the
mapping system (e.g. MGA2020 Zone 54). So the shared coordinate frame *is* grid
coordinates in the declared CRS — not merely an internal datum near the origin.
This is the fact that makes a map underlay actually placeable: it closes the
"where does this frame sit on the Earth" gap without any extra tie-point.

**The catch on Fact 2:** "usually" is doing load-bearing work, and the server
**cannot verify it**. If a project modelled near origin and set `crs` anyway,
every transform still runs, the reprojection still runs, and you get a map
underlay confidently drawn in the wrong hemisphere with no error raised. Two
consequences, both non-negotiable:

- The georeference must be an **explicit per-project opt-in** ("this project's
  shared coordinates are real MGA2020"), never inferred from the presence of a
  matrix or a `crs` string.
- The underlay must stay **advisory and visual only**. Nothing numeric (area,
  comparison, validation) may ever depend on it being correct. A mis-registered
  project produces a wrong *picture*, never wrong *data*. (Same discipline
  HANDOVER-units applies to the sanity band: detect, decorate, never corrupt.)

---

## Why the transform, not "origin + rotation scalars"

An earlier sketch was going to put `origin_easting` / `origin_northing` /
`rotation_deg` on `GeoReference`. **Drop that.** The model→shared matrix (Fact 1)
already carries origin *and* rotation, applied — it's strictly more faithful
than re-deriving two scalars pyRevit would have to compute anyway. So:

- `GeoReference` stays a **thin label** — just `crs` (and the opt-in flag,
  below). It does not carry placement math.
- The **placement math lives in the model→shared transform on the envelope**,
  which exists independently of georeferencing (comparison needs it too — see
  STRATEGY-SERVER "common coordinate frame": each project's rooms sit in their
  own model space until they share a datum). The transform earns its place on
  **two** independent grounds, so add it even before the underlay exists.

---

## Phase 1 — hoist the model→shared transform to the envelope  ✅ LANDED

**This is the only phase worth doing now.** It's useful with or without any map.

> **As shipped.** `ModelToShared { matrix: [f64; 6] }` in `contract.rs`, added as
> an optional `#[serde(default)] model_to_shared` on **both** `RoomPayload` and
> `StreamEnvelope` (no schema bump — still v5). Ingest *warns* (never rejects) on
> `|det|` drift from 1. The producer (`room_mate.py`) reads the transform **once
> per model** from `doc.ActiveProjectLocation` via duHast's
> `get_coordinate_system_translation_and_rotation`, reduces it to the 2D affine
> (`post_rooms.py::coordinate_system_to_affine`), and stamps it on the envelope;
> `translate_room` drops the now-redundant per-polygon copy. The affine mapping,
> pinned from source: rotation is returned as basis-vector **rows**, so
> `a,b = row0.x, row0.y`, `c,d = row1.x, row1.y`, `e,f = origin.x, origin.y`.

pyRevit currently emits the matrix per-room. Change it to emit **once per
model**, on the envelope. On the server:

```rust
/// The affine transform mapping a model's room points from Revit model space
/// into the project's SHARED coordinate system. One per model (Fact 1: it's the
/// same matrix on every room — a model-level relationship, not a per-room one),
/// so it rides the envelope, not each polygon.
///
/// This exists for TWO independent reasons: (a) it puts every room in a model
/// into one common frame, which cross-model comparison needs regardless of maps
/// (STRATEGY-SERVER "common coordinate frame"); (b) when the project is
/// survey-registered (Fact 2 / GeoReference), shared space IS grid space in the
/// declared CRS, which is what makes a map underlay placeable. It carries NO
/// unit conversion — see HANDOVER-units, geometry is never converted; this is a
/// rigid-body placement, not a scale.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ModelToShared {
    /// 2D affine as [a, b, c, d, e, f]: shared_x = a*x + c*y + e,
    /// shared_y = b*x + d*y + f. Rotation+translation from Revit's shared
    /// coordinates; the linear part is a pure rotation (no scale/shear), so
    /// |det| ≈ 1 — a useful ingest sanity check.
    pub matrix: [f64; 6],
}
```

Add it to **both** `RoomPayload` and `StreamEnvelope` (they stay in lockstep, as
with the units fields). Make it **optional** (`#[serde(default)]` →
`Option<ModelToShared>`): a model that doesn't declare one is un-placeable but
still renders fine via auto-fit, exactly as today. No schema bump — pure
additive relaxation, same reasoning as the units fields.

**Ingest check (turns "should be constant" into "provably constant"):** if
pyRevit still sends the matrix per-room during transition, validate on ingest
that every room's matrix is equal, and reject (422, specific message) if they
disagree — a per-room divergence means the "one frame per model" invariant is
violated and something unexpected is going on (linked models with their own
transforms?). Once pyRevit emits once per model, this check is moot but cheap to
keep as a guard against a regressing exporter. Also sanity-check |det| ≈ 1
(pure rotation) and warn — not reject — if it drifts, since a scaled matrix
would silently distort placement.

> **What shipped instead.** The per-room-equality guard was **not built**, and
> deliberately so. The transform never reaches the wire per-room: the producer
> reads it once from the document's `ProjectLocation` (a single model-level
> fact — each linked model is pushed as its own model with its own transform),
> so there is no per-room copy to diverge and nothing for the server to
> reconcile. What *did* ship is the `|det| ≈ 1` warn (`is_rigid`, tolerance
> `1e-6`), in both ingest paths — advisory only, exactly as specified.

**Convention note:** this is transport-agnostic contract + validation — lives in
`contract.rs` / service side, not in handlers or mcp.rs. Inline tests: matrix
round-trips, per-room-equality check passes on equal / fails on divergent,
|det| check.

---

## Phase 2 — the georeference opt-in in project settings

`GeoReference` (introduced by HANDOVER-units) stays thin but gains the explicit
opt-in that Fact 2's catch demands:

```rust
pub struct GeoReference {
    /// The datum/zone as the producer names it, e.g. "MGA2020-54". Opaque to
    /// the server — recorded, echoed, and used only to pick a reprojection
    /// definition on the underlay path. Never parsed for math server-side.
    pub crs: String,

    /// Explicit assertion that this project's SHARED coordinates are real
    /// coordinates in `crs` (Fact 2) — i.e. the survey registered them. MUST be
    /// set deliberately (per-project opt-in), NEVER inferred from the presence
    /// of a matrix or crs string: a project modelled near origin with crs set
    /// anyway would otherwise draw a map in the wrong hemisphere silently. When
    /// false/absent, the project can still be labelled with its crs but no
    /// aligned underlay is offered.
    #[serde(default)]
    pub survey_registered: bool,
}
```

Surface `crs` and `survey_registered` in `settings.html` and the settings-API
read path (and MCP `get_project_settings`, which reuses the settings core),
alongside the units fields. This is display + declaration only — no ingest
behaviour changes in this phase.

---

## Phase 3 — the map underlay (later; purely visual)

Only viable when a model has a `ModelToShared` (phase 1) **and** its project is
`survey_registered` (phase 2). Otherwise: no underlay offered, plan renders as
today.

### The easy 80%: fetch and draw

The transform chain is fully determined once the two preconditions hold:

```
room point (feet, Y-up, model space)
  → ModelToShared.matrix            → shared coords = grid coords in `crs`
  → reproject (crs → EPSG:3857)     → Web Mercator metres
  → Protomaps (PMTiles)             → basemap tiles, rendered client-side
  → draw behind the SVG room layer, same viewport
```

**Provider decision: Protomaps only.** The underlay is served as
[Protomaps](https://protomaps.com) — a single **PMTiles** archive (all tiles in
one file, served over HTTP Range requests from any static host or object store,
no tile-server process) rendered client-side. This is the one provider to build
against; the earlier "static-map vs XYZ/WMTS, commercial vs government WMTS"
menu is closed. It fits the project ethos: open, self-hostable, keyless when the
PMTiles file is served locally, Web Mercator (EPSG:3857) like every other XYZ
scheme.

Two consequences of the choice, both to accept deliberately:

- **The basemap is OSM-derived *vector*, not aerial imagery.** Protomaps'
  flagship basemaps are streets/buildings/labels styled in the browser — a
  schematic map, not a photo. The doc's earlier lean toward "government aerial
  WMTS" is dropped with this decision. If aerial photography is ever actually
  wanted, that's a *different* data source (a raster PMTiles archive you build,
  or another provider) — call it out then; it is not what "Protomaps" gives you.
- **It renders through a map library, not a bare `<image>`.** Vector PMTiles
  need a renderer — MapLibre GL JS (via the `pmtiles://` protocol plugin) or
  `protomaps-leaflet`. So the underlay is not literally an `<image>` sibling of
  the room `<path>` layer; it is that library's canvas/WebGL surface, positioned
  behind the room SVG and **kept in viewport lockstep** with it (see "the hard
  20%"). This is heavier than the single-script `proj4js` include — an honest
  cost against STRATEGY-BROWSER's no-build/vanilla ethos, and the main reason the
  underlay stays a clearly-scoped, independently-toggleable later phase.

### The hard 20%: don't hand-roll these

- **Reprojection is real geodesy.** `crs` (MGA2020 / GDA2020 / UTM) → Web
  Mercator is a proper transform. Browser side: `proj4js`. Do **not** approximate
  it — at building scale the error is visible. This is one of **two** new browser
  dependencies the underlay adds — `proj4js` (small, a single script include,
  consistent with STRATEGY-BROWSER's no-build/vanilla ethos) and the Protomaps
  renderer (heavier — see the provider note above).
- **Three coordinate frames in one viewport.** Room polygons are feet, Y-up;
  SVG is Y-down (already handled by the existing Y-flip — STRATEGY-BROWSER
  "Coordinates and units"); the underlay is metres, Web Mercator, Y-down.
  Seating model space onto the map = the existing Y-flip *plus* the
  ModelToShared matrix *plus* the reproject *plus* a scale/translate into the
  SVG viewport. Get the composition order right and test it against one known
  real-world building before trusting it.
- **Two renderers, one camera.** Because Protomaps draws to its own
  canvas/WebGL surface (not an SVG `<image>`), the composition above isn't a
  one-time transform — it must run on *every* pan/zoom to keep the map library's
  camera locked to the SVG viewport. The room SVG stays the source of truth for
  interaction; the map is a slaved layer whose centre/zoom/bearing are recomputed
  from the SVG viewport each frame (the reproject makes zoom levels and the
  ModelToShared rotation makes bearing non-trivial). This viewport-lockstep is
  the single biggest integration risk in the underlay and the reason it's a
  standalone phase.
- **The underlay is non-load-bearing.** Reassert the Fact-2 discipline in code:
  the underlay layer must be independently toggleable and its failure (bad
  tile fetch, mis-registered project, reprojection error) must degrade to "no
  underlay," never break the room render or touch any number.

---

## Open questions to resolve before Phase 3

1. **Which CRSs must be supported?** MGA2020 has multiple zones (49–56 for AU);
   confirm the set these projects actually use so the reprojection defs are
   bundled. Adding a zone is a proj4 definition string, not code.
2. ~~**Provider + credentials.** Static-map vs tiles; commercial (Mapbox /
   MapTiler) vs government WMTS.~~ **Decided: Protomaps only** (see Phase 3). The
   residual sub-questions the choice leaves open:
   - **Which PMTiles archive, hosted where?** A whole-country basemap is
     gigabytes; a per-project city/region extract is far smaller. Decide the
     extent and whether the roommate server serves the `.pmtiles` file itself
     (Range-request friendly) or it lives on separate static hosting. If
     Protomaps' *hosted* API is used instead of a self-hosted file, that
     reintroduces an API key to surface to the browser — prefer self-hosted to
     keep it keyless.
   - **Which renderer?** MapLibre GL JS (`pmtiles://` protocol) for full vector
     styling, vs the lighter `protomaps-leaflet`. This trades bundle weight
     against styling control and sets how the viewport-lockstep (above) is wired.
   - **Vector styling, or build a raster PMTiles?** The default is a vector OSM
     basemap; an aerial-imagery look would require sourcing/building raster
     PMTiles — only if genuinely needed.
3. ~~**Does pyRevit already expose the shared-coordinate transform cleanly?**
   Confirm it can emit the model→shared matrix once per model (Revit
   `ProjectLocation` / shared coordinates expose it). Phase 1's per-room-equality
   check is the safety net during transition, but the target is emit-once.~~
   **Resolved (Phase 1):** yes — duHast's
   `get_coordinate_system_translation_and_rotation(doc)` returns it directly from
   `doc.ActiveProjectLocation`, so the producer emits once per model with no
   transition period and no equality safety-net needed.

---

## Conventions (from CODING-CONVENTIONS.md)

- **Annotate the "why":** every field above carries its rationale — especially
  *why* `survey_registered` is opt-in and *why* the underlay is non-load-bearing.
  Keep that; these are exactly the decisions a future reader can't recover from
  the code.
- **Signal, not error:** an un-placeable model (no matrix, or not
  survey-registered) is a represented state → no underlay, render as today; not
  a failure. A divergent per-room matrix, by contrast, *is* a hard 422 (a broken
  invariant, not a missing-optional).
- **Dependency direction:** the transform + validation are transport-agnostic
  (contract/service). The underlay + `proj4js` are browser-only — they never
  reach the server; the server emits geometry + transform + crs as data and the
  renderer composes the picture (STRATEGY-BROWSER: "the server emits geometry as
  data, the renderer is swappable").
- **No schema bump:** all additions default/optional — a pre-georeference
  payload stays valid and unchanged in meaning.
- **Inline tests** at the bottom of each touched module.
