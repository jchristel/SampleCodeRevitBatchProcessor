//! Hierarchy gross-area footprints — the first geometry-processing service.
//!
//! Stage 1 (this file today): union a set of rooms' outer loops into a single
//! **hole-free** footprint per group. Later stages (tier dissolve, exclusions,
//! the endpoint, the viewer mode) build on this — see HANDOVER-hierarchy-areas.md.
//!
//! Transport-agnostic like every `service` module: it imports `geo` and
//! `crate::contract`, never `axum`/`rmcp`.
//!
//! The number this ultimately produces is an **aggregated room footprint**
//! (wall-zone- and filled-void-inclusive), NOT net room area and NOT a
//! standards-based gross — see the handover's "Naming / honesty" note before
//! labelling it anywhere.

use geo::{Area, BooleanOps, Coord, LineString, MultiPolygon, Polygon};
use serde::Serialize;

use crate::classify::TierValue;
use crate::contract::{Level, Loop, Room, SUPPORTED_SCHEMA};
use crate::settings::HierarchyExclusion;
use crate::state::AppState;

use super::rooms::assemble_rooms;
use super::ServiceError;

/// Perpendicular distance (in model units — feet) below which a vertex is
/// treated as lying *on* the line through its neighbours and dropped. Only
/// true-collinear points and float noise fall under this; a genuine corner sits
/// orders of magnitude above it. Tight on purpose: it removes redundant
/// vertices, never real geometry.
const COLLINEAR_EPS_FT: f64 = 1e-6;

/// Build a `geo` polygon from a room's **outer** loop only. Interior loops
/// (the room's own holes — a column or shaft) are dropped here by construction:
/// the footprint is the outline you'd trace around the room, so a room's own
/// void never subtracts from a group footprint. `None` for a loop that can't
/// form a polygon (fewer than three points — e.g. an unplaced room).
fn room_outer_polygon(room: &Room) -> Option<Polygon<f64>> {
    let outer = room.loops.first()?;
    if outer.points.len() < 3 {
        return None;
    }
    Some(Polygon::new(loop_to_linestring(outer), vec![]))
}

fn loop_to_linestring(l: &Loop) -> LineString<f64> {
    LineString::from(l.points.iter().map(|p| Coord { x: p.x, y: p.y }).collect::<Vec<_>>())
}

/// Stage 1 — the group footprint for one set of rooms (one hierarchy group on
/// one level). Union every room's outer loop, then rebuild each resulting
/// polygon from its **exterior ring alone**, discarding any interior holes (a
/// settled decision: enclosed open space — courtyards, shafts, the void a ring
/// of rooms encloses — counts as footprint area). The result is a
/// `MultiPolygon`: disconnected exterior rings ("islands", e.g. two separate
/// wings of one department) are all kept, never collapsed to one polygon.
///
/// Every exterior ring is run through [`dedup_collinear`] so a union that leaves
/// a redundant vertex where two rooms meet on a straight edge does not inflate
/// the vertex count — three edge-to-edge rooms forming a rectangle yield a
/// four-point polygon, not five.
pub fn group_footprint(rooms: &[Room]) -> MultiPolygon<f64> {
    footprint_of_rooms(rooms.iter())
}

fn footprint_of_rooms<'a>(rooms: impl Iterator<Item = &'a Room>) -> MultiPolygon<f64> {
    // Pairwise union into an accumulator. Fine for the room counts per group;
    // if profiling later shows it matters, geo's unary_union over the whole set
    // is the drop-in replacement (measure first — STRATEGY.md).
    let mut acc: MultiPolygon<f64> = MultiPolygon::new(vec![]);
    for room in rooms {
        if let Some(poly) = room_outer_polygon(room) {
            acc = acc.union(&MultiPolygon::new(vec![poly]));
        }
    }
    clean_exterior(&acc)
}

/// Rebuild every polygon from its **exterior ring alone** — discarding interior
/// holes (the settled "enclosed open space counts as area" rule) — and drop
/// redundant/collinear vertices.
///
/// Applied after *every* union, bottom tier and upward. NOTE this deliberately
/// departs from the handover's "strip once at the bottom" optimisation: unioning
/// two hole-free child footprints CAN enclose a new hole at a higher tier (a
/// courtyard bounded by several groups that meets only when they dissolve), and
/// leaving that hole in would punch the void out of the parent's area —
/// inconsistent with "enclosed open space counts *everywhere*". Stripping at
/// every tier is correct; stripping once is not. See
/// `test_parent_fills_courtyard_between_groups`.
fn clean_exterior(mp: &MultiPolygon<f64>) -> MultiPolygon<f64> {
    MultiPolygon::new(
        mp.iter()
            .map(|p| Polygon::new(dedup_collinear(p.exterior()), vec![]))
            .collect(),
    )
}

/// Dissolve already-clean child footprints into one parent footprint: union
/// them, then re-strip (a courtyard can appear here — see `clean_exterior`).
fn dissolve_footprints(children: &[&MultiPolygon<f64>]) -> MultiPolygon<f64> {
    let mut acc: MultiPolygon<f64> = MultiPolygon::new(vec![]);
    for child in children {
        acc = acc.union(*child);
    }
    clean_exterior(&acc)
}

