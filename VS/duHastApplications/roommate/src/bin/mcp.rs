//! roommate's MCP server: exposes the read side (`list_projects`,
//! `list_buildings`, `get_rooms`, `get_validation`) as MCP tools over stdio,
//! one per existing HTTP read route. Each tool is a thin adapter over
//! `roommate::service` -- parse params, call one service function, serialize
//! the result -- exactly like the Axum handlers in `roommate::handlers`, just
//! a second transport over the same domain layer. See
//! HANDOVER-service-layer.md.
//!
//! Ingest (`POST /rooms`) has no MCP equivalent here: an MCP client asking an
//! LLM to push a full room snapshot isn't a realistic flow, and the HTTP
//! server remains the ingest path.
//!
//! Run as a client-spawned subprocess (e.g. from an MCP host's config) --
//! stdout is reserved for the JSON-RPC stream, so all logging goes to
//! stderr. This is a distinct OS process from any running HTTP server: it
//! only sees the same room data if pointed at the same `[storage]` root via
//! `--settings`, since `MemStore` state isn't shared across processes.

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
use roommate::service::{projects, rooms, validation, ServiceError};
use roommate::state::Shared;

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct ProjectIdParams {
    /// The project id, as returned by `list_projects`.
    project_id: String,
}

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct GetRoomsParams {
    /// Scope the merge to one project id. Omit to merge every stored model.
    #[serde(default)]
    project: Option<String>,
    /// Opaque building key from `list_buildings`. Omit for no building filter.
    #[serde(default)]
    building: Option<String>,
}

/// Serialize any service response into a single text content block -- the
/// same `Serialize` types the HTTP handlers already return as JSON, just
/// wrapped for MCP instead of `axum::Json`.
fn json_result<T: serde::Serialize>(value: &T) -> Result<CallToolResult, McpError> {
    let json = serde_json::to_string(value)
        .map_err(|e| McpError::internal_error(format!("failed to serialize response: {e}"), None))?;
    Ok(CallToolResult::success(vec![ContentBlock::text(json)]))
}

/// `ServiceError` -> `McpError`. No HTTP status codes to map to here --
/// `NotFound`/`BadInput` both become `invalid_params` (the closest MCP
/// tool-call equivalent to "the caller gave us something we can't act on"),
/// `Internal` becomes `internal_error`.
fn to_mcp_error(err: ServiceError) -> McpError {
    match err {
        ServiceError::NotFound(msg) => McpError::invalid_params(msg, None),
        ServiceError::BadInput(msg) => McpError::invalid_params(msg, None),
        ServiceError::Internal(e) => {
            tracing::error!("internal service error: {e:#}");
            McpError::internal_error(e.to_string(), None)
        }
    }
}

// `tool_router` is read by the `#[tool_handler]`-generated dispatch code,
// but rustc's dead-code analysis doesn't see through that -- same false
// positive the rmcp SDK's own examples suppress this way.
#[allow(dead_code)]
#[derive(Clone)]
struct RoommateMcp {
    state: Shared,
    tool_router: ToolRouter<RoommateMcp>,
}

#[tool_router]
impl RoommateMcp {
    fn new(state: Shared) -> Self {
        Self { state, tool_router: Self::tool_router() }
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
    /// result's `store_empty` field reports whether anything has ever been
    /// pushed at all (there's no MCP equivalent of the HTTP 204 this maps to
    /// on the read route).
    #[tool(description = "Fetch merged rooms and levels across stored models, optionally scoped by project id and building key")]
    fn get_rooms(&self, Parameters(p): Parameters<GetRoomsParams>) -> Result<CallToolResult, McpError> {
        let result = rooms::assemble_rooms(&self.state, p.project.as_deref(), p.building.as_deref())
            .map_err(to_mcp_error)?;
        json_result(&result)
    }

    /// Runs the dRofus reconciliation QA report for one project -- see
    /// `service::validation::compute_project_validation`.
    #[tool(description = "Run the dRofus reconciliation validation report for one project")]
    fn get_validation(&self, Parameters(p): Parameters<ProjectIdParams>) -> Result<CallToolResult, McpError> {
        let result = validation::compute_project_validation(&self.state, &p.project_id).map_err(to_mcp_error)?;
        json_result(&result)
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
                "Read-only access to roommate's stored room and dRofus data. \
                 Requires the same [storage] root as the HTTP server (via --settings) \
                 to see real data -- this process does not share memory with it."
                    .to_string(),
            )
    }
}

#[derive(Parser)]
struct Args {
    /// Path to the TOML settings file (same file the HTTP server uses).
    #[arg(long)]
    settings: PathBuf,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // stderr, never stdout -- stdout is the JSON-RPC transport.
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info")
        .with_writer(std::io::stderr)
        .init();

    let args = Args::parse();
    let state = build_state(&args.settings)?;

    let service = RoommateMcp::new(state).serve(stdio()).await.inspect_err(|e| {
        tracing::error!("serving error: {e:?}");
    })?;
    service.waiting().await?;

    Ok(())
}
