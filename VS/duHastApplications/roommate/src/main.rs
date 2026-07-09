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
    get_project_buildings, get_project_validation, get_projects, get_rooms, ingest_rooms, ingest_rooms_stream,
};

/// Cap on the buffered `/rooms` body -- applies to the DECOMPRESSED size, since
/// `RequestDecompressionLayer` inflates before this limit is checked. FFE
/// exports run >100 MB uncompressed; sized generously above that rather than
/// tuned tight, since the streaming route (`/rooms/stream`) is the intended
/// home for anything approaching this ceiling anyway. See HANDOVER-gzip.md.
const ROOMS_BODY_LIMIT_BYTES: usize = 512 * 1024 * 1024;

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
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info,tower_http=info")
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

    let addr = "127.0.0.1:5151";
    let listener = tokio::net::TcpListener::bind(addr).await?;
    tracing::info!("viewer on http://{addr}  (POST room JSON to http://{addr}/rooms)");
    axum::serve(listener, app).await?;

    Ok(())
}
