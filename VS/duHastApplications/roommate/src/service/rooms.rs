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
use crate::drofus::{DrofusData, DrofusRecord};
use crate::settings::{BuiltinPropertyDef, HierarchyTier};
use crate::state::{AppState, ModelKey, ProjectSettings, SettingsRegistry};

use super::ServiceError;

/// A stored payload scoped to one request: its key, the (possibly
/// milestone-substituted) payload, and the project settings bundle it resolves
/// against — borrowed from the request's single settings snapshot, hence the
/// lifetime. The unit the three assembly phases pass between them.
type ScopedPayload<'a> = (ModelKey, RoomPayload, &'a ProjectSettings);

/// The dRofus a milestone view joins against, resolved once per project
/// (`project id → override`). A `Some(data)` is joined instead of the
/// project's current dRofus; a `None` *value* means "attempted, fall back to
/// current" (a missing or unparseable pin, memoised so it's neither re-parsed
/// nor re-warned). Empty on the non-milestone path.
type MilestoneDrofus = BTreeMap<String, Option<DrofusData>>;

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

    /// The owning model's `source` (e.g. "revit"). Carried so a downstream
    /// consumer — `service::comparison` — can resolve this room's canonical
    /// property names against the project's `builtin_properties` exactly the
    /// way assembly already did, rather than re-deriving it. Not part of the
    /// wire shape (the viewer never needs it), so skipped from serialization;
    /// the /rooms JSON is byte-for-byte unchanged.
    #[serde(skip)]
    pub source: String,
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
///
/// `drofus` is passed in explicitly rather than read off `bundle.drofus`, so a
/// milestone view can join a *pinned* dRofus snapshot instead of the project's
/// current data — the default (non-milestone) caller passes
/// `bundle.drofus.as_ref()`, identical to before.
fn assemble_room(bundle: &ProjectSettings, drofus: Option<&DrofusData>, room: &Room, source: &str) -> RoomResponse {
    // dRofus join: read the link property off the room, look up the record.
    let drofus = drofus.and_then(|d| {
        lookup_property(room, &d.link_property, source, &bundle.builtin_properties)
            .and_then(|key| d.by_id.get(&key).cloned())
    });

    // Classification resolved fresh — see staleness note on classify_room.
    let classification = classify_room(room, &bundle.hierarchy, source, &bundle.builtin_properties);

    let label = resolve_label_fields(room, &bundle.room_label, source, &bundle.builtin_properties);

    RoomResponse { room: room.clone(), drofus, classification, label, source: source.to_string() }
}

/// Sentinel `building` key for rooms whose "Building" tier didn't resolve —
/// distinct from any real `building_key` output since real keys never start
/// with `__`.
pub const UNCLASSIFIED_BUILDING_KEY: &str = "__unclassified__";

/// Opaque token identifying one building bucket, built from its resolved
/// `(code, name)` pair. Callers (the browser) never decode this — they just
/// echo it back to `/rooms?building=..` — so the encoding only has to be
/// stable for the lifetime of one response, not human-meaningful. Known
/// caveat: a literal `|` inside a code/name could in principle make two
/// distinct pairs collide (`("a|", "b")` and `("a", "|b")` both encode to
/// `"a||b"`); accepted, since a `|` inside a building code is not a realistic
/// input and the cost is only two buckets merging in the picker.
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
    /// A stable content revision summarising *which snapshot* each contributing
    /// model provides (see `scoped_revision`). Two idle responses return a
    /// byte-identical value; a real push bumps it. The viewer compares this one
    /// field instead of re-stringifying the whole payload every poll, so a quiet
    /// system triggers no re-render (see HANDOVER-viewer-performance.md).
    pub revision: String,
    pub levels: Vec<Level>,
    pub rooms: Vec<RoomResponse>,
}

