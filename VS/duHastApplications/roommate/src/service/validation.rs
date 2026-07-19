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
use crate::settings::{BuiltinPropertyDef, CompareMode, DrofusFieldConfig, FieldType};
use crate::state::{AppState, ModelKey};

use super::ServiceError;

/// Resolved link value → every `(room, source)` that resolved to it. A value
/// with more than one entry is an ambiguous (duplicate) link value, excluded
/// from the unmatched/mismatch checks. Borrows the rooms out of the stored
/// payloads, hence the lifetime.
type LinkValueIndex<'a> = BTreeMap<String, Vec<(&'a Room, &'a str)>>;

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

/// Per-room detail for a room that appears in some discrepancy list — the
/// human-friendly fields the CSV export shows beyond the bare `room_id`. Keyed
/// by `room_id` in `ValidationResponse::error_rooms`. Every field defaults to
/// `""` when the underlying property doesn't resolve (an absent room Number, or
/// a room that resolved no link value at all), so a consumer never has to
/// distinguish "absent" from "empty" here — the discrepancy lists already carry
/// that distinction where it matters.
#[derive(Serialize)]
pub struct ErrorRoomInfo {
    /// The room's Revit "Number" parameter value (resolved via `lookup_property`).
    pub number: String,
    /// The room's Revit "Name" parameter value (resolved via `lookup_property`).
    pub name: String,
    /// The room's dRofus link value — its value for the link property. `""` when
    /// the room resolved none (i.e. it's in `rooms_missing_link_value`).
    pub link_value: String,
}

/// Discrepancy tallies so a consumer (MCP `get_validation`, the browser panel)
/// can answer "how many discrepancies?" without re-summing the six lists.
/// Category counts are the **list lengths** — `duplicate_link_values` counts
/// duplicate-value *groups*, not the rooms in them — matching the panel's
/// existing issue count. `total` is their sum.
#[derive(Serialize)]
pub struct DiscrepancyCounts {
    pub total: usize,
    pub rooms_missing_link_value: usize,
    pub duplicate_link_values: usize,
    pub rooms_unmatched_in_drofus: usize,
    pub property_mismatches: usize,
    pub fields_absent_in_revit: usize,
    pub fields_empty_in_revit: usize,
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
    /// Discrepancy tallies (total + per-category) — see `DiscrepancyCounts`.
    pub discrepancies: DiscrepancyCounts,
    /// `room_id` → its `ErrorRoomInfo`, populated only for rooms that appear in
    /// some discrepancy list above. What the CSV export reads to fill its
    /// room_number/room_name/link-value columns.
    pub error_rooms: BTreeMap<String, ErrorRoomInfo>,
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
            discrepancies: DiscrepancyCounts {
                total: 0,
                rooms_missing_link_value: 0,
                duplicate_link_values: 0,
                rooms_unmatched_in_drofus: 0,
                property_mismatches: 0,
                fields_absent_in_revit: 0,
                fields_empty_in_revit: 0,
            },
            error_rooms: BTreeMap::new(),
        }
    }
}

/// The declaration for one dRofus field label, if the settings carry one.
fn field_config<'a>(drofus_fields: &'a [DrofusFieldConfig], label: &str) -> Option<&'a DrofusFieldConfig> {
    drofus_fields.iter().find(|f| f.label == label)
}

/// The configured QA override for one dRofus field label, or `None` when the
/// column has no declaration, or a declaration with no `qa` set (both mean
/// the default: numeric-adaptive if both sides parse as a number, else exact
/// string match).
fn compare_mode(drofus_fields: &[DrofusFieldConfig], label: &str) -> Option<CompareMode> {
    field_config(drofus_fields, label).and_then(|f| f.qa)
}

/// One side of a date comparison. Whether the pattern captured a UTC offset
/// decides how the two sides can be compared (see `date_match`).
enum ParsedDate {
    /// The pattern carried an offset (`%z`-family): a real instant.
    Zoned(chrono::DateTime<chrono::FixedOffset>),
    /// No offset in the pattern: a wall-clock reading with no timezone.
    Naive(chrono::NaiveDateTime),
}

