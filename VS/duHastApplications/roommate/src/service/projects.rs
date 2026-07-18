//! Project and building listings for the pickers — derived from stored
//! snapshots, with no storage or identity of their own.
//!
//! Moved verbatim out of `handlers::get_projects` / `handlers::get_project_buildings`
//! (see HANDOVER-service-layer.md).

use std::collections::BTreeMap;

use serde::Serialize;

use crate::classify::classify_room;

use super::rooms::{building_key, building_tier_index, UNCLASSIFIED_BUILDING_KEY};
use super::ServiceError;
use crate::state::AppState;

/// One known project, for the `/projects` picker.
#[derive(Serialize)]
pub struct ProjectSummary {
    pub id: String,
    pub name: String,
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
    /// True when another building in this response shares this one's name.
    /// The dedup key is (code, name), so same-name/different-code entries are
    /// legitimately distinct — but a picker that renders only names would show
    /// them identically. This flag tells the UI to disambiguate (e.g. append
    /// the code) without the backend dictating presentation.
    pub ambiguous: bool,
}

#[derive(Serialize)]
pub struct BuildingsResponse {
    /// False when no hierarchy tier is named "Building" — filtering isn't
    /// possible, and the whole project is effectively one building. Not an
    /// error: a project with no classification configured is a normal state.
    pub tier_configured: bool,
    pub buildings: Vec<BuildingSummary>,
}

/// Lists every project with at least one stored model AND a registered
/// settings bundle. Derived from `all_snapshots()` — a project's identity
/// already rides on every payload it stores, so no dedicated storage query is
/// needed. The registration filter mirrors `assemble_rooms`'s "skip on read"
/// policy: a stored-but-unregistered project (a dev seed that bypassed the
/// ingest check, or a settings file deleted after data existed) is invisible
/// to `/rooms`, so listing it here would offer the picker a project that can
/// never show anything. An empty list is a perfectly good answer for a
/// picker, unlike `/rooms`'s 204 (which exists for the poller's specific
/// "nothing posted yet" signal) — that distinction is an HTTP-adapter
/// concern, not reflected here.
pub fn list_projects(state: &AppState) -> Result<Vec<ProjectSummary>, ServiceError> {
    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;
    let registry = state.settings();

    let mut seen: BTreeMap<String, String> = BTreeMap::new();
    for (_key, payload) in &stored {
        if registry.settings_for(&payload.project.id).is_none() {
            continue; // skip on read, same as assemble_rooms
        }
        seen.entry(payload.project.id.clone())
            .or_insert_with(|| payload.project.name.clone());
    }

    let mut projects: Vec<ProjectSummary> = seen
        .into_iter()
        .map(|(id, name)| ProjectSummary { id, name })
        .collect();
    projects.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(projects)
}