/// Measured area of a footprint — the area of the actual dissolved polygon, the
/// only correct source (never a sum of child areas, which mishandles shared
/// wall zones and filled voids — see the handover).
pub fn footprint_area(footprint: &MultiPolygon<f64>) -> f64 {
    footprint.unsigned_area()
}

/// A room paired with its resolved classification path — the input to the tier
/// dissolve. In production this comes straight off a `RoomResponse` (which
/// already carries both `room` and `classification`); kept as a borrowed pair so
/// `areas` doesn't depend on the `rooms` service.
pub struct ClassifiedRoom<'a> {
    pub room: &'a Room,
    pub path: &'a [TierValue],
}

/// One hierarchy group's dissolved footprint at one tier, on one level.
#[derive(Debug)]
pub struct AreaGroup {
    pub level_id: String,
    /// The resolved path prefix identifying this group, outermost first. Its
    /// length is the tier depth: a top-tier group has one element, a bottom-tier
    /// group the full path. The last element is this group's own tier value.
    pub path: Vec<TierValue>,
    pub footprint: MultiPolygon<f64>,
    pub area: f64,
    /// `false` when a Case-A (`group`) exclusion withholds this group from its
    /// parent's dissolve — the group is still reported (its own area is real),
    /// but it does not contribute to any tier above it. Always `true` for a group
    /// no exclusion targets.
    pub counted_upward: bool,
}

/// The Phase-2 pipeline: per-level, per-tier dissolved footprints for a set of
/// classified rooms. Rooms are partitioned by level first (footprints never
/// union across floors — a per-level decision), then each level runs the
/// two-stage pipeline: build each bottom-tier group's footprint from its rooms,
/// then dissolve child footprints into parents tier by tier up to the top. Every
/// tier's area is measured from that tier's own dissolved polygon, never summed
/// from children. Returns bottom-tier groups first, then each tier above.
pub fn hierarchy_area_groups(rooms: &[ClassifiedRoom], exclusions: &[HierarchyExclusion]) -> Vec<AreaGroup> {
    // Stage 1 exclusion (Case B): drop excluded rooms before they become
    // geometry, so they vanish from every tier including their bottom group.
    // Partition the survivors by level, first-seen order for determinism.
    let mut by_level: Vec<(String, Vec<&ClassifiedRoom>)> = Vec::new();
    for cr in rooms {
        if is_room_excluded(&cr.room.id, exclusions) {
            continue;
        }
        match by_level.iter_mut().find(|(lid, _)| lid == &cr.room.level_id) {
            Some((_, v)) => v.push(cr),
            None => by_level.push((cr.room.level_id.clone(), vec![cr])),
        }
    }

    let mut out = Vec::new();
    for (level_id, level_rooms) in &by_level {
        out.extend(level_groups(level_id, level_rooms, exclusions));
    }
    out
}

fn level_groups(level_id: &str, rooms: &[&ClassifiedRoom], exclusions: &[HierarchyExclusion]) -> Vec<AreaGroup> {
    let num_tiers = rooms.iter().map(|r| r.path.len()).max().unwrap_or(0);
    if num_tiers == 0 {
        return Vec::new(); // no hierarchy configured -> no groups
    }

    // Stage 1: gather rooms into bottom-tier groups by full-path key (first-seen
    // order), then build each group's footprint. `classify_room` guarantees a
    // uniform-depth path, so `path.len() == num_tiers` for every room.
    let mut bottom: Vec<(Vec<TierValue>, Vec<&Room>)> = Vec::new();
    for cr in rooms {
        if cr.path.len() != num_tiers {
            continue;
        }
        match bottom.iter_mut().find(|(p, _)| path_eq(p, cr.path)) {
            Some((_, v)) => v.push(cr.room),
            None => bottom.push((cr.path.to_vec(), vec![cr.room])),
        }
    }

    let current: Vec<(Vec<TierValue>, MultiPolygon<f64>)> = bottom
        .into_iter()
        .map(|(path, rs)| (path, footprint_of_rooms(rs.into_iter())))
        .collect();

    let mut results: Vec<AreaGroup> =
        current.iter().map(|(path, fp)| emit(level_id, path.clone(), fp, exclusions)).collect();

    // Stage 2: dissolve upward. For each parent depth, group the tier below by
    // its path prefix and union each group's footprints — but a Case-A
    // (`group`) exclusion WITHHOLDS a child node from its parent's dissolve, so
    // the excluded group drops out of that tier and every tier above (its own
    // footprint was already emitted). The union stays a dumb "dissolve these
    // inputs" loop; the withhold is decided here, at the insertion point.
    let mut current = current;
    for depth in (0..num_tiers - 1).rev() {
        let mut parents: Vec<(Vec<TierValue>, Vec<&MultiPolygon<f64>>)> = Vec::new();
        for (path, fp) in &current {
            if is_group_excluded(path, exclusions) {
                continue; // withheld from its parent (and thus every tier above)
            }
            let prefix = &path[..=depth];
            match parents.iter_mut().find(|(p, _)| path_eq(p, prefix)) {
                Some((_, v)) => v.push(fp),
                None => parents.push((prefix.to_vec(), vec![fp])),
            }
        }
        let next: Vec<(Vec<TierValue>, MultiPolygon<f64>)> = parents
            .into_iter()
            .map(|(path, fps)| (path, dissolve_footprints(&fps)))
            .collect();
        results.extend(next.iter().map(|(path, fp)| emit(level_id, path.clone(), fp, exclusions)));
        current = next;
    }

    results
}

