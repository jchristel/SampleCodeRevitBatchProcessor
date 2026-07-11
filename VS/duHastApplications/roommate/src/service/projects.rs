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

    let mut seen: BTreeMap<String, String> = BTreeMap::new();
    for (_key, payload) in &stored {
        if state.settings_for(&payload.project.id).is_none() {
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
    let Some(bundle) = state.settings_for(project_id) else {
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

    Ok(BuildingsResponse { tier_configured: true, buildings })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Model, Project, RoomPayload, Snapshot};
    use crate::state::ProjectSettings;
    use crate::storage::MemStore;

    fn make_payload(project_id: &str, project_name: &str) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project_id.to_string(), name: project_name.to_string() },
            model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
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
        }
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
