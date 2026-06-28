use std::sync::{Arc, Mutex};

use axum::{
    extract::State,
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

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
#[derive(Default)]
struct AppState {
    latest: Mutex<Option<RoomPayload>>,
}

type Shared = Arc<AppState>;

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

    *state.latest.lock().unwrap() = Some(payload);

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
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter("revit_viewer=info,tower_http=info")
        .init();

    let state: Shared = Arc::new(AppState::default());

    let app = Router::new()
        .route("/rooms", post(ingest_rooms).get(get_rooms))
        // Serves the viewer page at "/" from ./static.
        .fallback_service(ServeDir::new("static"))
        // Lets the browser viewer call /rooms even if served from elsewhere.
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = "127.0.0.1:5151";
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    tracing::info!("viewer on http://{addr}  (POST room JSON to http://{addr}/rooms)");
    axum::serve(listener, app).await.unwrap();
}
