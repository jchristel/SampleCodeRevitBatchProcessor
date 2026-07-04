//! HTTP handlers for `/rooms`: the push (ingest) and the fetch (get).
//!
//! The fetch is where derived data is assembled — dRofus join and classification
//! are resolved *here*, layered onto a `RoomResponse` that leaves the stored
//! snapshot raw. Nothing derived is ever written back to state. This is the
//! "store raw, derive late" discipline made concrete: `/rooms` stays the
//! raw-geometry endpoint, and the join/classification are response-only.
//!
//! Per "endpoints follow fetch lifecycle", derived data that refreshes on its
//! own trigger (an adjacency graph, a `/hierarchy` grouping) earns its own
//! endpoint later — it isn't crammed in here.

use std::collections::BTreeMap;

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};

use crate::classify::{classify_room, TierValue};
use crate::contract::{lookup_property, Room, RoomPayload, SUPPORTED_SCHEMA};
use crate::drofus::DrofusRecord;
use crate::settings::HierarchyTier;
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

/// A room as sent to the viewer: the stored room plus any attached dRofus data
/// and its resolved classification path. Separate response type so the join
/// never mutates the stored snapshot, and so dRofus stays a distinct sub-object
/// (its own lifecycle — it will later refresh on its own trigger, so it must
/// not be fused into the room's own properties).
#[derive(Serialize)]
pub struct RoomResponse {
    #[serde(flatten)]
    pub room: Room,

    /// Present only when the room's link value matched a dRofus record.
    /// Absent (skipped) otherwise — an unmatched key is a signal, not an error.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub drofus: Option<DrofusRecord>,

    /// Full-depth classification path. Empty when no hierarchy is configured.
    pub classification: Vec<TierValue>,
}

/// Assemble one room's response: raw room + dRofus join + classification.
/// Pulled out so the single- and multi-model paths derive rooms identically —
/// the join/classify logic lives in exactly one place.
///
/// `source` comes from the owning model's `Model.source` (e.g. "revit") — it
/// picks which `BuiltinPropertyDef.by_source` entry `lookup_property` uses to
/// resolve a canonical name to this room's actual raw property name.
fn assemble_room(state: &Shared, room: &Room, source: &str) -> RoomResponse {
    // dRofus join: read the link property off the room, look up the record.
    let drofus = state.drofus.as_ref().and_then(|d| {
        lookup_property(room, &d.link_property, source, &state.builtin_properties)
            .and_then(|key| d.by_id.get(&key).cloned())
    });

    // Classification resolved fresh — see staleness note on classify_room.
    let classification = classify_room(room, &state.hierarchy, source, &state.builtin_properties);

    RoomResponse { room: room.clone(), drofus, classification }
}

/// One known project, for the `/projects` picker.
#[derive(Serialize)]
pub struct ProjectSummary {
    pub id: String,
    pub name: String,
}

