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

impl CustomValue {
    /// Best-effort typed read guided by the storage-type hint, falling back to
    /// the raw string's natural parse, and never panicking. Returns None only
    /// when nothing sensible can be produced. Callers that just want the string
    /// read `.value` directly and ignore this.
    pub fn as_f64(&self) -> Option<f64> {
        // Hint steers intent, but content wins: try to parse regardless, since
        // the declared type can lie (e.g. a String param holding "12.5").
        self.value.trim().parse::<f64>().ok()
    }
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
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Snapshot {
    /// When the model was *read* (sourced from the export's own timestamp), not
    /// when the server received it. The natural key for snapshot identity.
    pub taken_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoomPayload {
    pub schema_version: u32,

    /// v4 identity envelope. Tells the server *which* thing this snapshot is a
    /// version of, so two models POSTed to the same server no longer overwrite
    /// each other. The `(project, model)` pair locates the storage slot; the
    /// snapshot times it.
    pub project: Project,
    pub model: Model,
    pub snapshot: Snapshot,

    pub levels: Vec<Level>,
    pub rooms: Vec<Room>,
}

/// Schema version this server accepts. Now v5: the fixed, typed `builtin`
/// struct is gone — `Room.properties` is one flat, source-native map, and
/// "which properties are builtin" moved from a Rust type to a settings-driven,
/// per-source name mapping (see `BuiltinPropertyDef` / `lookup_property`).
/// A v4 producer (split builtin/custom) 422s loud rather than silently
/// misparsing. No transition window — update the extractor and the server
/// together.
pub const SUPPORTED_SCHEMA: u32 = 5;

/// Look up a room property by its *canonical* name (e.g. "Area"), resolving it
/// to the source-specific raw property name via `builtin_defs` before reading
/// the room's flat property map. Used by both the dRofus join and the
/// classifier so the lookup strategy is consistent and lives in one place.
///
/// When no `BuiltinPropertyDef` names `canonical_name`, or none of its
/// `by_source` entries match `source`, `canonical_name` is used verbatim as
/// the raw property name — this is what makes project/shared params (which
/// were never in the builtin set to begin with) work unchanged, and what lets
/// hierarchy/dRofus configs reference a raw name directly when no canonical
/// mapping is configured.
///
/// Returns `None` when the resolved property is absent or holds an empty
/// value.
pub fn lookup_property(
    room: &Room,
    canonical_name: &str,
    source: &str,
    builtin_defs: &[BuiltinPropertyDef],
) -> Option<String> {
    let raw_name = builtin_defs
        .iter()
        .find(|d| d.canonical == canonical_name)
        .and_then(|d| d.by_source.get(source))
        .map(String::as_str)
        .unwrap_or(canonical_name);

    room.properties
        .get(raw_name)
        .map(|v| v.value.clone())
        .filter(|s| !s.is_empty())
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

    /// CustomValue::as_f64 parses a numeric string regardless of storage_type.
    #[test]
    fn test_custom_value_as_f64() {
        let cv = |val: &str, st: Option<&str>| CustomValue {
            value: val.to_string(),
            storage_type: st.map(|s| s.to_string()),
        };

        assert_eq!(cv("3.14", Some("Double")).as_f64(), Some(3.14));
        assert_eq!(cv("42", Some("Integer")).as_f64(), Some(42.0));
        // Content wins over hint: a String param holding a number still parses.
        assert_eq!(cv("7.5", Some("String")).as_f64(), Some(7.5));
        // Truly non-numeric returns None.
        assert_eq!(cv("Finance", Some("String")).as_f64(), None);
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
}
