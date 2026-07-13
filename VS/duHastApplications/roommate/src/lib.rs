//! roommate — Revit → Rust → browser room viewer.
//!
//! Library crate shared by two binaries: `roommate` (the Axum HTTP server,
//! `src/main.rs`) and `mcp` (the MCP stdio server, `src/bin/mcp.rs`). Neither
//! binary's transport concerns leak into these modules — `service/` never
//! imports `axum` or `rmcp`, and `bootstrap` (settings → running `AppState`)
//! is shared verbatim so the two entry points can't drift on how a store gets
//! picked or a snapshot gets seeded. Each module carries its own rationale at
//! the top:
//!
//! - `contract`  — the JSON contract shared with the Revit extractor + the
//!                 cross-tier property lookup both consumers use.
//! - `settings`  — startup TOML config (sources, test seed, hierarchy defn).
//! - `drofus`    — reference-data loader + join dataset.
//! - `classify`  — room → full-depth classification path.
//! - `state`     — shared app state: settings registry + the snapshot store
//!                 behind its trait, plus the startup seed.
//! - `storage`   — the `SnapshotStore` trait and its two impls (`FsStore`
//!                 on disk, `MemStore` volatile).
//! - `bootstrap` — settings file path -> running `Shared` state, reused by
//!                 both binaries' `main()`.
//! - `handlers`  — thin Axum adapters: the `/rooms` push (plus the streaming
//!                 `/rooms/stream` push for large models) and the read-side
//!                 routes, which call into `service`.
//! - `service`   — transport-agnostic derive/assemble logic (dRofus join,
//!                 classification, validation), shared by `handlers` and the
//!                 MCP binary. See HANDOVER-service-layer.md.
//! - `settings_api` — read/save API behind the settings UI: transport-
//!                 agnostic core (reads shared with the MCP binary) + the
//!                 `/api/settings` Axum adapters; saves hot-swap the registry.

/// Where the HTTP server binds by default. Shared with `bin/mcp.rs`'s
/// `--server-url` default (its `upload_drofus` tool forwards over HTTP to
/// this address) so the two binaries can't drift on where the server lives.
pub const DEFAULT_HTTP_ADDR: &str = "127.0.0.1:5151";

pub mod bootstrap;
pub mod classify;
pub mod contract;
pub mod drofus;
pub mod handlers;
pub mod service;
pub mod settings;
pub mod settings_api;
pub mod state;
pub mod storage;
