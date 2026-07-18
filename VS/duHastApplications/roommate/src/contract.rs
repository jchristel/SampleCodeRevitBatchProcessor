//! The JSON contract shared with the Revit extractor, plus the one lookup that
//! reads across its two property tiers.
//!
//! This module is the *shape of the data* and nothing else — no I/O, no state,
//! no handlers. It's the load-bearing type layer both `drofus` and `classify`
//! depend on, which is why `lookup_property` lives here rather than in either
//! consumer: it inspects `Room`'s property tiers, so it belongs next to them,
//! and keeping it here means the two consumers depend on the contract, not on
//! each other.
//!
//! Every type here must match the Revit extractor's serializer. Ids and
//! `ElementId` values ride as strings on the wire (width-safe across the
//! IronPython/CLR seam); numeric `ElementId`s are parsed to `i64` only here,
//! server-side, where the width is safe. See STRATEGY.md "Expand the room
//! properties contract".

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use crate::settings::BuiltinPropertyDef;

/// A 2D point in Revit model space. Units are decimal feet, Y points UP.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Point2D {
    pub x: f64,
    pub y: f64,
}

/// A single closed loop of points. A room has one outer loop and zero or more
/// inner loops (holes, e.g. a column or shaft punched through the room).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Loop {
    pub points: Vec<Point2D>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Level {
    pub id: String,
    pub name: String,
    pub elevation: f64,
}

/// One custom property: the raw string value plus an optional storage-type
/// hint from Revit. Paired in one struct (not two parallel maps) so value and
/// type can't drift and an absent type degrades to "treat as string".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomValue {
    /// Raw value, always a string. Revit hands most params back as strings;
    /// any typing is deferred and done server-side, lazily.
    pub value: String,

    /// Revit's declared StorageType, forwarded as guidance only:
    /// "String" | "Integer" | "Double" | "ElementId". Optional — absent means
    /// "treat as string". This is a HINT: declared type and parseable content
    /// can disagree (a String param holding "12.5", an empty Double), so any
    /// coercion keyed off it must fall back to `value` on failure.
    ///
    /// Set by the Python extractor's DataProperty.storage_type field
    /// (str(p.StorageType) on the Revit parameter).
    #[serde(default)]
    pub storage_type: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Room {
    pub id: String,
    pub name: String,
    pub level_id: String,
    pub loops: Vec<Loop>,

    /// Raw properties as extracted, keyed by the *source's own* property name
    /// (e.g. Revit's `p.Definition.Name`). No builtin/custom split at the wire
    /// or storage level — that split isn't a type distinction anymore, it's a
    /// settings-driven, per-source *lookup* concern (see `lookup_property`),
    /// because no single fixed schema is guaranteed once a second source (e.g.
    /// IFC) can produce rooms alongside Revit. `#[serde(default)]` so a room
    /// with no properties still deserializes rather than failing.
    #[serde(default)]
    pub properties: BTreeMap<String, CustomValue>,
}

/// The human-meaningful container a model belongs to ("the hospital job").
/// Identity (`id`) is separated from display metadata (`name`) so a rename in
/// Revit never forks the stored record — storage keys on `id`, never `name`.
/// See STRATEGY.md "Identity".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    /// Stable, globally-unique key. Addressable/comparable across projects
    /// without collision — a GUID-like value, NOT "project 1".
    pub id: String,
    /// Mutable display label. Never used as a storage key.
    pub name: String,
}

/// A single Revit file. One project routinely has several (architectural,
/// structural, linked consultant models), each POSTing independently — so
/// `model` is the level that stops those overwriting each other.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Model {
    /// The Revit model GUID: stable across renames, unique per file. Preferred
    /// over file name (which would fork the record on rename). This is the key
    /// the in-memory store buckets snapshots under.
    pub id: String,
    /// Mutable display label. Never used as a storage key.
    pub name: String,
    /// Which producer created this data ("revit" today). Selects which
    /// `BuiltinPropertyDef.by_source` entry resolves a canonical property name
    /// to *this* model's raw property name — the disambiguator a second source
    /// (e.g. IFC) would need, since the same canonical concept can live under a
    /// different raw name per source. A plain string, not a closed enum: adding
    /// a source is a settings-file change, not a Rust code change.
    pub source: String,
}

