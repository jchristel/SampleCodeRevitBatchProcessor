# Roommate — Server

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Sources](STRATEGY-SOURCES.md) · [Browser](STRATEGY-BROWSER.md)

The Rust/axum process: what it stores, how it derives data at read time, and
how it's configured. Code is split across `src/` modules (`contract`,
`settings`, `drofus`, `classify`, `state`, `storage`, `handlers`, `main`), each
carrying its rationale in a module header, all with unit tests.

## Implemented

- **Module split.** One `main.rs` refactored into per-concern modules.
  `lookup_property` sits in `contract` (next to the types it inspects) so
  `drofus` and `classify` depend on the contract, not on each other — both the
  dRofus join and the classifier call through this one function, so neither
  assumes a tier or a source. It resolves names through the per-source mapping
  described in [Sources](STRATEGY-SOURCES.md); this doc covers what consumes
  the resolved value.
- **Classification hierarchy.** N-tier `[[hierarchy]]` from settings,
  validated at startup (a tier naming neither `code_property` nor
  `name_property` is a startup error, and duplicate tier names are also a
  startup error — needed once a tier name like `"Building"` is looked up by
  name, not just position). Resolves a full-depth path per room with latching
  `undefined` fill once a tier runs out of data — never a truncated path, so a
  partially-classified room stays visualizable rather than dropped. Resolved
  fresh per request, not cached. No general `/hierarchy` endpoint yet
  (deferred), though the "Building" tier now has its own consumer — see below.