/// A stable content revision for a `RoomsResult`, derived from the set of
/// contributing `(model, snapshot)` pairs. It changes only when a push replaces
/// a model's snapshot (a new `taken_at`) or when the set of contributing models
/// changes, and is byte-identical between two idle responses — which is exactly
/// the "has anything actually changed?" signal the viewer's poll needs.
///
/// It deliberately tracks snapshot *identity*, not derived data: a settings-only
/// change (a colour plan, a dRofus mapping) leaves the pushed geometry untouched
/// and does not move the revision. The set is sorted before hashing so
/// linked-model iteration order can't perturb the result. Milestone pins already
/// substituted their pinned payload upstream, so `snapshot.taken_at` here is the
/// snapshot actually rendered.
fn scoped_revision(scoped: &[ScopedPayload]) -> String {
    use std::hash::{Hash, Hasher};

    let mut parts: Vec<(&str, &str, &str)> = scoped
        .iter()
        .map(|(key, payload, _)| {
            (
                key.project_id.as_str(),
                key.model_id.as_str(),
                payload.snapshot.taken_at.as_str(),
            )
        })
        .collect();
    parts.sort_unstable();

    // DefaultHasher (SipHash with fixed keys) is deterministic across runs, so
    // the value is comparable even across a server restart — the client only
    // ever compares consecutive responses, but stability costs nothing here.
    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    parts.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

/// Merge every stored model's levels and rooms into one flat payload, scoped
/// by an optional project id, an optional opaque building key (from
/// `projects::list_buildings`), and an optional milestone name (from
/// `milestones::list_milestones`). When a building filter is given, a project
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
/// The milestone filter follows the same discipline: a project whose settings
/// define no milestone of that name contributes nothing, a model the
/// milestone doesn't pin contributes nothing, and a pinned model's payload is
/// the *pinned snapshot* loaded from the store instead of the latest — after
/// which every downstream step (level dedup, building filter, dRofus join,
/// classification) runs on the substituted payloads unchanged, so milestone
/// and building filters compose. A pin whose snapshot no longer exists is
/// skipped with a warning — a dangling pin is a signal, not an error, same as
/// an unmatched dRofus key.
///
/// dRofus join and classification are resolved here at response assembly — the
/// stored snapshots stay raw; derived data is never written back to state.
/// A milestone that pins a `drofus_snapshot` joins *that* stored CSV instead of
/// the project's current dRofus, resolved once per project (see below); a pin
/// whose snapshot is missing or unparseable falls back to the current dRofus
/// with a warning, the same signal-not-error stance as a dangling model pin.
///
/// Returns `Ok(None)` when nothing has ever been pushed to this server at all
/// -- the HTTP adapter's "204 No Content" case. A filter that merely matches
/// nothing is still `Ok(Some)` with empty vecs: the store has data, the
/// question just has an empty answer.
pub fn assemble_rooms(
    state: &AppState,
    project: Option<&str>,
    building: Option<&str>,
    milestone: Option<&str>,
) -> Result<Option<RoomsResult>, ServiceError> {
    let stored = state.all_snapshots().map_err(ServiceError::Internal)?;
    if stored.is_empty() {
        return Ok(None);
    }

    // One settings snapshot for the whole request — a save landing mid-merge
    // can't mix old and new bundles in one response. Held here for the length
    // of the request so `scoped`'s `&ProjectSettings` borrows stay valid.
    let registry = state.settings();

    // Three phases, each its own helper: scope the stored payloads to the
    // request (and resolve any milestone substitutions), dedup levels across
    // linked models, then derive the response rooms/levels.
    let (scoped, milestone_drofus) = scope_payloads(state, &registry, stored, project, milestone)?;
    let revision = scoped_revision(&scoped);
    let level_remap = dedup_levels(&scoped);
    let (levels, rooms) = assemble_scoped_rooms(&scoped, &level_remap, &milestone_drofus, building);

    Ok(Some(RoomsResult { schema_version: SUPPORTED_SCHEMA, revision, levels, rooms }))
}

/// Phase 1 — scope the stored payloads to the request. Drops any payload whose
/// project has no registered settings bundle (an unscoped merge is
/// per-project, so a model with nothing to classify/join against has no home —
/// see HANDOVER-per-project-settings.md "skip on read"), and, under a
/// milestone filter, *replaces* each surviving model's latest payload with the
/// snapshot the milestone pins for it (owned payloads, hence no `&` on the
/// tuple's payload slot). A project without the named milestone, or a model it
/// doesn't pin, contributes nothing — the building-filter discipline.
///
/// The second return value is the milestone's pinned dRofus, resolved once per
/// project (`project id → override`): `Some(data)` = joined instead of the
/// project's current dRofus; a `None` *value* means "attempted, fall back to
/// current" (a missing or unparseable pin), memoised so it's neither re-parsed
/// nor re-warned across a project's models. Empty on the non-milestone path.
/// Kept together with the scoping loop that fills it, since that's where the
/// pin is known.
fn scope_payloads<'r>(
    state: &AppState,
    registry: &'r SettingsRegistry,
    stored: Vec<(ModelKey, RoomPayload)>,
    project: Option<&str>,
    milestone: Option<&str>,
) -> Result<(Vec<ScopedPayload<'r>>, MilestoneDrofus), ServiceError> {
    let mut milestone_drofus: MilestoneDrofus = BTreeMap::new();
    let mut scoped: Vec<ScopedPayload> = Vec::new();

    for (key, payload) in stored {
        if project.is_some_and(|p| payload.project.id != p) {
            continue;
        }
        let Some(bundle) = registry.settings_for(&payload.project.id) else {
            continue;
        };
        match milestone {
            None => scoped.push((key, payload, bundle)),
            Some(wanted) => {
                let Some(ms) = bundle.milestones.iter().find(|m| m.name == wanted) else {
                    continue;
                };
                let Some(pinned_id) = ms.attachments.get(&key.model_id) else {
                    continue;
                };
                match state.get_snapshot(&key, pinned_id).map_err(ServiceError::Internal)? {
                    Some(pinned) => {
                        if let Some(drofus_pin) = &ms.drofus_snapshot
                            && !milestone_drofus.contains_key(&key.project_id)
                        {
                            let resolved = resolve_pinned_drofus(state, wanted, &key.project_id, drofus_pin)?;
                            milestone_drofus.insert(key.project_id.clone(), resolved);
                        }
                        scoped.push((key, pinned, bundle));
                    }
                    None => tracing::warn!(
                        "milestone '{}' pins snapshot {:?} for {}/{}, but no such snapshot exists — skipping the model",
                        wanted, pinned_id, key.project_id, key.model_id
                    ),
                }
            }
        }
    }

    Ok((scoped, milestone_drofus))
}

