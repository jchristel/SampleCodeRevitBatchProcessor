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

use crate::contract::{ModelToShared, Room, RoomPayload, StreamEnvelope, SUPPORTED_SCHEMA};
use crate::service::areas;
use crate::service::comparison::{self, ComparisonResponse};
use crate::service::drofus::{DrofusSnapshotInfo, DrofusSnapshotList};
use crate::service::milestones::MilestonesResponse;
use crate::service::projects::{BuildingsResponse, ProjectSummary};
use crate::service::snapshots::{LatestSnapshot, ProjectSnapshotsResponse};
use crate::service::validation::ValidationResponse;
use crate::service::{drofus, milestones, projects, rooms, snapshots, validation, ServiceError};
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
/// - a `taken_at` that isn't an RFC3339 UTC date-time (`validate_taken_at`).
///
/// Callers resolve a blank `taken_at` (`contract::ensure_taken_at`) BEFORE
/// this runs, so the id checked here is always the one the store will key on.
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

/// The snapshot id rule lives in the contract (`validate_snapshot_id`:
/// RFC3339, expressed in UTC); this is just its 422 adapter. The date-time
/// requirement subsumes the old per-character filename-safety checks — no
/// RFC3339 string can contain `/`, `\`, or `..` — and the store still
/// sanitises the one filename-hostile character it does contain (`:`) before
/// filesystem use.
fn validate_taken_at(taken_at: &str) -> Result<(), (StatusCode, String)> {
    crate::contract::validate_snapshot_id(taken_at).map_err(|e| (StatusCode::UNPROCESSABLE_ENTITY, e))
}

/// Tolerance for the `model_to_shared` rigidity check: the linear part should be
/// a pure rotation (`|det| ≈ 1`). Generous — its only job is to catch a matrix
/// that has silently picked up scale/shear, not to police float noise.
const MODEL_TO_SHARED_DET_TOL: f64 = 1e-6;

/// Warn (never reject) when a push carries a `model_to_shared` whose linear part
/// isn't a pure rotation — a scaled/sheared transform would silently distort
/// placement. This is advisory only (HANDOVER-georeferencing.md "the underlay is
/// non-load-bearing"; "signal, not error"): the geometry still stores and
/// renders, so a 422 would be wrong here. A missing transform is the normal
/// un-placed case and warns nothing.
fn warn_on_transform_drift(model_to_shared: Option<&ModelToShared>, project_id: &str, model_id: &str) {
    if let Some(m) = model_to_shared
        && !m.is_rigid(MODEL_TO_SHARED_DET_TOL)
    {
        tracing::warn!(
            "model_to_shared for {project_id}/{model_id} is not a pure rotation \
             (|det| = {:.6}, expected ≈ 1); placement may be distorted",
            m.determinant().abs()
        );
    }
}

/// Revit posts room data here. Returns 200 with a short summary, or 422 if the
/// payload fails any `validate_ingest` check. A blank/omitted snapshot id is
/// minted server-side first (`ensure_taken_at`); the response always carries
/// the resolved id so the pusher can attach follow-up uploads to it.
pub async fn ingest_rooms(
    State(state): State<Shared>,
    Json(mut payload): Json<RoomPayload>,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    let snapshot_id_generated = crate::contract::ensure_taken_at(&mut payload.snapshot);
    validate_ingest(
        &state,
        payload.schema_version,
        &payload.project.id,
        &payload.model.id,
        &payload.snapshot.taken_at,
    )?;
    warn_on_transform_drift(payload.model_to_shared.as_ref(), &payload.project.id, &payload.model.id);

    let count = payload.rooms.len();
    let snapshot_taken_at = payload.snapshot.taken_at.clone();
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
        snapshot_taken_at,
        snapshot_id_generated,
    }))
}

#[derive(Serialize)]
pub struct IngestResponse {
    pub accepted: bool,
    pub room_count: usize,
    /// The snapshot id this push was stored under — echoed back (or minted,
    /// see `snapshot_id_generated`) so the pusher can associate follow-up
    /// uploads with this exact snapshot.
    pub snapshot_taken_at: String,
    /// True when the server minted the id above because the payload left it
    /// blank; false when the payload supplied one and the server used it.
    ///
    /// It describes the *id*, not the snapshot: whether a snapshot was stored
    /// is reported by `accepted`/`room_count`. A producer that stamps its own
    /// `taken_at` (as the Revit one always does) therefore sees `false` here
    /// on every successful push.
    pub snapshot_id_generated: bool,
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

