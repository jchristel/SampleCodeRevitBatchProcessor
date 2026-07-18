# Roommate — Sources

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Server](STRATEGY-SERVER.md) · [Browser](STRATEGY-BROWSER.md) ·
[MCP](STRATEGY-MCP.md)

Everything that supplies raw data into the pipeline: the Revit/pyRevit
producer, and dRofus (external reference data, today's only other source).
Two different origins, same discipline — extract raw, let the server
interpret. See the [Index](STRATEGY.md) for the "Revit extracts, Rust
processes" principle and its disciplines (extract-dumb, ElementId
stringification, schema versioning), which apply to every source, not just
Revit.

## Implemented

- **Room properties: a flat, source-native map (v5).** `Room.properties:
  Map<String, { value, storage_type }>` — one bag per room, keyed by whatever
  property name the producer's own source uses. Replaces the original v3
  typed `builtin`/`custom` split, which assumed Revit's parameter set was a
  fixed, guaranteed schema — an assumption that stops holding the moment a
  second source (e.g. IFC, whose property sets are optional and
  exporter-dependent) becomes plausible. `CustomValue::as_f64` does lazy,
  best-effort numeric coercion, content-first, hint-guided.
- **Settings-driven canonical property mapping.** `[[builtin_properties]]`
  (`canonical`, `by_source: {source → raw name}`) resolves a stable name like
  `"Area"` to the right raw property name per producer, without a Rust code
  change — the seam that matters once names diverge across sources (a second
  producer, or a non-English Revit UI). No entry for a name/source falls back
  to matching the name verbatim, which is exactly today's single-source
  behaviour. Implemented server-side (`settings.rs`, `contract.rs`'s
  `lookup_property`; see [Server](STRATEGY-SERVER.md)), but it exists entirely
  because sources vary — that's why it's documented here.
- **`model.source`.** Every payload declares which producer created it (e.g.
  `"revit"`) — the key the mapping above resolves against. A plain string, not
  a closed Rust enum: adding a source is a settings-file change, not a
  recompile.
- **dRofus loader + join.** Two-header-row CSV read into a keyed map
  (`by_id: BTreeMap<String, DrofusRecord>`); joined onto rooms at `/rooms`
  response assembly as a separate `drofus` sub-object, leaving the stored
  snapshot raw. The `#[serde(tag = "type")]` source enum now has **two
  variants**: `File { path }` (read from disk once at startup — the original
  behaviour, unchanged) and `Upload` (data arrives via browser/HTTP upload,
  stored as timestamped snapshots — see the next bullet); an `Api` variant
  later still slots in with no other consumer touched. The loader itself is
  **byte-source-agnostic** (`load_drofus_from_reader`, with path and bytes
  wrappers; the bytes path strips a leading UTF-8 BOM, which Excel CSV
  exports routinely carry and the csv crate does not strip) — which source
  feeds it is dispatched in `bootstrap::load_project_bundle`, where the
  store is in scope. Row 2's non-link columns are also retained, as
  `reconciliation: BTreeMap<String, String>` (dRofus field label → the Revit
  property it corresponds to) — see [Server](STRATEGY-SERVER.md)'s data
  validation report, the first real consumer of the "kept for
  reconciliation" data below.
- **dRofus as an uploaded, snapshotted source (`type = "upload"`).** The
  previously-deferred item. A project declaring `[sources.drofus] type =
  "upload"` takes its dRofus data from `POST /projects/{id}/drofus` (raw
  `text/csv` body, drag-and-drop on the settings page or any HTTP client);
  each accepted upload is stored as a dated snapshot in the `SnapshotStore`
  (`<root>/<project>/drofus/<taken_at>.csv` — see
  [Server](STRATEGY-SERVER.md)), the latest one hydrated at startup and
  hot-swapped in after each upload. The snapshot id rides the shared upload
  envelope's rules via `?taken_at=` (see [Index](STRATEGY.md)). A project
  with the upload source but no upload yet is a legitimate "not configured
  yet" state (`drofus_configured: false` downstream), not a startup error —
  its `drofus_fields` get shape-only validation until the first CSV supplies
  a label set. This is also the storage groundwork milestones need to pin
  dRofus data (the pinning itself is still deferred).
