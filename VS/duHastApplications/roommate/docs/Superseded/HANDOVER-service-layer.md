# Handover — Service-Layer Extraction

For: Claude Code (desktop). A working brief for splitting transport from domain
logic so new capabilities (MCP tools, shortest path, F&E, drawings) attach
cheaply. Read alongside [STRATEGY-SERVER.md](STRATEGY-SERVER.md) — this doc is
the *how*; that doc is the *why the server is shaped this way*.

## Goal in one sentence

Extract the derive/assemble logic currently living inside the `/rooms` and
validation handlers into a transport-agnostic `service/` layer, so both the
existing Axum HTTP handlers and a future MCP server call the *same* functions,
and so later features are a new file rather than a change to existing ones.

## Why now (motivation)

Two things are coming that both want the same core logic:

1. **An MCP server**, exposing the read side (list projects, buildings,
   validation, rooms) as tools.
2. **New services down the line** — shortest path, F&E lists + validation,
   possibly drawings. Each should get its own endpoint/tool on its own trigger,
   matching the existing "endpoints follow fetch lifecycle" discipline noted in
   the `handlers.rs` header.

Today the derive logic (dRofus join, classification, validation assembly) is
welded to Axum inside the handler functions — they mix HTTP concerns
(`StatusCode`, `Query` extraction, `Json` wrapping) with the actual computation.
That weld is the only real obstacle to both goals.

## The principle to preserve

**Domain logic never imports a transport crate.** No `axum`, no `rmcp`, no
`StatusCode` inside `service/`. The modularity comes from dependency
*direction*, not from a framework. This mirrors the existing "store raw, derive
late" rule — derivation is already isolated to response assembly, which is
exactly what makes this extraction mostly mechanical.

Do **not** introduce a generic `Service` trait, a plugin registry, or any
speculative abstraction. Keep modules concrete and independent. The win is the
seam, not a framework.

## Target shape

```
src/
  service/
    mod.rs          // re-exports; shared ServiceError
    rooms.rs        // assemble_rooms(&AppState, filter) -> Result<Vec<RoomResponse>, ServiceError>
    validation.rs   // compute_validation(&AppState, project) -> Result<ValidationReport, ServiceError>
    projects.rs     // list_projects(&AppState), buildings(&AppState, project_id)
    // later, one file per capability — none touches the others:
    // pathfinding.rs   shortest_path(&AppState, from, to)
    // ffe.rs           ffe_list(&AppState, project) / ffe_validation(...)
    // drawings.rs
  http/             // Axum adapters: extract params, call service, map error -> StatusCode
  mcp/              // (later) tool defs: parse input, call the SAME service fn, serialize
```

`http/` and `mcp/` are thin adapters. Given a service that returns
`Result<DomainType, ServiceError>`, each adapter only (a) parses its own input
form and (b) translates the result into its own convention.

## The one piece to get right up front: the error type

A shared `ServiceError` enum is what lets both adapters wrap the same functions
without leaking HTTP-isms into the domain layer. Suggested:

```rust
pub enum ServiceError {
    NotFound(String),   // e.g. unknown project id
    BadInput(String),   // e.g. malformed filter
    Internal(anyhow::Error),
}
```

Then each transport maps it:
- HTTP: `NotFound -> 404`, `BadInput -> 400/422`, `Internal -> 500`.
- MCP: into the tool-error shape.

Keep the existing schema-version 422 semantics on ingest intact when the HTTP
adapter maps errors.

## Extraction plan (do in this order)

1. **Add `service/mod.rs` with `ServiceError`** and the transport mappings kept
   *out* of it (the mapping lives in the adapters).
2. **Extract `get_rooms` core → `service::rooms::assemble_rooms`.** Move the
   dRofus join + classification + `RoomResponse` assembly verbatim; leave the
   `Query`/`Json`/`StatusCode` handling in the handler, which now just calls the
   service fn. This is the template — get it clean before doing the rest.
3. **Extract validation → `service::validation::compute_validation`.** Same
   move. Reuse whatever room-assembly the rooms service already exposes rather
   than duplicating the join (F&E validation will want it too).
4. **Extract `projects` / `buildings` → `service::projects`.**
5. **Leave ingest (`POST /rooms`, `/rooms/stream`) in the HTTP layer.** It's a
   poor fit for MCP tools and has no derive logic worth sharing. Only the read
   side needs the service seam.
6. **Confirm handlers are now thin** — each should read as: extract params →
   call one service fn → map result/error. If a handler still contains
   join/classify logic, the extraction isn't finished.

## What this buys the future features

- **Shortest path / F&E / drawings** each become: one `service/` file + one
  route + (optionally) one MCP tool. Adding one never edits the others.
- **Shared inputs stay shared.** Pathfinding needs the same room/adjacency
  assembly; F&E validation reuses the dRofus join. Because that derivation lives
  in `service/` (not in a handler), new services import it directly.
- **Per-feature derived-data lifecycles** (e.g. an adjacency graph that rebuilds
  on ingest rather than per request) have a natural home in the service layer,
  invisible to both transports.

## Constraints / house style

- Add **plenty of annotation** to the Rust code — this project keeps rationale
  in module headers and comments; match that. Every new module gets a `//!`
  header explaining its seam.
- Keep unit tests alongside each module, as the existing `src/` modules do.
- A change touching more than one strategy layer updates every doc it touches;
  if this extraction changes how endpoints are described, update
  STRATEGY-SERVER.md too.

## Definition of done

- `service/` compiles with no `axum`/transport imports.
- Existing HTTP endpoints behave identically (same JSON, same status codes).
- `get_rooms`, validation, projects, and buildings handlers are thin adapters.
- Adding a hypothetical new read capability requires touching only a new
  `service/` file plus its route — demonstrated or at least clearly true by
  inspection.