/// Parse one side's raw string with its declared strftime pattern. Tries the
/// offset-aware form first (a pattern without `%z` never matches it), then
/// datetime, then bare date (midnight) — so one declaration covers whichever
/// granularity the column actually holds.
fn parse_date_side(s: &str, fmt: &str) -> Option<ParsedDate> {
    use chrono::{DateTime, NaiveDate, NaiveDateTime};
    if let Ok(dt) = DateTime::parse_from_str(s, fmt) {
        return Some(ParsedDate::Zoned(dt));
    }
    if let Ok(dt) = NaiveDateTime::parse_from_str(s, fmt) {
        return Some(ParsedDate::Naive(dt));
    }
    if let Ok(d) = NaiveDate::parse_from_str(s, fmt) {
        return Some(ParsedDate::Naive(d.and_hms_opt(0, 0, 0).expect("midnight is always valid")));
    }
    None
}

/// Typed comparison for a `Date`-declared field: parse both sides with their
/// declared patterns and compare what they denote, so two renderings of the
/// same moment don't count as a mismatch. Same `None = fall back` contract as
/// `numeric_match`: if either side fails to parse, the caller drops to the
/// string path — the declaration is a hint, not truth (the same stance
/// `CustomValue.storage_type` takes).
///
/// Comparison rule when the two sides differ in offset-awareness: two zoned
/// sides compare as instants; a zoned side against a naive side compares the
/// zoned side's *local* wall-clock reading against the naive one (the naive
/// side has no timezone to convert with, and its writer most plausibly wrote
/// local time); two naive sides compare directly.
fn date_match(drofus_value: &str, room_value: &str, drofus_fmt: &str, revit_fmt: &str) -> Option<bool> {
    let a = parse_date_side(drofus_value.trim(), drofus_fmt)?;
    let b = parse_date_side(room_value.trim(), revit_fmt)?;
    Some(match (a, b) {
        (ParsedDate::Zoned(a), ParsedDate::Zoned(b)) => a == b,
        (ParsedDate::Zoned(z), ParsedDate::Naive(n)) | (ParsedDate::Naive(n), ParsedDate::Zoned(z)) => {
            z.naive_local() == n
        }
        (ParsedDate::Naive(a), ParsedDate::Naive(b)) => a == b,
    })
}

/// A copy of `s` with every non-ASCII character replaced by `?`, mirroring
/// duHast's `encode_ascii` step (Python's `str.encode("ascii", "replace")`,
/// see `Objects/base.py`'s `to_json_utf`) that every room value already went
/// through before it reached this service. Used to re-check a string-compare
/// mismatch: if narrowing the dRofus side the same lossy way makes it equal
/// to the room value, the two sides agree and the mismatch was purely an
/// artefact of that export step (HANDOVER_utf8.md), not a real disagreement.
fn ascii_narrowed(s: &str) -> String {
    s.chars().map(|c| if c.is_ascii() { c } else { '?' }).collect()
}

/// Phase 1 — resolve every room's link-property value. Returns the room
/// count, the ids of rooms that resolved no value at all
/// (`rooms_missing_link_value`), and a map of resolved link value → every
/// `(room, source)` that resolved to it (so the caller can detect a value
/// shared by more than one room). Borrows the rooms out of `stored`.
fn resolve_link_values<'a>(
    project_id: &str,
    stored: &'a [(ModelKey, RoomPayload)],
    drofus: &DrofusData,
    builtin_defs: &[BuiltinPropertyDef],
) -> (usize, Vec<String>, LinkValueIndex<'a>) {
    let mut total_rooms = 0;
    let mut rooms_missing_link_value = Vec::new();
    let mut by_value: LinkValueIndex = BTreeMap::new();

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

    (total_rooms, rooms_missing_link_value, by_value)
}

