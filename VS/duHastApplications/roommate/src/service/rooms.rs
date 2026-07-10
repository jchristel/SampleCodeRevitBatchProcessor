//! `/rooms` fetch-side derive logic: dRofus join, classification, level dedup.
//!
//! Moved verbatim out of `handlers::get_rooms` (see HANDOVER-service-layer.md)
//! -- the join/classify logic never depended on `Query`/`Json`/`StatusCode`,
//! so the only real change here is the signature: plain `Option<&str>` filters
//! in, a plain `RoomsResult` out, no transport type touched.

use std::collections::{BTreeMap, BTreeSet};

use serde::Serialize;

use crate::classify::{classify_room, TierValue};
use crate::contract::{elevation_match, lookup_property, Level, Room, RoomPayload, SUPPORTED_SCHEMA};
use crate::drofus::DrofusRecord;
use crate::settings::{BuiltinPropertyDef, HierarchyTier};
use crate::state::{AppState, ModelKey, ProjectSettings};

use super::ServiceError;

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
/// `bundle` is the owning payload's project's settings (see
/// `AppState::settings_for`) — every field that used to come off `AppState`
/// directly now comes off this per-project bundle instead. `source` comes
/// from the owning model's `Model.source` (e.g. "revit") — it picks which
/// `BuiltinPropertyDef.by_source` entry `lookup_property` uses to resolve a
/// canonical name to this room's actual raw property name.
fn assemble_room(bundle: &ProjectSettings, room: &Room, source: &str) -> RoomResponse {
    // dRofus join: read the link property off the room, look up the record.
    let drofus = bundle.drofus.as_ref().and_then(|d| {
        lookup_property(room, &d.link_property, source, &bundle.builtin_properties)
            .and_then(|key| d.by_id.get(&key).cloned())
    });

    // Classification resolved fresh — see staleness note on classify_room.
    let classification = classify_room(room, &bundle.hierarchy, source, &bundle.builtin_properties);

    let label = resolve_label_fields(room, &bundle.room_label, source, &bundle.builtin_properties);

    RoomResponse { room: room.clone(), drofus, classification, label }
}

/// Sentinel `building` key for rooms whose "Building" tier didn't resolve —
/// distinct from any real `building_key` output since real keys never start
/// with `__`.
pub const UNCLASSIFIED_BUILDING_KEY: &str = "__unclassified__";

/// Opaque token identifying one building bucket, built from its resolved
/// `(code, name)` pair. Callers (the browser) never decode this — they just
/// echo it back to `/rooms?building=..` — so the encoding only has to be
/// stable and collision-free for the lifetime of one response, not
/// human-meaningful.
pub fn building_key(code: &Option<String>, name: &Option<String>) -> String {
    format!("{}|{}", code.as_deref().unwrap_or(""), name.as_deref().unwrap_or(""))
}

/// Index of the hierarchy tier named "Building", if one is configured.
/// Shared by `projects::list_buildings` and the `/rooms` building filter so
/// both resolve the exact same tier the exact same way.
pub fn building_tier_index(hierarchy: &[HierarchyTier]) -> Option<usize> {
    hierarchy.iter().position(|t| t.name == "Building")
}

/// Result of merging every stored model's levels and rooms into one flat
/// payload. Derives `Serialize` so both adapters (HTTP handler, MCP server)
/// can return it directly -- every field here is wire shape, nothing needs
/// stripping. "Nothing has ever been pushed" is not a field on this type; it
/// is `assemble_rooms` returning `None` (see there).
#[derive(serde::Serialize)]
pub struct RoomsResult {
    pub schema_version: u32,
    pub levels: Vec<Level>,
    pub rooms: Vec<RoomResponse>,
}