- **Project/building selection (`GET /projects`, `GET /projects/{id}/buildings`).**
  A single physical building is often split across multiple models (a subset
  of levels each, sometimes even split within one level), so the viewer needs
  to scope its view to one building's worth of models rather than everything
  ever pushed. Building has no identity or storage of its own — it's the
  hierarchy tier literally named `"Building"`, resolved via the same
  `classify_room` every room already goes through. `/projects` lists distinct
  projects across `all_snapshots()`; `/projects/{id}/buildings` resolves that
  tier for every room in a project and returns the distinct values (plus an
  "Unclassified" bucket for rooms where it didn't resolve), each keyed by an
  opaque token the browser echoes back rather than reconstructing. No tier
  named "Building" configured → `tier_configured: false`, not an error: the
  whole project is treated as one building.
- **Identity envelope (v4 → v5).** Every payload carries `project` / `model` /
  `snapshot`; `model` also carries `source` (see
  [Sources](STRATEGY-SOURCES.md)). `SUPPORTED_SCHEMA = 5`, hard-required, no
  transition window. Ids are immutable/keys; names are display-only.
- **Multi-model store, keyed.** Snapshots keyed by `(project id, model id)`,
  fixing the multi-document overwrite bug. `/rooms` merges every model's
  latest into one flat payload by default; optional `?project=`/`?building=`
  query params (the latter matched against the same Building tier as above)
  narrow that merge to one project or building. A model contributes its
  `levels` only when it contributed at least one matching room when a
  building filter is active — levels are their own array from a separate
  Revit export, so a floor can legitimately have zero rooms of a given
  building right now yet still belong to it; with no filter, every scoped
  model's levels are included exactly as before. A dedicated per-model
  endpoint is still deferred.
- **Swappable persistence (`SnapshotStore` trait).** `FsStore` writes
  `<root>/<project-guid>/{project.toml, <model-guid>/<ts>.json}` — an
  authoritative, two-way `project.toml`, upsert-on-push (creates unknown
  project/model structure), full snapshot history (one file per push).
  `MemStore` keeps the in-memory behaviour for `[storage]`-less/dev configs. A
  database is a future third impl behind the same trait.
- **Settings-file-relative paths.** Every relative path inside `settings.toml`
  (dRofus CSV, storage root, test snapshot) resolves against the settings
  file's own directory, not the process's current working directory — so the
  compiled exe behaves the same regardless of where it's launched from.
  (`static/`, served by `ServeDir::new("static")`, is the one exception: it's
  still cwd-relative, so the viewer page itself still needs the exe launched
  from the crate root, or `static/` copied alongside it.)
- **Sample dev config.** `settings/` holds a runnable example: `settings.toml`,
  a two-row `drofus.csv`, and a `test_snapshot.json` (a real v5 payload
  produced by `post_rooms.py`'s `translate()` against
  `test/Data/rooms.json`/`levels.json`) — `cargo run -- --settings
  settings/settings.toml` seeds and serves it with no manual POST needed.
- **Configurable room labels (`room_label`).** An ordered list of property
  names, resolved into `RoomResponse.label: Vec<String>` at response assembly
  so the viewer never hardcodes which fields it shows (see
  [Browser](STRATEGY-BROWSER.md)). `"$name"`/`"$id"` are intrinsic tokens for
  `Room`'s own fields (`lookup_property` only reads `room.properties`, so
  these can't go through it); anything else resolves through the exact same
  canonical/source mapping dRofus and classification already use. Defaults to
  `["$name", "$id"]` — today's label — so omitting the setting changes
  nothing. An unresolvable name just contributes nothing to that room's
  label, no startup validation needed. **Footgun worth knowing:** in TOML, a
  bare `key = value` after an opened `[[array-of-tables]]` section (like
  `[[builtin_properties]]`) attaches to that array's *last entry*, not back
  to the top-level table — and since `BuiltinPropertyDef` doesn't reject
  unknown fields, a misplaced `room_label` line is silently swallowed with no
  error. Top-level `Settings` keys must be declared before the first section
  header in `settings.toml`.

- **Data validation report (`GET /projects/{id}/validation`).** First real
  use of the pipeline surfaced a need to audit data quality, not just render
  it. Four checks, computed in one pass by the pure `compute_validation`
  (thin async wrapper does the `State`/`Path` extraction, same shape as
  `resolve_label_fields`): every room's `lookup_property` resolution against
  the dRofus link property (missing → `rooms_missing_link_value`); values
  grouped to catch a link value shared by more than one room
  (`duplicate_link_values` — ambiguous, so excluded from the remaining checks,
  since a shared link can't be uniquely matched to one room); each remaining
  room's value looked up in `DrofusData.by_id` (miss →
  `rooms_unmatched_in_drofus`); and for a hit, every `(dRofus label, Revit
  property)` pair in the newly-retained `reconciliation` map (see
  [Sources](STRATEGY-SOURCES.md)) compared between the two sides, trimmed
  string equality, recorded as a `PropertyMismatch` on disagreement — either
  side missing a value is skipped (absence, not disagreement, a different
  problem). `drofus_configured: false` (no dRofus source at all) short-circuits
  to an empty report, not an error, same discipline as `tier_configured` for
  buildings.

- **Gzip request decompression + streaming NDJSON ingest.** FFE exports run
  >100 MB uncompressed. Two independent, composable changes: (1)
  `RequestDecompressionLayer` (tower-http) inflates any `Content-Encoding: gzip`
  request body before it reaches a handler — transparent, so an uncompressed
  sender still works unchanged, and neither `ingest_rooms` nor the JSON
  contract needed to change at all. (2) A new `POST /rooms/stream` reads the
  body as line-delimited JSON (NDJSON: line 1 is `StreamEnvelope` — everything
  in `RoomPayload` except `rooms` — every following line is one `Room`)
  instead of buffering the whole body with `Json<RoomPayload>`, so peak memory
  is one line, not the entire payload; rooms are still accumulated into a
  `Vec` before handing the assembled `RoomPayload` to the same
  `state.set_snapshot` the buffered path uses, so storage stays identical —
  only *parsing* is streamed. The buffered `/rooms` route now also carries an
  explicit `DefaultBodyLimit` (previously unset, silently capped at axum's
  2 MB default) sized well above the largest expected export, since
  `DefaultBodyLimit` measures the *decompressed* size; `/rooms/stream`
  disables the limit entirely and relies on streaming instead. See
  HANDOVER-gzip.md / HANDOVER-streaming.md for the full rationale.
  **Honest limitation carried over unchanged:** the streaming handler still
  assembles all rooms into one `Vec` before storing, so it doesn't help if
  even that in-memory room set is too large — the deferred next step is a
  `SnapshotStore::put_streaming` that writes rooms to disk as they arrive.

**Deferred (design settled, not built):** snapshot-history query + delete UI,
per-model / `/hierarchy` endpoints, DB backend, an owning level above project.

## Data model: project → model → snapshot → {levels, rooms}

The moment the server *stores* data rather than relaying it, "the latest
payload" stops being meaningful — latest *for what?* Stored data needs a key
saying which thing each snapshot is a version of. Without identity, two
buildings POSTed to the same server overwrite each other — the multi-document
overwrite bug, since resolved (see Implemented).

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
  the fetch-lifecycle reason in [Browser](STRATEGY-BROWSER.md); the hierarchy
  over it is about identity and versioning, this layer is the geometry.

### Identity

Each level needs its own key, keying downward:

- **Project id** — stable, user-assigned or generated. Should be **globally
  unique** (a GUID-like key, not "project 1" scoped to nothing) — that lets a
  project be addressed, compared, or later re-parented under an owning entity
  without collision or renumbering, at no cost to take now.
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
Absent that need, the level is dead weight. The committed structure blocks
neither path: cross-project operations can be added without a new level, and an
owning level can be added above project later without disturbing anything below
it — additive, like snapshot history.

### Storage shape

Sketched as a nested `Map<ProjectId, Project>` → `Map<ModelId, Model>` →
ordered snapshots, so future endpoints (`/projects`,
`/projects/{id}/models`, `/projects/{p}/models/{m}/snapshots/latest`) get their
URL structure for free. **As shipped, this diverges deliberately in two ways:**
(1) the store keys on a *flat* `(project, model)` tuple, not the nested map —
simpler, fixes the overwrite bug equally, and nesting only earns its place once
endpoints actually address projects and models as separate resources; (2) `GET
/rooms` merges every stored model into one flat payload so the current viewer
keeps working unchanged — a stopgap that flattens stored identity (raw room ids
collide across models), replaced by `/projects/{p}/models/{m}` once the UI
addresses one model. Both are additive to fix later, not migrations.

## Missing tier data is a first-class state, not an error

The project has two "mismatch" cases where a reference that *should* resolve
*doesn't*, and both are diagnostic signals that two data sources disagreed:
the room↔level mismatch (a room's `level_id` has no match in the level export
— see [Sources](STRATEGY-SOURCES.md)) and the dRofus key mismatch (a room's
link key is present but absent from the dRofus map — also
[Sources](STRATEGY-SOURCES.md)). Missing classification tier data looks
similar but is the *opposite* case: nothing disagreed, the room is simply
classified only partway down — expected, incomplete-by-design, not a broken
reference. So the rule: **assign the room to the highest tier it has data for,
and set every tier below to an explicit `undefined`**, never a truncated path.
Surfacing partial classification is a purpose, not a side effect — "which
rooms aren't fully classified yet" is exactly the useful view while a
classification scheme is still being built out.

**Staleness caveat:** resolved classification is a cache over a static
definition plus the current snapshot — once rooms re-push or dRofus re-polls
mid-session, it must recompute, the server-side twin of the dRofus join's own
staleness note.