/// One timestamped push of one model. Its own contract level so "this floor as
/// it was last Tuesday" / "what changed since last push" become possible later
/// without restructuring — even though we only keep the latest for now.
///
/// Together with `schema_version` / `project` / `model` this forms the shared
/// **upload envelope**: the identity every upload type carries, rooms being
/// the first. Any future upload (FFE, etc.) associates back to room data by
/// exactly two keys — this snapshot id and the room id — so it must ride the
/// same envelope, resolved through the same `ensure_taken_at` /
/// `validate_snapshot_id` pair below rather than reimplementing either.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Snapshot {
    /// The snapshot id: an RFC3339 date-time expressed in UTC. When the model
    /// was *read* (sourced from the export's own timestamp), not when the
    /// server received it — except when a producer leaves it blank/omitted, in
    /// which case the server mints one at ingest (`ensure_taken_at`) and
    /// returns it in the ingest response. Blank never survives past the ingest
    /// trust boundary; storage and read code always see a concrete id.
    #[serde(default)]
    pub taken_at: String,
}

/// Resolve a possibly-blank snapshot id at the ingest trust boundary: a
/// blank/whitespace `taken_at` (or one from an omitted `snapshot` object,
/// which defaults to empty) is replaced with "now" in UTC, at the same
/// microsecond precision the Revit producer stamps. Returns whether an id was
/// generated so the ingest response can say so. Every upload type resolves
/// its snapshot id through this one function.
pub fn ensure_taken_at(snapshot: &mut Snapshot) -> bool {
    if snapshot.taken_at.trim().is_empty() {
        snapshot.taken_at = chrono::Utc::now()
            .format("%Y-%m-%dT%H:%M:%S%.6fZ")
            .to_string();
        return true;
    }
    false
}

/// Whether a (non-blank) snapshot id is acceptable: it must parse as RFC3339
/// AND be expressed in UTC (`Z` or `+00:00`). One rule covers everything the
/// id must guarantee: it's a real date-time (the contract's definition of a
/// snapshot id), it keeps the store's lexical-max-is-newest ordering sound (a
/// non-UTC offset would sort wrongly against UTC neighbours), and it can't
/// smuggle a path escape (no RFC3339 string contains `/`, `\`, or `..`) —
/// which is why ingest needs no separate filename-safety check for it.
pub fn validate_snapshot_id(taken_at: &str) -> Result<(), String> {
    let parsed = chrono::DateTime::parse_from_rfc3339(taken_at)
        .map_err(|e| format!("snapshot taken_at {taken_at:?} is not an RFC3339 date-time: {e}"))?;
    if parsed.offset().local_minus_utc() != 0 {
        return Err(format!(
            "snapshot taken_at {taken_at:?} must be expressed in UTC (\"Z\" or \"+00:00\"), not a local offset"
        ));
    }
    Ok(())
}

/// The affine transform mapping a model's room points from Revit model space
/// into the project's SHARED coordinate system. One per model, not per room:
/// it's a model-level `ProjectLocation` fact (the *same* relationship on every
/// room), so it rides the envelope rather than each polygon — see
/// HANDOVER-georeferencing.md "Fact 1".
///
/// It exists for two independent reasons: (a) it puts every room in a model into
/// one common frame, which cross-model comparison needs regardless of any map
/// (STRATEGY-SERVER "common coordinate frame"); (b) when the project is
/// survey-registered, shared space IS grid space in the declared CRS, which is
/// what later makes a map underlay placeable. It carries NO unit conversion —
/// this is a rigid-body placement (rotation + translation), not a scale, so
/// `|det|` of its linear part is ≈ 1 (a useful ingest sanity check).
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ModelToShared {
    /// 2D affine as `[a, b, c, d, e, f]`: `shared_x = a*x + c*y + e`,
    /// `shared_y = b*x + d*y + f`. The linear part `[[a, c], [b, d]]` is a pure
    /// rotation from Revit's shared-coordinate `ProjectLocation` (no scale or
    /// shear), so `|det| = |a*d - c*b| ≈ 1`.
    pub matrix: [f64; 6],
}