/// Merge every stored model's levels and rooms into one flat payload, scoped
/// by an optional project id and an optional opaque building key (from
/// `projects::list_buildings`). When a building filter is given, a project
/// whose hierarchy has no tier named "Building" matches *nothing* -- not
/// everything. The caller asked for a building; a project with no notion of
/// one can't answer that question, and `list_buildings` already tells a
/// well-behaved client `tier_configured: false` so it never sends this
/// combination. An empty result is honest; a silently ignored filter is not
/// (it used to leak a tier-less project's entire room set into a filtered
/// multi-project merge). A model contributes its `levels` only when it contributed at
/// least one matching room: levels are their own array from a separate Revit
/// export, so a floor can legitimately have zero rooms of a given building
/// right now yet still belong to it — dropping it would make the slider
/// flicker as classification changes. This rule only applies when a building
/// filter is actually active; with no filter, every scoped model's levels are
/// included exactly as before.
///
/// dRofus join and classification are resolved here at response assembly — the
/// stored snapshots stay raw; derived data is never written back to state.
///
/// Returns `Ok(None)` when nothing has ever been pushed to this server at all
/// -- the HTTP adapter's "204 No Content" case. A filter that merely matches
/// nothing is still `Ok(Some)` with empty vecs: the store has data, the
/// question just has an empty answer.
pub fn assemble_rooms(
    state: &AppState,
    project: Option<&str>,
    building: Option<&str>,
) -> Result<Option<RoomsResult>, ServiceError> {
    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;
    if stored.is_empty() {
        return Ok(None);
    }

    // Scope to the requested project (if any), then drop any payload whose
    // project has no registered settings bundle — an unscoped merge is now
    // inherently per-project, so a model with nothing to classify/join it
    // against has no home in the result (see
    // HANDOVER-per-project-settings.md: "skip on read").
    let scoped: Vec<(&ModelKey, &RoomPayload, &ProjectSettings)> = stored
        .iter()
        .filter(|(_key, payload)| project.map_or(true, |p| payload.project.id == p))
        .filter_map(|(key, payload)| state.settings_for(&payload.project.id).map(|bundle| (key, payload, bundle)))
        .collect();

    // Level dedup: a `Level.id` is only unique *within* its own model (same
    // caveat as room ids -- see `ModelKey`'s doc comment), so two linked
    // models that both define "the same" architectural level produce two
    // distinct `Level` rows with the same (name, elevation) but different
    // ids. Merge them: same name + same elevation (tolerant of cross-file
    // float drift via `elevation_match`, the same rounding discipline used
    // for dRofus property comparison) IS the same level, no further
    // disambiguation. First-seen id per group wins as the canonical id; every
    // other (project_id, model_id, level_id) triple that maps to that group
    // is remapped to it before rooms are serialized, so the level picker and
    // room filtering still agree on one id per real-world level.
    //
    // Grouped *per project*: level identity is only meaningful within one
    // project (the dedup exists for linked models of one job), so two
    // unrelated projects that both have a "Level 1" @ 0.0 keep their own
    // levels in an unscoped merge instead of collapsing onto whichever
    // project happened to be seen first.
    let mut canonical_levels: BTreeMap<String, Vec<Level>> = BTreeMap::new(); // project_id -> levels
    let mut level_remap: BTreeMap<(String, String, String), String> = BTreeMap::new(); // (project_id, model_id, level_id) -> canonical
    for (key, payload, _bundle) in &scoped {
        let project_levels = canonical_levels.entry(key.project_id.clone()).or_default();
        for level in &payload.levels {
            let canonical_id = match project_levels
                .iter()
                .find(|c| c.name == level.name && elevation_match(c.elevation, level.elevation))
            {
                Some(existing) => existing.id.clone(),
                None => {
                    project_levels.push(level.clone());
                    level.id.clone()
                }
            };
            level_remap.insert(
                (key.project_id.clone(), key.model_id.clone(), level.id.clone()),
                canonical_id,
            );
        }
    }

    let mut levels = Vec::new();
    // Keyed (project_id, canonical_id): canonical ids are model-local, so two
    // projects could in principle mint the same id -- a flat set would let one
    // project's level suppress another's.
    let mut emitted_level_ids: BTreeSet<(String, String)> = BTreeSet::new();
    let mut rooms: Vec<RoomResponse> = Vec::new();

    for (key, payload, bundle) in &scoped {
        // Building tier index is resolved from this payload's own project
        // bundle -- projects with different hierarchies coexist in one merge.
        let building_idx = building_tier_index(&bundle.hierarchy);
        let building_filter_active = building.is_some();

        let matching_rooms: Vec<&Room> = match (building, building_idx) {
            (Some(wanted), Some(idx)) => payload
                .rooms
                .iter()
                .filter(|room| {
                    let path = classify_room(room, &bundle.hierarchy, &payload.model.source, &bundle.builtin_properties);
                    match path.get(idx) {
                        Some(tier) if tier.undefined => wanted == UNCLASSIFIED_BUILDING_KEY,
                        Some(tier) => building_key(&tier.code, &tier.name) == *wanted,
                        None => false,
                    }
                })
                .collect(),
            // A building filter was requested but this project has no
            // "Building" tier: it can't answer the question, so it matches
            // nothing -- contributing all its rooms instead would leak them
            // into a response the caller believes is filtered.
            (Some(_), None) => Vec::new(),
            (None, _) => payload.rooms.iter().collect(),
        };

        if building_filter_active && matching_rooms.is_empty() {
            continue; // this model contributed nothing to the requested building
        }

        for level in &payload.levels {
            let canonical_id = level_remap
                .get(&(key.project_id.clone(), key.model_id.clone(), level.id.clone()))
                .cloned()
                .unwrap_or_else(|| level.id.clone());
            if emitted_level_ids.insert((key.project_id.clone(), canonical_id.clone())) {
                let mut level = level.clone();
                level.id = canonical_id;
                levels.push(level);
            }
        }
        rooms.extend(matching_rooms.into_iter().map(|room| {
            let mut response = assemble_room(bundle, room, &payload.model.source);
            if let Some(canonical_id) =
                level_remap.get(&(key.project_id.clone(), key.model_id.clone(), room.level_id.clone()))
            {
                response.room.level_id = canonical_id.clone();
            }
            response
        }));
    }

    Ok(Some(RoomsResult { schema_version: SUPPORTED_SCHEMA, levels, rooms }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{CustomValue, Model, Project, RoomPayload, Snapshot};
    use crate::drofus::DrofusData;
    use crate::state::AppState;
    use crate::storage::MemStore;

    fn make_room(id: &str, name: &str, props: &[(&str, &str)]) -> Room {
        let mut properties = BTreeMap::new();
        for (k, v) in props {
            properties.insert(k.to_string(), CustomValue { value: v.to_string(), storage_type: None });
        }
        Room { id: id.to_string(), name: name.to_string(), level_id: "1".to_string(), loops: vec![], properties }
    }

    fn make_drofus(link_property: &str) -> DrofusData {
        DrofusData {
            link_property: link_property.to_string(),
            by_id: BTreeMap::new(),
            reconciliation: BTreeMap::new(),
            all_labels: vec![],
        }
    }

    /// A minimal `ProjectSettings` bundle for tests that only care about the
    /// dRofus link property and the default room label.
    fn make_bundle(link_property: &str) -> ProjectSettings {
        ProjectSettings {
            drofus: Some(make_drofus(link_property)),
            hierarchy: vec![],
            builtin_properties: vec![],
            room_label: vec!["$name".to_string(), "$id".to_string()],
            drofus_fields: vec![],
        }
    }

    /// Registers one project's bundle under its id -- the shape
    /// `AppState::new` now takes in place of the old five flat fields.
    fn single_project(project_id: &str, bundle: ProjectSettings) -> std::collections::HashMap<String, ProjectSettings> {
        std::collections::HashMap::from([(project_id.to_string(), bundle)])
    }

    /// A bundle with a one-tier "Building" hierarchy keyed on `bldg_code`,
    /// for tests exercising the building filter across projects.
    fn make_bundle_with_building_tier() -> ProjectSettings {
        ProjectSettings {
            hierarchy: vec![HierarchyTier {
                name: "Building".to_string(),
                code_property: Some("bldg_code".to_string()),
                name_property: None,
            }],
            ..make_bundle("Number")
        }
    }

    fn make_payload(project_id: &str, model_id: &str, levels: Vec<Level>, rooms: Vec<Room>) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project_id.to_string(), name: "P".to_string() },
            model: Model { id: model_id.to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels,
            rooms,
        }
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
            by_source: std::collections::HashMap::from([("revit".to_string(), "Area".to_string())]),
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

    /// Two models under the same project each define "the same" level (same
    /// name, near-identical elevation, different model-local `Level.id`) --
    /// `assemble_rooms` must collapse them into one `Level` in the response
    /// and remap both models' rooms to point at that one canonical id.
    #[test]
    fn test_assemble_rooms_dedups_levels_by_name_and_elevation() {
        let mut room_a = make_room("r1", "Room A", &[]);
        room_a.level_id = "lvlA".to_string();
        let mut room_b = make_room("r2", "Room B", &[]);
        room_b.level_id = "lvlB".to_string();

        let payload_a = RoomPayload {
            schema_version: 5,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "modelA".to_string(), name: "A".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels: vec![Level { id: "lvlA".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![room_a],
        };
        let payload_b = RoomPayload {
            schema_version: 5,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "modelB".to_string(), name: "B".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:01Z".to_string() },
            // Same name, elevation drifted by float noise well within tolerance.
            levels: vec![Level { id: "lvlB".to_string(), name: "Level 1".to_string(), elevation: 0.000000001 }],
            rooms: vec![room_b],
        };

        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);
        state.set_snapshot(payload_a).unwrap();
        state.set_snapshot(payload_b).unwrap();

        let result = assemble_rooms(&state, Some("p1"), None).unwrap().expect("store has data");

        assert_eq!(result.levels.len(), 1, "same name+elevation levels must collapse to one");

        let canonical_id = result.levels[0].id.clone();
        assert_eq!(result.rooms.len(), 2);
        for room in &result.rooms {
            assert_eq!(room.room.level_id, canonical_id);
        }
    }

    /// An empty store is reported as `None`, distinct from a filter that
    /// simply matches nothing (which is `Some` with empty vecs).
    #[test]
    fn test_assemble_rooms_reports_store_empty() {
        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);

        let result = assemble_rooms(&state, None, None).unwrap();
        assert!(result.is_none(), "nothing has ever been pushed");
    }

    /// A payload whose project has no registered settings (and no default
    /// bundle configured) is skipped from an unscoped merge entirely -- it's
    /// not enough for the store to be non-empty; the project must actually be
    /// registered for its rooms to appear.
    #[test]
    fn test_assemble_rooms_skips_unregistered_project() {
        let payload = RoomPayload {
            schema_version: 5,
            project: Project { id: "unregistered".to_string(), name: "P".to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            levels: vec![Level { id: "l1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![make_room("r1", "Room A", &[])],
        };

        // Registry only knows "p1" -- "unregistered" has no bundle and no
        // default is configured.
        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);
        state.set_snapshot(payload).unwrap();

        let result = assemble_rooms(&state, None, None).unwrap().expect("the store did receive a push");
        assert!(result.rooms.is_empty(), "but the unregistered project's rooms must not appear");
        assert!(result.levels.is_empty());
    }

    /// Two *different* projects each define "Level 1" @ 0.0 -- an unscoped
    /// merge must keep both levels (level identity is only meaningful within
    /// a project), and each project's room must keep a level id minted from
    /// its own project's model, never remapped onto the other project's.
    #[test]
    fn test_assemble_rooms_level_dedup_does_not_cross_projects() {
        let mut room_a = make_room("r1", "Room A", &[]);
        room_a.level_id = "lvlA".to_string();
        let mut room_b = make_room("r2", "Room B", &[]);
        room_b.level_id = "lvlB".to_string();

        let payload_a = make_payload(
            "p1",
            "modelA",
            vec![Level { id: "lvlA".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            vec![room_a],
        );
        let payload_b = make_payload(
            "p2",
            "modelB",
            vec![Level { id: "lvlB".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            vec![room_b],
        );

        let registry = std::collections::HashMap::from([
            ("p1".to_string(), make_bundle("Number")),
            ("p2".to_string(), make_bundle("Number")),
        ]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);
        state.set_snapshot(payload_a).unwrap();
        state.set_snapshot(payload_b).unwrap();

        let result = assemble_rooms(&state, None, None).unwrap().expect("store has data");

        assert_eq!(result.levels.len(), 2, "same (name, elevation) in different projects must NOT collapse");
        assert_eq!(result.rooms.len(), 2);
        for room in &result.rooms {
            let expected = if room.room.id == "r1" { "lvlA" } else { "lvlB" };
            assert_eq!(room.room.level_id, expected, "each room keeps its own project's level id");
        }
    }

    /// Unscoped merge with a building filter: project A (Building tier, room
    /// in building B01) contributes its matching room and its levels; project
    /// B (no hierarchy at all) can't answer a building question, so it
    /// contributes nothing -- neither rooms nor levels.
    #[test]
    fn test_assemble_rooms_building_filter_excludes_tierless_project() {
        let mut room_a = make_room("r1", "Room A", &[("bldg_code", "B01")]);
        room_a.level_id = "lvlA".to_string();
        let mut room_b = make_room("r2", "Room B", &[]);
        room_b.level_id = "lvlB".to_string();

        let payload_a = make_payload(
            "p1",
            "modelA",
            vec![Level { id: "lvlA".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            vec![room_a],
        );
        let payload_b = make_payload(
            "p2",
            "modelB",
            vec![Level { id: "lvlB".to_string(), name: "Level 9".to_string(), elevation: 30.0 }],
            vec![room_b],
        );

        let registry = std::collections::HashMap::from([
            ("p1".to_string(), make_bundle_with_building_tier()),
            ("p2".to_string(), make_bundle("Number")), // no hierarchy
        ]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);
        state.set_snapshot(payload_a).unwrap();
        state.set_snapshot(payload_b).unwrap();

        let key = building_key(&Some("B01".to_string()), &None);
        let result = assemble_rooms(&state, None, Some(&key)).unwrap().expect("store has data");

        assert_eq!(result.rooms.len(), 1, "only project A's matching room");
        assert_eq!(result.rooms[0].room.id, "r1");
        assert_eq!(result.levels.len(), 1, "only project A's levels");
        assert_eq!(result.levels[0].name, "Level 1");
    }

    /// Scoped to a project with no Building tier while a building filter is
    /// active: the project can't answer the question, so the result is empty
    /// (not the project's whole room set) -- but the store is not empty.
    #[test]
    fn test_assemble_rooms_building_filter_on_tierless_project_is_empty() {
        let mut room_b = make_room("r2", "Room B", &[]);
        room_b.level_id = "lvlB".to_string();
        let payload_b = make_payload(
            "p2",
            "modelB",
            vec![Level { id: "lvlB".to_string(), name: "Level 9".to_string(), elevation: 30.0 }],
            vec![room_b],
        );

        let state = AppState::new(Box::new(MemStore::new()), single_project("p2", make_bundle("Number")), None);
        state.set_snapshot(payload_b).unwrap();

        let key = building_key(&Some("B01".to_string()), &None);
        let result = assemble_rooms(&state, Some("p2"), Some(&key))
            .unwrap()
            .expect("store is not empty, so this is Some with empty vecs");

        assert!(result.rooms.is_empty(), "a filter the project can't answer matches nothing");
        assert!(result.levels.is_empty());
    }
}
