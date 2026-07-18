//! Snapshot history listings: which dated snapshots exist for a project's
//! models, and the latest id for one model — the id a follow-up upload (FFE
//! etc.) attaches its data to, alongside a room id.
//!
//! Same shape as `projects`: model identity/names come from `all_snapshots()`
//! (the payload envelope already carries them, no dedicated storage query),
//! history per model comes from the store's snapshot index
//! (`list_snapshot_ids`), and an unregistered project is skipped on read —
//! the same policy as `list_projects`, since its snapshots can never be
//! served anyway.

use serde::Serialize;

use super::ServiceError;
use crate::state::{AppState, ModelKey};

/// One model's snapshot history, ascending — `latest` duplicates the last
/// element so a caller after just "what do I attach to" never re-derives it.
#[derive(Serialize)]
pub struct ModelSnapshots {
    pub id: String,
    pub name: String,
    pub snapshots: Vec<String>,
    pub latest: String,
}

#[derive(Serialize)]
pub struct ProjectSnapshotsResponse {
    pub models: Vec<ModelSnapshots>,
}

/// The latest snapshot id for one model — `GET .../snapshots/latest`.
#[derive(Serialize)]
pub struct LatestSnapshot {
    pub taken_at: String,
}

/// Every stored snapshot id for one project, grouped per model. A project
/// with nothing stored (or unknown, or unregistered) answers an empty list,
/// not an error — same soft-success discipline as the other listings.
pub fn list_project_snapshots(
    state: &AppState,
    project_id: &str,
) -> Result<ProjectSnapshotsResponse, ServiceError> {
    let registry = state.settings();
    if registry.settings_for(project_id).is_none() {
        return Ok(ProjectSnapshotsResponse { models: vec![] });
    }

    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;
    let mut models = Vec::new();
    for (key, payload) in &stored {
        if payload.project.id != project_id {
            continue;
        }
        let snapshots = state.list_snapshot_ids(key).map_err(ServiceError::Internal)?;
        // A model appears in `all_snapshots` only via a readable snapshot, so
        // an empty id list can't really happen — skip defensively if it does.
        let Some(latest) = snapshots.last().cloned() else { continue };
        models.push(ModelSnapshots {
            id: key.model_id.clone(),
            name: payload.model.name.clone(),
            snapshots,
            latest,
        });
    }
    models.sort_by(|a, b| a.name.cmp(&b.name).then_with(|| a.id.cmp(&b.id)));
    Ok(ProjectSnapshotsResponse { models })
}

/// The latest snapshot id for one model, or `None` when the model is unknown,
/// has no snapshots, or its project is unregistered (skip-on-read, as above).
/// `None` is the caller's "no latest exists" signal — the HTTP adapter turns
/// it into 404, unlike the listing's soft empty success, because this call
/// names one specific resource.
pub fn latest_snapshot(
    state: &AppState,
    project_id: &str,
    model_id: &str,
) -> Result<Option<LatestSnapshot>, ServiceError> {
    if state.settings().settings_for(project_id).is_none() {
        return Ok(None);
    }
    let key = ModelKey {
        project_id: project_id.to_string(),
        model_id: model_id.to_string(),
    };
    let ids = state.list_snapshot_ids(&key).map_err(ServiceError::Internal)?;
    Ok(ids.last().map(|taken_at| LatestSnapshot { taken_at: taken_at.clone() }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Model, Project, RoomPayload, Snapshot};
    use crate::state::ProjectSettings;
    use crate::storage::MemStore;

    fn make_payload(project_id: &str, model_id: &str, model_name: &str, ts: &str) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project_id.to_string(), name: "P".to_string() },
            model: Model { id: model_id.to_string(), name: model_name.to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: ts.to_string() },
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

    fn make_state() -> AppState {
        let registry = std::collections::HashMap::from([("p1".to_string(), make_bundle())]);
        AppState::new(Box::new(MemStore::new()), registry, None)
    }

    /// Two models under one project each get their own group, sorted by
    /// name, with `latest` mirroring the last (only, for MemStore) id.
    #[test]
    fn test_list_project_snapshots_groups_per_model() {
        let state = make_state();
        state.set_snapshot(make_payload("p1", "m2", "Struct", "2026-01-02T00:00:00Z")).unwrap();
        state.set_snapshot(make_payload("p1", "m1", "Arch", "2026-01-01T00:00:00Z")).unwrap();

        let result = list_project_snapshots(&state, "p1").unwrap();

        assert_eq!(result.models.len(), 2);
        assert_eq!(result.models[0].name, "Arch");
        assert_eq!(result.models[0].latest, "2026-01-01T00:00:00Z");
        assert_eq!(result.models[0].snapshots, vec!["2026-01-01T00:00:00Z".to_string()]);
        assert_eq!(result.models[1].name, "Struct");
    }

    /// An unknown or unregistered project answers an empty list, not an
    /// error — and never leaks another project's models.
    #[test]
    fn test_list_project_snapshots_unknown_and_unregistered_are_empty() {
        let state = make_state();
        state.set_snapshot(make_payload("p1", "m1", "Arch", "2026-01-01T00:00:00Z")).unwrap();
        state.set_snapshot(make_payload("ghost", "mg", "Ghost", "2026-01-01T00:00:00Z")).unwrap();

        assert!(list_project_snapshots(&state, "nonexistent").unwrap().models.is_empty());
        assert!(list_project_snapshots(&state, "ghost").unwrap().models.is_empty());
    }

    /// `latest_snapshot` answers the one id for a known model and `None` for
    /// an unknown model or an unregistered project.
    #[test]
    fn test_latest_snapshot() {
        let state = make_state();
        state.set_snapshot(make_payload("p1", "m1", "Arch", "2026-01-01T00:00:00Z")).unwrap();
        state.set_snapshot(make_payload("ghost", "mg", "Ghost", "2026-01-01T00:00:00Z")).unwrap();

        let latest = latest_snapshot(&state, "p1", "m1").unwrap().unwrap();
        assert_eq!(latest.taken_at, "2026-01-01T00:00:00Z");

        assert!(latest_snapshot(&state, "p1", "unknown-model").unwrap().is_none());
        assert!(latest_snapshot(&state, "ghost", "mg").unwrap().is_none());
    }
}
