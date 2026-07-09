//! HTTP handlers for `/rooms`, `/projects`, and validation: thin Axum
//! adapters over `service/` (see HANDOVER-service-layer.md). Each handler
//! extracts its own input form, calls exactly one `service` function, and
//! translates the result into HTTP -- `StatusCode`, `Query`, `Path`, `Json`
//! never leak past this file.
//!
//! Ingest (`ingest_rooms` / `ingest_rooms_stream`) is the exception: it has no
//! derive logic worth sharing with a future MCP server, so it stays here in
//! full per the handover doc.

use axum::{
    body::Body,
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use futures_util::StreamExt;
use serde::{Deserialize, Serialize};
use tokio::io::AsyncBufReadExt;
use tokio_util::io::StreamReader;

use crate::contract::{Room, RoomPayload, StreamEnvelope, SUPPORTED_SCHEMA};
use crate::service::projects::{BuildingsResponse, ProjectSummary};
use crate::service::validation::ValidationResponse;
use crate::service::{projects, rooms, validation, ServiceError};
use crate::state::Shared;

/// Revit posts room data here. Returns 200 with a short summary, or 422 if the
/// schema version is one this server doesn't understand.
pub async fn ingest_rooms(
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

    // A push for a project with no registered settings is rejected rather
    // than lazily accepted — pairs with `assemble_rooms`'s "skip on read"
    // policy (see HANDOVER-per-project-settings.md): a project must be
    // explicitly onboarded (a settings file registered under its id, or an
    // explicit `is_default` fallback) before it can push at all.
    if state.settings_for(&payload.project.id).is_none() {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("no settings configured for project '{}'", payload.project.id),
        ));
    }

    let count = payload.rooms.len();
    tracing::info!("received {} room(s)", count);

    // Persist. A storage failure (unwritable disk, etc.) is a real server error,
    // not a bad request — surface it as 500 rather than swallowing it.
    state.set_snapshot(payload).map_err(|e| {
        tracing::error!("failed to store snapshot: {e:#}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("could not store snapshot: {e}"),
        )
    })?;

    Ok(Json(IngestResponse {
        accepted: true,
        room_count: count,
    }))
}

#[derive(Serialize)]
pub struct IngestResponse {
    pub accepted: bool,
    pub room_count: usize,
}

/// Streaming ingest for very large models (NDJSON, see HANDOVER-streaming.md).
/// Reads the request body as a line-delimited stream instead of buffering it
/// whole with `Json<RoomPayload>`, so peak memory is one line, not the entire
/// (possibly >100 MB) payload. Line 1 is the envelope (identity + levels, no
/// rooms); every following line is one `Room`. If `RequestDecompressionLayer`
/// is in front (see `main.rs`), this stream is already the inflated bytes --
/// gzip and streaming compose without either side knowing about the other.
///
/// Rooms are still accumulated into a `Vec` before handing the assembled
/// `RoomPayload` to the existing store, so storage and everything downstream
/// stays byte-for-byte identical to the buffered path -- streaming changes
/// only how the body is *read*. Honest limitation: peak memory is therefore
/// the in-memory room set, not the raw JSON text (still a real win, since the
/// text is ~40% empty-string overhead). If even that Vec is too large, the
/// next step is a `SnapshotStore::put_streaming` that writes rooms to disk as
/// they arrive -- deferred until the Vec itself is the ceiling.
pub async fn ingest_rooms_stream(
    State(state): State<Shared>,
    body: Body,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    let stream = body
        .into_data_stream()
        .map(|r| r.map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e)));
    let reader = StreamReader::new(stream);
    let mut lines = reader.lines();

    let envelope_line = lines
        .next_line()
        .await
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("read error: {e}")))?
        .ok_or((StatusCode::BAD_REQUEST, "empty body".into()))?;

    let envelope: StreamEnvelope = serde_json::from_str(&envelope_line)
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("bad envelope: {e}")))?;

    if envelope.schema_version != SUPPORTED_SCHEMA {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!(
                "schema_version {} not supported; this server speaks {}",
                envelope.schema_version, SUPPORTED_SCHEMA
            ),
        ));
    }

    // Same registration check as the buffered path -- checked as soon as the
    // envelope's project id is known, before the (potentially large) room
    // stream is read at all.
    if state.settings_for(&envelope.project.id).is_none() {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("no settings configured for project '{}'", envelope.project.id),
        ));
    }

    let mut rooms: Vec<Room> = Vec::new();
    while let Some(line) = lines
        .next_line()
        .await
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("read error: {e}")))?
    {
        if line.trim().is_empty() {
            continue; // tolerate a trailing blank line
        }
        let room: Room = serde_json::from_str(&line)
            .map_err(|e| (StatusCode::BAD_REQUEST, format!("bad room line: {e}")))?;
        rooms.push(room);
    }

    let count = rooms.len();
    tracing::info!("streamed {} room(s)", count);

    let payload = RoomPayload {
        schema_version: envelope.schema_version,
        project: envelope.project,
        model: envelope.model,
        snapshot: envelope.snapshot,
        levels: envelope.levels,
        rooms,
    };

    state.set_snapshot(payload).map_err(|e| {
        tracing::error!("failed to store snapshot: {e:#}");
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("could not store snapshot: {e}"),
        )
    })?;

    Ok(Json(IngestResponse { accepted: true, room_count: count }))
}

