//! dRofus reconciliation QA: does each room's Revit data agree with dRofus.
//!
//! Moved verbatim out of `handlers::get_project_validation` (see
//! HANDOVER-service-layer.md) -- `compute_validation` never touched a
//! transport type to begin with, so this extraction only adds the
//! `AppState`/`Option<DrofusData>` handling that the handler used to do
//! inline.

use std::collections::{BTreeMap, BTreeSet};

use serde::Serialize;

use crate::contract::{lookup_property, numeric_match, property_presence, PropertyPresence, Room, RoomPayload};
use crate::drofus::DrofusData;
use crate::settings::{BuiltinPropertyDef, CompareMode, DrofusFieldConfig};
use crate::state::{AppState, ModelKey};

use super::ServiceError;

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

/// One reconciled field where dRofus has a real value but the matched room's
/// corresponding Revit property doesn't (see `PropertyPresence`). Kept as two
/// separate response lists rather than one, because the two cases mean
/// different things: landing here via `Absent` means the property was never
/// extracted from Revit for this room at all -- a mapping typo or a
/// parameter the extractor never wired up, worth flagging loudly; via
/// `Empty` it just means nobody has filled the value in yet, an ordinary
/// per-room gap.
#[derive(Serialize)]
pub struct MissingInRevit {
    pub room_id: String,
    pub drofus_id: String,
    pub field: String,
}

/// Whether one dRofus CSV field (row 1) is actually checked by this QA pass,
/// and if so, which Revit property it's checked against. A field overridden
/// `Ignore` in settings is left out of this list entirely -- that's a
/// deliberate exclusion (e.g. a sync timestamp that will legitimately always
/// differ), not a coverage gap someone needs to notice and fix.
#[derive(Serialize)]
pub struct FieldCoverage {
    pub label: String,
    pub checked: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub revit_property: Option<String>,
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
    pub fields_absent_in_revit: Vec<MissingInRevit>,
    pub fields_empty_in_revit: Vec<MissingInRevit>,
    pub field_coverage: Vec<FieldCoverage>,
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
            fields_absent_in_revit: vec![],
            fields_empty_in_revit: vec![],
            field_coverage: vec![],
        }
    }
}

/// The configured QA override for one dRofus field label, or `None` when the
/// column has no declaration, or a declaration with no `qa` set (both mean
/// the default: numeric-adaptive if both sides parse as a number, else exact
/// string match).
fn compare_mode(drofus_fields: &[DrofusFieldConfig], label: &str) -> Option<CompareMode> {
    drofus_fields.iter().find(|f| f.label == label).and_then(|f| f.qa)
}

