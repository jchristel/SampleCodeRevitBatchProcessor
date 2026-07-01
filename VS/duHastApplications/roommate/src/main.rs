use std::{
    path::PathBuf,
    sync::{Arc, Mutex},
};

use anyhow::Context;
use axum::{
    extract::State,
    http::StatusCode,
    routing::post,
    Json, Router,
};
use clap::Parser;
use serde::{Deserialize, Serialize};
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

// ---------- Settings ----------

/// Top-level server settings, parsed once at startup from a TOML file.
#[derive(Debug, Deserialize)]
struct Settings {
    pub sources: Sources,

    /// Dev-only: when present, seeds the server with a snapshot from disk at
    /// startup so no manual POST is needed. Omit in prod.
    #[serde(default)]
    pub test_data: Option<TestData>,
}

/// External data sources joined onto the Revit snapshot.
#[derive(Debug, Deserialize)]
struct Sources {
    pub drofus: DrofusSource,
}

/// dRofus source. `#[serde(tag = "type")]` lets the TOML `type` field pick the
/// variant — adding an `Api` variant later is a loader-only change; all
/// consumers of `AppState` stay untouched.
#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
enum DrofusSource {
    /// Current: load from a local file.
    File { path: PathBuf },
    // Future: Api { url: String, api_key: String },
}

/// Dev-only seed data. Kept separate from `drofus` so removing this test seam
/// later is a one-section deletion with no other changes.
#[derive(Debug, Deserialize)]
struct TestData {
    /// Path to a pre-exported snapshot (same JSON shape a POST sends).
    pub snapshot_path: PathBuf,
}

// ---------- CLI ----------

#[derive(Parser)]
struct Args {
    /// Path to the TOML settings file.
    #[arg(long)]
    settings: PathBuf,
}

fn load_settings(path: &PathBuf) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("could not read settings file: {}", path.display()))?;
    toml::from_str(&raw).context("failed to parse settings TOML")
}

// ---------- JSON contract (must match the Revit add-in's serializer) ----------

/// A 2D point in Revit model space. Units are decimal feet, Y points UP.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
struct Point2D {
    x: f64,
    y: f64,
}

/// A single closed loop of points. A room has one outer loop and zero or more
/// inner loops (holes, e.g. a column or shaft punched through the room).
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Loop {
    points: Vec<Point2D>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Level {
    id: String,
    name: String,
    elevation: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Room {
    id: String,
    name: String,
    level_id: String,
    loops: Vec<Loop>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct RoomPayload {
    schema_version: u32,
    levels: Vec<Level>,
    rooms: Vec<Room>,
}

const SUPPORTED_SCHEMA: u32 = 2;

// ---------- Shared state ----------

/// In-memory store of the last payload received. Mutex is fine: this is a
/// single-user local tool, not a high-concurrency service.
struct AppState {
    latest: Mutex<Option<RoomPayload>>,

    /// Resolved dRofus source held for future join at response assembly.
    /// Loaded once at startup; handlers read it directly from state.
    drofus: Option<DrofusSource>,
}

impl AppState {
    fn new(drofus: DrofusSource) -> Self {
        Self {
            latest: Mutex::new(None),
            drofus: Some(drofus),
        }
    }

    /// Shared setter used by both the push handler and the startup seed so the
    /// two paths can never drift to different representations.
    fn set_snapshot(&self, payload: RoomPayload) {
        *self.latest.lock().unwrap() = Some(payload);
    }
}

type Shared = Arc<AppState>;

// ---------- Startup helpers ----------

fn seed_if_test(state: &AppState, test_data: Option<&TestData>) -> anyhow::Result<()> {
    if let Some(test) = test_data {
        let raw = std::fs::read_to_string(&test.snapshot_path).with_context(|| {
            format!(
                "could not read test snapshot: {}",
                test.snapshot_path.display()
            )
        })?;
        // Parse into the same type the push handler accepts — seed and push
        // converge on one representation and can never drift.
        let snapshot: RoomPayload =
            serde_json::from_str(&raw).context("failed to parse test snapshot JSON")?;
        state.set_snapshot(snapshot);
        tracing::info!("seeded snapshot from {}", test.snapshot_path.display());
    }
    Ok(())
}

// ---------- Handlers ----------

/// Revit posts room data here. Returns 200 with a short summary, or 422 if the
/// schema version is one this server doesn't understand.
async fn ingest_rooms(
    State(state): State<Shared>,
    Json(payload): Json<RoomPayload>,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    if payload.schema_version != SUPPORTED_SCHEMA {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!(
                "schema_version {} not supported; this server speaks {}",
                payload.schema_version, SUPPORTED_SCHEMA
            ),
        ));
    }

    let count = payload.rooms.len();
    tracing::info!("received {} room(s)", count);

    state.set_snapshot(payload);

    Ok(Json(IngestResponse {
        accepted: true,
        room_count: count,
    }))
}

#[derive(Serialize)]
struct IngestResponse {
    accepted: bool,
    room_count: usize,
}

/// The viewer fetches the most recent payload here. Returns 204 if nothing has
/// been posted yet, so the front-end can show an empty state.
async fn get_rooms(State(state): State<Shared>) -> Result<Json<RoomPayload>, StatusCode> {
    match state.latest.lock().unwrap().clone() {
        Some(payload) => Ok(Json(payload)),
        None => Err(StatusCode::NO_CONTENT),
    }
}

// ---------- Wiring ----------

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info,tower_http=info")
        .init();

    let args = Args::parse();
    let settings = load_settings(&args.settings)
        .with_context(|| format!("bad settings file: {}", args.settings.display()))?;

    tracing::info!("settings loaded from {}", args.settings.display());

    let Settings { sources, test_data } = settings;
    let state: Shared = Arc::new(AppState::new(sources.drofus));

    seed_if_test(&state, test_data.as_ref())?;

    let app = Router::new()
        .route("/rooms", post(ingest_rooms).get(get_rooms))
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