    let mut envelope: StreamEnvelope = serde_json::from_str(&envelope_line)
        .map_err(|e| (StatusCode::BAD_REQUEST, format!("bad envelope: {e}")))?;

    // Same resolve-then-pre-flight as the buffered path -- run as soon as the
    // envelope is parsed, before the (potentially large) room stream is read.
    let snapshot_id_generated = crate::contract::ensure_taken_at(&mut envelope.snapshot);
    validate_ingest(
        &state,
        envelope.schema_version,
        &envelope.project.id,
        &envelope.model.id,
        &envelope.snapshot.taken_at,
    )?;
    warn_on_transform_drift(envelope.model_to_shared.as_ref(), &envelope.project.id, &envelope.model.id);

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

    let snapshot_taken_at = envelope.snapshot.taken_at.clone();
    let payload = RoomPayload {
        schema_version: envelope.schema_version,
        project: envelope.project,
        model: envelope.model,
        snapshot: envelope.snapshot,
        model_to_shared: envelope.model_to_shared,
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

    Ok(Json(IngestResponse { accepted: true, room_count: count, snapshot_taken_at, snapshot_id_generated }))
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

/// Lists every stored snapshot id for one project, grouped per model — see
/// `service::snapshots::list_project_snapshots`.
pub async fn get_project_snapshots(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<ProjectSnapshotsResponse>, StatusCode> {
    let result = snapshots::list_project_snapshots(&state, &project_id).map_err(map_service_error)?;
    Ok(Json(result))
}

/// The latest snapshot id for one model — the cheap "what snapshot do I
/// attach my follow-up upload to" call. 404 when the model (or its project)
/// has no latest: unlike the listing's soft empty success, this names one
/// specific resource — see `service::snapshots::latest_snapshot`.
pub async fn get_model_latest_snapshot(
    State(state): State<Shared>,
    Path((project_id, model_id)): Path<(String, String)>,
) -> Result<Json<LatestSnapshot>, StatusCode> {
    let result = snapshots::latest_snapshot(&state, &project_id, &model_id).map_err(map_service_error)?;
    match result {
        None => Err(StatusCode::NOT_FOUND),
        Some(latest) => Ok(Json(latest)),
    }
}

/// Lists every uploaded dRofus snapshot id for one project — see
/// `service::drofus::list_drofus_snapshots`. Soft-empty for unknown
/// projects, same as the model-snapshot listing.
pub async fn get_drofus_snapshots(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<DrofusSnapshotList>, StatusCode> {
    let result = drofus::list_drofus_snapshots(&state, &project_id).map_err(map_service_error)?;
    Ok(Json(result))
}

/// A parsed summary of the latest uploaded dRofus CSV for one project — see
/// `service::drofus::get_drofus_snapshot`. 404 when there is none: this
/// names one specific resource, same convention as
/// `get_model_latest_snapshot`.
pub async fn get_drofus_latest(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<DrofusSnapshotInfo>, StatusCode> {
    let result = drofus::get_drofus_snapshot(&state, &project_id, None).map_err(map_service_error)?;
    match result {
        None => Err(StatusCode::NOT_FOUND),
        Some(info) => Ok(Json(info)),
    }
}

/// Lists one project's milestones for the viewer's picker — see
/// `service::milestones::list_milestones`.
pub async fn get_project_milestones(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<MilestonesResponse>, StatusCode> {
    let result = milestones::list_milestones(&state, &project_id).map_err(map_service_error)?;
    Ok(Json(result))
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

/// Optional scoping for `GET /rooms`. All absent keeps today's behaviour:
/// merge every stored model globally (backwards compatible). `milestone`
/// names a per-project milestone; models are then served from the snapshots
/// that milestone pins instead of their latest (see
/// `service::rooms::assemble_rooms`).
#[derive(Deserialize)]
pub struct RoomsQuery {
    #[serde(default)]
    pub project: Option<String>,
    #[serde(default)]
    pub building: Option<String>,
    #[serde(default)]
    pub milestone: Option<String>,
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
    let result = rooms::assemble_rooms(
        &state,
        query.project.as_deref(),
        query.building.as_deref(),
        query.milestone.as_deref(),
    )
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

/// Optional building/milestone scoping for `GET /projects/{id}/areas` (the
/// project itself is the path id). Same scoping vocabulary as `/rooms`.
#[derive(Deserialize)]
pub struct AreasQuery {
    #[serde(default)]
    pub building: Option<String>,
    #[serde(default)]
    pub milestone: Option<String>,
}

/// Hierarchy gross-area footprints for one project — see
/// `service::areas::assemble_areas`. 204 when nothing has ever been posted
/// (mirrors `/rooms`); a scope matching nothing is 200 with empty `groups`.
pub async fn get_project_areas(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
    Query(query): Query<AreasQuery>,
) -> Result<Json<areas::AreasResult>, StatusCode> {
    let result = areas::assemble_areas(&state, &project_id, query.building.as_deref(), query.milestone.as_deref())
        .map_err(map_service_error)?;
    match result {
        None => Err(StatusCode::NO_CONTENT),
        Some(result) => Ok(Json(result)),
    }
}

/// The baseline milestone plus the milestones to compare against it. A POST
/// body rather than query params because the compared set is a list (repeated
/// query keys don't deserialize cleanly, and milestone names can contain any
/// character) — the same POST-that-reads shape `drofus-check` uses.
#[derive(Deserialize)]
pub struct ComparisonRequest {
    pub baseline: String,
    #[serde(default)]
    pub others: Vec<String>,
}

/// Milestone comparison for one project — see
/// `service::comparison::compare_milestones`. A read, but POST-shaped for its
/// list input. A project with no `comparison_key` configured returns 200 with
/// `comparison_key_configured: false` (a real state the client renders), not an
/// error.
pub async fn compare_project_milestones(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
    Json(req): Json<ComparisonRequest>,
) -> Result<Json<ComparisonResponse>, StatusCode> {
    let result = comparison::compare_milestones(&state, &project_id, &req.baseline, &req.others)
        .map_err(map_service_error)?;
    Ok(Json(result))
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
            milestones: vec![],
            comparison_key: None,
            comparison_properties: vec![],
            hierarchy_exclusions: vec![],        }
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

        let result = get_rooms(State(state), Query(RoomsQuery { project: None, building: None, milestone: None })).await;
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
            model_to_shared: None,
            levels: vec![Level { id: "l1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));
        state.set_snapshot(payload).unwrap();

        let result = get_rooms(
            State(state),
            Query(RoomsQuery { project: Some("nonexistent".to_string()), building: None, milestone: None }),
        )
        .await
        .unwrap();

        assert!(result.0.rooms.is_empty());
    }

    /// A project/model id that could escape the storage root as a path
    /// component -- or a `taken_at` that isn't an RFC3339 UTC date-time
    /// (which rules out anything path-shaped) -- is rejected 422 before
    /// anything is written: ids become `root/<project_id>/<model_id>` and
    /// `taken_at` becomes the snapshot filename in `FsStore`.
    #[tokio::test]
    async fn test_ingest_rooms_rejects_path_unsafe_identity() {
        let good_ts = "2026-01-01T00:00:00Z";
        let cases = [
            ("../escape", good_ts),
            ("a/b", good_ts),
            ("a\\b", good_ts),
            ("  ", good_ts),
            ("m1", "..\\..\\evil"),
            ("m1", "2026/01/01"),
            ("m1", "2026-01-01T00:00:00+10:00"), // parses, but not UTC
        ];
        for (model_id, taken_at) in cases {
            let payload = RoomPayload {
                schema_version: SUPPORTED_SCHEMA,
                project: Project { id: "p1".to_string(), name: "P".to_string() },
                model: Model { id: model_id.to_string(), name: "M".to_string(), source: "revit".to_string() },
                snapshot: Snapshot { taken_at: taken_at.to_string() },
                model_to_shared: None,
                levels: vec![],
                rooms: vec![],
            };
            let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

            let result = ingest_rooms(State(state), Json(payload)).await;
            match result {
                Err((status, msg)) => {
                    assert_eq!(status, StatusCode::UNPROCESSABLE_ENTITY, "model {model_id:?} taken_at {taken_at:?}");
                    assert!(
                        msg.contains("unsafe") || msg.contains("RFC3339") || msg.contains("UTC"),
                        "message names the problem: {msg}"
                    );
                }
                Ok(_) => panic!("expected 422 for model {model_id:?} taken_at {taken_at:?}"),
            }
        }

        // A normal ISO timestamp (with its `:`) still passes, and is echoed
        // back untouched.
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: good_ts.to_string() },
            model_to_shared: None,
            levels: vec![],
            rooms: vec![],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));
        let response = ingest_rooms(State(state), Json(payload)).await.unwrap();
        assert_eq!(response.0.snapshot_taken_at, good_ts);
        assert!(!response.0.snapshot_id_generated);
    }

    /// The ingest response's JSON keys are the producer-facing contract (the
    /// pyRevit client reads this body), so they're asserted as *text*: the
    /// Rust-side assertions elsewhere in this module would survive a rename
    /// that silently broke every consumer.
    #[test]
    fn test_ingest_response_wire_keys() {
        let json = serde_json::to_string(&IngestResponse {
            accepted: true,
            room_count: 26,
            snapshot_taken_at: "2026-07-15T11:18:58.186000Z".to_string(),
            snapshot_id_generated: false,
        })
        .unwrap();

        assert!(json.contains(r#""snapshot_id_generated":false"#), "unexpected wire shape: {json}");
        assert!(json.contains(r#""snapshot_taken_at":"2026-07-15T11:18:58.186000Z""#));
        assert!(json.contains(r#""room_count":26"#));
    }

    /// A blank (or omitted -- serde defaults it to blank) snapshot id is no
    /// longer an error: the server mints one and the response carries it, so
    /// the pusher can attach follow-up uploads to the same snapshot.
    #[tokio::test]
    async fn test_ingest_rooms_generates_snapshot_id_when_blank() {
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "".to_string() },
            model_to_shared: None,
            levels: vec![],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

        let response = ingest_rooms(State(state.clone()), Json(payload)).await.unwrap();

        assert!(response.0.snapshot_id_generated);
        assert!(crate::contract::validate_snapshot_id(&response.0.snapshot_taken_at).is_ok());
        // The store keyed the push under exactly the id the response reports.
        let key = crate::state::ModelKey { project_id: "p1".into(), model_id: "m1".into() };
        assert_eq!(state.list_snapshot_ids(&key).unwrap(), vec![response.0.snapshot_taken_at.clone()]);
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
            model_to_shared: None,
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

    /// A push carrying a `model_to_shared` is accepted and the transform is
    /// stored on the snapshot verbatim -- it rides the envelope end to end.
    #[tokio::test]
    async fn test_ingest_rooms_stores_model_to_shared() {
        let matrix = [0.9704980833640151, -0.2411088347339701, 0.2411088347339701, 0.9704980833640151, 945737.6, 20545096.5];
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            model_to_shared: Some(ModelToShared { matrix }),
            levels: vec![],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

        let _ = ingest_rooms(State(state.clone() as Shared), Json(payload)).await.expect("accepted");

        let stored = state.all_snapshots().unwrap();
        let (_, payload) = stored.iter().find(|(k, _)| k.model_id == "m1").expect("stored");
        assert_eq!(payload.model_to_shared.expect("carried through").matrix, matrix);
    }

    /// A `model_to_shared` whose linear part isn't a pure rotation (here a 2×
    /// scale, |det| = 4) is still *accepted* -- the drift is a `tracing::warn!`,
    /// never a 422 (advisory only; the geometry still stores and renders).
    #[tokio::test]
    async fn test_ingest_rooms_accepts_non_rigid_model_to_shared() {
        let payload = RoomPayload {
            schema_version: SUPPORTED_SCHEMA,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            model_to_shared: Some(ModelToShared { matrix: [2.0, 0.0, 0.0, 2.0, 0.0, 0.0] }),
            levels: vec![],
            rooms: vec![make_room("r1", "Room A")],
        };
        let state: Shared = std::sync::Arc::new(AppState::new(Box::new(MemStore::new()), single_project("p1"), None));

        let response = ingest_rooms(State(state), Json(payload)).await.expect("accepted despite det drift");
        assert!(response.0.accepted);
    }
}
