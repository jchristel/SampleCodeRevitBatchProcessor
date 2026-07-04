//! roommate — Revit → Rust → browser room viewer.
//!
//! `main` is deliberately thin: parse args, load settings + dRofus (fail fast),
//! build shared state, wire the router. All the substance lives in the modules
//! below, each carrying its own rationale at the top:
//!
//! - `contract`  — the JSON contract shared with the Revit extractor + the
//!                 cross-tier property lookup both consumers use.
//! - `settings`  — startup TOML config (sources, test seed, hierarchy defn).
//! - `drofus`    — reference-data loader + join dataset.
//! - `classify`  — room → full-depth classification path.
//! - `state`     — shared in-memory store + startup seed.
//! - `handlers`  — the `/rooms` push and fetch, where derived data is assembled.

mod classify;
mod contract;
mod drofus;
mod handlers;
mod settings;
mod state;
mod storage;

use std::path::PathBuf;
use std::sync::Arc;

use anyhow::Context;
use axum::{
    routing::{get, post},
    Router,
};
use clap::Parser;
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

use crate::drofus::load_drofus;
use crate::handlers::{get_project_buildings, get_project_validation, get_projects, get_rooms, ingest_rooms};
use crate::settings::{load_settings, Settings};
use crate::state::{seed_if_test, AppState, Shared};
use crate::storage::{FsStore, MemStore, SnapshotStore};

#[derive(Parser)]
struct Args {
    /// Path to the TOML settings file.
    #[arg(long)]
    settings: PathBuf,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info,tower_http=info")
        .init();

    let args = Args::parse();
    let settings = load_settings(&args.settings)
        .with_context(|| format!("bad settings file: {}", args.settings.display()))?;

    tracing::info!("settings loaded from {}", args.settings.display());

    let Settings { sources, storage, test_data, hierarchy, builtin_properties, room_label } = settings;
    let drofus = load_drofus(&sources.drofus)?;

    // Pick the backend from config: a `[storage]` root → persistent FsStore,
    // otherwise the volatile MemStore (dev/test). Both satisfy SnapshotStore, so
    // this is the only line that knows which one is running.
    let store: Box<dyn SnapshotStore> = match storage {
        Some(cfg) => {
            tracing::info!("persistent storage at {}", cfg.root.display());
            Box::new(FsStore::new(cfg.root)?)
        }
        None => {
            tracing::info!("no [storage] configured — using in-memory store");
            Box::new(MemStore::new())
        }
    };

    let state: Shared = Arc::new(AppState::new(store, drofus, hierarchy, builtin_properties, room_label));

    seed_if_test(&state, test_data.as_ref())?;

    let app = Router::new()
        .route("/rooms", post(ingest_rooms).get(get_rooms))
        .route("/projects", get(get_projects))
        .route("/projects/{id}/buildings", get(get_project_buildings))
        .route("/projects/{id}/validation", get(get_project_validation))
        // Serves the viewer page at "/" from ./static.
        .fallback_service(ServeDir::new("static"))
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
