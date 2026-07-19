//! roommate's MCP server: exposes the read side (`list_projects`,
//! `list_buildings`, `get_rooms`, `get_validation`, `get_hierarchy_areas`,
//! `list_snapshots`, `get_latest_snapshot`, `list_milestones`,
//! `list_drofus_snapshots`, `get_drofus_snapshot`) as MCP tools over stdio, one
//! per existing HTTP read route. Each tool is a thin adapter over `roommate::service` -- parse
//! params, call one service function, serialize the result -- exactly like
//! the Axum handlers in `roommate::handlers`, just a second transport over
//! the same domain layer. See HANDOVER-service-layer.md.
//!
//! Ingest (`POST /rooms`) has no MCP equivalent here: an MCP client asking an
//! LLM to push a full room snapshot isn't a realistic flow, and the HTTP
//! server remains the ingest path.
//!
//! The one mutating tool, `upload_drofus`, doesn't break that rule: it never
//! writes this process's state or the store — it reads a CSV file and
//! *forwards it over HTTP* to the running server (`--server-url`, default the
//! shared `DEFAULT_HTTP_ADDR`), which stays the single writer and hot-swaps
//! its own registry. The `reqwest` dependency this adds is an HTTP *client*;
//! the "no transport crate leaks into the other binary" rule is about server
//! frameworks (`mcp.rs` still never imports `axum`), and `main.rs` still
//! never imports `rmcp` or `reqwest`.
//!
//! Run as a client-spawned subprocess (e.g. from an MCP host's config) --
//! stdout is reserved for the JSON-RPC stream, so all logging goes to
//! stderr. This is a distinct OS process from any running HTTP server: it
//! only sees the same room data if pointed at the same `[storage]` root via
//! `--server-settings`, since `MemStore` state isn't shared across processes.

use std::path::PathBuf;

use clap::Parser;
use rmcp::{
    handler::server::{router::tool::ToolRouter, wrapper::Parameters},
    model::{CallToolResult, ContentBlock, Implementation, ServerCapabilities, ServerInfo},
    schemars, tool, tool_handler, tool_router,
    transport::stdio,
    ErrorData as McpError, ServerHandler, ServiceExt,
};

use roommate::bootstrap::build_state;
use roommate::service::{
    areas, comparison, drofus, milestones, projects, rooms, snapshots, validation, ServiceError,
};
use roommate::settings_api::{self, SettingsError};
use roommate::state::Shared;
use roommate::DEFAULT_HTTP_ADDR;

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct ProjectIdParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct ModelIdParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
    /// The model id, as returned by `list_snapshots`.
    model_id: String,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct GetRoomsParams {
    /// Scope the merge to one project id. Omit to merge every stored model.
    #[serde(default)]
    project: Option<String>,
    /// Opaque building key from `list_buildings`. Omit for no building filter.
    #[serde(default)]
    building: Option<String>,
    /// Milestone name from `list_milestones`: serve the snapshots that
    /// milestone pins instead of each model's latest. Omit for latest.
    #[serde(default)]
    milestone: Option<String>,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct AreasParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
    /// Opaque building key from `list_buildings`. Omit for no building filter.
    #[serde(default)]
    building: Option<String>,
    /// Milestone name from `list_milestones`: measure the snapshots that
    /// milestone pins instead of each model's latest. Omit for latest.
    #[serde(default)]
    milestone: Option<String>,
}

/// Serialize any service response into a single text content block -- the
/// same `Serialize` types the HTTP handlers already return as JSON, just
/// wrapped for MCP instead of `axum::Json`.
fn json_result<T: serde::Serialize>(value: &T) -> Result<CallToolResult, McpError> {
    let json = serde_json::to_string(value)
        .map_err(|e| McpError::internal_error(format!("failed to serialize response: {e}"), None))?;
    Ok(CallToolResult::success(vec![ContentBlock::text(json)]))
}

