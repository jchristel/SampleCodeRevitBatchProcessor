# Roommate — MCP

Part of the Roommate strategy docs: [Index](STRATEGY.md) ·
[Sources](STRATEGY-SOURCES.md) · [Server](STRATEGY-SERVER.md) ·
[Browser](STRATEGY-BROWSER.md)

A second front door onto the same stored room/dRofus data: an MCP (Model
Context Protocol) server, so any MCP-aware client (Claude Desktop, Claude
Code, or another agent host) can call the read side as tools instead of
issuing HTTP requests. This exists because [Server](STRATEGY-SERVER.md)'s
`service/` extraction made the derive/assemble logic transport-agnostic —
this doc is what that extraction bought: a second adapter that was a new
binary plus tool definitions, not a rewrite. See HANDOVER-service-layer.md
for the extraction itself.

## Implemented

- **Separate binary, shared lib crate.** The crate is now `lib.rs` (every
  domain module: `contract`, `settings`, `drofus`, `classify`, `state`,
  `storage`, `service`, `handlers`, plus the new `bootstrap`) plus two bins:
  `main.rs` (the Axum HTTP server) and `bin/mcp.rs` (this MCP server). Neither
  bin's transport crate leaks into the other — `mcp.rs` never imports `axum`,
  `main.rs` never imports `rmcp` — the same "dependency direction is the
  seam" principle `service/` already applies, taken one layer further out.
  `bootstrap::build_state` (settings file → running `AppState`: load
  settings, load dRofus, validate `drofus_fields`, pick the storage backend,
  seed dev/test data) is shared verbatim by both binaries' `main()` so they
  can't drift on that wiring.
- **`rmcp` (the official Rust MCP SDK), stdio transport.** `RoommateMcp` in
  `bin/mcp.rs` holds a `Shared` (`Arc<AppState>`) plus the `#[tool_router]`-
  generated `ToolRouter`. Each tool method deserializes its params (via
  `Parameters<T>`, `T: Deserialize + schemars::JsonSchema` — the JSON schema
  an MCP client sees is derived from the struct, never hand-written),
  calls exactly one `service::` function, and serializes the `Serialize`
  result straight into a `CallToolResult` text block — the same discipline
  as the Axum handlers, just for a different wire format. Logging goes to
  **stderr only**: stdout is the JSON-RPC stream, and anything else written
  there (an errant `println!`, a stdout-default `tracing_subscriber`)
  silently corrupts the protocol.
- **Four tools, one per existing read route:** `list_projects`,
  `list_buildings`, `get_rooms` (project/building filters optional),
  `get_validation`. Ingest (`POST /rooms`, `/rooms/stream`) has no MCP
  counterpart — an LLM pushing a full room snapshot isn't a realistic flow,
  and the HTTP server remains the only ingest path.
- **`ServiceError` → `McpError` mapping.** `NotFound`/`BadInput` both become
  `McpError::invalid_params` (MCP's tool-call error surface has no direct
  404/400 split); `Internal` becomes `McpError::internal_error`. Required
  giving `ServiceError` real `Display`/`Error` impls (previously `Debug`-only,
  since nothing needed to stringify it before this).
- **`RoomsResult` gained `#[derive(Serialize)]`.** The HTTP handler had never
  serialized it directly — it hand-built a `json!` from its fields to omit
  `store_empty` from the wire shape. The MCP tool returns `RoomsResult`
  as-is, `store_empty` included: there's no MCP equivalent of the HTTP 204
  that field exists to drive, so it's just a plain field in the JSON payload
  instead of a transport-level signal.
- **`Implementation::from_build_env()` reports the wrong crate.** It's a
  plain function whose body bakes in `env!("CARGO_PKG_NAME"/"CARGO_PKG_VERSION")`
  at *rmcp's own* compile time, not the caller's — using it made `initialize`
  report `serverInfo: {"name": "rmcp", "version": "2.1.0"}` instead of ours.
  Confirmed via a manual stdio smoke test (raw JSON-RPC `initialize` piped
  into the compiled binary). Fixed with
  `Implementation::new("roommate-mcp", env!("CARGO_PKG_VERSION"))` instead —
  worth remembering if a future `rmcp` upgrade tempts reverting to the
  SDK-provided helper.
- **Process isolation is real, not just theoretical.** A stdio MCP server is
  spawned as a fresh OS process by its client — it never shares memory with
  a long-running `roommate` HTTP server. The two only see the same room data
  if both are launched with `--server-settings` pointing at a file whose
  `[storage]` section names the same `FsStore` root; with no `[storage]`
  section (`MemStore`), the MCP process starts empty regardless of what the
  HTTP server has stored. Verified end-to-end: a smoke-test run of `mcp.exe`
  against the repo's own `settings/server.toml` returned both the
  `[test_data]`-seeded project *and* a project previously pushed to the HTTP
  server's on-disk `FsStore` — proving the shared-root mechanism, not just
  asserting it.
- **`src/bin/` needed a `.gitignore` fix.** The repo's root `.gitignore`
  carries the standard Visual Studio "Build results" block, which has a
  blanket `[Bb]in/` rule (line ~240) meant for .NET build-output
  directories — it also matched Rust's `src/bin/` convention (multiple
  binaries per crate), silently excluding `bin/mcp.rs` from git. Fixed with
  `!VS/duHastApplications/roommate/src/bin/` placed *after* that rule (a
  negation earlier in the file, before a later blanket rule, loses — gitignore
  is evaluated top-to-bottom, last match wins).

## Open items / things to watch

- **F&E validation reuse gap applies here too.** The deferred-reuse note in
  [Server](STRATEGY-SERVER.md) (`compute_validation` not routing through
  `assemble_room`'s join) is unaffected by MCP existing — the MCP tool calls
  the same `service::validation::compute_project_validation` the HTTP route
  does, so whatever that function does or doesn't reuse is inherited as-is.
- **New `service/` capabilities are a tool away, not a rewrite.** Per the
  handover doc's whole premise: shortest path, F&E, drawings each become one
  `service/` file, one HTTP route, and (optionally) one `#[tool]` method
  here — none of the three touches the others.
- **No resources or prompts exposed**, only tools — matches the handover
  doc's "read side ... as tools" scope. Worth revisiting if an MCP client
  wants to browse stored snapshots as resources rather than calling a tool
  per query, but nothing today motivates it.
- **Not yet packaged for a specific MCP host.** Wiring `mcp.exe` into a
  concrete client's config (e.g. Claude Desktop's `mcpServers` entry) is
  unstarted — this doc covers the server side only.