impl ModelToShared {
    /// Determinant of the linear part `[[a, c], [b, d]]` = `a*d - c*b`. A pure
    /// rotation gives `|det| ≈ 1`; a value that has drifted means a scaled or
    /// sheared matrix that would silently distort placement.
    pub fn determinant(&self) -> f64 {
        let [a, b, c, d, _e, _f] = self.matrix;
        a * d - c * b
    }

    /// Whether the transform is a rigid-body placement (pure rotation), i.e.
    /// `|det| ≈ 1` within `tol`. Used at ingest to *warn* (not reject) — a
    /// non-rigid transform is advisory-suspect, not a broken contract.
    pub fn is_rigid(&self, tol: f64) -> bool {
        (self.determinant().abs() - 1.0).abs() <= tol
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomPayload {
    pub schema_version: u32,

    /// v4 identity envelope. Tells the server *which* thing this snapshot is a
    /// version of, so two models POSTed to the same server no longer overwrite
    /// each other. The `(project, model)` pair locates the storage slot; the
    /// snapshot times it. `snapshot` is `#[serde(default)]`: omitting it (or
    /// its `taken_at`) asks the server to mint the id — see `ensure_taken_at`.
    pub project: Project,
    pub model: Model,
    #[serde(default)]
    pub snapshot: Snapshot,

    /// Optional model→shared placement transform for this model (see
    /// `ModelToShared`). Absent on an un-placed model, which still renders fine
    /// via auto-fit exactly as before — `#[serde(default)]` keeps every
    /// pre-georeference payload valid and unchanged in meaning (no schema bump).
    #[serde(default)]
    pub model_to_shared: Option<ModelToShared>,

    pub levels: Vec<Level>,
    pub rooms: Vec<Room>,
}

/// The first NDJSON line of a streamed push (`POST /rooms/stream`): everything
/// in `RoomPayload` EXCEPT `rooms`, which arrive as subsequent lines, one room
/// per line. Kept as its own type (rather than making `rooms` optional on
/// `RoomPayload`) so the envelope deserializes on its own with no rooms
/// present, and so `RoomPayload` itself keeps `rooms` guaranteed for every
/// other consumer. See HANDOVER-streaming.md.
#[derive(Debug, Clone, Deserialize)]
pub struct StreamEnvelope {
    pub schema_version: u32,
    pub project: Project,
    pub model: Model,
    #[serde(default)]
    pub snapshot: Snapshot,
    /// Model→shared placement transform, in lockstep with `RoomPayload` (a
    /// streamed push carries identical envelope metadata; only `rooms` differ).
    #[serde(default)]
    pub model_to_shared: Option<ModelToShared>,
    pub levels: Vec<Level>,
}

/// Schema version this server accepts. Now v5: the fixed, typed `builtin`
/// struct is gone — `Room.properties` is one flat, source-native map, and
/// "which properties are builtin" moved from a Rust type to a settings-driven,
/// per-source name mapping (see `BuiltinPropertyDef` / `lookup_property`).
/// A v4 producer (split builtin/custom) 422s loud rather than silently
/// misparsing. No transition window — update the extractor and the server
/// together.
///
/// Still 5 after `snapshot.taken_at` became omittable: that change is a pure
/// relaxation — every payload that was valid v5 before is still valid and
/// means the same thing — and bumps are reserved for changes that would make
/// an existing producer's payload misparse or change meaning.
///
/// Still 5 after the optional `model_to_shared` envelope field was added
/// (HANDOVER-georeferencing.md Phase 1): same reasoning — it defaults to
/// `None`, so a pre-georeference payload stays valid and means exactly what it
/// did (an un-placed model, rendered via auto-fit).
pub const SUPPORTED_SCHEMA: u32 = 5;

/// Resolve a *canonical* property name (e.g. "Area") to the source-specific
/// raw property name a room's `properties` map actually keys on, via
/// `builtin_defs`. Shared by `lookup_property` and `property_presence` so the
/// two can never disagree on what a canonical name resolves to.
///
/// When no `BuiltinPropertyDef` names `canonical_name`, or none of its
/// `by_source` entries match `source`, `canonical_name` is used verbatim as
/// the raw property name — this is what makes project/shared params (which
/// were never in the builtin set to begin with) work unchanged, and what lets
/// hierarchy/dRofus configs reference a raw name directly when no canonical
/// mapping is configured.
fn resolve_raw_name<'a>(
    canonical_name: &'a str,
    source: &str,
    builtin_defs: &'a [BuiltinPropertyDef],
) -> &'a str {
    builtin_defs
        .iter()
        .find(|d| d.canonical == canonical_name)
        .and_then(|d| d.by_source.get(source))
        .map(String::as_str)
        .unwrap_or(canonical_name)
}