/// Minimal percent-encoding for URL path/query components. The values that
/// pass through here are constrained by construction — project ids are
/// path-safe (`is_path_safe_component`) and `taken_at` is RFC3339, whose only
/// URL-reserved character is the `+` of a numeric offset — so a tiny
/// encode-everything-non-unreserved loop beats a dependency.
fn urlencode(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for b in s.bytes() {
        match b {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => out.push(b as char),
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    out
}

/// `ServiceError` -> `McpError`. Only `Internal` exists today (variants join
/// with their first producer -- see `ServiceError`); it becomes
/// `internal_error`.
fn to_mcp_error(err: ServiceError) -> McpError {
    match err {
        ServiceError::Internal(e) => {
            tracing::error!("internal service error: {e:#}");
            McpError::internal_error(e.to_string(), None)
        }
    }
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct CompareMilestonesParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
    /// The baseline milestone name (from `list_milestones`) every other is
    /// compared against.
    baseline: String,
    /// The milestone names to compare against the baseline. Any equal to the
    /// baseline is skipped.
    #[serde(default)]
    others: Vec<String>,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct GetDrofusSnapshotParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
    /// A dRofus snapshot id from `list_drofus_snapshots`. Omit for the latest.
    #[serde(default)]
    taken_at: Option<String>,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct UploadDrofusParams {
    /// The project id, as returned by `list_projects`. Its settings must
    /// declare `[sources.drofus] type = "upload"`.
    project_id: String,
    /// Absolute path to the dRofus CSV export to upload.
    path: String,
    /// Snapshot id (RFC3339 UTC date-time) to store the upload under. Omit
    /// to let the server mint one; the result reports the resolved id.
    #[serde(default)]
    taken_at: Option<String>,
}

// `tool_router` is read by the `#[tool_handler]`-generated dispatch code,
// but rustc's dead-code analysis doesn't see through that -- same false
// positive the rmcp SDK's own examples suppress this way.
#[allow(dead_code)]
#[derive(Clone)]
struct RoommateMcp {
    state: Shared,
    server_url: String,
    tool_router: ToolRouter<RoommateMcp>,
}

#[tool_router]
impl RoommateMcp {
    fn new(state: Shared, server_url: String) -> Self {
        Self { state, server_url, tool_router: Self::tool_router() }
    }

    /// Lists every project with at least one stored model -- see
    /// `service::projects::list_projects`.
    #[tool(description = "List every project with at least one stored model")]
    fn list_projects(&self) -> Result<CallToolResult, McpError> {
        let result = projects::list_projects(&self.state).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Lists the distinct "Building" classification values for one project
    /// -- see `service::projects::list_buildings`.
    #[tool(description = "List the distinct Building classification values found in one project's rooms")]
    fn list_buildings(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = projects::list_buildings(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Merges every stored model's levels and rooms, optionally scoped by
    /// project and building -- see `service::rooms::assemble_rooms`. The
    /// service's `None` ("nothing has ever been pushed" -- the HTTP 204 case)
    /// has no MCP status-code equivalent, so it becomes a short plain-text
    /// answer instead of a JSON body; an LLM client reads either just fine.
    #[tool(description = "Fetch merged rooms and levels across stored models, optionally scoped by project id, building key, and milestone name. A project whose hierarchy has no 'Building' tier matches nothing under a building filter (check list_buildings' tier_configured before filtering); under a milestone filter, models are served from the snapshots that milestone pins instead of their latest.")]
    fn get_rooms(&self, Parameters(p): Parameters<GetRoomsParams>) -> Result<CallToolResult, McpError> {
        let result = rooms::assemble_rooms(&self.state, p.project.as_deref(), p.building.as_deref(), p.milestone.as_deref())
            .map_err(to_mcp_error)?;
        match result {
            None => Ok(CallToolResult::success(vec![ContentBlock::text(
                "no snapshots have been pushed to this server yet",
            )])),
            Some(result) => json_result(&result),
        }
    }

    /// Lists one project's milestones (named dated snapshot pins) -- see
    /// `service::milestones::list_milestones`.
    #[tool(description = "List one project's milestones: named dates with data snapshots pinned to them, newest first — each carries its model-pin count and its pinned dRofus snapshot id (drofus_snapshot) when one is set. Pass a milestone's name to get_rooms to view the project as captured at that milestone, rooms AND dRofus.")]
    fn list_milestones(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = milestones::list_milestones(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Compares N milestones against a baseline for one project -- see
    /// `service::comparison::compare_milestones`. A project with no
    /// `comparison_key` configured returns `comparison_key_configured: false`.
    #[tool(description = "Compare milestones for one project: one baseline milestone versus each of the others (a star diff, not all-pairs). \
                          Reports rooms added and removed relative to the baseline, and per-property differences on rooms present in both, \
                          over the project's configured comparison property set. Rooms are matched by the project's user-defined comparison_key \
                          property (its own setting, NOT the dRofus link property); if none is configured the result is comparison_key_configured: false.")]
    fn compare_milestones(&self, Parameters(p): Parameters<CompareMilestonesParams>) -> Result<CallToolResult, McpError> {
        let result = comparison::compare_milestones(&self.state, &p.project_id, &p.baseline, &p.others).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Lists every stored snapshot id for one project, grouped per model --
    /// see `service::snapshots::list_project_snapshots`.
    #[tool(description = "List every stored snapshot id (RFC3339 UTC taken_at) for one project, grouped per model, each group carrying its latest")]
    fn list_snapshots(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = snapshots::list_project_snapshots(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// The latest snapshot id for one model -- see
    /// `service::snapshots::latest_snapshot`. The service's `None` (the HTTP
    /// 404 case) becomes a short plain-text answer, same convention as
    /// `get_rooms`' empty-store case.
    #[tool(description = "Get the latest snapshot id (taken_at) for one model of one project")]
    fn get_latest_snapshot(&self, Parameters(p): Parameters<ModelIdParams>) -> Result<CallToolResult, McpError> {
        let result = snapshots::latest_snapshot(&self.state, &p.project_id, &p.model_id).map_err(to_mcp_error)?;
        match result {
            None => Ok(CallToolResult::success(vec![ContentBlock::text(
                "no snapshots stored for that project/model",
            )])),
            Some(latest) => json_result(&latest),
        }
    }

    /// Runs the dRofus reconciliation QA report for one project -- see
    /// `service::validation::compute_project_validation`.
    #[tool(description = "Run the dRofus reconciliation validation report for one project. Includes a 'discrepancies' summary (total plus a per-category breakdown) for a one-shot count, and 'error_rooms' (room_id -> number/name/link value) for the flagged rooms.")]
    fn get_validation(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = validation::compute_project_validation(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Hierarchy gross-area footprints for one project -- see
    /// `service::areas::assemble_areas`. Shares the exact read logic the HTTP
    /// `GET /projects/{id}/areas` uses; `None` (nothing pushed) mirrors
    /// `get_rooms`' empty-store message.
    #[tool(description = "Compute per-level, per-tier dissolved gross-area footprints for one project, optionally scoped by building key and milestone name. Each group carries its resolved classification path, its measured footprint area (an aggregated ROOM FOOTPRINT — wall-zone/void-inclusive, NOT net area or a standards gross), whether it counts toward tiers above it (a settings exclusion can withhold a group), and its hole-free exterior rings. Area at every tier is measured from that tier's own dissolved polygon, so a parent's area is not the sum of its children's.")]
    fn get_hierarchy_areas(&self, Parameters(p): Parameters<AreasParams>) -> Result<CallToolResult, McpError> {
        let result = areas::assemble_areas(&self.state, &p.project_id, p.building.as_deref(), p.milestone.as_deref())
            .map_err(to_mcp_error)?;
        match result {
            None => Ok(CallToolResult::success(vec![ContentBlock::text(
                "no snapshots have been pushed to this server yet",
            )])),
            Some(result) => json_result(&result),
        }
    }

    /// Lists every uploaded dRofus snapshot id for one project -- see
    /// `service::drofus::list_drofus_snapshots`.
    #[tool(description = "List every uploaded dRofus CSV snapshot id (RFC3339 UTC taken_at) for one project, ascending, with the latest. \
                          Reads the shared store fresh, so an upload forwarded moments ago shows here immediately.")]
    fn list_drofus_snapshots(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = drofus::list_drofus_snapshots(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// A parsed summary of one uploaded dRofus CSV -- see
    /// `service::drofus::get_drofus_snapshot`. The service's `None` (the
    /// HTTP 404 case) becomes a short plain-text answer, same convention as
    /// `get_latest_snapshot`.
    #[tool(description = "Get a parsed summary (record count, link property, field labels) of one uploaded dRofus CSV -- the given taken_at, or the latest when omitted. \
                          Reads the shared store fresh.")]
    fn get_drofus_snapshot(&self, Parameters(p): Parameters<GetDrofusSnapshotParams>) -> Result<CallToolResult, McpError> {
        let result = drofus::get_drofus_snapshot(&self.state, &p.project_id, p.taken_at.as_deref()).map_err(to_mcp_error)?;
        match result {
            None => Ok(CallToolResult::success(vec![ContentBlock::text(
                "no such dRofus upload stored for that project",
            )])),
            Some(info) => json_result(&info),
        }
    }

    /// Uploads a dRofus CSV by FORWARDING it to the running HTTP server --
    /// this process never writes the store itself (see the module doc): the
    /// server validates, stores, and hot-swaps its own registry, staying the
    /// single writer.
    #[tool(description = "Upload a dRofus CSV export (given as an absolute file path) for one project. \
                          Forwards the file over HTTP to the running roommate server, which validates it against the project's \
                          drofus_fields before storing it as a dated snapshot and applying it live -- so the HTTP server must be running. \
                          The project's settings must declare [sources.drofus] type = \"upload\". \
                          Note the staleness asymmetry: after an upload, this process's own get_rooms/get_validation still join the \
                          dRofus data loaded at ITS startup; list_drofus_snapshots/get_drofus_snapshot read the store fresh and see the new upload immediately.")]
    async fn upload_drofus(&self, Parameters(p): Parameters<UploadDrofusParams>) -> Result<CallToolResult, McpError> {
        let bytes = std::fs::read(&p.path)
            .map_err(|e| McpError::invalid_params(format!("could not read CSV file {:?}: {e}", p.path), None))?;

        let mut url = format!("{}/projects/{}/drofus", self.server_url.trim_end_matches('/'), urlencode(&p.project_id));
        if let Some(taken_at) = &p.taken_at {
            url.push_str(&format!("?taken_at={}", urlencode(taken_at)));
        }

        let response = reqwest::Client::new()
            .post(&url)
            .header("Content-Type", "text/csv")
            .body(bytes)
            .send()
            .await
            .map_err(|e| {
                McpError::internal_error(
                    format!(
                        "the roommate HTTP server is not reachable at {} ({e}) -- \
                         start it (it is the single writer for uploads) and retry",
                        self.server_url
                    ),
                    None,
                )
            })?;

        let status = response.status();
        let body = response.text().await.unwrap_or_default();
        if status.is_success() {
            Ok(CallToolResult::success(vec![ContentBlock::text(body)]))
        } else {
            // The server's rejection text is the real validator -- pass it on
            // verbatim, marked caller-addressable.
            Err(McpError::invalid_params(format!("server answered {status}: {body}"), None))
        }
    }

    // Settings tools are READ-ONLY by design: this is a separate process from
    // the HTTP server, so a write from here could not hot-swap that server's
    // in-memory registry -- the file and the serving process would silently
    // disagree until a restart. Mutation stays behind the HTTP settings UI
    // (see `settings_api`'s module doc), matching the "Read-only access
    // against local state" contract `get_info` declares. `upload_drofus`
    // above is not an exception: it forwards to that HTTP server rather than
    // writing anything from this process.

    /// Lists every project settings file with its headline facts -- see
    /// `settings_api::list_project_files`.
    #[tool(description = "List every project settings file (project id, is_default, whether dRofus is configured). \
                          Reads the files fresh, so a settings change saved through the HTTP UI shows here immediately; \
                          this process's own get_rooms/get_validation behavior still reflects the settings loaded at its startup.")]
    fn list_project_settings(&self) -> Result<CallToolResult, McpError> {
        let dir = self.projects_dir()?;
        let result = settings_api::list_project_files(&dir).map_err(settings_to_mcp_error)?;
        json_result(&result)
    }

    /// One project's parsed settings as JSON -- see
    /// `settings_api::get_project_file`.
    #[tool(description = "Get one project's settings (hierarchy, dRofus source, builtin properties, room label, QA fields) as JSON. \
                          Reads the file fresh, so a settings change saved through the HTTP UI shows here immediately; \
                          this process's own get_rooms/get_validation behavior still reflects the settings loaded at its startup.")]
    fn get_project_settings(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let dir = self.projects_dir()?;
        let (file, settings) = settings_api::get_project_file(&dir, &p.project_id).map_err(settings_to_mcp_error)?;
        json_result(&serde_json::json!({ "file": file, "settings": settings }))
    }

    /// The `--project-settings` directory this process was started with --
    /// always present for this binary (the arg is required), so the error arm
    /// is defensive only.
    fn projects_dir(&self) -> Result<std::path::PathBuf, McpError> {
        self.state
            .projects_dir()
            .cloned()
            .ok_or_else(|| McpError::internal_error("no project settings directory configured", None))
    }
}

/// `SettingsError` -> `McpError`: caller-addressable problems (unknown id,
/// invalid input) become `invalid_params`; the rest `internal_error`.
fn settings_to_mcp_error(err: SettingsError) -> McpError {
    match err {
        SettingsError::NotFound(msg) | SettingsError::Invalid(msg) | SettingsError::Conflict(msg) => {
            McpError::invalid_params(msg, None)
        }
        SettingsError::NotFileBacked => {
            McpError::internal_error("no project settings directory configured", None)
        }
        SettingsError::Internal(e) => {
            tracing::error!("settings read error: {e:#}");
            McpError::internal_error(e.to_string(), None)
        }
    }
}

#[tool_handler]
impl ServerHandler for RoommateMcp {
    fn get_info(&self) -> ServerInfo {
        // Not `Implementation::from_build_env()` -- it's a plain fn whose body
        // bakes in `env!()` at *rmcp's own* compile time, so it always reports
        // "rmcp"/rmcp's version rather than ours (confirmed via a stdio smoke
        // test). Name and version explicitly instead.
        ServerInfo::new(ServerCapabilities::builder().enable_tools().build())
            .with_server_info(Implementation::new("roommate-mcp", env!("CARGO_PKG_VERSION")))
            .with_instructions(
                "Read-only access to roommate's stored room and dRofus data -- this process never \
                 writes its own state or the store. The one mutating tool, upload_drofus, forwards \
                 the CSV over HTTP to the running roommate server, which stays the single writer \
                 and hot-swaps its own registry. Requires the same [storage] root as the HTTP \
                 server (via --server-settings) to see real data -- this process does not share \
                 memory with it."
                    .to_string(),
            )
    }
}

#[derive(Parser)]
struct Args {
    /// Path to the server-wide TOML settings file (same file the HTTP server
    /// uses via `--server-settings`).
    #[arg(long)]
    server_settings: PathBuf,

    /// Path to the directory of per-project TOML settings files (same
    /// directory the HTTP server uses via `--project-settings`).
    #[arg(long)]
    project_settings: PathBuf,

    /// Base URL of the running roommate HTTP server, used only by the
    /// `upload_drofus` tool (which forwards uploads to it). Defaults to the
    /// address the server binary binds by default.
    #[arg(long, default_value_t = format!("http://{DEFAULT_HTTP_ADDR}"))]
    server_url: String,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // stderr, never stdout -- stdout is the JSON-RPC transport. Filter on the
    // *current* crate name (this said "revit_viewer", the crate's old name,
    // which silently dropped every log event). RUST_LOG still wins when set.
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("roommate=info")),
        )
        .with_writer(std::io::stderr)
        .init();

    let args = Args::parse();
    let state = build_state(&args.server_settings, &args.project_settings)?;

    let service = RoommateMcp::new(state, args.server_url).serve(stdio()).await.inspect_err(|e| {
        tracing::error!("serving error: {e:?}");
    })?;
    service.waiting().await?;

    Ok(())
}