/// Load and parse a milestone's pinned dRofus CSV for one project. A missing
/// or unparseable pin resolves to `None` with a warning (fall back to the
/// project's current dRofus — signal, not error, same stance as a dangling
/// model pin).
fn resolve_pinned_drofus(
    state: &AppState,
    milestone: &str,
    project_id: &str,
    drofus_pin: &str,
) -> Result<Option<DrofusData>, ServiceError> {
    match state.get_drofus(project_id, drofus_pin).map_err(ServiceError::Internal)? {
        Some(bytes) => match crate::drofus::load_drofus_from_bytes(&bytes) {
            Ok(data) => Ok(Some(data)),
            Err(e) => {
                tracing::warn!(
                    "milestone '{}' pins dRofus snapshot {:?} for project {}, but it failed to parse ({e:#}) — falling back to current dRofus",
                    milestone, drofus_pin, project_id
                );
                Ok(None)
            }
        },
        None => {
            tracing::warn!(
                "milestone '{}' pins dRofus snapshot {:?} for project {}, but no such snapshot exists — falling back to current dRofus",
                milestone, drofus_pin, project_id
            );
            Ok(None)
        }
    }
}

/// Phase 2 — level dedup across linked models. A `Level.id` is only unique
/// *within* its own model (same caveat as room ids -- see `ModelKey`'s doc
/// comment), so two linked models that both define "the same" architectural
/// level produce two distinct `Level` rows with the same (name, elevation) but
/// different ids. Merge them: same name + same elevation (tolerant of
/// cross-file float drift via `elevation_match`, the same rounding discipline
/// used for dRofus property comparison) IS the same level. Returns the remap
/// `(project_id, model_id, level_id) -> canonical id`; first-seen id per group
/// wins as canonical, so the level picker and room filtering agree on one id
/// per real-world level.
///
/// Grouped *per project*: level identity is only meaningful within one project
/// (the dedup exists for linked models of one job), so two unrelated projects
/// that both have a "Level 1" @ 0.0 keep their own levels in an unscoped merge
/// instead of collapsing onto whichever project happened to be seen first.
fn dedup_levels(scoped: &[ScopedPayload<'_>]) -> BTreeMap<(String, String, String), String> {
    let mut canonical_levels: BTreeMap<String, Vec<Level>> = BTreeMap::new(); // project_id -> levels
    let mut level_remap: BTreeMap<(String, String, String), String> = BTreeMap::new();
    for (key, payload, _bundle) in scoped {
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
    level_remap
}

/// Phase 3 — derive the response levels and rooms from the scoped payloads.
/// Applies the optional building filter (a project with no "Building" tier
/// matches nothing under it, never everything), emits each canonical level
/// once per project, and joins each room against its effective dRofus (the
/// milestone-pinned override when one resolved, else the project's current
/// dRofus — identical to pre-pinning behaviour), remapping room `level_id`s to
/// the canonical ids from phase 2.
fn assemble_scoped_rooms(
    scoped: &[ScopedPayload<'_>],
    level_remap: &BTreeMap<(String, String, String), String>,
    milestone_drofus: &MilestoneDrofus,
    building: Option<&str>,
) -> (Vec<Level>, Vec<RoomResponse>) {
    let mut levels = Vec::new();
    // Keyed (project_id, canonical_id): canonical ids are model-local, so two
    // projects could in principle mint the same id -- a flat set would let one
    // project's level suppress another's.
    let mut emitted_level_ids: BTreeSet<(String, String)> = BTreeSet::new();
    let mut rooms: Vec<RoomResponse> = Vec::new();

    for (key, payload, bundle) in scoped {
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
        // A milestone-pinned dRofus override wins when it resolved; otherwise
        // (no milestone, no pin, or a pin that fell back) the project's current
        // dRofus — identical to pre-pinning behaviour.
        let effective_drofus = match milestone_drofus.get(&key.project_id) {
            Some(Some(data)) => Some(data),
            _ => bundle.drofus.as_ref(),
        };
        rooms.extend(matching_rooms.into_iter().map(|room| {
            let mut response = assemble_room(bundle, effective_drofus, room, &payload.model.source);
            if let Some(canonical_id) =
                level_remap.get(&(key.project_id.clone(), key.model_id.clone(), room.level_id.clone()))
            {
                response.room.level_id = canonical_id.clone();
            }
            response
        }));
    }

    (levels, rooms)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{CustomValue, Model, Project, RoomPayload, Snapshot};
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

    /// A dRofus dataset with one record: link id `id` carries `label` = `value`.
    /// Used by the milestone-pinning tests to make the *current* dRofus differ
    /// from the *pinned* one for the same room, so the join source is what the
    /// assertion actually distinguishes.
    fn make_drofus_with_record(link_property: &str, id: &str, label: &str, value: &str) -> DrofusData {
        DrofusData {
            link_property: link_property.to_string(),
            by_id: BTreeMap::from([(
                id.to_string(),
                DrofusRecord { fields: BTreeMap::from([(label.to_string(), value.to_string())]) },
            )]),
            reconciliation: BTreeMap::new(),
            all_labels: vec![label.to_string()],
        }
    }

    /// A bundle whose *current* dRofus yields `current_value` (`NetArea`) for
    /// link id "1", with one "Design Freeze" milestone pinning model "m1" to
    /// `pinned_ts` and optionally a `drofus_snapshot`.
    fn bundle_for_drofus_pin(current_value: &str, pinned_ts: &str, drofus_ts: Option<&str>) -> ProjectSettings {
        ProjectSettings {
            drofus: Some(make_drofus_with_record("Number", "1", "NetArea", current_value)),
            milestones: vec![crate::settings::Milestone {
                name: "Design Freeze".to_string(),
                date: "2026-06-30".to_string(),
                drofus_snapshot: drofus_ts.map(|s| s.to_string()),
                attachments: std::collections::BTreeMap::from([("m1".to_string(), pinned_ts.to_string())]),
            }],
            ..make_bundle("Number")
        }
    }

    /// A two-header-row dRofus CSV pinning link id "1" to one `NetArea` value —
    /// the on-store form a `drofus_snapshot` pin loads and parses.
    fn drofus_csv(net_area: &str) -> Vec<u8> {
        format!("DrofusRoomId,NetArea\nNumber,NetArea\n1,{net_area}\n").into_bytes()
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
            milestones: vec![],
            comparison_key: None,
            comparison_properties: vec![],
            hierarchy_exclusions: vec![],        }
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
            model_to_shared: None,
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
            model_to_shared: None,
            levels: vec![Level { id: "lvlA".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![room_a],
        };
        let payload_b = RoomPayload {
            schema_version: 5,
            project: Project { id: "p1".to_string(), name: "P".to_string() },
            model: Model { id: "modelB".to_string(), name: "B".to_string(), source: "revit".to_string() },
            snapshot: Snapshot { taken_at: "2026-01-01T00:00:01Z".to_string() },
            model_to_shared: None,
            // Same name, elevation drifted by float noise well within tolerance.
            levels: vec![Level { id: "lvlB".to_string(), name: "Level 1".to_string(), elevation: 0.000000001 }],
            rooms: vec![room_b],
        };

        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);
        state.set_snapshot(payload_a).unwrap();
        state.set_snapshot(payload_b).unwrap();

        let result = assemble_rooms(&state, Some("p1"), None, None).unwrap().expect("store has data");

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

        let result = assemble_rooms(&state, None, None, None).unwrap();
        assert!(result.is_none(), "nothing has ever been pushed");
    }

    /// The response revision is stable while idle, moves when a push replaces a
    /// model's snapshot, and moves again when the set of contributing models
    /// changes -- this is the one value the viewer polls on instead of
    /// re-stringifying the whole payload (see `scoped_revision`).
    #[test]
    fn test_assemble_rooms_revision_tracks_pushes() {
        let level = vec![Level { id: "l1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }];
        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);
        state
            .set_snapshot(make_payload("p1", "m1", level.clone(), vec![make_room("r1", "Room A", &[])]))
            .unwrap();

        let rev1 = assemble_rooms(&state, None, None, None).unwrap().expect("store has data").revision;
        let rev1_again = assemble_rooms(&state, None, None, None).unwrap().expect("store has data").revision;
        assert_eq!(rev1, rev1_again, "an idle store must return a byte-identical revision every poll");

        // Re-push the same model slot with a newer snapshot id: revision moves.
        let mut newer = make_payload("p1", "m1", level.clone(), vec![make_room("r1", "Room A", &[])]);
        newer.snapshot.taken_at = "2026-02-02T00:00:00Z".to_string();
        state.set_snapshot(newer).unwrap();
        let rev2 = assemble_rooms(&state, None, None, None).unwrap().expect("store has data").revision;
        assert_ne!(rev1, rev2, "a new snapshot for a model must change the revision");

        // A second contributing model changes the set, hence the revision again.
        state
            .set_snapshot(make_payload("p1", "m2", level, vec![make_room("r2", "Room B", &[])]))
            .unwrap();
        let rev3 = assemble_rooms(&state, None, None, None).unwrap().expect("store has data").revision;
        assert_ne!(rev2, rev3, "adding a contributing model must change the revision");
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
            model_to_shared: None,
            levels: vec![Level { id: "l1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
            rooms: vec![make_room("r1", "Room A", &[])],
        };

        // Registry only knows "p1" -- "unregistered" has no bundle and no
        // default is configured.
        let state = AppState::new(Box::new(MemStore::new()), single_project("p1", make_bundle("Number")), None);
        state.set_snapshot(payload).unwrap();

        let result = assemble_rooms(&state, None, None, None).unwrap().expect("the store did receive a push");
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

        let result = assemble_rooms(&state, None, None, None).unwrap().expect("store has data");

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
        let result = assemble_rooms(&state, None, Some(&key), None).unwrap().expect("store has data");

        assert_eq!(result.rooms.len(), 1, "only project A's matching room");
        assert_eq!(result.rooms[0].room.id, "r1");
        assert_eq!(result.levels.len(), 1, "only project A's levels");
        assert_eq!(result.levels[0].name, "Level 1");
    }

    /// A bundle defining one milestone that pins model "m1" to `pinned_ts`.
    fn make_bundle_with_milestone(pinned_ts: &str) -> ProjectSettings {
        make_bundle_with_milestone_drofus(pinned_ts, None)
    }

    /// Like `make_bundle_with_milestone`, but the milestone also pins a
    /// `drofus_snapshot` when `drofus_ts` is `Some`.
    fn make_bundle_with_milestone_drofus(pinned_ts: &str, drofus_ts: Option<&str>) -> ProjectSettings {
        ProjectSettings {
            milestones: vec![crate::settings::Milestone {
                name: "Design Freeze".to_string(),
                date: "2026-06-30".to_string(),
                drofus_snapshot: drofus_ts.map(|s| s.to_string()),
                attachments: std::collections::BTreeMap::from([("m1".to_string(), pinned_ts.to_string())]),
            }],
            ..make_bundle("Number")
        }
    }

    /// A milestone view serves the *pinned* (older) snapshot's rooms while
    /// the default view keeps serving the latest — the core milestone
    /// behavior. Uses FsStore because pinning to history needs a store that
    /// actually keeps it.
    #[test]
    fn test_assemble_rooms_milestone_serves_pinned_snapshot() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-pin-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let old_ts = "2026-06-01T00:00:00Z";
        let mut old = make_payload("p1", "m1", vec![], vec![make_room("r1", "Old Room", &[])]);
        old.snapshot.taken_at = old_ts.to_string();
        let mut new = make_payload("p1", "m1", vec![], vec![make_room("r2", "New Room", &[])]);
        new.snapshot.taken_at = "2026-07-01T00:00:00Z".to_string();

        let state = AppState::new(Box::new(store), single_project("p1", make_bundle_with_milestone(old_ts)), None);
        state.set_snapshot(old).unwrap();
        state.set_snapshot(new).unwrap();

        let latest = assemble_rooms(&state, Some("p1"), None, None).unwrap().expect("store has data");
        assert_eq!(latest.rooms.len(), 1);
        assert_eq!(latest.rooms[0].room.name, "New Room");

        let pinned = assemble_rooms(&state, Some("p1"), None, Some("Design Freeze")).unwrap().expect("store has data");
        assert_eq!(pinned.rooms.len(), 1);
        assert_eq!(pinned.rooms[0].room.name, "Old Room", "milestone view serves the pinned snapshot");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Under a milestone filter, a model the milestone doesn't pin
    /// contributes nothing, and a project defining no milestone of that name
    /// contributes nothing at all — same discipline as the building filter.
    #[test]
    fn test_assemble_rooms_milestone_excludes_unpinned_and_unknown() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-excl-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let ts = "2026-06-01T00:00:00Z";
        let mut pinned_model = make_payload("p1", "m1", vec![], vec![make_room("r1", "Pinned", &[])]);
        pinned_model.snapshot.taken_at = ts.to_string();
        let mut unpinned_model = make_payload("p1", "m2", vec![], vec![make_room("r2", "Unpinned", &[])]);
        unpinned_model.snapshot.taken_at = ts.to_string();

        let state = AppState::new(Box::new(store), single_project("p1", make_bundle_with_milestone(ts)), None);
        state.set_snapshot(pinned_model).unwrap();
        state.set_snapshot(unpinned_model).unwrap();

        let result = assemble_rooms(&state, Some("p1"), None, Some("Design Freeze")).unwrap().expect("store has data");
        assert_eq!(result.rooms.len(), 1, "only the pinned model contributes");
        assert_eq!(result.rooms[0].room.name, "Pinned");

        // A milestone name this project never defined matches nothing.
        let unknown = assemble_rooms(&state, Some("p1"), None, Some("Nonexistent")).unwrap().expect("store has data");
        assert!(unknown.rooms.is_empty());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// The whole dRofus-pinning feature in one test: a milestone that pins a
    /// `drofus_snapshot` joins that stored CSV, while the default (latest) view
    /// joins the project's current dRofus — same room, different join source.
    #[test]
    fn test_assemble_rooms_milestone_joins_pinned_drofus() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-drofus-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let old_model_ts = "2026-06-01T00:00:00Z";
        let old_drofus_ts = "2026-06-01T09:00:00Z";
        // Same room (link id "1") in both snapshots, so only the dRofus differs.
        let mut old = make_payload("p1", "m1", vec![], vec![make_room("r1", "Room", &[("Number", "1")])]);
        old.snapshot.taken_at = old_model_ts.to_string();
        let mut new = make_payload("p1", "m1", vec![], vec![make_room("r1", "Room", &[("Number", "1")])]);
        new.snapshot.taken_at = "2026-07-01T00:00:00Z".to_string();

        // Current dRofus yields "new-value"; the pinned CSV yields "old-value".
        let bundle = bundle_for_drofus_pin("new-value", old_model_ts, Some(old_drofus_ts));
        let state = AppState::new(Box::new(store), single_project("p1", bundle), None);
        state.set_snapshot(old).unwrap();
        state.set_snapshot(new).unwrap();
        state.put_drofus("p1", old_drofus_ts, &drofus_csv("old-value")).unwrap();

        let latest = assemble_rooms(&state, Some("p1"), None, None).unwrap().expect("store has data");
        assert_eq!(
            latest.rooms[0].drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"new-value".to_string()),
            "default view joins the current dRofus"
        );

        let pinned = assemble_rooms(&state, Some("p1"), None, Some("Design Freeze")).unwrap().expect("store has data");
        assert_eq!(
            pinned.rooms[0].drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"old-value".to_string()),
            "milestone view joins the pinned dRofus snapshot"
        );

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A `drofus_snapshot` pointing at an id that was never uploaded falls back
    /// to the current dRofus with a warning — the room is still returned, not
    /// dropped (dRofus is a join, not the room itself).
    #[test]
    fn test_assemble_rooms_milestone_missing_drofus_pin_falls_back() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-drofus-miss-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let model_ts = "2026-06-01T00:00:00Z";
        let mut pinned_model = make_payload("p1", "m1", vec![], vec![make_room("r1", "Room", &[("Number", "1")])]);
        pinned_model.snapshot.taken_at = model_ts.to_string();

        // Pins a dRofus id that is never put into the store.
        let bundle = bundle_for_drofus_pin("current-value", model_ts, Some("2026-01-01T00:00:00Z"));
        let state = AppState::new(Box::new(store), single_project("p1", bundle), None);
        state.set_snapshot(pinned_model).unwrap();

        let result = assemble_rooms(&state, Some("p1"), None, Some("Design Freeze")).unwrap().expect("store has data");
        assert_eq!(result.rooms.len(), 1, "the room is still returned (fallback, not dropped)");
        assert_eq!(
            result.rooms[0].drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"current-value".to_string()),
            "falls back to the current dRofus"
        );

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A milestone with model pins but no `drofus_snapshot` joins the current
    /// dRofus — guards the default (pre-pinning) path.
    #[test]
    fn test_assemble_rooms_milestone_without_drofus_pin_uses_current() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-drofus-none-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let model_ts = "2026-06-01T00:00:00Z";
        let mut pinned_model = make_payload("p1", "m1", vec![], vec![make_room("r1", "Room", &[("Number", "1")])]);
        pinned_model.snapshot.taken_at = model_ts.to_string();

        let bundle = bundle_for_drofus_pin("current-value", model_ts, None);
        let state = AppState::new(Box::new(store), single_project("p1", bundle), None);
        state.set_snapshot(pinned_model).unwrap();

        let result = assemble_rooms(&state, Some("p1"), None, Some("Design Freeze")).unwrap().expect("store has data");
        assert_eq!(
            result.rooms[0].drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"current-value".to_string())
        );

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Multi-project isolation: in an unscoped `?milestone=` merge, project A's
    /// pinned dRofus must not leak onto project B's rooms — B keeps its own
    /// current dRofus.
    #[test]
    fn test_assemble_rooms_milestone_drofus_pin_does_not_cross_projects() {
        let dir = std::env::temp_dir().join(format!("roommate-ms-drofus-iso-{}", std::process::id()));
        let store = crate::storage::FsStore::new(dir.clone()).unwrap();

        let model_ts = "2026-06-01T00:00:00Z";
        let a_drofus_ts = "2026-06-01T09:00:00Z";

        let mut a = make_payload("pA", "m1", vec![], vec![make_room("rA", "Room A", &[("Number", "1")])]);
        a.snapshot.taken_at = model_ts.to_string();
        let mut b = make_payload("pB", "m1", vec![], vec![make_room("rB", "Room B", &[("Number", "1")])]);
        b.snapshot.taken_at = model_ts.to_string();

        // A pins a dRofus snapshot; B has no pin, so its current dRofus stands.
        let registry = std::collections::HashMap::from([
            ("pA".to_string(), bundle_for_drofus_pin("A-current", model_ts, Some(a_drofus_ts))),
            ("pB".to_string(), bundle_for_drofus_pin("B-current", model_ts, None)),
        ]);
        let state = AppState::new(Box::new(store), registry, None);
        state.set_snapshot(a).unwrap();
        state.set_snapshot(b).unwrap();
        state.put_drofus("pA", a_drofus_ts, &drofus_csv("A-pinned")).unwrap();

        let result = assemble_rooms(&state, None, None, Some("Design Freeze")).unwrap().expect("store has data");
        let room_a = result.rooms.iter().find(|r| r.room.id == "rA").expect("A present");
        let room_b = result.rooms.iter().find(|r| r.room.id == "rB").expect("B present");
        assert_eq!(
            room_a.drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"A-pinned".to_string()),
            "A joins its own pinned dRofus"
        );
        assert_eq!(
            room_b.drofus.as_ref().unwrap().fields.get("NetArea"),
            Some(&"B-current".to_string()),
            "B keeps its current dRofus — A's pin did not leak across"
        );

        std::fs::remove_dir_all(&dir).ok();
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
        let result = assemble_rooms(&state, Some("p2"), Some(&key), None)
            .unwrap()
            .expect("store is not empty, so this is Some with empty vecs");

        assert!(result.rooms.is_empty(), "a filter the project can't answer matches nothing");
        assert!(result.levels.is_empty());
    }
}