/// The three states a room property can be in — distinguished because they
/// mean different things for data-quality reporting: `Absent` means the
/// property was never extracted from Revit for this room at all (a mapping
/// typo or a parameter the extractor never wired up — a setup problem worth
/// flagging loudly), while `Empty` means the property exists but nobody has
/// filled in a value yet (an ordinary per-room gap).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PropertyPresence {
    /// No property of the resolved raw name exists on this room at all.
    Absent,
    /// The property exists but its value is an empty string.
    Empty,
    /// The property exists with a non-empty value.
    Present(String),
}

/// Look up a room property by its *canonical* name, resolving it to the
/// source-specific raw property name first (see `resolve_raw_name`), then
/// reporting which of the three `PropertyPresence` states it's in. Used where
/// the absent/empty distinction matters (data-quality reporting); most
/// callers just want `lookup_property`'s collapsed `Option<String>`.
pub fn property_presence(
    room: &Room,
    canonical_name: &str,
    source: &str,
    builtin_defs: &[BuiltinPropertyDef],
) -> PropertyPresence {
    let raw_name = resolve_raw_name(canonical_name, source, builtin_defs);
    match room.properties.get(raw_name) {
        None => PropertyPresence::Absent,
        Some(v) if v.value.is_empty() => PropertyPresence::Empty,
        Some(v) => PropertyPresence::Present(v.value.clone()),
    }
}

/// Look up a room property by its *canonical* name (e.g. "Area"), resolving it
/// to the source-specific raw property name via `builtin_defs` before reading
/// the room's flat property map. Used by both the dRofus join and the
/// classifier so the lookup strategy is consistent and lives in one place.
///
/// Returns `None` when the resolved property is absent or holds an empty
/// value — i.e. collapses `PropertyPresence::Absent`/`Empty` together. A thin
/// wrapper over `property_presence` so the two can never drift apart.
pub fn lookup_property(
    room: &Room,
    canonical_name: &str,
    source: &str,
    builtin_defs: &[BuiltinPropertyDef],
) -> Option<String> {
    match property_presence(room, canonical_name, source, builtin_defs) {
        PropertyPresence::Present(v) => Some(v),
        PropertyPresence::Absent | PropertyPresence::Empty => None,
    }
}

/// IEEE 754 zero has two bit patterns (`0.0` and `-0.0`) that compare equal
/// numerically but format differently (`"-0"` vs `"0"`) -- collapse to the
/// positive form before formatting so a genuine zero never spuriously
/// mismatches itself.
fn normalize_zero(v: f64) -> f64 {
    if v == 0.0 {
        0.0
    } else {
        v
    }
}

/// Count the digits after the decimal point in a raw numeric string -- the
/// "stated precision" of a value as authored. This has to run on the string,
/// not the parsed `f64`: reformatting a parsed float loses (`"1.50"` ->
/// `1.5`) or fabricates (binary rounding noise) digits that were never part
/// of what was actually written.
fn decimal_places(s: &str) -> usize {
    s.trim().split_once('.').map_or(0, |(_, frac)| frac.len())
}

