# Roommate — Sources

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Server](STRATEGY-SERVER.md) · [Browser](STRATEGY-BROWSER.md)

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
- **dRofus loader + join.** Two-header-row CSV read once at startup into a
  keyed map (`by_id: BTreeMap<String, DrofusRecord>`); joined onto rooms at
  `/rooms` response assembly as a separate `drofus` sub-object, leaving the
  stored snapshot raw. `File` variant behind a `#[serde(tag = "type")]` enum,
  ready for an `Api` variant later with no other consumer touched. Row 2's
  non-link columns are also retained now, as `reconciliation: BTreeMap<String,
  String>` (dRofus field label → the Revit property it corresponds to) — see
  [Server](STRATEGY-SERVER.md)'s data validation report, the first real
  consumer of the "kept for reconciliation" data below.
- **Transport: HTTP POST to localhost.** Revit add-ins run in-process on .NET;
  POST is simplest, most debuggable, language-agnostic, and the same
  `HttpClient` carries over to a future C# add-in. Alternatives considered:
  WebSocket (only if the server needs to push updates back), named pipe
  (lowest latency, more fiddly cross-language), file watch (crude but simple).
  The cost the split adds is **serialization overhead** — extract, JSON-encode,
  send, decode — almost always worth it for the decoupling, but the thing to
  measure on a huge model.

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
  data. Row 2's other columns are the Revit param names those fields
  correspond to, kept for reconciliation — now actually retained and used
  (see Implemented above), not just parsed and discarded.

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