- **Per-column dRofus type/QA declarations (`drofus_fields`).** One
  declaration per dRofus column — `label` (matches row 1), an optional `type`
  (`string` default, `numeric`, or `date`), an optional `format` (required,
  and only meaningful, when `type = "date"` — a chrono strftime-style
  pattern, since dRofus hands dates back as formatted text, e.g.
  `"6/29/2026 5:01:01 PM +10:00"`, not a structured value), an optional
  `revit_format` (a second strftime pattern for the *Revit* side of a date
  comparison, when the room property renders dates differently from the
  dRofus column — absent means `format` covers both sides), and an optional
  `qa` override (`exact` forces string comparison even when both sides parse
  as numbers; `ignore` excludes the column from comparison *and* the
  coverage report entirely). Deliberately **one** table answering "what is
  this column," not two: the QA override started life as its own standalone
  list (`drofus_field_overrides`/`CompareMode`) until a colour-rooms-by-date
  feature idea came up that needs to actually parse a column's type, not
  just skip it in QA — a second, separate "what is this column" table would
  only have drifted from the first, so the override was folded into this
  more general per-column declaration instead. `type`/`format`/`revit_format`
  now have their first consumer: [Server](STRATEGY-SERVER.md)'s validation
  report parses a `date`-declared column's values with the declared
  pattern(s) and compares the parsed instants instead of the raw strings
  (the colour-rooms-by-date viewer feature that motivated typing the column
  is still unbuilt). Everything is validated at startup: a `date` field
  needs a `format`, a `format`/`revit_format` on anything else is almost
  certainly a mistake, each pattern must be a valid strftime string, and
  every `label` must actually exist in the loaded CSV.
- **Transport: HTTP POST to localhost.** Revit add-ins run in-process on .NET;
  POST is simplest, most debuggable, language-agnostic, and the same
  `HttpClient` carries over to a future C# add-in. Alternatives considered:
  WebSocket (only if the server needs to push updates back), named pipe
  (lowest latency, more fiddly cross-language), file watch (crude but simple).
  The cost the split adds is **serialization overhead** — extract, JSON-encode,
  send, decode — almost always worth it for the decoupling, but the thing to
  measure on a huge model.
- **Snapshot id is the producer's to state, the server's to fill.** The
  upload envelope's `snapshot.taken_at` (an RFC3339 UTC date-time — see
  [Index](STRATEGY.md) "The upload envelope") may be omitted, in which case
  the server mints one at ingest and reports it in the response. The Revit
  producer keeps supplying its own deliberately: its timestamp says when the
  model was *read*, which receipt time can't. A future upload type with no
  meaningful read-time just leaves it blank.