/// The typed comparison ladder for one reconciled field, each rung falling
/// through to the next on `None`: a `Date`-declared field is compared as
/// parsed instants first (two renderings of one moment agree); then
/// `numeric_match` when both sides parse as numbers; finally string equality
/// (with the ASCII-narrowing re-check that forgives duHast's lossy
/// `encode_ascii` export step — see `ascii_narrowed`). `Exact` mode skips both
/// typed rungs and forces the string comparison.
fn field_values_agree(drofus_value: &str, room_value: &str, field_cfg: Option<&DrofusFieldConfig>) -> bool {
    let exact_mode = field_cfg.and_then(|f| f.qa) == Some(CompareMode::Exact);
    let date = if exact_mode {
        None
    } else {
        field_cfg.filter(|f| f.field_type == FieldType::Date).and_then(|f| {
            let fmt = f.format.as_deref()?; // always Some on Date (validated at startup)
            let revit_fmt = f.revit_format.as_deref().unwrap_or(fmt);
            date_match(drofus_value, room_value, fmt, revit_fmt)
        })
    };
    let numeric = if exact_mode || date.is_some() {
        None
    } else {
        numeric_match(drofus_value, room_value)
    };
    match (date, numeric) {
        (Some(date_matches), _) => date_matches,
        (None, Some(numeric_matches)) => numeric_matches,
        (None, None) => {
            drofus_value.trim() == room_value.trim()
                || ascii_narrowed(drofus_value.trim()) == room_value.trim()
        }
    }
}

/// Phase 3 — which dRofus fields this pass actually checks: every row-1 label
/// except those overridden `Ignore` (a deliberate exclusion, hidden from this
/// report entirely rather than shown as "not checked"), each flagged with
/// whether row 2 mapped it to a Revit property.
fn compute_field_coverage(drofus: &DrofusData, drofus_fields: &[DrofusFieldConfig]) -> Vec<FieldCoverage> {
    let ignored: BTreeSet<&str> = drofus_fields
        .iter()
        .filter(|f| f.qa == Some(CompareMode::Ignore))
        .map(|f| f.label.as_str())
        .collect();
    drofus
        .all_labels
        .iter()
        .filter(|label| !ignored.contains(label.as_str()))
        .map(|label| FieldCoverage {
            label: label.clone(),
            checked: drofus.reconciliation.contains_key(label),
            revit_property: drofus.reconciliation.get(label).cloned(),
        })
        .collect()
}

/// Resolve the human-friendly detail (`ErrorRoomInfo`) for every room whose id
/// is in `error_ids`, in a single pass over the project's rooms. Number, name
/// and link value all go through `lookup_property` the same way
/// `resolve_link_values` resolves the link value — so canonical→raw resolution
/// (and the source dimension) stays consistent with the rest of the pass, and a
/// property that doesn't resolve degrades to `""` (the CSV shows a blank cell).
///
/// Keyed by `room_id`, which is only unique within a model — the same
/// pre-existing caveat the discrepancy lists already carry (a colliding id from
/// a second linked model resolves to whichever room is seen last). This is a
/// detail lookup for display, not an identity the checks depend on.
fn collect_error_rooms(
    project_id: &str,
    stored: &[(ModelKey, RoomPayload)],
    drofus: &DrofusData,
    builtin_defs: &[BuiltinPropertyDef],
    error_ids: &BTreeSet<String>,
) -> BTreeMap<String, ErrorRoomInfo> {
    let mut error_rooms = BTreeMap::new();
    for (_key, payload) in stored {
        if payload.project.id != project_id {
            continue;
        }
        let source = &payload.model.source;
        for room in &payload.rooms {
            if !error_ids.contains(&room.id) {
                continue;
            }
            error_rooms.insert(
                room.id.clone(),
                ErrorRoomInfo {
                    number: lookup_property(room, "Number", source, builtin_defs).unwrap_or_default(),
                    name: lookup_property(room, "Name", source, builtin_defs).unwrap_or_default(),
                    link_value: lookup_property(room, &drofus.link_property, source, builtin_defs)
                        .unwrap_or_default(),
                },
            );
        }
    }
    error_rooms
}