/// Pure computation behind `compute_project_validation` — pulled out so it's
/// testable without a full `AppState`, same shape as `resolve_label_fields`.
///
/// Four checks, in order: (1) does every room resolve a value for the link
/// property; (2) among those that do, is the value actually unique per room
/// (a shared value is ambiguous — recorded, then excluded from the rest);
/// (3) does each remaining room's value find a dRofus record; (4) for rooms
/// that do, does every reconciled, non-`Ignore`d property agree between the
/// two sides. Also reports `field_coverage`: which dRofus fields this pass
/// actually checks at all, for the panel's "what's being QA'd" reference.
pub fn compute_validation(
    project_id: &str,
    stored: &[(ModelKey, RoomPayload)],
    drofus: &DrofusData,
    builtin_defs: &[BuiltinPropertyDef],
    drofus_fields: &[DrofusFieldConfig],
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
    let mut fields_absent_in_revit = Vec::new();
    let mut fields_empty_in_revit = Vec::new();

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
            if compare_mode(drofus_fields, label) == Some(CompareMode::Ignore) {
                continue;
            }
            // Normalize the dRofus side the same way `lookup_property`
            // already does for the Revit side: a blank cell is "no value
            // here", not a real empty-string value to compare against. A
            // dRofus-side absence isn't tracked further -- only Revit-side
            // absence is (see `MissingInRevit`'s doc comment for why).
            let Some(drofus_value) = record.fields.get(label).filter(|s| !s.is_empty()) else {
                continue;
            };
            match property_presence(room, revit_property, source, builtin_defs) {
                PropertyPresence::Absent => fields_absent_in_revit.push(MissingInRevit {
                    room_id: room.id.clone(),
                    drofus_id: value.clone(),
                    field: label.clone(),
                }),
                PropertyPresence::Empty => fields_empty_in_revit.push(MissingInRevit {
                    room_id: room.id.clone(),
                    drofus_id: value.clone(),
                    field: label.clone(),
                }),
                PropertyPresence::Present(room_value) => {
                    let matches = if compare_mode(drofus_fields, label) == Some(CompareMode::Exact) {
                        drofus_value.trim() == room_value.trim()
                    } else {
                        numeric_match(drofus_value, &room_value)
                            .unwrap_or_else(|| drofus_value.trim() == room_value.trim())
                    };
                    if !matches {
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
    }

    // Which dRofus fields this pass actually checks: every row-1 label
    // except those overridden `Ignore` (a deliberate exclusion, hidden from
    // this report entirely rather than shown as "not checked").
    let ignored: BTreeSet<&str> = drofus_fields
        .iter()
        .filter(|f| f.qa == Some(CompareMode::Ignore))
        .map(|f| f.label.as_str())
        .collect();
    let field_coverage: Vec<FieldCoverage> = drofus
        .all_labels
        .iter()
        .filter(|label| !ignored.contains(label.as_str()))
        .map(|label| FieldCoverage {
            label: label.clone(),
            checked: drofus.reconciliation.contains_key(label),
            revit_property: drofus.reconciliation.get(label).cloned(),
        })
        .collect();

    ValidationResponse {
        drofus_configured: true,
        link_property: Some(drofus.link_property.clone()),
        total_rooms,
        rooms_missing_link_value,
        duplicate_link_values,
        rooms_unmatched_in_drofus,
        property_mismatches,
        fields_absent_in_revit,
        fields_empty_in_revit,
        field_coverage,
    }
}

/// Data-quality report for the header's validation panel — see
/// `ValidationResponse`/`compute_validation`. `drofus_configured: false` is a
/// normal, non-error result (no dRofus source at all) and is returned as
/// `Ok`; a storage read failure is a real internal error and surfaces as
/// `ServiceError::Internal`, so the HTTP adapter can still map it to 500
/// exactly as it does today.
pub fn compute_project_validation(state: &AppState, project_id: &str) -> Result<ValidationResponse, ServiceError> {
    let Some(drofus) = state.drofus.as_ref() else {
        return Ok(ValidationResponse::drofus_not_configured());
    };

    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;

    Ok(compute_validation(project_id, &stored, drofus, &state.builtin_properties, &state.drofus_fields))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{CustomValue, Model, Project, Snapshot};
    use crate::drofus::DrofusRecord;

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
        // `all_labels` mirrors the real loader's row-1 label set: the union
        // of every reconciled label and every field label that shows up in
        // any record (the real CSV always has a row-1 label for a column
        // regardless of whether row 2 mapped it).
        let mut all_labels: BTreeSet<String> = BTreeSet::new();
        for (id, fields) in records {
            let mut f = BTreeMap::new();
            for (k, v) in *fields {
                f.insert(k.to_string(), v.to_string());
                all_labels.insert(k.to_string());
            }
            by_id.insert(id.to_string(), DrofusRecord { fields: f });
        }
        let mut reconciliation_map = BTreeMap::new();
        for (k, v) in reconciliation {
            reconciliation_map.insert(k.to_string(), v.to_string());
            all_labels.insert(k.to_string());
        }
        DrofusData {
            link_property: link_property.to_string(),
            by_id,
            reconciliation: reconciliation_map,
            all_labels: all_labels.into_iter().collect(),
        }
    }

    /// A room with no value for the link property is reported, not silently
    /// dropped.
    #[test]
    fn test_compute_validation_missing_link_value() {
        let room = make_room("1", "Room", &[]); // no "Number" property
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[], &[]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

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

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

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

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

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

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.rooms_unmatched_in_drofus.is_empty());
        assert_eq!(result.property_mismatches.len(), 1);
        let mismatch = &result.property_mismatches[0];
        assert_eq!(mismatch.field, "NetArea");
        assert_eq!(mismatch.room_value, "25.5");
        assert_eq!(mismatch.drofus_value, "30.0");
    }

    /// The reported bug: a unit-conversion float artifact (Revit's
    /// `"1.49999935417"` vs dRofus's `"1.5"`) must not be flagged once both
    /// are rounded to the lesser stated precision.
    #[test]
    fn test_compute_validation_numeric_tolerance_no_false_mismatch() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Area", "1.49999935417")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("NetArea", "1.5")])], &[("NetArea", "Area")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.property_mismatches.is_empty());
    }

    /// A blank dRofus cell must be treated as "no value here", not compared
    /// against Revit's real value -- previously this produced a false
    /// `""` vs `"25.5"` mismatch.
    #[test]
    fn test_compute_validation_empty_drofus_value_not_flagged() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Area", "25.5")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("NetArea", "")])], &[("NetArea", "Area")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.property_mismatches.is_empty());
        assert!(result.fields_absent_in_revit.is_empty());
        assert!(result.fields_empty_in_revit.is_empty());
    }

    /// dRofus has a real value but the room has no such Revit property at
    /// all -- the serious case (mapping/model-setup problem), reported
    /// separately from a merely-blank value.
    #[test]
    fn test_compute_validation_field_absent_in_revit() {
        let room = make_room("1", "Room", &[("Number", "1")]); // no "Area" property at all
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("NetArea", "30.0")])], &[("NetArea", "Area")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.property_mismatches.is_empty());
        assert!(result.fields_empty_in_revit.is_empty());
        assert_eq!(result.fields_absent_in_revit.len(), 1);
        assert_eq!(result.fields_absent_in_revit[0].field, "NetArea");
    }

    /// dRofus has a real value, the room's Revit property exists but is
    /// blank -- an ordinary per-room gap, reported separately from `Absent`.
    #[test]
    fn test_compute_validation_field_empty_in_revit() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Area", "")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("NetArea", "30.0")])], &[("NetArea", "Area")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.property_mismatches.is_empty());
        assert!(result.fields_absent_in_revit.is_empty());
        assert_eq!(result.fields_empty_in_revit.len(), 1);
        assert_eq!(result.fields_empty_in_revit[0].field, "NetArea");
    }

    /// A field overridden `Ignore` is skipped entirely: no mismatch, no
    /// absent/empty entry, and no row in the coverage report.
    #[test]
    fn test_compute_validation_ignore_override_skips_field_entirely() {
        let room = make_room("1", "Room", &[("Number", "1"), ("SyncTime", "2026-07-02")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("LastSync", "2026-06-29")])], &[("LastSync", "SyncTime")]);
        // Also declares the field's type -- proves `qa: Ignore` and `type:
        // Date` coexist: QA still skips it, independent of what a future
        // date-consuming feature would do with the same declaration.
        let drofus_fields = vec![crate::settings::DrofusFieldConfig {
            label: "LastSync".to_string(),
            field_type: crate::settings::FieldType::Date,
            format: Some("%Y-%m-%d".to_string()),
            qa: Some(CompareMode::Ignore),
        }];

        let result = compute_validation("p1", &stored, &drofus, &[], &drofus_fields);

        assert!(result.property_mismatches.is_empty());
        assert!(result.fields_absent_in_revit.is_empty());
        assert!(result.fields_empty_in_revit.is_empty());
        assert!(result.field_coverage.iter().all(|c| c.label != "LastSync"));
    }

    /// The coverage report shows every dRofus field: a reconciled one as
    /// checked (with its mapped Revit property), an unmapped one as
    /// unchecked.
    #[test]
    fn test_compute_validation_field_coverage() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Area", "25.5")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus(
            "Number",
            &[("1", &[("NetArea", "25.5"), ("Notes", "not mapped")])],
            &[("NetArea", "Area")],
        );

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        let net_area = result.field_coverage.iter().find(|c| c.label == "NetArea").unwrap();
        assert!(net_area.checked);
        assert_eq!(net_area.revit_property.as_deref(), Some("Area"));

        let notes = result.field_coverage.iter().find(|c| c.label == "Notes").unwrap();
        assert!(!notes.checked);
        assert!(notes.revit_property.is_none());
    }
}
