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
use crate::drofus::{DrofusData, DrofusRecord};
use crate::settings::{BuiltinPropertyDef, HierarchyTier};
use crate::state::{ModelKey, Shared};

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

    /// Resolved room-label fields, in the order configured by
    /// `Settings.room_label` (e.g. `["$name", "Area", "$id"]`). Only the
    /// fields that actually resolved — an unconfigured or unresolvable name
    /// contributes nothing, same discipline as `drofus`/`classification`.
    /// The viewer renders whatever's here without needing to know property
    /// names itself.
    pub label: Vec<String>,
}

/// Resolve one room's label fields from the configured, ordered name list.
/// `"$name"` / `"$id"` are intrinsic tokens for `Room`'s own fields (not
/// reachable via `lookup_property`, which only reads `room.properties`);
/// anything else is a canonical property name resolved the same way
/// dRofus/classification already are, so a second source (or a differently-
/// named property) needs no change here.
fn resolve_label_fields(
    room: &Room,
    fields: &[String],
    source: &str,
    builtin_defs: &[BuiltinPropertyDef],
) -> Vec<String> {
    fields
        .iter()
        .filter_map(|name| match name.as_str() {
            "$name" => Some(room.name.clone()).filter(|s| !s.is_empty()),
            "$id" => Some(room.id.clone()),
            canonical => lookup_property(room, canonical, source, builtin_defs),
        })
        .collect()
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

    let label = resolve_label_fields(room, &state.room_label, source, &state.builtin_properties);

    RoomResponse { room: room.clone(), drofus, classification, label }
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

/// One link-property value shared by more than one room — ambiguous, so it's
/// excluded from the unmatched/mismatch checks below rather than guessing
/// which room a dRofus record actually describes.
#[derive(Serialize)]
pub struct DuplicateLinkValue {
    pub value: String,
    pub room_ids: Vec<String>,
}

/// One property where a uniquely-matched room and its dRofus record disagree.
#[derive(Serialize)]
pub struct PropertyMismatch {
    pub room_id: String,
    pub drofus_id: String,
    /// The dRofus field label (row 1) — the same key `reconciliation` and
    /// `DrofusRecord.fields` use.
    pub field: String,
    pub room_value: String,
    pub drofus_value: String,
}

/// Data-quality report for one project's rooms against dRofus, for the
/// header's validation panel. An on-demand aggregate over the whole
/// snapshot, not a per-room render concern — see STRATEGY-SOURCES.md.
#[derive(Serialize)]
pub struct ValidationResponse {
    /// False when no dRofus source is configured at all — every list below
    /// is then empty, not an error (a project not using dRofus is normal).
    pub drofus_configured: bool,
    pub link_property: Option<String>,
    pub total_rooms: usize,
    pub rooms_missing_link_value: Vec<String>,
    pub duplicate_link_values: Vec<DuplicateLinkValue>,
    pub rooms_unmatched_in_drofus: Vec<String>,
    pub property_mismatches: Vec<PropertyMismatch>,
}

impl ValidationResponse {
    fn drofus_not_configured() -> Self {
        Self {
            drofus_configured: false,
            link_property: None,
            total_rooms: 0,
            rooms_missing_link_value: vec![],
            duplicate_link_values: vec![],
            rooms_unmatched_in_drofus: vec![],
            property_mismatches: vec![],
        }
    }
}

/// Pure computation behind `get_project_validation` — pulled out so it's
/// testable without a full `AppState`, same shape as `resolve_label_fields`.
///
/// Four checks, in order: (1) does every room resolve a value for the link
/// property; (2) among those that do, is the value actually unique per room
/// (a shared value is ambiguous — recorded, then excluded from the rest);
/// (3) does each remaining room's value find a dRofus record; (4) for rooms
/// that do, does every reconciled property agree between the two sides.
fn compute_validation(
    project_id: &str,
    stored: &[(ModelKey, RoomPayload)],
    drofus: &DrofusData,
    builtin_defs: &[BuiltinPropertyDef],
) -> ValidationResponse {
    let mut total_rooms = 0;
    let mut rooms_missing_link_value = Vec::new();
    // Resolved link value -> every (room, source) that resolved to it.
    let mut by_value: BTreeMap<String, Vec<(&Room, &str)>> = BTreeMap::new();

    for (_key, payload) in stored {
        if payload.project.id != project_id {
            continue;
        }
        for room in &payload.rooms {
            total_rooms += 1;
            match lookup_property(room, &drofus.link_property, &payload.model.source, builtin_defs) {
                Some(value) => by_value.entry(value).or_default().push((room, &payload.model.source)),
                None => rooms_missing_link_value.push(room.id.clone()),
            }
        }
    }

    let mut duplicate_link_values = Vec::new();
    let mut rooms_unmatched_in_drofus = Vec::new();
    let mut property_mismatches = Vec::new();

    for (value, rooms) in &by_value {
        if rooms.len() > 1 {
            duplicate_link_values.push(DuplicateLinkValue {
                value: value.clone(),
                room_ids: rooms.iter().map(|(r, _)| r.id.clone()).collect(),
            });
            continue; // ambiguous -- can't uniquely match, so no further checks
        }
        let (room, source) = rooms[0];
        let Some(record) = drofus.by_id.get(value) else {
            rooms_unmatched_in_drofus.push(room.id.clone());
            continue;
        };
        for (label, revit_property) in &drofus.reconciliation {
            let drofus_value = record.fields.get(label);
            let room_value = lookup_property(room, revit_property, source, builtin_defs);
            // Only compare when both sides actually have a value -- one side
            // missing is a different problem (absence), not a disagreement.
            if let (Some(drofus_value), Some(room_value)) = (drofus_value, room_value) {
                if drofus_value.trim() != room_value.trim() {
                    property_mismatches.push(PropertyMismatch {
                        room_id: room.id.clone(),
                        drofus_id: value.clone(),
                        field: label.clone(),
                        room_value,
                        drofus_value: drofus_value.clone(),
                    });
                }
            }
        }
    }

    ValidationResponse {
        drofus_configured: true,
        link_property: Some(drofus.link_property.clone()),
        total_rooms,
        rooms_missing_link_value,
        duplicate_link_values,
        rooms_unmatched_in_drofus,
        property_mismatches,
    }
}

/// Data-quality report for the header's validation panel — see
/// `ValidationResponse`/`compute_validation`.
pub async fn get_project_validation(
    State(state): State<Shared>,
    Path(project_id): Path<String>,
) -> Result<Json<ValidationResponse>, StatusCode> {
    let Some(drofus) = state.drofus.as_ref() else {
        return Ok(Json(ValidationResponse::drofus_not_configured()));
    };

    let stored = state.all_snapshots().map_err(|e| {
        tracing::error!("failed to read snapshots: {e:#}");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    Ok(Json(compute_validation(&project_id, &stored, drofus, &state.builtin_properties)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{CustomValue, Model, Project, Snapshot};
    use std::collections::HashMap;

    fn make_room(id: &str, name: &str, props: &[(&str, &str)]) -> Room {
        let mut properties = BTreeMap::new();
        for (k, v) in props {
            properties.insert(k.to_string(), CustomValue { value: v.to_string(), storage_type: None });
        }
        Room { id: id.to_string(), name: name.to_string(), level_id: "1".to_string(), loops: vec![], properties }
    }

    fn make_payload(project_id: &str, rooms: Vec<Room>) -> (ModelKey, RoomPayload) {
        let key = ModelKey { project_id: project_id.to_string(), model_id: "m1".to_string() };
        let payload = RoomPayload {
            schema_version: 5,
            project: Project { id: project_id.to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels: vec![],
            rooms,
        };
        (key, payload)
    }

    fn make_drofus(
        link_property: &str,
        records: &[(&str, &[(&str, &str)])],
        reconciliation: &[(&str, &str)],
    ) -> DrofusData {
        let mut by_id = BTreeMap::new();
        for (id, fields) in records {
            let mut f = BTreeMap::new();
            for (k, v) in *fields {
                f.insert(k.to_string(), v.to_string());
            }
            by_id.insert(id.to_string(), DrofusRecord { fields: f });
        }
        let mut reconciliation_map = BTreeMap::new();
        for (k, v) in reconciliation {
            reconciliation_map.insert(k.to_string(), v.to_string());
        }
        DrofusData { link_property: link_property.to_string(), by_id, reconciliation: reconciliation_map }
    }

    /// A room with no value for the link property is reported, not silently
    /// dropped.
    #[test]
    fn test_compute_validation_missing_link_value() {
        let room = make_room("1", "Room", &[]); // no "Number" property
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[], &[]);

        let result = compute_validation("p1", &stored, &drofus, &[]);

        assert_eq!(result.total_rooms, 1);
        assert_eq!(result.rooms_missing_link_value, vec!["1".to_string()]);
        assert!(result.duplicate_link_values.is_empty());
    }

    /// Two rooms sharing one link value are ambiguous: reported as a
    /// duplicate, and excluded from the unmatched/mismatch checks (neither
    /// can be uniquely said to be the room a dRofus record describes).
    #[test]
    fn test_compute_validation_duplicate_excluded_from_other_checks() {
        let rooms = vec![
            make_room("1", "Room A", &[("Number", "101")]),
            make_room("2", "Room B", &[("Number", "101")]),
        ];
        let (key, payload) = make_payload("p1", rooms);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("101", &[])], &[]);

        let result = compute_validation("p1", &stored, &drofus, &[]);

        assert_eq!(result.duplicate_link_values.len(), 1);
        let dup = &result.duplicate_link_values[0];
        assert_eq!(dup.value, "101");
        assert_eq!(dup.room_ids, vec!["1".to_string(), "2".to_string()]);
        assert!(result.rooms_unmatched_in_drofus.is_empty());
        assert!(result.property_mismatches.is_empty());
    }

    /// A room whose (unique) link value isn't in the dRofus map is reported
    /// as unmatched.
    #[test]
    fn test_compute_validation_unmatched_in_drofus() {
        let room = make_room("1", "Room", &[("Number", "999")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[])], &[]);

        let result = compute_validation("p1", &stored, &drofus, &[]);

        assert_eq!(result.rooms_unmatched_in_drofus, vec!["1".to_string()]);
    }

    /// A uniquely-matched room: an agreeing reconciled field produces no
    /// mismatch, a disagreeing one does.
    #[test]
    fn test_compute_validation_property_mismatch_and_agreement() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Area", "25.5"), ("Department", "Cardiology")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus(
            "Number",
            &[("1", &[("NetArea", "30.0"), ("Dept", "Cardiology")])],
            &[("NetArea", "Area"), ("Dept", "Department")],
        );

        let result = compute_validation("p1", &stored, &drofus, &[]);

        assert!(result.rooms_unmatched_in_drofus.is_empty());
        assert_eq!(result.property_mismatches.len(), 1);
        let mismatch = &result.property_mismatches[0];
        assert_eq!(mismatch.field, "NetArea");
        assert_eq!(mismatch.room_value, "25.5");
        assert_eq!(mismatch.drofus_value, "30.0");
    }

    /// `$name`/`$id` resolve to the room's own fields, not `room.properties`.
    #[test]
    fn test_resolve_label_fields_intrinsic_tokens() {
        let room = make_room("324772", "Room 101", &[]);
        let fields = vec!["$name".to_string(), "$id".to_string()];
        let label = resolve_label_fields(&room, &fields, "revit", &[]);
        assert_eq!(label, vec!["Room 101".to_string(), "324772".to_string()]);
    }

    /// Any other configured name falls through to the same canonical/source
    /// resolution dRofus and classification already use.
    #[test]
    fn test_resolve_label_fields_canonical_fallback() {
        let room = make_room("1", "Room", &[("Area", "25.5")]);
        let defs = vec![BuiltinPropertyDef {
            canonical: "Area".to_string(),
            by_source: HashMap::from([("revit".to_string(), "Area".to_string())]),
        }];
        let fields = vec!["Area".to_string()];
        let label = resolve_label_fields(&room, &fields, "revit", &defs);
        assert_eq!(label, vec!["25.5".to_string()]);
    }

    /// A configured name that doesn't resolve is silently skipped, not turned
    /// into an empty-string entry.
    #[test]
    fn test_resolve_label_fields_skips_unresolved() {
        let room = make_room("1", "Room", &[]);
        let fields = vec!["$name".to_string(), "Nonexistent".to_string(), "$id".to_string()];
        let label = resolve_label_fields(&room, &fields, "revit", &[]);
        assert_eq!(label, vec!["Room".to_string(), "1".to_string()]);
    }
}