/// Pure computation behind `compute_project_validation` — pulled out so it's
/// testable without a full `AppState`, same shape as `resolve_label_fields`.
///
/// Four checks, in order: (1) does every room resolve a value for the link
/// property (`resolve_link_values`); (2) among those that do, is the value
/// actually unique per room (a shared value is ambiguous — recorded, then
/// excluded from the rest); (3) does each remaining room's value find a dRofus
/// record; (4) for rooms that do, does every reconciled, non-`Ignore`d
/// property agree between the two sides (`field_values_agree`). Also reports
/// `field_coverage` (`compute_field_coverage`): which dRofus fields this pass
/// actually checks at all, for the panel's "what's being QA'd" reference.
pub fn compute_validation(
    project_id: &str,
    stored: &[(ModelKey, RoomPayload)],
    drofus: &DrofusData,
    builtin_defs: &[BuiltinPropertyDef],
    drofus_fields: &[DrofusFieldConfig],
) -> ValidationResponse {
    let (total_rooms, rooms_missing_link_value, by_value) =
        resolve_link_values(project_id, stored, drofus, builtin_defs);

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
                    if !field_values_agree(drofus_value, &room_value, field_config(drofus_fields, label)) {
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

    // Per-category counts (list lengths — duplicate counts as groups, matching
    // the panel's issue count) and their total, so a consumer needn't re-sum.
    let discrepancies = DiscrepancyCounts {
        total: rooms_missing_link_value.len()
            + duplicate_link_values.len()
            + rooms_unmatched_in_drofus.len()
            + property_mismatches.len()
            + fields_absent_in_revit.len()
            + fields_empty_in_revit.len(),
        rooms_missing_link_value: rooms_missing_link_value.len(),
        duplicate_link_values: duplicate_link_values.len(),
        rooms_unmatched_in_drofus: rooms_unmatched_in_drofus.len(),
        property_mismatches: property_mismatches.len(),
        fields_absent_in_revit: fields_absent_in_revit.len(),
        fields_empty_in_revit: fields_empty_in_revit.len(),
    };

    // Every room id that appears in any discrepancy list — the set the CSV
    // export needs number/name/link-value for.
    let mut error_ids: BTreeSet<String> = BTreeSet::new();
    error_ids.extend(rooms_missing_link_value.iter().cloned());
    error_ids.extend(duplicate_link_values.iter().flat_map(|d| d.room_ids.iter().cloned()));
    error_ids.extend(rooms_unmatched_in_drofus.iter().cloned());
    error_ids.extend(property_mismatches.iter().map(|m| m.room_id.clone()));
    error_ids.extend(fields_absent_in_revit.iter().map(|m| m.room_id.clone()));
    error_ids.extend(fields_empty_in_revit.iter().map(|m| m.room_id.clone()));
    let error_rooms = collect_error_rooms(project_id, stored, drofus, builtin_defs, &error_ids);

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
        field_coverage: compute_field_coverage(drofus, drofus_fields),
        discrepancies,
        error_rooms,
    }
}

