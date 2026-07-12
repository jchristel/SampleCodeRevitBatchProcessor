//! Room classification: resolve each room to a full-depth path through the
//! configured hierarchy tiers.
//!
//! The one rule that shapes everything here (STRATEGY.md "Establish a room
//! classification hierarchy"): missing tier data is a *represented* state, not
//! an error. Once a tier lacks data, it and every tier below become an explicit
//! `undefined` — never a truncated path, never a dropped room. That keeps the
//! grouping tree uniform-depth so a viewer can render "undefined Sub-department"
//! as its own visible group, and makes "which rooms aren't classified yet"
//! legible instead of a black hole.
//!
//! Resolved fresh per request, not cached — the result is a function of (static
//! hierarchy + current snapshot), so a cache would need invalidating on every
//! push or dRofus re-poll. Negligible cost at this scale; correctness over a
//! premature optimisation.

use serde::Serialize;

use crate::contract::{lookup_property, Room};
use crate::settings::{BuiltinPropertyDef, HierarchyTier};

/// One tier's resolved value for a room. `undefined` is a REPRESENTED value,
/// not an absence — every room gets one of these per tier, so the grouping tree
/// is uniform-depth and a viewer can render "undefined Sub-department" as its
/// own group rather than dropping the room.
#[derive(Debug, Clone, Serialize)]
pub struct TierValue {
    pub tier: String,
    /// None when this tier (or a tier above it) had no data — i.e. undefined.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    /// True once classification has fallen through to undefined at this tier.
    pub undefined: bool,
}

/// Resolve one room to a full-depth classification path.
///
/// RULE: once a tier has no data, that tier AND every tier below it are
/// `undefined`. A room missing tier 1 is undefined all the way down —
/// still visualizable as a distinct group.
///
/// NOTE: resolved fresh per `/rooms` request, not cached. The result is a
/// function of (static hierarchy + current snapshot); caching it would require
/// recomputation on every new snapshot push or dRofus re-poll. At this scale
/// the per-request cost is negligible — prefer correctness over a premature
/// optimisation.
pub fn classify_room(
    room: &Room,
    tiers: &[HierarchyTier],
    source: &str,
    builtin_defs: &[BuiltinPropertyDef],
) -> Vec<TierValue> {
    let mut path = Vec::with_capacity(tiers.len());
    let mut fell_through = false;

    for tier in tiers {
        // Resolve this tier's code/name from the room. `as_deref` turns the
        // Option<String> config field into Option<&str> for lookup; a tier may
        // define code, name, or both, so either lookup can be None.
        let code = tier
            .code_property
            .as_deref()
            .and_then(|p| lookup_property(room, p, source, builtin_defs));
        let name = tier
            .name_property
            .as_deref()
            .and_then(|p| lookup_property(room, p, source, builtin_defs));

        // A tier resolves if *either* of its referenced properties is present.
        let has_data = code.is_some() || name.is_some();

        // `fell_through` latches: once any tier is undefined, all below it are too
        // (a room can't be classified deeper than its first gap). So push
        // undefined if we've already fallen through OR this tier has no data.
        if fell_through || !has_data {
            fell_through = true;
            path.push(TierValue {
                tier: tier.name.clone(),
                code: None,
                name: None,
                undefined: true,
            });
        } else {
            path.push(TierValue {
                tier: tier.name.clone(),
                code,
                name,
                undefined: false,
            });
        }
    }
    path
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::CustomValue;
    use std::collections::BTreeMap;

    // Helpers ----------------------------------------------------------------

    fn make_room(id: &str, custom: BTreeMap<&str, (&str, Option<&str>)>) -> Room {
        Room {
            id: id.to_string(),
            name: "Test Room".to_string(),
            level_id: "1".to_string(),
            loops: vec![],
            properties: custom
                .into_iter()
                .map(|(k, (val, st))| {
                    (
                        k.to_string(),
                        CustomValue {
                            value: val.to_string(),
                            storage_type: st.map(|s| s.to_string()),
                        },
                    )
                })
                .collect(),
        }
    }

    fn make_tier(name: &str, code_prop: Option<&str>, name_prop: Option<&str>) -> HierarchyTier {
        HierarchyTier {
            name: name.to_string(),
            code_property: code_prop.map(|s| s.to_string()),
            name_property: name_prop.map(|s| s.to_string()),
        }
    }

    /// A fully-classified room produces a full path with no undefined tiers.
    #[test]
    fn test_classify_room_fully_classified() {
        let room = make_room(
            "r1",
            BTreeMap::from([
                ("bldg_code", ("B01", None)),
                ("dept_code", ("D02", None)),
            ]),
        );
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
        ];

        let path = classify_room(&room, &tiers, "revit", &[]);

        assert_eq!(path.len(), 2);
        assert_eq!(path[0].code.as_deref(), Some("B01"));
        assert!(!path[0].undefined);
        assert_eq!(path[1].code.as_deref(), Some("D02"));
        assert!(!path[1].undefined);
    }

    /// A room missing the sub-department property: Building + Department
    /// resolve, Sub-department and everything below become undefined.
    #[test]
    fn test_classify_room_partial_undefined() {
        let room = make_room(
            "r1",
            BTreeMap::from([
                ("bldg_code", ("B01", None)),
                ("dept_code", ("D02", None)),
                // sub_dept_code absent
            ]),
        );
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
            make_tier("SubDept", Some("sub_dept_code"), None),
        ];

        let path = classify_room(&room, &tiers, "revit", &[]);

        assert!(!path[0].undefined);
        assert!(!path[1].undefined);
        assert!(path[2].undefined);
    }

    /// A room missing tier 1 is undefined all the way down.
    #[test]
    fn test_classify_room_all_undefined() {
        let room = make_room("r1", BTreeMap::new()); // no custom props
        let tiers = vec![
            make_tier("Building", Some("bldg_code"), None),
            make_tier("Department", Some("dept_code"), None),
        ];

        let path = classify_room(&room, &tiers, "revit", &[]);

        assert!(path.iter().all(|t| t.undefined));
    }
}