- **Gzip + NDJSON streaming push (`post_rooms.py`).** FFE exports run >100 MB
  uncompressed, too large to hold as one JSON string client-side or buffer
  whole server-side. `post_payload_stream` (the path `room_mate.py` actually
  calls) never builds a second full `rooms` list or one giant `json.dumps`
  string: it gzip-compresses a line-delimited stream — one envelope line
  (`build_envelope`), then one line per room, translated (`translate_room`)
  and written as each is read off the duHast export — straight to
  `POST /rooms/stream`. Peak memory is therefore one room, not the whole
  export (see [Server](STRATEGY-SERVER.md)'s matching streaming-ingest note).
  The older fully-buffered `translate()`/`post_payload` pair (whole payload in
  one dict, one `StringContent` POST to `/rooms`) is kept only because it's
  what regenerates `settings/test_snapshot.json` and suits small/manual
  pushes — `translate()` is now `build_envelope` + a loop over
  `translate_room`, so both paths share one translation, not two to keep in
  sync.
- **The model→shared transform is stamped on the envelope, not per room.** The
  duHast export carries the shared-coordinate placement on *every* geometry
  object (`DataGeometryBase.translation_coord` / `rotation_coord`), but it's one
  document-level `ProjectLocation` fact repeated. `room_mate.py` reads it once
  per model (`get_coordinate_system_translation_and_rotation(doc)`), reduces it
  to the 2D affine, and puts it on the envelope as `model_to_shared` (see
  [Index](STRATEGY.md) "The upload envelope"); `translate_room` therefore
  deliberately drops the per-polygon copy, keeping room geometry raw model-space
  points. Because it rides the envelope, the streaming path carries it on line 1
  with no per-room scan. Georeferencing Phase 1 — see
  `docs/HANDOVER-georeferencing.md`.

## Why sources need reconciling, not just parsing

A typed `BuiltinProperties` struct (v3) made sense while Revit's Room schema
was the only schema: Revit guarantees a fixed set of built-in parameters on
every Room, so a non-`Option` typed field was a correct, not just convenient,
model. That guarantee is *not* transferable to a second source. IFC property
sets (Psets) are optional and exporter-dependent — the same concept (e.g.
area) can live in `Pset_SpaceCommon.NetFloorArea` from one tool, be named
differently, or be absent from another. So "guaranteed present" stops being
true even for what feels like a core field.

That's why the wire shape moved to one flat, source-native map, with
reconciliation pushed to a settings-driven, per-source name table rather than
Rust types: a second source is a settings-file change (a new `by_source` entry
per canonical property, keyed by that source's name), not a new struct field.
The tradeoff is real — `properties.builtin.area: f64` was a compile-time
guarantee; a flat map with a runtime-resolved name is not — but that guarantee
was never something IFC (or any second source) could actually promise, so
keeping it in the type system was enforcing a fiction.

## Reference: dRofus CSV format

The dRofus export is CSV, not JSON — the one input that isn't machine-JSON,
since it's a dRofus-side export in its native tabular form:

```
DrofusRoomId,   NetArea,     Department,  ...   ← row 1: dRofus property names
RevitDrofusKey, d_net_area,  d_dept,      ...   ← row 2: matching Revit param names
<key value>,    <value>,     <value>,     ...   ← row 3+: data
```

The two header rows are the join spec and must both be retained:

- **Row 2, column 0** names the Revit room property whose *value* holds the
  dRofus id — the link, constant for the whole file, read once at load.
- **Row 1** is the dRofus field labels — the display layer for the joined
  data, and retained in full as `DrofusData.all_labels` regardless of
  whether row 2 mapped a given column (needed so [Server](STRATEGY-SERVER.md)'s
  coverage report can show an unmapped column as "not checked" rather than
  omitting it silently). Row 2's other columns are the Revit param names
  those fields correspond to, kept for reconciliation — now actually
  retained and used (see Implemented above), not just parsed and discarded.

The link is a direct value match and dRofus ids are unique, so the loader
builds a flat `Map<String, DrofusRecord>` — no collision handling needed.

**Design notes on the join:**

- **Store raw, join late.** The parsed map sits in server state; it's attached
  at `/rooms` assembly, never at load — keeps `/rooms` the raw-geometry
  endpoint and leaves the Revit snapshot untouched.
- **Separate sub-object, not merged into `properties` — a lifecycle
  decision.** dRofus will eventually be polled mid-session for fresh data,
  independent of the Revit push. Fusing it into `properties` would couple two
  different-lifecycle things into one bag; a separate sub-object keeps the
  seam where that future refresh boundary actually is.
- **Unmatched key is a signal, not an error.** A room with no linking value
  just gets no dRofus data. A key present on the room but absent from the map
  is a useful mismatch — the two exports saw different model state, same
  diagnostic role as the room↔level join below.

## Open items / things to watch

- **Extraction is the dominant cost (measured).** ~840 rooms exported in ~11s
  (~13ms/room) — normal-to-good for Revit boundary extraction, and almost
  entirely Revit API time: single-threaded on Revit's main thread because it
  must be. Serialization, POST, and server storage are milliseconds against
  this. The real optimization axis for the slow side is **extracting less or
  incrementally** (fewer params, skip unneeded rooms, pull only changed rooms
  since the last snapshot — the snapshot hierarchy leaves that door open), not
  server-side speed or language choice. Only worth attacking if near-live
  updates while modeling are wanted.
- **Room ↔ level join.** Each room's `level.id` must match an `id` in the level
  export. A mismatch surfaces as rooms landing on a fallback level named by raw
  id — a useful signal that the two collectors saw different model state.
- **Level ordering source.** The viewer's slider orders by the level export's
  `elevation` field (real elevations, in mm), not by `offset_from_level` (the
  room's offset from its level, which was always 0.0 and useless for
  ordering).
