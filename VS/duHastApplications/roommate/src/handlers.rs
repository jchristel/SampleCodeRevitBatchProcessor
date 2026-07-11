//! HTTP handlers for `/rooms`, `/projects`, and validation: thin Axum
//! adapters over `service/` (see HANDOVER-service-layer.md). Each handler
//! extracts its own input form, calls exactly one `service` function, and
//! translates the result into HTTP -- `StatusCode`, `Query`, `Path`, `Json`
//! never leak past this file.
//!
//! Ingest (`ingest_rooms` / `ingest_rooms_stream`) is the exception: it has no
//! derive logic worth sharing with the MCP server (which deliberately exposes
//! no ingest -- see `src/bin/mcp.rs`), so it stays here in full per the
//! handover doc.

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

/// Reject a project/model id that can't safely become a filesystem path
/// component. `FsStore` builds paths as `root/<project_id>/<model_id>` straight
/// from these ids, and the client currently sends the Revit document *title*
/// as the model id — a title containing `/`, `\`, or `..` would be a path
/// traversal out of the storage root. Same startup-loud spirit as settings
/// validation, applied at the ingest trust boundary; shared by both ingest
/// handlers, and the predicate itself (`state::is_path_safe_component`) is
/// shared with the settings API so the two agree on what a safe id is.
fn validate_id(kind: &str, id: &str) -> Result<(), (StatusCode, String)> {
    if !crate::state::is_path_safe_component(id) {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("{kind} id {id:?} is empty or contains characters unsafe for storage paths"),
        ));
    }
    Ok(())
}

/// Every pre-flight check both ingest routes share, in one place so the
/// buffered and streaming paths can't drift on what gets rejected:
/// - a schema version this server doesn't speak;
/// - a project with no registered settings — rejected rather than lazily
///   accepted, pairing with `assemble_rooms`'s "skip on read" policy (see
///   HANDOVER-per-project-settings.md): a project must be explicitly
///   onboarded (a settings file registered under its id, or an explicit
///   `is_default` fallback) before it can push at all;
/// - identity ids unsafe as storage path components (`validate_id`);
/// - a `taken_at` unsafe as a snapshot *filename* (`validate_taken_at`).
///
/// Takes already-parsed identity fields (not a payload) so the streaming
/// route can run it from the envelope line alone, before reading any rooms.
fn validate_ingest(
    state: &Shared,
    schema_version: u32,
    project_id: &str,
    model_id: &str,
    taken_at: &str,
) -> Result<(), (StatusCode, String)> {
    if schema_version != SUPPORTED_SCHEMA {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("schema_version {schema_version} not supported; this server speaks {SUPPORTED_SCHEMA}"),
        ));
    }
    if state.settings().settings_for(project_id).is_none() {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("no settings configured for project '{project_id}'"),
        ));
    }
    validate_id("project", project_id)?;
    validate_id("model", model_id)?;
    validate_taken_at(taken_at)
}

/// `taken_at` becomes the snapshot *filename* (`FsStore::snapshot_filename`),
/// so it gets the same trust-boundary treatment as the ids -- with two
/// differences: `:` is allowed (ISO-8601 needs it; the store sanitises it
/// before filesystem use), and an empty value is rejected because it would
/// produce a file literally named `.json` and wreck the store's
/// lexical-max-is-newest ordering.
fn validate_taken_at(taken_at: &str) -> Result<(), (StatusCode, String)> {
    let bad = taken_at.trim().is_empty()
        || taken_at.contains("..")
        || taken_at.contains(['/', '\\', '<', '>', '"', '|', '?', '*'])
        || taken_at.chars().any(|c| c.is_control());
    if bad {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            format!("snapshot taken_at {taken_at:?} is empty or contains characters unsafe for storage filenames"),
        ));
    }
    Ok(())
}

/// Revit posts room data here. Returns 200 with a short summary, or 422 if the
/// payload fails any `validate_ingest` check.
pub async fn ingest_rooms(
    State(state): State<Shared>,
    Json(payload): Json<RoomPayload>,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    validate_ingest(
        &state,
        payload.schema_version,
        &payload.project.id,
        &payload.model.id,
        &payload.snapshot.taken_at,
    )?;

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

    // Same pre-flight as the buffered path -- run as soon as the envelope is
    // parsed, before the (potentially large) room stream is read at all.
    validate_ingest(
        &state,
        envelope.schema_version,
        &envelope.project.id,
        &envelope.model.id,
        &envelope.snapshot.taken_at,
    )?;

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
/// handler below returned before the service extraction. Only `Internal`
/// exists today (variants join with their first producer -- see
/// `ServiceError`), so every service failure is a 500.
fn map_service_error(err: ServiceError) -> StatusCode {
    match err {
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
/// 204 when nothing has ever been posted (the service's `None` case); a
/// project/building filter matching nothing still returns 200 with empty
/// arrays. `RoomsResult` serializes directly — every field is wire shape, so
/// no hand-built JSON is needed here.
pub async fn get_rooms(
    State(state): State<Shared>,
    Query(query): Query<RoomsQuery>,
) -> Result<Json<rooms::RoomsResult>, StatusCode> {
    let result = rooms::assemble_rooms(&state, query.project.as_deref(), query.building.as_deref())
        .map_err(map_service_error)?;

    match result {
        None => Err(StatusCode::NO_CONTENT),
        Some(result) => Ok(Json(result)),
    }
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
        match result {
            Err(status) => assert_eq!(status, StatusCode::NO_CONTENT),
            Ok(_) => panic!("expected 204 for an empty store"),
        }
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

        assert!(result.0.rooms.is_empty());
    }

    /// A project/model id that could escape the storage root as a path
    /// component -- or a `taken_at` that could escape the model dir as a
    /// filename -- is rejected 422 before anything is written: ids become
    /// `root/<project_id>/<model_id>` and `taken_at` becomes the snapshot
    /// filename in `FsStore` verbatim.
    #[tokio::test]
    async fn test_ingest_rooms_rejects_path_unsafe_identity() {
        let good_ts = "2026-01-01T00:00:00Z";
        let cases = [
            ("../escape", good_ts),
            ("a/b", good_ts),
            ("a\\b", good_ts),
            ("  ", good_ts),
            ("m1", ""),
            ("m1", "..\\..\\evil"),
            ("m1", "2026/01/01"),
        ];
        for (model_id, taken_at) in cases {
            let payload = RoomPayload {
                schema_version: SUPPORTED_SCHEMA,
                project: Project { id: "p1".to_string(), name: "P".to_string() },
                model: Model { id: model_id.to_string(), name: "M".to_string(), source: "revit".to_string() },
                snapshot: Snapshot { taken_at: taken_at.to_string() },
                levels: vec![],
                rooms: vec![],
            };
            let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

            let result = ingest_rooms(State(state), Json(payload)).await;
            match result {
                Err((status, msg)) => {
                    assert_eq!(status, StatusCode::UNPROCESSABLE_ENTITY, "model {model_id:?} taken_at {taken_at:?}");
                    assert!(msg.contains("unsafe") || msg.contains("empty"), "message names the problem: {msg}");
                }
                Ok(_) => panic!("expected 422 for model {model_id:?} taken_at {taken_at:?}"),
            }
        }

        // A normal ISO timestamp (with its `:`) still passes.
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: good_ts.to_string() },
            levels: vec![],
            rooms: vec![],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));
        assert!(ingest_rooms(State(state), Json(payload)).await.is_ok());
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