/// Lists every project with at least one stored model. Derived from
/// `all_snapshots()` — a project's identity already rides on every payload it
/// stores, so no dedicated storage query is needed. `200 []` when nothing has
/// been pushed yet: an empty list is a perfectly good answer for a picker,
/// unlike `/rooms`'s 204 (which exists for the poller's specific
/// "nothing posted yet" signal).
pub async fn get_projects(State(state): State<Shared>) -> Result<Json<Vec<ProjectSummary>>, StatusCode> {
    let stored = state.all_snapshots().map_err(|e| {
        tracing::error!("failed to read snapshots: {e:#}");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    let mut seen: BTreeMap<String, String> = BTreeMap::new();
    for (_key, payload) in &stored {
        seen.entry(payload.project.id.clone())
            .or_insert_with(|| payload.project.name.clone());
    }

    let mut projects: Vec<ProjectSummary> = seen
        .into_iter()
        .map(|(id, name)| ProjectSummary { id, name })
        .collect();
    projects.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(Json(projects))
}

/// Sentinel `building` key for rooms whose "Building" tier didn't resolve —
/// distinct from any real `building_key` output since real keys never start
/// with `__`.
const UNCLASSIFIED_BUILDING_KEY: &str = "__unclassified__";

/// Opaque token identifying one building bucket, built from its resolved
/// `(code, name)` pair. Callers (the browser) never decode this — they just
/// echo it back to `/rooms?building=..` — so the encoding only has to be
/// stable and collision-free for the lifetime of one response, not
/// human-meaningful.
fn building_key(code: &Option<String>, name: &Option<String>) -> String {
    format!("{}|{}", code.as_deref().unwrap_or(""), name.as_deref().unwrap_or(""))
}

/// Index of the hierarchy tier named "Building", if one is configured.
/// Shared by `get_project_buildings` and the `/rooms` building filter so both
/// resolve the exact same tier the exact same way.
fn building_tier_index(hierarchy: &[HierarchyTier]) -> Option<usize> {
    hierarchy.iter().position(|t| t.name == "Building")
}

/// One building bucket, for the `/projects/{id}/buildings` picker.
#[derive(Serialize)]
pub struct BuildingSummary {
    /// Opaque — pass straight through to `/rooms?building=..`.
    pub key: String,
    pub code: Option<String>,
    pub name: Option<String>,
    /// True only for the synthetic "rooms with no Building tier value" bucket.
    pub unclassified: bool,
}

#[derive(Serialize)]
pub struct BuildingsResponse {
    /// False when no hierarchy tier is named "Building" — filtering isn't
    /// possible, and the whole project is effectively one building. Not an
    /// error: a project with no classification configured is a normal state.
    pub tier_configured: bool,
    pub buildings: Vec<BuildingSummary>,
}

/// Lists the distinct "Building" classification values found across every
/// room in one project's stored models, using `classify_room` exactly as it
/// already runs for `/rooms` — building selection has no identity or storage
/// of its own, it's a filter over the classification that already exists.
pub async fn get_project_buildings(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<BuildingsResponse>, StatusCode> {
    let Some(idx) = building_tier_index(&state.hierarchy) else {
        return Ok(Json(BuildingsResponse { tier_configured: false, buildings: vec![] }));
    };

    let stored = state.all_snapshots().map_err(|e| {
        tracing::error!("failed to read snapshots: {e:#}");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    // key -> (code, name). An unrecognized project_id just yields zero rows
    // below, not an error — consistent with how an unmatched dRofus/level key
    // is a signal, not a failure, elsewhere in this project.
    let mut classified: BTreeMap<String, (Option<String>, Option<String>)> = BTreeMap::new();
    let mut has_unclassified = false;

    for (_key, payload) in &stored {
        if payload.project.id != project_id {
            continue;
        }
        for room in &payload.rooms {
            let path = classify_room(room, &state.hierarchy, &payload.model.source, &state.builtin_properties);
            let Some(tier) = path.get(idx) else { continue };
            if tier.undefined {
                has_unclassified = true;
            } else {
                classified
                    .entry(building_key(&tier.code, &tier.name))
                    .or_insert_with(|| (tier.code.clone(), tier.name.clone()));
            }
        }
    }

    let mut buildings: Vec<BuildingSummary> = classified
        .into_iter()
        .map(|(key, (code, name))| BuildingSummary { key, code, name, unclassified: false })
        .collect();
    buildings.sort_by(|a, b| {
        a.name
            .as_deref()
            .unwrap_or("")
            .cmp(b.name.as_deref().unwrap_or(""))
            .then_with(|| a.code.as_deref().unwrap_or("").cmp(b.code.as_deref().unwrap_or("")))
    });
    // Only a real, non-phantom option: emitted solely when a room actually
    // landed there.
    if has_unclassified {
        buildings.push(BuildingSummary {
            key: UNCLASSIFIED_BUILDING_KEY.to_string(),
            code: None,
            name: None,
            unclassified: true,
        });
    }

    Ok(Json(BuildingsResponse { tier_configured: true, buildings }))
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

/// The viewer fetches here. Now that the store holds *many* models, this merges
/// every stored model's levels and rooms into one flat payload — so the viewer
/// (which expects flat `levels` + `rooms`) keeps working unchanged against a
/// keyed store. Returns 204 when nothing has been posted yet.
///
/// `?project=..` scopes the merge to one project; `?building=..` (the opaque
/// key from `/projects/{id}/buildings`) additionally filters *rooms* by their
/// resolved "Building" tier value. If no tier is named "Building", `building`
/// is a no-op rather than an error — same graceful degrade as the buildings
/// endpoint. A model contributes its `levels` only when it contributed at
/// least one matching room: levels are their own array from a separate Revit
/// export, so a floor can legitimately have zero rooms of a given building
/// right now yet still belong to it — dropping it would make the slider
/// flicker as classification changes. This rule only applies when a building
/// filter is actually active; with no filter, every scoped model's levels are
/// included exactly as before.
///
/// dRofus join and classification are resolved here at response assembly — the
/// stored snapshots stay raw; derived data is never written back to state.
pub async fn get_rooms(
    State(state): State<Shared>,
    Query(query): Query<RoomsQuery>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let stored = state.all_snapshots().map_err(|e| {
        tracing::error!("failed to read snapshots: {e:#}");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;
    if stored.is_empty() {
        return Err(StatusCode::NO_CONTENT);
    }

    let scoped: Vec<_> = stored
        .iter()
        .filter(|(_key, payload)| {
            query.project.as_deref().map_or(true, |p| payload.project.id == p)
        })
        .collect();

    let building_idx = building_tier_index(&state.hierarchy);
    let building_filter_active = query.building.is_some() && building_idx.is_some();

    let mut levels = Vec::new();
    let mut rooms: Vec<RoomResponse> = Vec::new();

    for (_key, payload) in &scoped {
        let matching_rooms: Vec<&Room> = if let (Some(wanted), Some(idx)) = (&query.building, building_idx) {
            payload
                .rooms
                .iter()
                .filter(|room| {
                    let path = classify_room(room, &state.hierarchy, &payload.model.source, &state.builtin_properties);
                    match path.get(idx) {
                        Some(tier) if tier.undefined => wanted == UNCLASSIFIED_BUILDING_KEY,
                        Some(tier) => building_key(&tier.code, &tier.name) == *wanted,
                        None => false,
                    }
                })
                .collect()
        } else {
            payload.rooms.iter().collect()
        };

        if building_filter_active && matching_rooms.is_empty() {
            continue; // this model contributed nothing to the requested building
        }

        levels.extend(payload.levels.iter().cloned());
        rooms.extend(
            matching_rooms
                .into_iter()
                .map(|room| assemble_room(&state, room, &payload.model.source)),
        );
    }

    // Report the accepted schema version (all stored payloads share it — the
    // ingest check guarantees it), so the viewer's version check still holds.
    Ok(Json(serde_json::json!({
        "schema_version": SUPPORTED_SCHEMA,
        "levels": levels,
        "rooms": rooms,
    })))
}