/// Lists the distinct "Building" classification values found across every
/// room in one project's stored models, using `classify_room` exactly as it
/// already runs for `/rooms` — building selection has no identity or storage
/// of its own, it's a filter over the classification that already exists.
///
/// A project with no registered settings bundle behaves exactly like a
/// registered project with no "Building" tier configured: `tier_configured:
/// false`, not an error — this endpoint has no separate "unregistered"
/// signal, since an empty/absent building list means the same thing to the
/// picker either way.
pub fn list_buildings(state: &AppState, project_id: &str) -> Result<BuildingsResponse, ServiceError> {
    let registry = state.settings();
    let Some(bundle) = registry.settings_for(project_id) else {
        return Ok(BuildingsResponse { tier_configured: false, buildings: vec![] });
    };
    let Some(idx) = building_tier_index(&bundle.hierarchy) else {
        return Ok(BuildingsResponse { tier_configured: false, buildings: vec![] });
    };

    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;

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
            let path = classify_room(room, &bundle.hierarchy, &payload.model.source, &bundle.builtin_properties);
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
        .map(|(key, (code, name))| BuildingSummary { key, code, name, unclassified: false, ambiguous: false })
        .collect();
    // Nameless entries are exempt: they display their code, which the
    // (code, name) dedup key already keeps distinct among them — and the
    // synthetic unclassified bucket below has no name either.
    let mut name_counts: BTreeMap<String, usize> = BTreeMap::new();
    for b in &buildings {
        if let Some(name) = &b.name {
            *name_counts.entry(name.clone()).or_insert(0) += 1;
        }
    }
    for b in &mut buildings {
        if let Some(name) = &b.name {
            b.ambiguous = name_counts[name] > 1;
        }
    }
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
            ambiguous: false,
        });
    }

    Ok(BuildingsResponse { tier_configured: true, buildings })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{CustomValue, Model, Project, Room, RoomPayload, Snapshot};
    use crate::settings::HierarchyTier;
    use crate::state::ProjectSettings;
    use crate::storage::MemStore;

    fn make_payload(project_id: &str, project_name: &str) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project_id.to_string(), name: project_name.to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
            model_to_shared: None,
            levels: vec![],
            rooms: vec![],
        }
    }

    fn make_bundle() -> ProjectSettings {
        ProjectSettings {
            drofus: None,
            hierarchy: vec![],
            builtin_properties: vec![],
            room_label: vec!["$name".to_string()],
            drofus_fields: vec![],
            milestones: vec![],
            comparison_key: None,
            comparison_properties: vec![],
            hierarchy_exclusions: vec![],        }
    }

    /// A stored-but-unregistered project is skipped from the listing — same
    /// skip-on-read policy as `assemble_rooms`, so the picker never offers a
    /// project whose rooms can never be shown.
    #[test]
    fn test_list_projects_skips_unregistered_project() {
        let registry = std::collections::HashMap::from([("p1".to_string(), make_bundle())]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);
        state.set_snapshot(make_payload("p1", "Registered")).unwrap();
        state.set_snapshot(make_payload("ghost", "Unregistered")).unwrap();

        let projects = list_projects(&state).unwrap();

        assert_eq!(projects.len(), 1);
        assert_eq!(projects[0].id, "p1");
    }

    fn make_room(id: &str, props: &[(&str, &str)]) -> Room {
        let mut properties = std::collections::BTreeMap::new();
        for (k, v) in props {
            properties.insert(k.to_string(), CustomValue { value: v.to_string(), storage_type: None });
        }
        Room { id: id.to_string(), name: "Room".to_string(), level_id: "1".to_string(), loops: vec![], properties }
    }

    /// A bundle with a one-tier "Building" hierarchy resolving both a code
    /// and a name property, for the picker-labeling tests.
    fn make_building_bundle() -> ProjectSettings {
        ProjectSettings {
            hierarchy: vec![HierarchyTier {
                name: "Building".to_string(),
                code_property: Some("bldg_code".to_string()),
                name_property: Some("bldg_name".to_string()),
            }],
            ..make_bundle()
        }
    }

    fn state_with_rooms(rooms: Vec<Room>) -> AppState {
        let registry = std::collections::HashMap::from([("p1".to_string(), make_building_bundle())]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);
        let mut payload = make_payload("p1", "P One");
        payload.rooms = rooms;
        state.set_snapshot(payload).unwrap();
        state
    }

    /// Two buildings sharing a name but with different codes are legitimately
    /// distinct (dedup key is (code, name)) — both must be flagged ambiguous
    /// so a name-only picker can disambiguate them, while a uniquely-named
    /// building stays unflagged.
    #[test]
    fn test_list_buildings_flags_shared_name_distinct_codes() {
        let state = state_with_rooms(vec![
            make_room("r1", &[("bldg_code", "B01"), ("bldg_name", "Rouse Hill Hospital")]),
            make_room("r2", &[("bldg_code", "B02"), ("bldg_name", "Rouse Hill Hospital")]),
            make_room("r3", &[("bldg_code", "B03"), ("bldg_name", "Somewhere Else")]),
        ]);

        let result = list_buildings(&state, "p1").unwrap();

        assert_eq!(result.buildings.len(), 3);
        let flags: Vec<(Option<&str>, bool)> =
            result.buildings.iter().map(|b| (b.code.as_deref(), b.ambiguous)).collect();
        assert!(flags.contains(&(Some("B01"), true)));
        assert!(flags.contains(&(Some("B02"), true)));
        assert!(flags.contains(&(Some("B03"), false)));
    }

    /// A name collision where one twin resolved no code at all: both are
    /// still flagged — the code-bearing entry carries the visible
    /// distinction, and the UI leaves the codeless one as the bare name.
    #[test]
    fn test_list_buildings_flags_shared_name_with_missing_code() {
        let state = state_with_rooms(vec![
            make_room("r1", &[("bldg_code", "B01"), ("bldg_name", "Rouse Hill Hospital")]),
            make_room("r2", &[("bldg_name", "Rouse Hill Hospital")]),
        ]);

        let result = list_buildings(&state, "p1").unwrap();

        assert_eq!(result.buildings.len(), 2);
        assert!(result.buildings.iter().all(|b| b.ambiguous));
        assert!(result.buildings.iter().any(|b| b.code.is_none()));
    }

    /// Nameless entries never trip the ambiguity check: code-only buildings
    /// display their (unique-by-dedup-key) codes, and the synthetic
    /// unclassified bucket has no name either.
    #[test]
    fn test_list_buildings_nameless_entries_not_ambiguous() {
        let state = state_with_rooms(vec![
            make_room("r1", &[("bldg_code", "B01")]),
            make_room("r2", &[("bldg_code", "B02")]),
            make_room("r3", &[]), // no tier data at all -> unclassified bucket
        ]);

        let result = list_buildings(&state, "p1").unwrap();

        assert_eq!(result.buildings.len(), 3);
        assert!(result.buildings.iter().all(|b| !b.ambiguous));
        assert!(result.buildings.last().unwrap().unclassified);
    }

    /// With an `is_default` fallback bundle configured, an otherwise
    /// unregistered project IS listed — consistent with `assemble_rooms`,
    /// which serves its rooms through the same fallback.
    #[test]
    fn test_list_projects_default_bundle_admits_unregistered_project() {
        let state = AppState::new(Box::new(MemStore::new()), std::collections::HashMap::new(), Some(make_bundle()));
        state.set_snapshot(make_payload("anything", "Via Default")).unwrap();

        let projects = list_projects(&state).unwrap();

        assert_eq!(projects.len(), 1);
        assert_eq!(projects[0].id, "anything");
    }
}