/// `ServiceError` -> `StatusCode`, with no body -- matches what every read
/// handler below returned before this extraction (a bare `StatusCode` on
/// failure, since none of today's failure paths produce a `NotFound`/
/// `BadInput`; the mapping exists for when a future service function does).
fn map_service_error(err: ServiceError) -> StatusCode {
    match err {
        ServiceError::NotFound(msg) => {
            tracing::warn!("not found: {msg}");
            StatusCode::NOT_FOUND
        }
        ServiceError::BadInput(msg) => {
            tracing::warn!("bad input: {msg}");
            StatusCode::BAD_REQUEST
        }
        ServiceError::Internal(e) => {
            tracing::error!("internal service error: {e:#}");
            StatusCode::INTERNAL_SERVER_ERROR
        }
    }
}

/// Lists every project with at least one stored model — see
/// `service::projects::list_projects`. `200 []` when nothing has been pushed
/// yet: an empty list is a perfectly good answer for a picker, unlike
/// `/rooms`'s 204 (which exists for the poller's specific "nothing posted
/// yet" signal).
pub async fn get_projects(State(state): State<Shared>) -> Result<Json<Vec<ProjectSummary>>, StatusCode> {
    let projects = projects::list_projects(&state).map_err(map_service_error)?;
    Ok(Json(projects))
}

/// Lists the distinct "Building" classification values for one project — see
/// `service::projects::list_buildings`.
pub async fn get_project_buildings(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<BuildingsResponse>, StatusCode> {
    let buildings = projects::list_buildings(&state, &project_id).map_err(map_service_error)?;
    Ok(Json(buildings))
}

/// Optional scoping for `GET /rooms`. Both absent keeps today's behaviour:
/// merge every stored model globally (backwards compatible).
#[derive(Deserialize)]
pub struct RoomsQuery {
    #[serde(default)]
    pub project: Option<String>,
    #[serde(default)]
    pub building: Option<String>,
}

/// The viewer fetches here — see `service::rooms::assemble_rooms`. Returns
/// 204 when nothing has ever been posted (`store_empty`); a project/building
/// filter matching nothing still returns 200 with empty arrays.
pub async fn get_rooms(
    State(state): State<Shared>,
    Query(query): Query<RoomsQuery>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let result = rooms::assemble_rooms(&state, query.project.as_deref(), query.building.as_deref())
        .map_err(map_service_error)?;

    if result.store_empty {
        return Err(StatusCode::NO_CONTENT);
    }

    // Report the accepted schema version (all stored payloads share it — the
    // ingest check guarantees it), so the viewer's version check still holds.
    Ok(Json(serde_json::json!({
        "schema_version": result.schema_version,
        "levels": result.levels,
        "rooms": result.rooms,
    })))
}

/// Data-quality report for the header's validation panel — see
/// `service::validation::compute_project_validation`.
pub async fn get_project_validation(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<ValidationResponse>, StatusCode> {
    let report = validation::compute_project_validation(&state, &project_id).map_err(map_service_error)?;
    Ok(Json(report))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Level, Model, Project, Snapshot};
    use crate::drofus::DrofusData;
    use crate::state::{AppState, ProjectSettings};
    use crate::storage::MemStore;
    use std::collections::BTreeMap;

    fn make_room(id: &str, name: &str) -> Room {
        Room { id: id.to_string(), name: name.to_string(), level_id: "1".to_string(), loops: vec![], properties: BTreeMap::new() }
    }

    fn make_drofus() -> DrofusData {
        DrofusData {
            link_property: "Number".to_string(),
            by_id: BTreeMap::new(),
            reconciliation: BTreeMap::new(),
            all_labels: vec![],
        }
    }

    fn make_bundle() -> ProjectSettings {
        ProjectSettings {
            drofus: Some(make_drofus()),
            hierarchy: vec![],
            builtin_properties: vec![],
            room_label: vec!["$name".to_string(), "$id".to_string()],
            drofus_fields: vec![],
        }
    }

    /// Registers one project's bundle under its id -- the shape
    /// `AppState::new` now takes in place of the old five flat fields.
    fn single_project(project_id: &str) -> std::collections::HashMap<String, ProjectSettings> {
        std::collections::HashMap::from([(project_id.to_string(), make_bundle())])
    }

    /// An empty store yields 204 through the full handler, not just at the
    /// service layer -- the one behavior that genuinely lives at the HTTP
    /// seam (`service::rooms::assemble_rooms` has no notion of "204").
    #[tokio::test]
    async fn test_get_rooms_returns_204_when_store_empty() {
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

        let result = get_rooms(State(state), Query(RoomsQuery { project: None, building: None })).await;
        assert_eq!(result.unwrap_err(), StatusCode::NO_CONTENT);
    }

    /// A project filter matching nothing still returns 200 with empty
    /// arrays -- distinct from a truly empty store.
    #[tokio::test]
    async fn test_get_rooms_empty_filter_result_is_200_not_204() {
        let payload = RoomPayload {
            schema_version: 5,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels: vec![Level { id: "l1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));
        state.set_snapshot(payload).unwrap();

        let result = get_rooms(
            State(state),
            Query(RoomsQuery { project: Some("nonexistent".to_string()), building: None }),
        )
        .await
        .unwrap();

        let rooms = result.0["rooms"].as_array().unwrap();
        assert!(rooms.is_empty());
    }

    /// A push for a project with no registered settings (and no default
    /// bundle) is rejected 422, not silently stored -- pairs with
    /// `assemble_rooms`'s "skip on read" for the same case.
    #[tokio::test]
    async fn test_ingest_rooms_rejects_unregistered_project() {
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "unregistered".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels: vec![],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

        let result = ingest_rooms(State(state), Json(payload)).await;
        match result {
            Err((status, _)) => assert_eq!(status, StatusCode::UNPROCESSABLE_ENTITY),
            Ok(_) => panic!("expected 422 for an unregistered project"),
        }
    }
}
