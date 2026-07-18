# Roommate — Server

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Sources](STRATEGY-SOURCES.md) · [Browser](STRATEGY-BROWSER.md) ·
[MCP](STRATEGY-MCP.md)

The Rust/axum process: what it stores, how it derives data at read time, and
how it's configured. Code is a library crate (`lib.rs`) split across `src/`
modules (`contract`, `settings`, `drofus`, `classify`, `state`, `storage`,
`bootstrap`, `service`, `handlers`, `settings_api`) plus two binaries —
`main.rs` (this HTTP server) and `bin/mcp.rs` (see [MCP](STRATEGY-MCP.md)) —
each module carrying its rationale in a header, all with unit tests.

## Implemented

- **Module split.** One `main.rs` refactored into per-concern modules.
  `lookup_property` sits in `contract` (next to the types it inspects) so
  `drofus` and `classify` depend on the contract, not on each other — both the
  dRofus join and the classifier call through this one function, so neither
  assumes a tier or a source. It resolves names through the per-source mapping
  described in [Sources](STRATEGY-SOURCES.md); this doc covers what consumes
  the resolved value.
- **Service layer.** The derive/assemble logic behind the read-side endpoints
  (dRofus join, classification, validation assembly) lives in `service/`, not
  in `handlers`. `handlers` is now a thin Axum adapter layer: extract params,
  call one `service` function, translate the result to HTTP. `service/` never
  imports `axum` — the seam is dependency direction, not a framework — which
  is exactly what let the MCP server ([MCP](STRATEGY-MCP.md)) call the same
  functions `handlers` does without touching this layer at all. Ingest
  (`POST /rooms`, `/rooms/stream`) has no derive logic worth sharing and stays
  entirely in `handlers`. See Superseded/HANDOVER-service-layer.md.

  **Deferred gap:** `service::validation::compute_validation` still resolves
  each room's dRofus link value with its own direct `lookup_property` call
  rather than going through `service::rooms::assemble_room`'s join —
  unchanged from before this extraction (no regression), but it means the
  "future features reuse the join" benefit HANDOVER-service-layer.md
  anticipates for F&E validation isn't wired up yet. Left alone deliberately:
  validation's duplicate-link-value detection and missing-vs-unmatched
  distinction are structurally different from "assemble one room for
  display," so routing through `assemble_room` now would mean either losing
  that distinction or paying for classification/label work validation
  doesn't use — a speculative abstraction with no current payoff.
  `assemble_room` stays private (`rooms.rs`-only) until F&E validation is
  actually being built and its real needs are known; at that point, widen its
  visibility to `pub(crate)` and decide there whether it fits.
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
  whole project is treated as one building. Distinctness is the `(code, name)`
  pair, so two buildings can legitimately share a name (different codes, or
  one resolved a name but no code — a represented state, since a tier resolves
  when *either* property is present); such entries carry `ambiguous: true` so
  a picker that renders names can disambiguate (the viewer appends the code)
  instead of showing two identical options. Nameless entries and the
  Unclassified bucket are exempt from the flag.
- **Identity envelope (v4 → v5).** Every payload carries `project` / `model` /
  `snapshot`; `model` also carries `source` (see
  [Sources](STRATEGY-SOURCES.md)). `SUPPORTED_SCHEMA = 5`, hard-required, no
  transition window. Ids are immutable/keys; names are display-only.
