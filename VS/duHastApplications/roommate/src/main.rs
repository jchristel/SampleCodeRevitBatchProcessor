//! roommate — the Axum HTTP server binary. Deliberately thin: parse args,
//! build shared state via `roommate::bootstrap`, wire the router. All the
//! substance lives in the `roommate` lib crate (see its own header for the
//! module index). The `mcp` binary (`src/bin/mcp.rs`) is the other consumer
//! of that lib crate, over stdio instead of HTTP.

use std::path::PathBuf;

use axum::{
    extract::DefaultBodyLimit,
    routing::{get, post},
    Router,
};
use clap::Parser;
use tower_http::{cors::CorsLayer, decompression::RequestDecompressionLayer, services::ServeDir, trace::TraceLayer};

use roommate::bootstrap::build_state;
use roommate::handlers::{
    compare_project_milestones, get_drofus_latest, get_drofus_snapshots, get_model_latest_snapshot,
    get_project_areas, get_project_buildings, get_project_milestones, get_project_snapshots,
    get_project_validation, get_projects, get_rooms, ingest_rooms, ingest_rooms_stream,
};
use roommate::settings_api::{
    http_create_project, http_drofus_check, http_get_project, http_get_project_resolved,
    http_list_projects, http_update_project, http_upload_drofus,
};
use roommate::DEFAULT_HTTP_ADDR;

/// Cap on the buffered `/rooms` body -- applies to the DECOMPRESSED size, since
/// `RequestDecompressionLayer` inflates before this limit is checked. FFE
/// exports run >100 MB uncompressed; sized generously above that rather than
/// tuned tight, since the streaming route (`/rooms/stream`) is the intended
/// home for anything approaching this ceiling anyway. See HANDOVER-gzip.md.
const ROOMS_BODY_LIMIT_BYTES: usize = 512 * 1024 * 1024;

/// Cap on a dRofus CSV upload body (decompressed, same as above). Real dRofus
/// exports are a few MB of CSV; 32 MB is generous headroom. Without an
/// explicit layer this route would get axum's silent 2 MB default.
const DROFUS_BODY_LIMIT_BYTES: usize = 32 * 1024 * 1024;

#[derive(Parser)]
struct Args {
    /// Path to the server-wide TOML settings file (`[storage]`, `[test_data]`).
    #[arg(long)]
    server_settings: PathBuf,

    /// Path to a directory of per-project TOML settings files (one per
    /// project, each declaring its own `project_id`). See
    /// HANDOVER-per-project-settings.md.
    #[arg(long)]
    project_settings: PathBuf,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Filter on the *current* crate name -- this said "revit_viewer" (the
    // crate's old name) for a while, which silently dropped every log event
    // the server emitted. RUST_LOG still wins when set.
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("roommate=info,tower_http=info")),
        )
        .init();

    let args = Args::parse();
    let state = build_state(&args.server_settings, &args.project_settings)?;

    let app = Router::new()
        .route(
            "/rooms",
            post(ingest_rooms).get(get_rooms).layer(DefaultBodyLimit::max(ROOMS_BODY_LIMIT_BYTES)),
        )
        // Streaming NDJSON ingest for models too large to buffer whole (see
        // HANDOVER-streaming.md) -- disables the body limit entirely and relies
        // on line-by-line reading to keep peak memory low instead.
        .route(
            "/rooms/stream",
            post(ingest_rooms_stream).layer(DefaultBodyLimit::disable()),
        )
        .route("/projects", get(get_projects))
        .route("/projects/{id}/buildings", get(get_project_buildings))
        .route("/projects/{id}/validation", get(get_project_validation))
        // Snapshot history: everything per project (grouped by model), and the
        // per-model latest a follow-up upload attaches its data to.
        .route("/projects/{id}/snapshots", get(get_project_snapshots))
        // Milestones: named dated pins over snapshots, defined per project in
        // its settings file; the viewer's dropdown reads this list.
        .route("/projects/{id}/milestones", get(get_project_milestones))
        // Hierarchy gross-area footprints: dissolved per-tier polygons + areas,
        // scoped by ?building=/?milestone= like /rooms. See service::areas.
        .route("/projects/{id}/areas", get(get_project_areas))
        // Milestone comparison: a baseline-vs-each-other diff of rooms and a
        // user-defined property set. POST (not GET) for its list body — see
        // `handlers::compare_project_milestones`.
        .route("/projects/{id}/comparison", post(compare_project_milestones))
        .route(
            "/projects/{project_id}/models/{model_id}/snapshots/latest",
            get(get_model_latest_snapshot),
        )
        // dRofus upload ingest + its read side: uploaded CSVs are timestamped
        // project-scoped snapshots in the store (see settings_api's
        // `upload_drofus` for the validate-before-store pipeline).
        .route(
            "/projects/{id}/drofus",
            post(http_upload_drofus).layer(DefaultBodyLimit::max(DROFUS_BODY_LIMIT_BYTES)),
        )
        .route("/projects/{id}/drofus/snapshots", get(get_drofus_snapshots))
        .route("/projects/{id}/drofus/latest", get(get_drofus_latest))
        // Settings read/save API behind static/settings.html — see
        // `settings_api`'s module doc for the save pipeline and trust model.
        .route("/api/settings/projects", get(http_list_projects).post(http_create_project))
        .route("/api/settings/projects/{id}", get(http_get_project).put(http_update_project))
        // Viewer-only resolving read: same as the GET above but falls back to the
        // is_default file, so the viewer's payload id (not a settings project_id)
        // still finds its colour plans. Editors keep the strict route above.
        .route("/api/settings/resolve/{id}", get(http_get_project_resolved))
        .route("/api/settings/drofus-check", post(http_drofus_check))
        // Serves the viewer page at "/" from ./static.
        .fallback_service(ServeDir::new("static"))
        // Inflate gzip request bodies (Content-Encoding: gzip) before Json/NDJSON
        // parsing sees them. Transparent: a non-gzip body passes through
        // untouched, so an uncompressed sender still works -- purely additive.
        // Added before Cors/Trace so it sits innermost (Router::layer wraps
        // outward: the layer added last runs first on the request path), i.e.
        // decompression happens right before the body reaches a handler.
        .layer(RequestDecompressionLayer::new())
        // Lets the browser viewer call /rooms even if served from elsewhere.
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = DEFAULT_HTTP_ADDR;
    let listener = tokio::net::TcpListener::bind(addr).await?;
    tracing::info!("viewer on http://{addr}  (POST room JSON to http://{addr}/rooms)");
    axum::serve(listener, app).await?;

    Ok(())
}
