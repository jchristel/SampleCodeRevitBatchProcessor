//! Milestone listings for the viewer's dropdown: which named dated pins a
//! project defines. Read from the project's *settings bundle* (the registry),
//! not storage — milestones are settings-resident (see
//! `settings::Milestone`), so this list hot-updates the moment a settings
//! save lands, no push required.

use serde::Serialize;

use super::ServiceError;
use crate::state::AppState;

/// One milestone as the picker sees it. `attached_models` is a *count* of
/// model pins, not the pin map itself — the dropdown only labels options, and
/// the settings UI (which edits the pins) reads the full map through the
/// settings API instead. `drofus_snapshot` is the exception: it's a single
/// scalar, not a map, and surfacing it here is what lets a consumer (notably
/// the MCP `list_milestones` tool) see *whether and what* dRofus a milestone
/// pins without a second `get_project_settings` call. Absent when the
/// milestone joins the current dRofus (no pin).
#[derive(Serialize)]
pub struct MilestoneSummary {
    pub name: String,
    pub date: String,
    pub attached_models: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub drofus_snapshot: Option<String>,
}

#[derive(Serialize)]
pub struct MilestonesResponse {
    pub milestones: Vec<MilestoneSummary>,
}

/// Every milestone one project defines, newest date first (the order a
/// picker wants under a "Latest" default). Unknown or unregistered project →
/// empty list, not an error — same soft-success discipline as
/// `list_buildings`.
pub fn list_milestones(state: &AppState, project_id: &str) -> Result<MilestonesResponse, ServiceError> {
    let registry = state.settings();
    let Some(bundle) = registry.settings_for(project_id) else {
        return Ok(MilestonesResponse { milestones: vec![] });
    };

    let mut milestones: Vec<MilestoneSummary> = bundle
        .milestones
        .iter()
        .map(|m| MilestoneSummary {
            name: m.name.clone(),
            date: m.date.clone(),
            attached_models: m.attachments.len(),
            drofus_snapshot: m.drofus_snapshot.clone(),
        })
        .collect();
    // Both accepted date shapes (`YYYY-MM-DD`, RFC3339) start with the
    // lexically-sortable date part, so string order == chronological order.
    milestones.sort_by(|a, b| b.date.cmp(&a.date).then_with(|| a.name.cmp(&b.name)));
    Ok(MilestonesResponse { milestones })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::settings::Milestone;
    use crate::state::ProjectSettings;
    use crate::storage::MemStore;
    use std::collections::BTreeMap;

    fn make_milestone(name: &str, date: &str) -> Milestone {
        Milestone {
            name: name.to_string(),
            date: date.to_string(),
            drofus_snapshot: None,
            attachments: BTreeMap::from([("m1".to_string(), "2026-01-01T00:00:00Z".to_string())]),
        }
    }

    fn make_bundle(milestones: Vec<Milestone>) -> ProjectSettings {
        ProjectSettings {
            drofus: None,
            hierarchy: vec![],
            builtin_properties: vec![],
            room_label: vec!["$name".to_string()],
            drofus_fields: vec![],
            milestones,
            comparison_key: None,
            comparison_properties: vec![],
            hierarchy_exclusions: vec![],        }
    }

    /// Milestones list newest date first, each carrying its pin count and its
    /// dRofus pin when set (absent otherwise).
    #[test]
    fn test_list_milestones_newest_first() {
        let mut pinned = make_milestone("Design Freeze", "2026-06-30");
        pinned.drofus_snapshot = Some("2026-06-29T17:00:00Z".to_string());
        let bundle = make_bundle(vec![make_milestone("Concept", "2026-03-01"), pinned]);
        let registry = std::collections::HashMap::from([("p1".to_string(), bundle)]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);

        let result = list_milestones(&state, "p1").unwrap();

        assert_eq!(result.milestones.len(), 2);
        assert_eq!(result.milestones[0].name, "Design Freeze");
        assert_eq!(result.milestones[1].name, "Concept");
        assert_eq!(result.milestones[0].attached_models, 1);
        assert_eq!(result.milestones[0].drofus_snapshot.as_deref(), Some("2026-06-29T17:00:00Z"));
        assert_eq!(result.milestones[1].drofus_snapshot, None, "no pin → absent");
    }

    /// An unknown/unregistered project answers an empty list, not an error.
    #[test]
    fn test_list_milestones_unknown_project_is_empty() {
        let registry = std::collections::HashMap::from([("p1".to_string(), make_bundle(vec![]))]);
        let state = AppState::new(Box::new(MemStore::new()), registry, None);

        assert!(list_milestones(&state, "p1").unwrap().milestones.is_empty());
        assert!(list_milestones(&state, "nonexistent").unwrap().milestones.is_empty());
    }
}
