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
binary plus tool definitions, not a rewrite. See
Superseded/HANDOVER-service-layer.md for the extraction itself.

## Implemented

- **Separate binary, shared lib crate.** The crate is now `lib.rs` (every
  domain module: `contract`, `settings`, `drofus`, `classify`, `state`,
  `storage`, `service`, `handlers`, `settings_api`, plus `bootstrap`) plus two bins:
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
- **Twelve tools: one per existing read route, two settings reads, and one
  forwarded upload.**
  `list_projects`, `list_buildings`, `get_rooms` (project/building/milestone
  filters optional), `get_validation`, `list_snapshots`,
  `get_latest_snapshot`, `list_milestones`, `list_drofus_snapshots`, and
  `get_drofus_snapshot` mirror the nine HTTP read routes (snapshot-history,
  milestone, and dRofus-upload endpoints: see [Server](STRATEGY-SERVER.md);
  `get_latest_snapshot` and `get_drofus_snapshot` map the service's `None` —
  HTTP's 404 — to a short plain-text answer, same convention as `get_rooms`'
  empty-store case).
  **Milestone dRofus pinning is inherited, not re-plumbed:** `get_rooms`'s
  `milestone` filter calls the same `assemble_rooms` the HTTP route does, and
  that function resolves a milestone's pinned dRofus snapshot below the
  transport seam — so a milestone view over MCP substitutes both the pinned
  *model* snapshots and the pinned *dRofus* CSV automatically, no MCP-specific
  code. `list_milestones` surfaces each milestone's `drofus_snapshot` id (its
  `MilestoneSummary`, alongside the model-pin count) so a client sees whether
  and what dRofus a milestone pins without a second `get_project_settings`
  call. Authoring a pin stays HTTP/settings-UI only (the read-only stance
  below), though `get_project_settings` exposes the raw pins for reading.
  `list_project_settings` / `get_project_settings` reuse `settings_api`'s
  transport-agnostic read core (see [Server](STRATEGY-SERVER.md)'s settings
  API bullet); they parse the TOML files fresh per call, so a change saved
  through the HTTP settings UI shows in them immediately — while this
  process's own `get_rooms`/`get_validation` still run on the registry
  loaded at its startup. Settings tools are read-only by design: this is a
  separate process from the HTTP server, so a write from here could not
  hot-swap that server's in-memory registry — the file and the serving
  process would silently disagree until a restart. Mutation stays behind the
  HTTP settings UI, matching the "Read-only access" contract `get_info`
  declares. Ingest (`POST /rooms`, `/rooms/stream`) has no MCP counterpart
  either — an LLM pushing a full room snapshot isn't a realistic flow, and
  the HTTP server remains the only ingest path.
- **`upload_drofus`: mutation by forwarding, not by writing.** The one
  mutating tool doesn't break the read-only stance, it routes around the
  split-brain problem: it reads a dRofus CSV from an absolute file path and
  POSTs it to the running HTTP server's `/projects/{id}/drofus`
  (`--server-url`, defaulting to the `DEFAULT_HTTP_ADDR` const both binaries
  share so they can't drift), so the HTTP server stays the single writer and
  hot-swaps its own registry. The HTTP server must be running — a connect
  failure answers a clear "start it and retry", and a non-2xx passes the
  server's rejection text through verbatim (the server is the real
  validator). This adds `reqwest` (no default features — loopback plain
  HTTP, no TLS stack) to the crate: an HTTP *client*, which doesn't breach
  the "neither bin's transport crate leaks into the other" rule — that rule
  is about server frameworks, and `mcp.rs` still never imports `axum` while
  `main.rs` never imports `rmcp`/`reqwest`. **Staleness asymmetry, stated in
  the tool description so it doesn't read as a bug:** after a forwarded
  upload, this process's own `get_rooms`/`get_validation` still join the
  dRofus data loaded at *its* startup (registries aren't shared), while
  `list_drofus_snapshots`/`get_drofus_snapshot` read the shared store fresh
  and see the new upload immediately.
- **`ServiceError` → `McpError` mapping.** `NotFound`/`BadInput` both become
  `McpError::invalid_params` (MCP's tool-call error surface has no direct
  404/400 split); `Internal` becomes `McpError::internal_error`. Required
  giving `ServiceError` real `Display`/`Error` impls (previously `Debug`-only,
  since nothing needed to stringify it before this).
- **`RoomsResult` derives `Serialize`; "nothing pushed yet" is not a field
  on it.** `assemble_rooms` returns `Option<RoomsResult>` — the old
  `store_empty` bool (a transport concern smuggled through the domain type;
  removed in the code-review fixes, see HANDOVER-review-fixes.md) is gone,
  so both adapters can serialize the result directly. Each maps `None` its
  own way: the HTTP handler answers 204 No Content, the `get_rooms` tool
  answers a short plain-text "no snapshots have been pushed" block (MCP has
  no status-code equivalent, and an LLM client reads either just fine). A
  `Some` with empty vecs is different and flows through as JSON: the store
  has data, the question just has an empty answer.
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
- **Host wiring shipped.** Concrete client configs now exist so the server plugs
  into a real MCP host, not just a raw stdio pipe: a project-scoped `.mcp.json`
  at the crate root (Claude Code — build-free via `cargo run -q`, whose `-q` keeps
  cargo's status lines off the JSON-RPC stdout) and a Claude Desktop `mcpServers`
  snippet with absolute paths, both in [mcp-host-setup.md](mcp-host-setup.md)
  alongside build + verify steps. Verified: the committed `.mcp.json` command run
  end-to-end returns `get_hierarchy_areas` over stdio with no cargo noise leaking
  into the transport. Adding another host is a copy-paste of the same
  `command`/`args`; both share the HTTP server's `--server-settings` /
  `--project-settings`, so the two front doors see identical data.

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
  per query, but nothing today motivates it. (Host *packaging*, which used to be
  the other open item here, is now done — see Implemented /
  [mcp-host-setup.md](mcp-host-setup.md).)