/// Compare two raw numeric strings tolerant of float-precision drift: round
/// both to the *lesser* of their two stated decimal precisions, rather than
/// to a fixed epsilon. This is what lets dRofus's `"1.5"` agree with Revit's
/// `"1.49999935417"` (a unit-conversion rounding artifact) -- dRofus only
/// stated 1 decimal digit of precision, so disagreement past that digit
/// isn't a real mismatch, whereas two values that both state 6 digits of
/// precision and differ in the 6th are a genuine disagreement.
///
/// Returns `None` when either side doesn't parse as a number at all; callers
/// should fall back to exact string comparison in that case.
pub fn numeric_match(a: &str, b: &str) -> Option<bool> {
    let x: f64 = a.trim().parse().ok()?;
    let y: f64 = b.trim().parse().ok()?;
    let n = decimal_places(a).min(decimal_places(b));
    let x = normalize_zero(x);
    let y = normalize_zero(y);
    Some(format!("{:.*}", n, x) == format!("{:.*}", n, y))
}

/// Same rounding discipline as `numeric_match`, for a value that was never a
/// string to begin with (`Level.elevation` arrives as a parsed JSON number,
/// so any "stated precision" it once had is already gone by the time Rust
/// sees it). Approximated instead: format to a generous fixed precision, then
/// trim trailing zeros, so a value authored as a clean `0.0` collapses to 0
/// decimals while one carrying real float noise from a unit conversion keeps
/// a long non-zero tail. Falls back to exact equality on the vanishingly
/// unlikely chance both trimmed strings fail to parse.
pub fn elevation_match(a: f64, b: f64) -> bool {
    const PRECISION: usize = 9;
    let sa = format!("{:.*}", PRECISION, normalize_zero(a));
    let sb = format!("{:.*}", PRECISION, normalize_zero(b));
    numeric_match(sa.trim_end_matches('0'), sb.trim_end_matches('0')).unwrap_or(a == b)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    /// A v5 payload (identity envelope incl. `model.source`, plus a flat,
    /// source-native room properties map) survives a serde round-trip intact.
    #[test]
    fn test_v5_room_properties_round_trip() {
        let json = serde_json::json!({
            "schema_version": 5,
            "project":  { "id": "p1", "name": "Hospital Job" },
            "model":    { "id": "m-guid", "name": "ARCH", "source": "revit" },
            "snapshot": { "taken_at": "2026-05-09T11:13:34Z" },
            "levels": [{ "id": "lvl1", "name": "Level 1", "elevation": 0.0 }],
            "rooms": [{
                "id": "r1",
                "name": "Office",
                "level_id": "lvl1",
                "loops": [],
                "properties": {
                    "Number": { "value": "101", "storage_type": "String" },
                    "Area": { "value": "25.5", "storage_type": "Double" },
                    "Dept": { "value": "Finance", "storage_type": "String" }
                }
            }]
        });

        let payload: RoomPayload = serde_json::from_value(json).unwrap();
        let room = &payload.rooms[0];

        assert_eq!(payload.model.source, "revit");
        assert_eq!(room.properties["Number"].value, "101");
        assert_eq!(room.properties["Area"].value, "25.5");
        assert_eq!(
            room.properties["Dept"].storage_type,
            Some("String".to_string())
        );

        // Confirm round-trip: serialise and re-parse.
        let serialised = serde_json::to_string(&payload).unwrap();
        let reparsed: RoomPayload = serde_json::from_str(&serialised).unwrap();
        assert_eq!(reparsed.rooms[0].properties["Number"].value, "101");
    }

    /// A room JSON with no "properties" key deserialises to an empty map —
    /// proves the `#[serde(default)]` wiring is correct.
    #[test]
    fn test_room_deserialises_to_empty_properties() {
        let json = serde_json::json!({
            "id": "r1",
            "name": "Office",
            "level_id": "lvl1",
            "loops": []
            // no "properties" key
        });

        let room: Room = serde_json::from_value(json).unwrap();
        assert!(room.properties.is_empty());
    }

    /// `model_to_shared` round-trips on `RoomPayload`: present it deserializes
    /// into the affine and survives re-serialization; absent it defaults to
    /// `None` (the pre-georeference payload, unchanged in meaning).
    #[test]
    fn test_model_to_shared_round_trips_and_defaults_to_none() {
        let base = serde_json::json!({
            "schema_version": 5,
            "project":  { "id": "p1", "name": "Hospital Job" },
            "model":    { "id": "m-guid", "name": "ARCH", "source": "revit" },
            "snapshot": { "taken_at": "2026-05-09T11:13:34Z" },
            "levels": [],
            "rooms": []
        });

        // Absent → None.
        let without: RoomPayload = serde_json::from_value(base.clone()).unwrap();
        assert!(without.model_to_shared.is_none());

        // Present → the affine, and it round-trips.
        let mut with = base;
        with["model_to_shared"] = serde_json::json!({
            "matrix": [0.9704980833640151, -0.2411088347339701, 0.2411088347339701, 0.9704980833640151, 945737.6456106724, 20545096.538269494]
        });
        let payload: RoomPayload = serde_json::from_value(with).unwrap();
        let mts = payload.model_to_shared.expect("present");
        assert!((mts.matrix[4] - 945737.6456106724).abs() < 1e-6);

        // Survives a serialize→parse cycle (compared with tolerance: a JSON f64
        // round-trip can differ by an ULP between the `from_value` and
        // `from_str` paths, which is not what this test is about).
        let reparsed: RoomPayload =
            serde_json::from_str(&serde_json::to_string(&payload).unwrap()).unwrap();
        let back = reparsed.model_to_shared.expect("present after round-trip");
        for (a, b) in back.matrix.iter().zip(mts.matrix.iter()) {
            // Absolute 1e-6 (sub-micron in feet) absorbs the ULP-scale drift a
            // ~1e7 grid coordinate picks up crossing the JSON f64 boundary.
            assert!((a - b).abs() < 1e-6, "round-trip drifted: {a} vs {b}");
        }
    }

    /// `is_rigid` accepts the real geo_data.json rotation (a pure ~13.95° spin,
    /// |det| ≈ 1) and rejects a scaled matrix that would distort placement.
    #[test]
    fn test_model_to_shared_determinant_flags_non_rigid() {
        let rigid = ModelToShared {
            matrix: [0.9704980833640151, -0.2411088347339701, 0.2411088347339701, 0.9704980833640151, 945737.6, 20545096.5],
        };
        assert!((rigid.determinant() - 1.0).abs() < 1e-9);
        assert!(rigid.is_rigid(1e-6));

        // Identity is trivially rigid.
        assert!(ModelToShared { matrix: [1.0, 0.0, 0.0, 1.0, 0.0, 0.0] }.is_rigid(1e-6));

        // A 2× scale on both axes: det = 4, not rigid.
        let scaled = ModelToShared { matrix: [2.0, 0.0, 0.0, 2.0, 0.0, 0.0] };
        assert!(!scaled.is_rigid(1e-6));
    }

    /// A `StreamEnvelope` (line 1 of a `/rooms/stream` push) deserializes with
    /// no `rooms` key present -- proves it doesn't accidentally require one.
    #[test]
    fn test_stream_envelope_deserializes_without_rooms() {
        let json = serde_json::json!({
            "schema_version": 5,
            "project":  { "id": "p1", "name": "Hospital Job" },
            "model":    { "id": "m-guid", "name": "ARCH", "source": "revit" },
            "snapshot": { "taken_at": "2026-05-09T11:13:34Z" },
            "levels": [{ "id": "lvl1", "name": "Level 1", "elevation": 0.0 }]
        });

        let envelope: StreamEnvelope = serde_json::from_value(json).unwrap();
        assert_eq!(envelope.schema_version, 5);
        assert_eq!(envelope.project.id, "p1");
        assert_eq!(envelope.model.source, "revit");
        assert_eq!(envelope.levels.len(), 1);
        // No `model_to_shared` key present → defaults to None (in lockstep with
        // RoomPayload), so an un-placed streamed push stays valid.
        assert!(envelope.model_to_shared.is_none());
    }

    /// A payload with no "snapshot" key at all still deserializes (the
    /// server-generates case) — `taken_at` arrives empty for `ensure_taken_at`
    /// to resolve.
    #[test]
    fn test_payload_deserializes_without_snapshot() {
        let json = serde_json::json!({
            "schema_version": 5,
            "project":  { "id": "p1", "name": "Hospital Job" },
            "model":    { "id": "m-guid", "name": "ARCH", "source": "revit" },
            "levels": [],
            "rooms": []
        });

        let payload: RoomPayload = serde_json::from_value(json.clone()).unwrap();
        assert_eq!(payload.snapshot.taken_at, "");

        let envelope: StreamEnvelope = serde_json::from_value(json).unwrap();
        assert_eq!(envelope.snapshot.taken_at, "");
    }

    /// A blank/omitted taken_at is replaced with a generated UTC id that
    /// passes the contract's own validation; a supplied one is left alone.
    #[test]
    fn test_ensure_taken_at_generates_only_when_blank() {
        let mut blank = Snapshot { taken_at: "  ".to_string() };
        assert!(ensure_taken_at(&mut blank));
        assert!(validate_snapshot_id(&blank.taken_at).is_ok(), "generated id must be valid: {}", blank.taken_at);

        let mut supplied = Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() };
        assert!(!ensure_taken_at(&mut supplied));
        assert_eq!(supplied.taken_at, "2026-01-01T00:00:00Z");
    }

    /// The snapshot id rule: RFC3339, expressed in UTC. Non-dates (including
    /// anything path-shaped) and non-UTC offsets are rejected; "Z" and
    /// "+00:00" both count as UTC.
    #[test]
    fn test_validate_snapshot_id() {
        assert!(validate_snapshot_id("2026-01-01T00:00:00Z").is_ok());
        assert!(validate_snapshot_id("2026-01-01T00:00:00.123456Z").is_ok());
        assert!(validate_snapshot_id("2026-01-01T00:00:00+00:00").is_ok());

        assert!(validate_snapshot_id("2026-01-01T00:00:00+10:00").is_err());
        assert!(validate_snapshot_id("not-a-date").is_err());
        assert!(validate_snapshot_id("2026/01/01").is_err());
        assert!(validate_snapshot_id("..\\..\\evil").is_err());
        assert!(validate_snapshot_id("").is_err());
    }

    /// lookup_property resolves a canonical name to a source-specific raw
    /// property name before reading the room's map.
    #[test]
    fn test_lookup_property_resolves_via_source_mapping() {
        let mut properties = BTreeMap::new();
        properties.insert(
            "Fläche".to_string(),
            CustomValue { value: "25.5".to_string(), storage_type: Some("Double".to_string()) },
        );
        let room = Room {
            id: "r1".into(),
            name: "Office".into(),
            level_id: "lvl1".into(),
            loops: vec![],
            properties,
        };

        let defs = vec![BuiltinPropertyDef {
            canonical: "Area".to_string(),
            by_source: HashMap::from([("revit_de".to_string(), "Fläche".to_string())]),
        }];

        assert_eq!(
            lookup_property(&room, "Area", "revit_de", &defs),
            Some("25.5".to_string())
        );
        // A source with no configured mapping falls back to matching the
        // canonical name verbatim — and finds nothing here, correctly.
        assert_eq!(lookup_property(&room, "Area", "revit", &defs), None);
    }

    /// With no builtin_defs at all, lookup_property matches the raw property
    /// map directly by name — the same behaviour project/shared params always
    /// had, and what tests elsewhere (classify.rs) rely on.
    #[test]
    fn test_lookup_property_falls_through_with_no_defs() {
        let mut properties = BTreeMap::new();
        properties.insert(
            "Dept".to_string(),
            CustomValue { value: "Finance".to_string(), storage_type: None },
        );
        let room = Room {
            id: "r1".into(),
            name: "Office".into(),
            level_id: "lvl1".into(),
            loops: vec![],
            properties,
        };

        assert_eq!(
            lookup_property(&room, "Dept", "revit", &[]),
            Some("Finance".to_string())
        );
    }

    /// The reported bug: dRofus's `"1.5"` (1 stated decimal) agrees with
    /// Revit's `"1.49999935417"` (a unit-conversion rounding artifact) once
    /// both are rounded to the lesser of the two stated precisions.
    #[test]
    fn test_numeric_match_adaptive_precision() {
        assert_eq!(numeric_match("1.5", "1.49999935417"), Some(true));
    }

    /// Two values that both state 6 digits of precision and genuinely differ
    /// at that precision are a real mismatch, not noise to round away.
    #[test]
    fn test_numeric_match_genuine_disagreement_at_stated_precision() {
        assert_eq!(numeric_match("1.500001", "1.499999"), Some(false));
    }

    /// A value with no decimal point at all (0 stated decimals) forces
    /// whole-number comparison.
    #[test]
    fn test_numeric_match_integer_side_forces_whole_number_compare() {
        assert_eq!(numeric_match("150", "150.0000001"), Some(true));
        assert_eq!(numeric_match("150", "150.6"), Some(false));
    }

    /// Either side failing to parse as a number falls back to `None` so the
    /// caller knows to use exact string comparison instead.
    #[test]
    fn test_numeric_match_non_numeric_returns_none() {
        assert_eq!(numeric_match("Cardiology", "25.5"), None);
        assert_eq!(numeric_match("25.5", "Cardiology"), None);
    }

    /// `elevation_match` approximates stated precision from a bare `f64` by
    /// trimming trailing zeros off a fixed-precision format, rather than
    /// requiring a raw string.
    #[test]
    fn test_elevation_match_trims_float_noise() {
        // A "clean" 0.0 vs a value carrying float noise many decimals out.
        assert!(elevation_match(0.0, 0.000000000_1));
        assert!(elevation_match(12.0, 12.000000001));
        // 12.6, not 12.5 -- avoids depending on round-half-to-even tie-breaking.
        assert!(!elevation_match(12.0, 12.6));
    }

    /// Negative zero and positive zero must compare equal, not mismatch on
    /// their differing sign when formatted.
    #[test]
    fn test_elevation_match_negative_zero() {
        assert!(elevation_match(-0.0, 0.0));
    }

    /// `property_presence` distinguishes a property that was never extracted
    /// at all (`Absent` -- a mapping/setup problem) from one that exists but
    /// is blank (`Empty` -- an ordinary per-room gap), and reports a real
    /// value as `Present`.
    #[test]
    fn test_property_presence_distinguishes_absent_empty_present() {
        let mut properties = BTreeMap::new();
        properties.insert(
            "Blank".to_string(),
            CustomValue { value: "".to_string(), storage_type: None },
        );
        properties.insert(
            "Filled".to_string(),
            CustomValue { value: "25.5".to_string(), storage_type: None },
        );
        let room = Room { id: "r1".into(), name: "Office".into(), level_id: "lvl1".into(), loops: vec![], properties };

        assert_eq!(property_presence(&room, "Missing", "revit", &[]), PropertyPresence::Absent);
        assert_eq!(property_presence(&room, "Blank", "revit", &[]), PropertyPresence::Empty);
        assert_eq!(
            property_presence(&room, "Filled", "revit", &[]),
            PropertyPresence::Present("25.5".to_string())
        );
    }

    /// `lookup_property`'s existing collapsed behavior must survive the
    /// refactor onto `property_presence` unchanged: both `Absent` and `Empty`
    /// read as `None`.
    #[test]
    fn test_lookup_property_still_collapses_absent_and_empty_to_none() {
        let mut properties = BTreeMap::new();
        properties.insert(
            "Blank".to_string(),
            CustomValue { value: "".to_string(), storage_type: None },
        );
        let room = Room { id: "r1".into(), name: "Office".into(), level_id: "lvl1".into(), loops: vec![], properties };

        assert_eq!(lookup_property(&room, "Missing", "revit", &[]), None);
        assert_eq!(lookup_property(&room, "Blank", "revit", &[]), None);
    }
}