fn emit(level_id: &str, path: Vec<TierValue>, footprint: &MultiPolygon<f64>, exclusions: &[HierarchyExclusion]) -> AreaGroup {
    let counted_upward = !is_group_excluded(&path, exclusions);
    AreaGroup {
        level_id: level_id.to_string(),
        area: footprint_area(footprint),
        footprint: footprint.clone(),
        path,
        counted_upward,
    }
}

/// Case B — is this room id withheld before geometry (stage 1)?
fn is_room_excluded(id: &str, exclusions: &[HierarchyExclusion]) -> bool {
    exclusions.iter().any(|e| match e {
        HierarchyExclusion::Rooms { ids } => ids.iter().any(|x| x == id),
        HierarchyExclusion::Group { .. } => false,
    })
}

/// Case A — is this group (identified by its own, last tier value) withheld from
/// its parent's dissolve (stage 2)? Matches an exclusion whose `tier` names this
/// group's tier and whose `value` equals the resolved code or name.
fn is_group_excluded(path: &[TierValue], exclusions: &[HierarchyExclusion]) -> bool {
    let Some(last) = path.last() else { return false };
    exclusions.iter().any(|e| match e {
        HierarchyExclusion::Group { tier, value } => {
            tier == &last.tier
                && (last.code.as_deref() == Some(value.as_str())
                    || last.name.as_deref() == Some(value.as_str()))
        }
        HierarchyExclusion::Rooms { .. } => false,
    })
}

// ============================ endpoint / wire shape ============================

/// Wire result of `GET /projects/{id}/areas`: per-level, per-tier dissolved
/// footprints for one project's rooms, scoped like `/rooms`. One computation
/// feeds both asks — the plan-view overlay (uses `rings`) and the summary table
/// (uses `area`/`counted_upward`, ignores `rings`).
#[derive(Serialize)]
pub struct AreasResult {
    pub schema_version: u32,
    /// The scoped level set (same shape `/rooms` returns) so the viewer can draw
    /// each level's footprints on that level's plan.
    pub levels: Vec<Level>,
    pub groups: Vec<AreaGroupResponse>,
}

/// One group's dissolved footprint at one tier on one level, in wire shape.
#[derive(Serialize)]
pub struct AreaGroupResponse {
    pub level_id: String,
    /// Resolved classification prefix, outermost first (the group's identity).
    pub path: Vec<TierValue>,
    /// Measured **aggregated room footprint** area — wall-zone/void-inclusive,
    /// NOT net room area (see the module's naming note).
    pub area: f64,
    /// `false` when a Case-A exclusion withholds this group from tiers above it.
    pub counted_upward: bool,
    /// Hole-free exterior rings; each is a list of `[x, y]` points, multiple
    /// rings meaning islands. Closing point dropped — the viewer re-closes for a
    /// `<polygon>` (no even-odd path needed, holes are already stripped).
    pub rings: Vec<Vec<[f64; 2]>>,
}

impl From<AreaGroup> for AreaGroupResponse {
    fn from(g: AreaGroup) -> Self {
        AreaGroupResponse {
            level_id: g.level_id,
            path: g.path,
            area: g.area,
            counted_upward: g.counted_upward,
            rings: rings_of(&g.footprint),
        }
    }
}

fn rings_of(mp: &MultiPolygon<f64>) -> Vec<Vec<[f64; 2]>> {
    mp.iter()
        .map(|poly| {
            let pts = &poly.exterior().0;
            let n = if pts.len() >= 2 && pts.first() == pts.last() { pts.len() - 1 } else { pts.len() };
            pts[..n].iter().map(|c| [c.x, c.y]).collect()
        })
        .collect()
}

/// Assemble the areas result for one project, scoped like `/rooms`. Reuses
/// `assemble_rooms` for the scoped, classified room set (respecting
/// project/building/milestone exactly as `/rooms` does — a milestone view reuses
/// its pinned snapshots), so grouping runs off the same classification the room
/// render already resolved. Exclusions come from the project's resolved bundle
/// (server-used config, unlike client-only colour plans). `Ok(None)` when
/// nothing has ever been pushed (the handler's 204), mirroring `assemble_rooms`.
pub fn assemble_areas(
    state: &AppState,
    project: &str,
    building: Option<&str>,
    milestone: Option<&str>,
) -> Result<Option<AreasResult>, ServiceError> {
    let Some(rooms) = assemble_rooms(state, Some(project), building, milestone)? else {
        return Ok(None);
    };

    let exclusions = state
        .settings()
        .settings_for(project)
        .map(|b| b.hierarchy_exclusions.clone())
        .unwrap_or_default();

    let classified: Vec<ClassifiedRoom> = rooms
        .rooms
        .iter()
        .map(|r| ClassifiedRoom { room: &r.room, path: &r.classification })
        .collect();

    let groups = hierarchy_area_groups(&classified, &exclusions)
        .into_iter()
        .map(AreaGroupResponse::from)
        .collect();

    Ok(Some(AreasResult { schema_version: SUPPORTED_SCHEMA, levels: rooms.levels, groups }))
}