/// Data-quality report for the header's validation panel — see
/// `ValidationResponse`/`compute_validation`. `drofus_configured: false` is a
/// normal, non-error result — covers both "no dRofus source configured for
/// this project" and "this project has no registered settings at all" (the
/// latter has no separate signal here, same as `list_buildings`) — and is
/// returned as `Ok`; a storage read failure is a real internal error and
/// surfaces as `ServiceError::Internal`, so the HTTP adapter can still map it
/// to 500 exactly as it does today.
pub fn compute_project_validation(state: &AppState, project_id: &str) -> Result<ValidationResponse, ServiceError> {
    let registry = state.settings();
    let Some(bundle) = registry.settings_for(project_id) else {
        return Ok(ValidationResponse::drofus_not_configured());
    };
    let Some(drofus) = bundle.drofus.as_ref() else {
        return Ok(ValidationResponse::drofus_not_configured());
    };

    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;

    Ok(compute_validation(project_id, &stored, drofus, &bundle.builtin_properties, &bundle.drofus_fields))
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
            model_to_shared: None,
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

    /// A discrepant room carries its number/name/link-value in `error_rooms`
    /// (what the CSV export shows beyond the id), and the discrepancy counts
    /// tally the lists.
    #[test]
    fn test_compute_validation_error_rooms_and_counts() {
        let room = make_room(
            "r1",
            "Office 101",
            &[("Number", "101"), ("Name", "Office"), ("Area", "25.5")],
        );
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("101", &[("NetArea", "30.0")])], &[("NetArea", "Area")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        // One mismatch (Area 25.5 vs NetArea 30.0), and the counts reflect it.
        assert_eq!(result.property_mismatches.len(), 1);
        assert_eq!(result.discrepancies.property_mismatches, 1);
        assert_eq!(result.discrepancies.total, 1);

        // The mismatched room's detail: Revit Number/Name params + link value.
        let info = result.error_rooms.get("r1").expect("mismatched room has detail");
        assert_eq!(info.number, "101");
        assert_eq!(info.name, "Office");
        assert_eq!(info.link_value, "101");
    }

    /// A room missing its link value appears in `error_rooms` with an empty
    /// `link_value` (there is none to resolve), while its Name still resolves;
    /// the counts tally the missing-link category and the total.
    #[test]
    fn test_compute_validation_error_rooms_missing_link_value_blank() {
        let room = make_room("r1", "Office", &[("Name", "Office")]); // no "Number"
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[], &[]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert_eq!(result.rooms_missing_link_value, vec!["r1".to_string()]);
        assert_eq!(result.discrepancies.rooms_missing_link_value, 1);
        assert_eq!(result.discrepancies.total, 1);

        let info = result.error_rooms.get("r1").expect("missing-link room has detail");
        assert_eq!(info.link_value, "", "no link value resolved → blank");
        assert_eq!(info.number, "", "no Number param → blank");
        assert_eq!(info.name, "Office");
    }

    /// The reported bug: the Revit export's ASCII-narrowing step replaces any
    /// non-ASCII character with `?` before the value reaches this service, so
    /// a room value that legitimately started with an en dash arrives as
    /// `?`. That must not be flagged once the dRofus side is narrowed the
    /// same lossy way and the two agree (HANDOVER_utf8.md).
    #[test]
    fn test_compute_validation_ascii_narrowing_no_false_mismatch() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Department", "Loading Dock ? Option 2")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus(
            "Number",
            &[("1", &[("Dept", "Loading Dock \u{2013} Option 2")])],
            &[("Dept", "Department")],
        );

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert!(result.property_mismatches.is_empty());
    }

    /// A genuine content mismatch that merely happens to contain a literal
    /// `?` on the dRofus side must still be reported -- narrowing only
    /// rescues a mismatch when it's the *sole* difference, not any mismatch
    /// touching a `?` character.
    #[test]
    fn test_compute_validation_ascii_narrowing_does_not_mask_genuine_mismatch() {
        let room = make_room("1", "Room", &[("Number", "1"), ("Department", "MECH")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("Dept", "SM.EX?")])], &[("Dept", "Department")]);

        let result = compute_validation("p1", &stored, &drofus, &[], &[]);

        assert_eq!(result.property_mismatches.len(), 1);
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
            revit_format: None,
            qa: Some(CompareMode::Ignore),
        }];

        let result = compute_validation("p1", &stored, &drofus, &[], &drofus_fields);

        assert!(result.property_mismatches.is_empty());
        assert!(result.fields_absent_in_revit.is_empty());
        assert!(result.fields_empty_in_revit.is_empty());
        assert!(result.field_coverage.iter().all(|c| c.label != "LastSync"));
    }

    /// A `Date` field declaration for tests: the shipped dRofus pattern,
    /// optionally a distinct Revit-side pattern, optionally a QA override.
    fn date_field(label: &str, revit_format: Option<&str>, qa: Option<CompareMode>) -> DrofusFieldConfig {
        DrofusFieldConfig {
            label: label.to_string(),
            field_type: FieldType::Date,
            format: Some("%-m/%-d/%Y %-I:%M:%S %p %z".to_string()),
            revit_format: revit_format.map(|s| s.to_string()),
            qa,
        }
    }

    const DROFUS_DATE_FMT: &str = "%-m/%-d/%Y %-I:%M:%S %p %z";

    /// `date_match` with the shipped dRofus pattern: two renderings of the
    /// same instant agree, different instants disagree, and an unparseable
    /// side yields `None` (fall back to string comparison).
    #[test]
    fn test_date_match_same_instant_different_rendering() {
        // Same instant: 5:01:01 PM +10:00 == 7:01:01 AM +00:00.
        assert_eq!(
            date_match(
                "6/29/2026 5:01:01 PM +10:00",
                "6/29/2026 7:01:01 AM +00:00",
                DROFUS_DATE_FMT,
                DROFUS_DATE_FMT,
            ),
            Some(true)
        );
        assert_eq!(
            date_match(
                "6/29/2026 5:01:01 PM +10:00",
                "6/29/2026 5:01:02 PM +10:00",
                DROFUS_DATE_FMT,
                DROFUS_DATE_FMT,
            ),
            Some(false)
        );
        assert_eq!(
            date_match("not a date", "6/29/2026 5:01:01 PM +10:00", DROFUS_DATE_FMT, DROFUS_DATE_FMT),
            None
        );
    }

    /// A distinct `revit_format` parses the room side with its own pattern; a
    /// zoned dRofus side against a naive Revit side compares the zoned side's
    /// local wall-clock reading.
    #[test]
    fn test_date_match_revit_format_and_mixed_offset() {
        assert_eq!(
            date_match(
                "6/29/2026 5:01:01 PM +10:00",
                "2026-06-29 17:01:01",
                DROFUS_DATE_FMT,
                "%Y-%m-%d %H:%M:%S",
            ),
            Some(true)
        );
        assert_eq!(
            date_match(
                "6/29/2026 5:01:01 PM +10:00",
                "2026-06-29 07:01:01",
                DROFUS_DATE_FMT,
                "%Y-%m-%d %H:%M:%S",
            ),
            Some(false),
            "a naive side is a wall-clock reading, not a UTC instant"
        );
    }

    /// A `Date`-declared field where the two sides differ textually but
    /// denote the same instant produces no mismatch; `qa = "exact"` on the
    /// same field forces the textual comparison and reports it.
    #[test]
    fn test_compute_validation_date_field_same_instant_not_flagged() {
        let room = make_room("1", "Room", &[("Number", "1"), ("SyncTime", "6/29/2026 7:01:01 AM +00:00")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus(
            "Number",
            &[("1", &[("LastSync", "6/29/2026 5:01:01 PM +10:00")])],
            &[("LastSync", "SyncTime")],
        );

        let typed = vec![date_field("LastSync", None, None)];
        let result = compute_validation("p1", &stored, &drofus, &[], &typed);
        assert!(result.property_mismatches.is_empty(), "same instant, different rendering: no mismatch");

        let exact = vec![date_field("LastSync", None, Some(CompareMode::Exact))];
        let result = compute_validation("p1", &stored, &drofus, &[], &exact);
        assert_eq!(result.property_mismatches.len(), 1, "exact mode forces the textual comparison");
    }

    /// A `Date` declaration whose values don't actually parse falls back to
    /// the string path -- the declaration is a hint, not truth, so a
    /// free-text value in a date-labeled column still compares as a string.
    #[test]
    fn test_compute_validation_date_field_unparseable_falls_back_to_string() {
        let room = make_room("1", "Room", &[("Number", "1"), ("SyncTime", "pending")]);
        let (key, payload) = make_payload("p1", vec![room]);
        let stored = vec![(key, payload)];
        let drofus = make_drofus("Number", &[("1", &[("LastSync", "pending")])], &[("LastSync", "SyncTime")]);

        let typed = vec![date_field("LastSync", None, None)];
        let result = compute_validation("p1", &stored, &drofus, &[], &typed);
        assert!(result.property_mismatches.is_empty(), "equal strings agree on the fallback path");
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