- **Snapshot id: RFC3339 UTC, omittable, echoed back.** The envelope is now
  explicitly the shared *upload envelope* for any future upload type (see
  [Index](STRATEGY.md) "The upload envelope"). `snapshot.taken_at` must parse
  as RFC3339 expressed in UTC (`contract::validate_snapshot_id`, 422
  otherwise — this one rule replaced the old per-character filename checks
  for `taken_at`, since no RFC3339 string can contain `/`, `\`, or `..`, and
  a non-UTC offset would corrupt lexical-max-is-newest ordering). A
  blank/omitted `snapshot` is resolved server-side (`ensure_taken_at`, UTC
  now at the producer's own microsecond precision) *before* validation, in
  both ingest paths; the ingest response carries `snapshot_taken_at` and
  `snapshot_id_generated` so a pusher always learns the id its follow-up
  uploads should attach to. The flag answers "did the server mint this id?",
  not "was a snapshot stored?" (that's `accepted`/`room_count`) — a producer
  that stamps its own `taken_at`, as the Revit one does, sees `false` on every
  successful push. Still v5: a pure relaxation, not a bump.
- **Snapshot history endpoints (`GET /projects/{id}/snapshots`,
  `GET /projects/{p}/models/{m}/snapshots/latest`).** The read side of
  snapshot identity: the first lists every stored snapshot id per model of a
  project (`{ models: [{ id, name, snapshots: [..asc], latest }] }`, soft
  empty for unknown/unregistered projects, same skip-on-read as
  `/projects`); the second answers just the latest id for one model — the
  "what do I attach this follow-up upload to" call — and 404s when there is
  none, since it names one specific resource. Backed by a new
  `SnapshotStore::list_snapshot_ids`: the manifest's `ModelEntry` now indexes
  each model's snapshot ids (`snapshots`, kept sorted, upserted per push), so
  listing history never opens the possibly->100 MB snapshot JSONs. Same
  reconciliation stance as `list_models` — filesystem wins: a file the
  manifest doesn't index (e.g. stored before this field existed) is included
  with a best-effort id recovered from its sanitised filename, a manifest id
  with no file is dropped, both warned. `MemStore` reports just its current
  latest (it keeps no history by design).
- **Multi-model store, keyed.** Snapshots keyed by `(project id, model id)`,
  fixing the multi-document overwrite bug. `/rooms` merges every model's
  latest into one flat payload by default; optional `?project=`/`?building=`
  query params (the latter matched against the same Building tier as above)
  narrow that merge to one project or building. Under an active building
  filter, a project whose hierarchy has no "Building" tier matches *nothing*,
  not everything — the caller asked for a building, and a project with no
  notion of one can't answer that question (a silently ignored filter used to
  leak such a project's entire room set into a filtered multi-project merge;
  `list_buildings`' `tier_configured: false` already tells a well-behaved
  client not to send the combination). A model contributes its
  `levels` only when it contributed at least one matching room when a
  building filter is active — levels are their own array from a separate
  Revit export, so a floor can legitimately have zero rooms of a given
  building right now yet still belong to it; with no filter, every scoped
  model's levels are included exactly as before. Levels are also
  deduplicated across the merge, scoped per project (two projects' "Level 1"
  never collapse into each other): a `Level.id` is only unique *within* its own
  model (same caveat as room ids), so two linked models defining "the same"
  architectural level would otherwise appear twice. Equal `name` and
  `elevation` — elevation compared with the same adaptive-precision rounding
  as the validation report's numeric comparison below, tolerant of
  cross-file float drift — collapse to one canonical level; every
  contributing room's `level_id` is remapped to it before serialization, so
  the level picker and room filtering agree on one id per real-world level.
  A dedicated per-model endpoint is still deferred.
- **Swappable persistence (`SnapshotStore` trait).** `FsStore` writes
  `<root>/<project-guid>/{project.toml, <model-guid>/<ts>.json}` — a two-way
  `project.toml` manifest, upsert-on-push (creates unknown project/model
  structure), full snapshot history (one file per push). The manifest is the
  *index* (readable without opening any snapshot), the snapshot files are the
  record — and list-reads reconcile the manifest against the directory tree,
  with the filesystem winning on disagreement, so a hand-edited or stale
  manifest can't hide models that exist on disk. A re-push with a duplicate
  `taken_at` is skipped with a warning rather than overwriting the snapshot
  it duplicates. `MemStore` keeps the in-memory behaviour (latest-only, no
  history) for `[storage]`-less/dev configs. A database is a future third
  impl behind the same trait.
- **Settings-file-relative paths.** Every relative path inside a settings
  file (dRofus CSV in a per-project file; storage root and test snapshot in
  `server.toml`) resolves against that settings file's own directory, not the
  process's current working directory — so the compiled exe behaves the same
  regardless of where it's launched from.
  (`static/`, served by `ServeDir::new("static")`, is the one exception: it's
  still cwd-relative, so the viewer page itself still needs the exe launched
  from the crate root, or `static/` copied alongside it.)
- **Sample dev config.** `settings/` holds a runnable example: `server.toml`
  (storage root + dev seed), `projects/sample-project.toml` (classification,
  dRofus source, room label — one file per project, see
  Superseded/HANDOVER-per-project-settings.md), a two-row `drofus.csv`, and a
  `test_snapshot.json` (a real v5 payload produced by `post_rooms.py`'s
  `translate()` against `test/Data/rooms.json`/`levels.json`) — `cargo run --
  --server-settings settings/server.toml --project-settings
  settings/projects` seeds and serves it with no manual POST needed.
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
  header in a project settings file.

- **Project display name (`name`).** The settings file is where a project's
  human-readable name is *authored*; `project_id` stays the identity (matched
  against `RoomPayload.project.id`, and a storage path key), so the two can't
  be the same field — an id can't be renamed, a label must be. Optional:
  absent means the project displays under its id, which is what every consumer
  did before the field existed. Non-empty when present, validated at load —
  omitting the key is how you say "no name", so a blank one is a mistake, not
  a way to say it. The name reaches storage the same way it always did, via
  the producer: `/api/settings/projects` carries it, the pusher sends it back
  as `project.name` (see room_mate's `fetch_projects`), and the store's
  `project.toml` manifest mirrors it for `/projects` to serve. So the server
  never reads a name *out* of settings to answer `/projects` — that endpoint
  still reports what was pushed, and a renamed project shows its new name
  after the next push. Unlike ids, names are **not** unique across files:
  consumers that label by name disambiguate collisions themselves (the pyRevit
  picker appends the id, as `list_buildings` already flags ambiguous
  buildings).

- **Settings read/save API + UI (`/api/settings/*`, `static/settings.html`).**
  The per-project TOML files are editable from the browser: a settings page
  (sibling of the viewer, linked from its header) lists every file in the
  projects dir — a file that fails to parse still gets a row carrying its
  error, since this UI is exactly the tool you'd reach for to notice a rotten
  file — and edits identity, dRofus source, hierarchy, builtin properties,
  room label, and QA fields through a form. `settings_api.rs` mirrors the
  handler/service split inside one module: a transport-agnostic core over the
  projects dir (typed `SettingsError`) plus thin Axum adapters
  (`GET/POST /api/settings/projects`, `GET/PUT /api/settings/projects/{id}`,
  and `POST /api/settings/drofus-check`, a dry-run of a dRofus CSV path
  powering the form's "check" button and its label dropdowns). The TOML files
  remain the single source of truth: reads parse them fresh per call (no
  filename bookkeeping in `AppState`), and a save validates the candidate
  through the exact startup pipeline (`bootstrap::load_project_bundle`)
  before installing the file and hot-swapping the in-process registry — a
  file this API accepts can never fail the next boot, and a rejected save
  leaves the existing file untouched. For an `upload`-sourced project that
  validation includes the store: the `drofus_fields` labels are checked
  against the *latest stored CSV* (which is why `load_project_bundle` now
  takes the store), and saving before any upload exists is fine — shape-only
  validation until data arrives. An update cannot rename a project id;
  a second `is_default` file is rejected; saves are serialized end-to-end by
  a lock so the scan-then-write race is structurally impossible. Writes are
  HTTP-only — the MCP binary reuses the core's *read* functions but never
  writes (see [MCP](STRATEGY-MCP.md): separate process, so its write could
  not hot-swap this process's registry). Access control is the `127.0.0.1`
  bind, same trust model as ingest.

- **Data validation report (`GET /projects/{id}/validation`).** First real
  use of the pipeline surfaced a need to audit data quality, not just render
  it. Computed in one pass by the pure `compute_validation` (thin async
  wrapper does the `State`/`Path` extraction, same shape as
  `resolve_label_fields`):
  - Every room's `lookup_property` resolution against the dRofus link
    property (missing → `rooms_missing_link_value`); values grouped to catch
    a link value shared by more than one room (`duplicate_link_values` —
    ambiguous, so excluded from the remaining checks, since a shared link
    can't be uniquely matched to one room); each remaining room's value
    looked up in `DrofusData.by_id` (miss → `rooms_unmatched_in_drofus`).
  - For a hit, every `(dRofus label, Revit property)` pair in the
    `reconciliation` map (see [Sources](STRATEGY-SOURCES.md)) is checked,
    unless that field's `drofus_fields` declaration sets `qa = "ignore"` (see
    Sources), in which case it's skipped entirely — not compared, not listed
    in `field_coverage` either, since that's a deliberate exclusion (e.g. a
    last-synchronised timestamp expected to always differ), not a coverage
    gap.
  - **Comparison is numeric-adaptive, not plain string equality.**
    `contract::numeric_match` parses both sides as `f64` and, if both parse,
    rounds each to the *lesser* of the two raw strings' stated decimal
    precision before comparing — dRofus's `"1.5"` agrees with Revit's
    `"1.49999935417"` (a unit-conversion rounding artifact) because dRofus
    only stated one decimal digit of precision, so disagreement past that
    digit isn't real. Falls back to exact (trimmed) string equality when
    either side isn't numeric, or when the field's `qa` override forces
    `"exact"`. No fixed epsilon anywhere — precision is inferred per
    comparison from the data itself, never configured.
  - **A `type = "date"` field gets a typed comparison of its own**
    (`date_match`): both sides are parsed with the declared strftime pattern
    (`format`, with an optional `revit_format` for when the Revit side
    renders dates differently from the dRofus column) — trying zoned
    datetime, then naive datetime, then bare date (midnight) — and compared
    by what they denote, so two renderings of the same moment don't
    false-flag. Two offset-aware sides compare as instants; a zoned side
    against a naive one compares the zoned side's *local* wall-clock reading
    (the naive writer most plausibly wrote local time); two naive sides
    compare directly. Same fall-back contract as `numeric_match`: if either
    side fails to parse, the comparison drops to the string path — the
    declaration is a hint, not truth.
  - **A string-equality mismatch gets one more check before it's reported:
    has the Revit side already lost the disputed character?** duHast's own
    export step (`Objects/base.py`'s `to_json_utf` → `Utilities/utility.py`'s
    `encode_ascii`) narrows every string to ASCII before it ever reaches this
    service, replacing anything outside `0x00`-`0x7F` with a literal `?` —
    e.g. an en dash arrives as `?`. dRofus keeps the original character, so a
    field that's otherwise identical false-flags on that one glyph alone. On
    a string-equality mismatch (an exact-mode field, the non-numeric
    fallback, or a date field whose values didn't parse),
    `ascii_narrowed` re-runs the comparison with the dRofus side narrowed the
    same lossy way; agreement there means the mismatch was purely an
    artifact of the export's encoding step, not real disagreement. A
    mismatch that merely *contains* a `?` without narrowing to full equality
    still fails. See `Superseded/HANDOVER_utf8.md`.
  - **The dRofus side is normalized the same way the Revit side always
    was:** a blank CSV cell reads as absent, not as a real empty-string value
    to compare against — otherwise a blank dRofus cell would false-flag
    against any real Revit value. A dRofus-side absence isn't tracked
    further: the dRofus export is the source of truth for whether a field
    has a value at all, so a field it never populated isn't this report's
    problem.
  - **Revit-side absence is split into two distinct severities** via
    `contract::PropertyPresence` (`Absent | Empty | Present`), used wherever
    `lookup_property`'s collapsed `Option<String>` isn't precise enough:
    `Absent` (the property was never extracted from Revit for this room at
    all) → `fields_absent_in_revit`, a likely mapping typo or a parameter the
    extractor never wired up, worth flagging loudly as a setup problem;
    `Empty` (the property exists but nobody filled in a value) →
    `fields_empty_in_revit`, an ordinary per-room gap. Both are only reported
    when dRofus actually has a value for that field — nothing on the Revit
    side to compare against yet isn't an error.
  - **`field_coverage`** answers "which dRofus columns does this pass
    actually check" — every `all_labels` entry (see Sources) except
    `qa = "ignore"`-declared ones, each flagged `checked` (present in
    `reconciliation`) with its mapped Revit property when so. Makes the
    previously-implicit "a blank Revit-name cell in row 2 means this column
    isn't checked" convention visible in the running server, not just
    legible from the CSV.
  - `drofus_configured: false` (no dRofus source at all) short-circuits to an
    empty report, not an error, same discipline as `tier_configured` for
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
  Superseded/HANDOVER-gzip.md / Superseded/HANDOVER-streaming.md for the
  full rationale.
  **Honest limitation carried over unchanged:** the streaming handler still
  assembles all rooms into one `Vec` before storing, so it doesn't help if
  even that in-memory room set is too large — the deferred next step is a
  `SnapshotStore::put_streaming` that writes rooms to disk as they arrive.

- **Milestones (`[[milestones]]` in project settings, `GET
  /projects/{id}/milestones`, `/rooms?milestone=`).** A milestone is a named
  date with data snapshots *explicitly pinned* to it (`attachments`: model id
  → snapshot `taken_at`), so the viewer can show the project as captured at
  that milestone instead of each model's latest push. Definitions live in
  the per-project settings TOML — not storage — because they're user-authored
  per-project metadata with the same lifecycle as hierarchy/room_label, and
  riding that file buys the whole save pipeline (validation, atomic install,
  hot-reload) for free; the settings UI edits them like any other section.
  Load-time validation: non-empty unique names (the name is the identity
  `/rooms?milestone=` matches on), a date that parses (`YYYY-MM-DD` or
  RFC3339), every pin a valid snapshot id — but NOT pin *existence*, which
  settings can't see; a pin to since-deleted data is a read-time skip+warn,
  same signal-not-error stance as an unmatched dRofus key. Read semantics
  in `assemble_rooms` follow the building-filter discipline: a project
  defining no milestone of that name contributes nothing, a model the
  milestone doesn't pin contributes nothing, and a pinned model's payload is
  the pinned snapshot loaded via `SnapshotStore::get_snapshot` — substituted
  *before* level dedup / building filter / dRofus join / classification, so
  every downstream step (and the building filter) composes unchanged. A
  milestone can also pin **one dRofus snapshot** (`drofus_snapshot`, the
  optional field beside `attachments`): under that milestone, `assemble_rooms`
  joins the pinned CSV loaded from the store (`get_drofus` +
  `load_drofus_from_bytes`) instead of the project's current dRofus, resolved
  once per project and memoised so an unscoped multi-project `?milestone=`
  merge never cross-joins one project's pinned dRofus onto another's rooms. A
  pin whose snapshot is missing or unparseable falls back to the current
  dRofus with a warning — the same signal-not-error stance as a dangling model
  pin (the room is still served, just joined against current data). This kept
  the milestone substitution on its existing seam: it changes *which*
  `DrofusData` feeds the join, nothing downstream. The one remaining
  deliberate v1 limit: the **validation report stays latest-based** regardless
  of the milestone selection (it resolves its own dRofus link independently —
  see the Service-layer "deferred gap").

- **Colour plans (`[[colour_plans]]` in project settings) — stored verbatim,
  the server computes nothing.** A colour plan is a named, per-project
  room-colouring config the *browser* applies (see
  [Browser](STRATEGY-BROWSER.md)); the server's entire involvement is serde
  round-tripping through the settings save pipeline. It parses no property
  value for colour, computes no colour, and grows no `/colour` endpoint — the
  same "axum stays a pure JSON API" line that kept CSV export and QA rendering
  client-side; the viewer reads the plans via the existing
  `GET /api/settings/projects/{id}`. The one server responsibility is
  **light load-time validation** (`validate_colour_plans`, alongside the other
  settings-only validators in `load_settings`): at most one plan `active`, and
  a `Bands` colouring must be a sorted, disjoint partition (`[lo, hi)`, each
  band's `hi <=` the next's `lo`, open ends only at the extremes) — rejecting
  overlap/out-of-order loudly so the browser can do a simple ordered
  first-match scan; and a date-range `format`, when given, must be a valid
  strftime pattern (same dry-run as `drofus_fields`). Property names are *not*
  validated (source-native, vary — an unresolvable name just renders grey
  client-side, the `room_label` precedent). The mode/colouring enums are internally-tagged struct variants
  (`ColourMode` on `kind`, `Colouring` on `style`), which round-trip through
  toml exactly like `DrofusSource` — verified by `test_settings_toml_round_trip`.

- **Hierarchy gross-area footprints (`GET /projects/{id}/areas`).** The first
  endpoint that does real geometry, not property lookup: it unions room outlines
  into a dissolved footprint per hierarchy group, per level. `service::areas`
  (transport-agnostic, over the `geo` crate) runs a two-stage pipeline per level
  — build each **bottom-tier** group's footprint from its rooms' outer loops
  (union → keep exterior rings only, discarding interior holes → dedup collinear
  vertices), then dissolve child footprints into parents tier by tier up to the
  top. Grouping reuses `classify_room`'s resolved path verbatim (the `undefined`
  bucket is a real group, not a dropped room); the endpoint reuses
  `assemble_rooms` for the scoped, already-classified room set, so `?building=` /
  `?milestone=` scoping and classification come for free. **Islands** (disconnected
  exterior rings — separate wings of one group) are always kept: the result is a
  `MultiPolygon` at every tier. **Holes are discarded at every tier, not just the
  bottom** — unioning two hole-free child footprints can enclose a courtyard that
  belongs to no room, and "enclosed open space counts as area" must hold
  everywhere, so the strip runs after every union (this deliberately corrects the
  design note that said stripping once suffices). Each tier's area is the
  *measured* area of its own dissolved polygon, never a sum of children (which
  would mishandle shared wall zones and filled voids) — so parent area ≠ Σ child
  areas by design. **Exclusions** (`[[hierarchy_exclusions]]` in project settings,
  on `ProjectSettings` since the server uses them — unlike client-only colour
  plans) come in two kinds whose match implies the pipeline stage: a `group`
  match withholds a resolved group from its parent's dissolve (Case A, stage 2 —
  drops from that tier and above, still reported with `counted_upward: false`); a
  `rooms` match drops rooms before any union (Case B, stage 1 — gone from every
  tier including their own group). The number is named an **aggregated room
  footprint** (wall-zone/void-inclusive), *not* net area or a standards gross.
  One computation feeds both asks — the plan-view overlay (rings) and the summary
  table (areas) — so there is no second pipeline. The response carries hole-free
  exterior rings, so the browser needs only `<polygon>`, no even-odd fill dance.
  New geometry dependency: `geo` (`BooleanOps::union`, `MultiPolygon`), the first
  crate that makes the Rust-side geometry-performance argument real rather than
  potential; pairwise union today, `unary_union`/`rayon` held in reserve until
  measurement warrants (STRATEGY.md "Parallelism has a threshold").

- **dRofus upload ingest (`POST /projects/{id}/drofus`) + snapshotted
  storage.** The previously-deferred dRofus-as-snapshotted-source (see
  [Sources](STRATEGY-SOURCES.md) for the source-model side). Raw `text/csv`
  body — the `/rooms/stream` raw-body precedent, no multipart dependency —
  with the snapshot id as `?taken_at=`, resolved/validated/echoed through the
  same contract functions as rooms ingest, and an explicit 32 MB
  `DefaultBodyLimit` (axum's default is a silent 2 MB). **Validate before
  store, order load-bearing:** the CSV is parsed and its labels checked
  against the project's `drofus_fields` *before* `put_drofus` — a stored CSV
  is hydrated at every boot, so accepting a bad one would fail the next
  startup of both binaries. Storage: `<root>/<project>/drofus/<taken_at>.csv`
  (same `:`→`-` filename sanitisation, `.csv` extension), indexed by a new
  `drofus_snapshots` list on the project manifest with the same
  filesystem-wins reconciliation as model snapshots; `drofus/` is a reserved
  name `list_models` explicitly skips (else it would surface as a phantom
  model). Duplicate `taken_at`: skip + warn, reported as `stored: false`.
  The upload core lives in `settings_api` because that's where the mutation
  machinery already is: it runs under the same `SAVE_LOCK` as settings saves
  and shares their `reload_and_swap` tail, so an upload and a save can never
  race or diverge on how a registry is rebuilt — and the freshly-stored CSV
  goes live without a restart iff it is the store's lexical-max latest (an
  older backfill correctly doesn't displace a newer one). Bootstrap
  consequence: the store is constructed *before* the project bundles load,
  and `load_project_bundle` takes it as a parameter, since an
  `upload`-sourced project hydrates its dRofus data from the store. Read
  side: `GET /projects/{id}/drofus/snapshots` (soft-empty listing) and
  `GET /projects/{id}/drofus/latest` (parsed summary, 404 when none) via a
  new `service/drofus.rs`, both also exposed as MCP tools (see
  [MCP](STRATEGY-MCP.md)).

**Deferred (design settled, not built):** snapshot delete UI (the history
*query* now exists — see the endpoints above), per-model / `/hierarchy`
endpoints, DB backend, and an owning level above project. (The
colour-rooms-by-date-proximity viewer feature that used to sit here is now built
as the date-range colour mode — see [Browser](STRATEGY-BROWSER.md) — reading a
room's date property against the plan's own `near_date` / `format`, distinct
from `drofus_fields`' QA-side typed date comparison above.)

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
- **Snapshot id** — a timestamp is the natural key: an RFC3339 date-time in
  UTC, sourced from the export's existing `"date processed"` field so it
  reflects when the model was *read*, not when the server received it. A
  producer with no meaningful read-time may omit it and let the server mint
  one at ingest (receipt time is then the honest semantics) — the ingest
  response reports the resolved id either way.
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
  comparable." **The first half of the datum now exists:** each model may carry a
  `model_to_shared` transform on its envelope (see [Index](STRATEGY.md) "The
  upload envelope") that maps its room points from model space into the project's
  *shared* coordinate system — so the rooms of one project's linked models land
  in one frame. What that does **not** yet give you is a frame shared *across*
  projects: two survey-registered projects in the same CRS become directly
  comparable, but the general cross-project case still needs an explicit
  alignment. The transform is the enabler, deliberately shipped ahead of any
  comparison or map that consumes it (georeferencing Phase 1 — see
  `docs/HANDOVER-georeferencing.md`); nothing numeric depends on it being present
  or correct.

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