/// Two classification prefixes name the same group when their resolved values
/// match tier-for-tier (`tier` label is positional and always agrees, so only
/// code/name/undefined need comparing).
fn path_eq(a: &[TierValue], b: &[TierValue]) -> bool {
    a.len() == b.len()
        && a.iter()
            .zip(b)
            .all(|(x, y)| x.code == y.code && x.name == y.name && x.undefined == y.undefined)
}

/// Drop vertices that lie on the straight line between their neighbours (and any
/// exact duplicates). Operates on a closed ring and returns a closed ring. Leaves
/// a triangle (three distinct vertices) untouched — nothing there is redundant.
fn dedup_collinear(ring: &LineString<f64>) -> LineString<f64> {
    let pts = &ring.0;
    // A closed ring repeats its first point last; work over the distinct cycle.
    let distinct = if pts.len() >= 2 && pts.first() == pts.last() {
        &pts[..pts.len() - 1]
    } else {
        &pts[..]
    };
    let n = distinct.len();
    if n < 4 {
        return ring.clone();
    }

    let mut kept: Vec<Coord<f64>> = Vec::with_capacity(n);
    for i in 0..n {
        let prev = distinct[(i + n - 1) % n];
        let cur = distinct[i];
        let next = distinct[(i + 1) % n];

        // Perpendicular distance of `cur` from the line prev->next. Zero (within
        // eps) means collinear; a coincident prev/next with cur elsewhere is a
        // spike, also redundant for an area footprint.
        let cross = (cur.x - prev.x) * (next.y - prev.y) - (cur.y - prev.y) * (next.x - prev.x);
        let base = ((next.x - prev.x).powi(2) + (next.y - prev.y).powi(2)).sqrt();
        let dist = if base > 0.0 { cross.abs() / base } else { 0.0 };
        if dist > COLLINEAR_EPS_FT {
            kept.push(cur);
        }
    }

    // Guard: never simplify a ring out of existence.
    if kept.len() < 3 {
        return ring.clone();
    }
    kept.push(kept[0]); // re-close
    LineString::from(kept)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::Point2D;

    /// Build a room from one or more loops of `(x, y)` corners. First loop is the
    /// outer boundary; any further loops are the room's own holes.
    fn room(id: &str, loops: &[&[(f64, f64)]]) -> Room {
        Room {
            id: id.to_string(),
            name: id.to_string(),
            level_id: "L1".to_string(),
            loops: loops
                .iter()
                .map(|pts| Loop {
                    points: pts.iter().map(|&(x, y)| Point2D { x, y }).collect(),
                })
                .collect(),
            properties: Default::default(),
        }
    }

    fn rect(x0: f64, y0: f64, x1: f64, y1: f64) -> Vec<(f64, f64)> {
        vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    }

    /// Distinct exterior vertices of a single-polygon footprint (closing point
    /// dropped), as an unordered set of rounded coords for order-independent
    /// comparison.
    fn corners(poly: &Polygon<f64>) -> Vec<(i64, i64)> {
        let pts = &poly.exterior().0;
        let distinct = &pts[..pts.len().saturating_sub(1)];
        let mut out: Vec<(i64, i64)> = distinct
            .iter()
            .map(|c| ((c.x * 1e6).round() as i64, (c.y * 1e6).round() as i64))
            .collect();
        out.sort_unstable();
        out
    }

    fn approx(a: f64, b: f64) {
        assert!((a - b).abs() < 1e-6, "expected ~{b}, got {a}");
    }

    // ---- Phase 2 helpers ----

    fn tv(tier: &str, name: &str) -> TierValue {
        TierValue { tier: tier.to_string(), code: None, name: Some(name.to_string()), undefined: false }
    }

    fn undef(tier: &str) -> TierValue {
        TierValue { tier: tier.to_string(), code: None, name: None, undefined: true }
    }

    /// A room on `level` with the given outer rectangle and classification path.
    fn croom(id: &str, level: &str, r: Vec<(f64, f64)>) -> Room {
        let mut room = room(id, &[&r]);
        room.level_id = level.to_string();
        room
    }

    /// Find the single group whose path matches `want` (by tier names / undefined).
    fn group<'a>(groups: &'a [AreaGroup], level: &str, want: &[TierValue]) -> &'a AreaGroup {
        groups
            .iter()
            .find(|g| g.level_id == level && path_eq(&g.path, want))
            .unwrap_or_else(|| panic!("no group {want:?} on {level}"))
    }

    /// Two departments dissolve into a building: each tier's area is measured
    /// from its own polygon, and the building equals the whole union.
    #[test]
    fn test_two_tier_dissolve_areas() {
        // DeptA = two adjacent rooms (area 200); DeptB = one room (area 100).
        let rooms = vec![
            (croom("a1", "L1", rect(0.0, 0.0, 10.0, 10.0)), vec![tv("Building", "B1"), tv("Dept", "A")]),
            (croom("a2", "L1", rect(10.0, 0.0, 20.0, 10.0)), vec![tv("Building", "B1"), tv("Dept", "A")]),
            (croom("b1", "L1", rect(20.0, 0.0, 30.0, 10.0)), vec![tv("Building", "B1"), tv("Dept", "B")]),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let g = hierarchy_area_groups(&cls, &[]);

        approx(group(&g, "L1", &[tv("Building", "B1"), tv("Dept", "A")]).area, 200.0);
        approx(group(&g, "L1", &[tv("Building", "B1"), tv("Dept", "B")]).area, 100.0);
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 300.0);
    }

    /// The correctness case for stripping at every tier: two departments each
    /// hole-free, but together they enclose a courtyard that belongs to no room.
    /// The building footprint must FILL that courtyard (enclosed space counts),
    /// so building area ≠ Σ department areas.
    #[test]
    fn test_parent_fills_courtyard_between_groups() {
        // 30x30 frame. Dept A = bottom + left + top (a C, open on the right).
        // Dept B = the right bar. Together they ring a 10x10 courtyard.
        let path_a = vec![tv("Building", "B1"), tv("Dept", "A")];
        let path_b = vec![tv("Building", "B1"), tv("Dept", "B")];
        let rooms = vec![
            (croom("bottom", "L1", rect(0.0, 0.0, 30.0, 10.0)), path_a.clone()),
            (croom("left", "L1", rect(0.0, 10.0, 10.0, 20.0)), path_a.clone()),
            (croom("top", "L1", rect(0.0, 20.0, 30.0, 30.0)), path_a.clone()),
            (croom("right", "L1", rect(20.0, 10.0, 30.0, 20.0)), path_b.clone()),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let g = hierarchy_area_groups(&cls, &[]);

        let a = group(&g, "L1", &path_a).area; // C-shape, no hole
        let b = group(&g, "L1", &path_b).area; // the bar
        let building = group(&g, "L1", &[tv("Building", "B1")]).area;
        approx(a, 700.0);
        approx(b, 100.0);
        approx(building, 900.0); // courtyard (100) filled at the parent tier
        assert!((building - (a + b)).abs() > 50.0, "parent must exceed Σ children by the filled courtyard");
    }

    /// The same department on two levels forms two independent bottom groups and
    /// two independent building footprints — the pipeline never unions floors.
    #[test]
    fn test_per_level_groups_are_independent() {
        let path = vec![tv("Building", "B1"), tv("Dept", "A")];
        let rooms = vec![
            (croom("l1", "L1", rect(0.0, 0.0, 10.0, 10.0)), path.clone()),
            (croom("l2", "L2", rect(0.0, 0.0, 10.0, 20.0)), path.clone()),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let g = hierarchy_area_groups(&cls, &[]);

        approx(group(&g, "L1", &path).area, 100.0);
        approx(group(&g, "L2", &path).area, 200.0);
        // Building tier exists per level, each equal to its one department.
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 100.0);
        approx(group(&g, "L2", &[tv("Building", "B1")]).area, 200.0);
    }

    /// An `undefined` classification is a real group, not a dropped room — it
    /// dissolves and reports area like any other.
    #[test]
    fn test_undefined_bucket_is_a_real_group() {
        let rooms = vec![
            (croom("known", "L1", rect(0.0, 0.0, 10.0, 10.0)), vec![tv("Building", "B1"), tv("Dept", "A")]),
            (croom("unk", "L1", rect(10.0, 0.0, 20.0, 10.0)), vec![tv("Building", "B1"), undef("Dept")]),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let g = hierarchy_area_groups(&cls, &[]);

        approx(group(&g, "L1", &[tv("Building", "B1"), undef("Dept")]).area, 100.0);
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 200.0);
    }

    /// No hierarchy configured (empty paths) yields no groups, not a panic.
    #[test]
    fn test_no_hierarchy_yields_no_groups() {
        let r = croom("r", "L1", rect(0.0, 0.0, 10.0, 10.0));
        let cls = vec![ClassifiedRoom { room: &r, path: &[] }];
        assert!(hierarchy_area_groups(&cls, &[]).is_empty());
    }

    // ---- Phase 3: exclusions ----

    /// Case A (`group`): the Outdoor department is withheld from the building
    /// dissolve — the building no longer includes it, but Outdoor is still
    /// reported (its own area intact) and flagged `counted_upward = false`.
    #[test]
    fn test_exclude_group_withholds_from_parent_but_keeps_group() {
        let path_in = vec![tv("Building", "B1"), tv("Dept", "Inside")];
        let path_out = vec![tv("Building", "B1"), tv("Dept", "Outdoor")];
        let rooms = vec![
            (croom("i1", "L1", rect(0.0, 0.0, 10.0, 10.0)), path_in.clone()),
            (croom("o1", "L1", rect(10.0, 0.0, 30.0, 10.0)), path_out.clone()),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let excl = vec![HierarchyExclusion::Group { tier: "Dept".to_string(), value: "Outdoor".to_string() }];
        let g = hierarchy_area_groups(&cls, &excl);

        // Building excludes Outdoor: 100, not 100 + 200.
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 100.0);
        // Outdoor is still reported with its own real area, flagged not-counted.
        let outdoor = group(&g, "L1", &path_out);
        approx(outdoor.area, 200.0);
        assert!(!outdoor.counted_upward, "excluded group is marked not counted upward");
        // The included department is untouched and still counts upward.
        let inside = group(&g, "L1", &path_in);
        approx(inside.area, 100.0);
        assert!(inside.counted_upward);
    }

    /// Case B (`rooms`): an excluded room never becomes geometry, so it is gone
    /// from every tier — its own bottom group AND the building — the most
    /// destructive case (unlike Case A, it shrinks the group's own area too).
    #[test]
    fn test_exclude_rooms_drops_from_every_tier() {
        let path_a = vec![tv("Building", "B1"), tv("Dept", "A")];
        let rooms = vec![
            (croom("keep", "L1", rect(0.0, 0.0, 10.0, 10.0)), path_a.clone()),
            (croom("drop", "L1", rect(10.0, 0.0, 20.0, 10.0)), path_a.clone()),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let excl = vec![HierarchyExclusion::Rooms { ids: vec!["drop".to_string()] }];
        let g = hierarchy_area_groups(&cls, &excl);

        // Bottom group and building both shrink to just the kept room.
        approx(group(&g, "L1", &path_a).area, 100.0);
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 100.0);
    }

    /// An exclusion at a middle tier (Department) withholds that whole subtree
    /// from the top tier while leaving the department and its sub-departments
    /// reported — the withhold propagates upward through the dissolve.
    #[test]
    fn test_exclude_group_at_middle_tier_propagates_up() {
        // 3 tiers: Building / Dept / Sub. Exclude Dept = "Outdoor".
        let inside = |sub: &str| vec![tv("Building", "B1"), tv("Dept", "Inside"), tv("Sub", sub)];
        let outdoor = |sub: &str| vec![tv("Building", "B1"), tv("Dept", "Outdoor"), tv("Sub", sub)];
        let rooms = vec![
            (croom("i", "L1", rect(0.0, 0.0, 10.0, 10.0)), inside("S1")),
            (croom("o", "L1", rect(10.0, 0.0, 30.0, 10.0)), outdoor("S2")),
        ];
        let cls: Vec<ClassifiedRoom> = rooms.iter().map(|(r, p)| ClassifiedRoom { room: r, path: p }).collect();
        let excl = vec![HierarchyExclusion::Group { tier: "Dept".to_string(), value: "Outdoor".to_string() }];
        let g = hierarchy_area_groups(&cls, &excl);

        // Building = Inside subtree only.
        approx(group(&g, "L1", &[tv("Building", "B1")]).area, 100.0);
        // Outdoor department and its sub-department are still reported.
        approx(group(&g, "L1", &[tv("Building", "B1"), tv("Dept", "Outdoor")]).area, 200.0);
        approx(group(&g, "L1", &outdoor("S2")).area, 200.0);
        assert!(!group(&g, "L1", &[tv("Building", "B1"), tv("Dept", "Outdoor")]).counted_upward);
    }

    /// A single plain room → one ring, its four corners, its own area.
    #[test]
    fn test_single_room_outer_ring() {
        let fp = group_footprint(&[room("r", &[&rect(0.0, 0.0, 10.0, 8.0)])]);
        assert_eq!(fp.0.len(), 1, "one room -> one polygon");
        assert!(fp.0[0].interiors().is_empty(), "no holes");
        assert_eq!(corners(&fp.0[0]).len(), 4);
        approx(footprint_area(&fp), 80.0);
    }

    /// A room with its own interior hole (a column): the hole is ignored, so the
    /// footprint is the full outer square — the "discard interior holes" rule at
    /// its most basic (enclosed void counts as area).
    #[test]
    fn test_room_hole_is_ignored() {
        let outer = rect(0.0, 0.0, 10.0, 10.0);
        let hole = rect(3.0, 3.0, 7.0, 7.0);
        let fp = group_footprint(&[room("r", &[&outer, &hole])]);
        assert_eq!(fp.0.len(), 1);
        assert!(fp.0[0].interiors().is_empty());
        approx(footprint_area(&fp), 100.0); // hole filled, not 100 - 16
    }

    /// Two rooms with a gap between them → two islands survive (a MultiPolygon at
    /// every tier, never special-cased to one).
    #[test]
    fn test_two_disjoint_clusters_keep_two_islands() {
        let fp = group_footprint(&[
            room("a", &[&rect(0.0, 0.0, 10.0, 10.0)]),
            room("b", &[&rect(20.0, 0.0, 30.0, 10.0)]),
        ]);
        assert_eq!(fp.0.len(), 2, "disconnected rooms stay separate islands");
        approx(footprint_area(&fp), 200.0);
    }

    /// Two rooms sharing an edge dissolve to one ring with no sliver, and the
    /// collinear midpoints where the shared edge meets the boundary are removed.
    #[test]
    fn test_adjacent_rooms_dissolve_no_sliver() {
        let fp = group_footprint(&[
            room("a", &[&rect(0.0, 0.0, 10.0, 10.0)]),
            room("b", &[&rect(10.0, 0.0, 20.0, 10.0)]),
        ]);
        assert_eq!(fp.0.len(), 1, "adjacent rooms merge into one polygon");
        assert_eq!(corners(&fp.0[0]).len(), 4, "merged rectangle has 4 corners, no sliver vertex");
        approx(footprint_area(&fp), 200.0);
    }

    /// The reviewed case: STORAGE + HALL on top, STAIR full-width below, all one
    /// group → a single polygon with EXACTLY four corners. Without the collinear
    /// dedup the raw union leaves a fifth point where STORAGE meets HALL on the
    /// straight top edge.
    #[test]
    fn test_three_rooms_dissolve_to_four_corners() {
        let storage = rect(0.0, 10.0, 15.0, 20.0); // top-left
        let hall = rect(15.0, 10.0, 24.0, 20.0); // top-right
        let stair = rect(0.0, 0.0, 24.0, 10.0); // full-width bottom
        let fp = group_footprint(&[room("storage", &[&storage]), room("hall", &[&hall]), room("stair", &[&stair])]);

        assert_eq!(fp.0.len(), 1, "three connected rooms -> one polygon");
        assert!(fp.0[0].interiors().is_empty());
        assert_eq!(
            corners(&fp.0[0]),
            vec![(0, 0), (0, 20_000_000), (24_000_000, 0), (24_000_000, 20_000_000)],
            "exactly the four outer corners (collinear STORAGE|HALL point dropped)"
        );
        approx(footprint_area(&fp), 24.0 * 20.0);
    }

    /// `dedup_collinear` directly: a square with a redundant midpoint on one
    /// edge (and an exact duplicate corner) collapses back to four vertices,
    /// while a genuine corner is never dropped. Locked independently so the
    /// four-corner guarantee doesn't silently depend on the union backend.
    #[test]
    fn test_dedup_collinear_removes_only_redundant_points() {
        // Closed ring: corners of a 10x10 square + a collinear midpoint (10,5)
        // on the right edge + a duplicate of (0,0) at the end before closing.
        let ring = LineString::from(vec![
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 5.0), // collinear on the right edge
            (10.0, 10.0),
            (0.0, 10.0),
            (0.0, 0.0), // closing point
        ]);
        let out = dedup_collinear(&ring);
        let distinct = &out.0[..out.0.len() - 1];
        assert_eq!(distinct.len(), 4, "the collinear midpoint is dropped, real corners kept");
        assert!(out.0.first() == out.0.last(), "ring stays closed");
    }

    /// Two rooms meant to abut, but whose shared edge coordinates disagree by
    /// float noise (Revit exports aren't bit-identical across rooms). They must
    /// still dissolve to one clean ring — no sliver polygon, no spurious second
    /// island. Confirms the union backend's precision covers noise-level
    /// mismatch, so no explicit vertex-snap pre-pass is needed at this scale.
    #[test]
    fn test_noise_level_gap_still_dissolves() {
        let a = rect(0.0, 0.0, 10.0, 10.0);
        // b's left edge is a hair off from a's right edge (x = 10 ± 1e-9).
        let b = vec![(10.0 + 1e-9, 0.0), (20.0, 0.0), (20.0, 10.0), (10.0 - 1e-9, 10.0)];
        let fp = group_footprint(&[room("a", &[&a]), room("b", &[&b])]);
        assert_eq!(fp.0.len(), 1, "noise-level mismatch must not split into two islands");
        approx(footprint_area(&fp), 200.0);
    }

    /// A ring of four rooms encloses a courtyard: the union has an interior hole,
    /// which stage 1 strips, so the footprint area includes the courtyard
    /// (enclosed open space counts as footprint — a banked, accepted consequence).
    #[test]
    fn test_ring_of_rooms_fills_courtyard() {
        // A 30x30 outer square as a 10-wide frame of four rooms around a 10x10 void.
        let fp = group_footprint(&[
            room("bottom", &[&rect(0.0, 0.0, 30.0, 10.0)]),
            room("top", &[&rect(0.0, 20.0, 30.0, 30.0)]),
            room("left", &[&rect(0.0, 10.0, 10.0, 20.0)]),
            room("right", &[&rect(20.0, 10.0, 30.0, 20.0)]),
        ]);
        assert_eq!(fp.0.len(), 1, "the frame dissolves to one outer ring");
        assert!(fp.0[0].interiors().is_empty(), "the enclosed courtyard hole is stripped");
        approx(footprint_area(&fp), 900.0); // 30*30, courtyard filled (not 900 - 100)
    }

    // ---- Phase 4: the endpoint (assemble_areas end-to-end over AppState) ----

    mod endpoint {
        use super::*;
        use crate::contract::{CustomValue, Level, Model, Project, RoomPayload, Snapshot};
        use crate::settings::HierarchyTier;
        use crate::state::{AppState, ProjectSettings};
        use crate::storage::MemStore;
        use std::collections::{BTreeMap, HashMap};

        /// A 2-tier bundle (Building/Dept, each keyed on a name property), with
        /// the given footprint exclusions.
        fn bundle(exclusions: Vec<HierarchyExclusion>) -> ProjectSettings {
            ProjectSettings {
                drofus: None,
                hierarchy: vec![
                    HierarchyTier { name: "Building".to_string(), code_property: None, name_property: Some("bldg".to_string()) },
                    HierarchyTier { name: "Dept".to_string(), code_property: None, name_property: Some("dept".to_string()) },
                ],
                builtin_properties: vec![],
                room_label: vec!["$name".to_string()],
                drofus_fields: vec![],
                milestones: vec![],
                comparison_key: None,
                comparison_properties: vec![],
                hierarchy_exclusions: exclusions,
            }
        }

        /// A room with an outer rectangle and `bldg`/`dept` classification props.
        fn geo_room(id: &str, bldg: &str, dept: &str, r: Vec<(f64, f64)>) -> Room {
            let mut properties = BTreeMap::new();
            properties.insert("bldg".to_string(), CustomValue { value: bldg.to_string(), storage_type: None });
            properties.insert("dept".to_string(), CustomValue { value: dept.to_string(), storage_type: None });
            Room {
                id: id.to_string(),
                name: id.to_string(),
                level_id: "L1".to_string(),
                loops: vec![Loop { points: r.iter().map(|&(x, y)| Point2D { x, y }).collect() }],
                properties,
            }
        }

        fn state_with(rooms: Vec<Room>, exclusions: Vec<HierarchyExclusion>) -> AppState {
            let registry = HashMap::from([("p1".to_string(), bundle(exclusions))]);
            let state = AppState::new(Box::new(MemStore::new()), registry, None);
            let payload = RoomPayload {
                schema_version: 5,
                project: Project { id: "p1".to_string(), name: "P".to_string() },
                model: Model { id: "m1".to_string(), name: "M".to_string(), source: "revit".to_string() },
                snapshot: Snapshot { taken_at: "2026-01-01T00:00:00Z".to_string() },
                model_to_shared: None,
                levels: vec![Level { id: "L1".to_string(), name: "Level 1".to_string(), elevation: 0.0 }],
                rooms,
            };
            state.set_snapshot(payload).unwrap();
            state
        }

        fn find<'a>(r: &'a AreasResult, dept: Option<&str>) -> &'a AreaGroupResponse {
            r.groups
                .iter()
                .find(|g| match dept {
                    Some(d) => g.path.len() == 2 && g.path[1].name.as_deref() == Some(d),
                    None => g.path.len() == 1, // the Building group
                })
                .expect("group present")
        }

        /// End-to-end: the endpoint scopes + classifies via assemble_rooms, groups
        /// per tier, and returns wire shape with levels, areas, and hole-free rings.
        #[test]
        fn test_assemble_areas_happy_path() {
            let rooms = vec![
                geo_room("in", "B1", "Inside", vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
                geo_room("out", "B1", "Outdoor", vec![(10.0, 0.0), (30.0, 0.0), (30.0, 10.0), (10.0, 10.0)]),
            ];
            let state = state_with(rooms, vec![]);
            let r = assemble_areas(&state, "p1", None, None).unwrap().expect("store has data");

            assert_eq!(r.schema_version, SUPPORTED_SCHEMA);
            assert_eq!(r.levels.len(), 1);
            approx(find(&r, Some("Inside")).area, 100.0);
            approx(find(&r, Some("Outdoor")).area, 200.0);
            let building = find(&r, None);
            approx(building.area, 300.0);
            assert!(building.counted_upward);
            // Hole-free ring, closing point dropped -> a 4-corner rectangle.
            assert_eq!(building.rings.len(), 1);
            assert_eq!(building.rings[0].len(), 4, "one exterior ring, 4 points, no closing dup");
        }

        /// A Case-A exclusion loaded from the project bundle takes effect through
        /// the endpoint: the building excludes Outdoor, which is still reported.
        #[test]
        fn test_assemble_areas_applies_bundle_exclusion() {
            let rooms = vec![
                geo_room("in", "B1", "Inside", vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]),
                geo_room("out", "B1", "Outdoor", vec![(10.0, 0.0), (30.0, 0.0), (30.0, 10.0), (10.0, 10.0)]),
            ];
            let excl = vec![HierarchyExclusion::Group { tier: "Dept".to_string(), value: "Outdoor".to_string() }];
            let state = state_with(rooms, excl);
            let r = assemble_areas(&state, "p1", None, None).unwrap().expect("store has data");

            approx(find(&r, None).area, 100.0); // building excludes Outdoor
            let outdoor = find(&r, Some("Outdoor"));
            approx(outdoor.area, 200.0); // still reported
            assert!(!outdoor.counted_upward);
        }

        /// Nothing pushed -> None (the handler's 204), mirroring assemble_rooms.
        #[test]
        fn test_assemble_areas_empty_store_is_none() {
            let registry = HashMap::from([("p1".to_string(), bundle(vec![]))]);
            let state = AppState::new(Box::new(MemStore::new()), registry, None);
            assert!(assemble_areas(&state, "p1", None, None).unwrap().is_none());
        }
    }
}
