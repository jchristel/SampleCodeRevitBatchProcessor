# Roommate — Architecture & Strategy

Notes capturing the design decisions behind the Revit → Rust → browser room
viewer. Written as a reference to come back to, not a spec. Split across four
docs along the pipeline's own boundaries, so each can be read (and changed)
without pulling in the other two:

- **This doc** — the pipeline overview, the core split principle that governs
  all three layers, and the current wire contract they all share.
- **[Sources](STRATEGY-SOURCES.md)** — everything that supplies raw data:
  the Revit/pyRevit producer and dRofus (today's only external reference
  source). What each extracts, its raw format, and how the server reconciles
  property names across sources.
- **[Server](STRATEGY-SERVER.md)** — the Rust/axum process: data model,
  storage, classification, settings.
- **[Browser](STRATEGY-BROWSER.md)** — the SVG viewer: rendering strategy,
  UI growth path, endpoint design from the fetch side.

A change that touches more than one layer (the v5 property rework did all
three) should update every doc it touches — that's the cost of the split, and
worth it for how much easier each doc is to read in isolation the rest of the
time.

## What exists today

A three-part pipeline, decoupled across a process and a language boundary:

1. **Producer (IronPython / pyRevit).** Extracts room outlines and level data
   from a Revit model, translates them into a versioned JSON contract, and
   POSTs to the local server. Declares which producer it is (`model.source`,
   e.g. `"revit"`) so the server can resolve property names correctly if a
   second source (e.g. IFC) ever joins Revit. Details: [Sources](STRATEGY-SOURCES.md).
2. **Server (Rust / axum).** Receives the JSON, holds every model's latest
   payload keyed by `(project, model)`, persists it (or holds it in memory),
   and serves it back on request. Also serves the viewer page. Details:
   [Server](STRATEGY-SERVER.md).
3. **Viewer (browser / SVG).** Fetches the payload, draws room outlines as a
   floor plan, with a level slider to switch floors. Polls every 2s so a fresh
   POST appears without a manual refresh. Details: [Browser](STRATEGY-BROWSER.md).

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
- **Version the schema.** Practised through v1 → v5 so far. A mismatch surfaces
  loudly (HTTP 422) instead of silently misrendering.
- **Ids and `ElementId` values are 64-bit ints at the source, strings in the
  contract.** Revit 2024+ made `ElementId` 64-bit (`Int64`); IronPython 2.7 can
  truncate a large id across the CLR boundary, especially via the deprecated
  32-bit `IntegerValue`, which fails silently with a wrapped number rather than
  an error. Rule: read `.Value` and `str()` it at extraction, never touch
  `IntegerValue`; the contract carries `id`, `level_id`, and any
  ElementId-storage custom property as `String` for exactly this reason. Rust
  parses to `i64` only where it actually needs the number, where the width is
  safe.

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
50ms Rust algorithm is the wrong end. (Measured: ~840 rooms in ~11s, ~13ms/room,
almost entirely Revit API time — see [Sources](STRATEGY-SOURCES.md).)

Two related notes:

- "Old language" is not the real issue; *interpreted and CLR-hosted* is. The
  reason to reach for Rust is compiled performance plus real threads, not age.
- Parallelism has a threshold. Threading a few hundred rooms can be slower than
  a tight single-threaded loop once overhead is counted. Rayon pays off at scale
  (thousands of independent elements). Measure before parallelizing.

## Current contract (v5 — shipped)

```json
{
  "schema_version": 5,
  "project":  { "id": "p1", "name": "Hospital Job" },
  "model":    { "id": "<revit-guid>", "name": "Project1-ARCH", "source": "revit" },
  "snapshot": { "taken_at": "2026-05-09T11:13:34Z" },
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
      ],
      "properties": {
        "Number": { "value": "101", "storage_type": "String" },
        "Area": { "value": "25.5", "storage_type": "Double" },
        "d_dept_code": { "value": "D02", "storage_type": "String" }
      }
    }
  ]
}
```

Convention: `loops[0]` is the outer boundary, `loops[1..]` are holes. Room
`properties` is one flat map keyed by the producer's own raw property names —
why it's shaped this way, and how the server reconciles names across sources,
is in [Sources](STRATEGY-SOURCES.md). The `(project.id, model.id)` pair is the
store key; ids are immutable, names are display-only — see
[Server](STRATEGY-SERVER.md) for the full data model. On the `/rooms`
*response* (not the push), each room additionally carries a `drofus` sub-object
when its link key matched, and a `classification` path — both derived at
response assembly, never stored (see Server and Sources respectively).
