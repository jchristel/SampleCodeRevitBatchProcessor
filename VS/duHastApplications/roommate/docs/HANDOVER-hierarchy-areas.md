# HANDOVER — Hierarchy gross areas

Design for a new feature: compute a **gross-area footprint per hierarchy group**
(building, department, sub-department — any N-tier scheme), expose it two ways —
as dissolved polygons on plan views, and as a project-statistics summary table —
and let a user exclude specific rooms or whole groups from those footprints.

This is a **design handover, not shipped code.** It captures every decision
reached in review so the build can start from settled semantics rather than
re-litigating them. Written to sit beside the existing HANDOVER-*.md docs; fold
the parts that ship into STRATEGY-SERVER.md / STRATEGY-BROWSER.md as they land,
per the split-doc discipline in STRATEGY.md.

Read [STRATEGY.md](STRATEGY.md) and [CODING-CONVENTIONS.md](CODING-CONVENTIONS.md)
first — this doc assumes both.

---

## Why this is the feature that cashes in the core bet

Everything the server derives today — dRofus join, classification, labels,
validation, milestone diff — is **property lookup and comparison. No geometry.**
This feature is the first that does real polygon processing: unioning room
outlines into a dissolved footprint per group, then dissolving those upward per
tier. That is exactly the "polygon boolean ops / room merging" work STRATEGY.md
names (§ "A caveat to stay honest about") as the thing that finally makes the
Rust-side performance argument *real* rather than potential. Treat it as a
deliberate crossing of that line, not an incremental derive.

---

## The two-stage pipeline (the spine of the whole feature)

Everything below hangs off one shape. Keep it literal in the code:

1. **Build each bottom-tier group's footprint from its rooms.**
   Gather the outer loops of every room in the group → union → **for each
   resulting polygon keep the exterior ring only, discard all interior holes**
   (see "Hole handling" — this is a settled call) → that is the group footprint,
   a hole-free MultiPolygon.

2. **Dissolve child footprints into each parent, tier by tier, up to the top.**
   A parent's footprint is the union of its children's (already hole-free)
   footprints. Because the inputs are already solids, no hole can reappear at a
   higher tier — so the strip in stage 1 runs exactly once, never again upward.

**Ordering is load-bearing, not just efficient.** Strip holes at the bottom,
*then* dissolve up. Unioning first and stripping last would give the same top
answer but wrong intermediate-tier areas. Bottom-strip-then-dissolve is correct,
not merely faster.

Grouping reuses `classify::classify_room` verbatim — every room already resolves
to its full tier path with the `undefined` latch. This feature groups by that
resolved path and must **not** grow a second classification vocabulary. The
`undefined` buckets become real area groups too ("unclassified sub-department
footprint"), consistent with how partial classification is surfaced everywhere
else.

---

## Islands vs. holes — different things, both real, treated oppositely

The user's word was "islands"; the geometry has two distinct concepts and they
are handled in opposite ways. Do not conflate them in the types or the comments.

- **Islands** = disconnected *exterior* rings (two physically separate wings of
  one department; a building-level group that genuinely forms separate blobs).
  **Always kept.** The output type is a MultiPolygon at *every* tier, never a
  single polygon — design for multiple exterior rings from the start, don't
  special-case "usually one."
- **Holes** = *interior* rings, voids inside an exterior ring (a column, a
  shaft, an enclosed courtyard). **Always discarded** (settled — see below).

So a group footprint is: one-or-more exterior rings (islands, all kept), each
with its interiors thrown away.

---

## Hole handling — DECISION: discard all interior holes, keep only exterior rings

Considered and rejected: an area threshold (fill columns < N m², keep
courtyards). Rejected because it needs a **configured epsilon**, which is a
small philosophical departure from the rest of the server — the numeric QA path
is proud of inferring precision per-comparison rather than carrying a fixed
epsilon anywhere. "Discard all holes" needs no number at all, so it stays clean.

**Consequence, banked and accepted:** enclosed open space reads as floor plate.
A department that wraps entirely around an atrium has that atrium filled into its
area; a column void vanishes; a courtyard bounded by several departments gets
closed at whatever tier those footprints meet (they meet at centrelines — see
next section — so it closes). Net rule: **enclosed open space counts as area,
everywhere.** For an "aggregated gross footprint" number this is a defensible,
consistent definition — the footprint is the outline you'd trace around the
group. The summary must never *label* it as usable or net area (see "Naming").

In `geo` terms the strip is: rebuild each `Polygon` from `.exterior()` alone,
dropping `.interiors()`.

---

## Why parent area ≠ Σ child areas (and why you must measure, never add)

A room belongs to exactly one hierarchy path, so **rooms never overlap** — there
is no double-counting of room interiors. If gross meant "sum of room net areas,"
parent *would* equal Σ children and arithmetic would be fine.

It doesn't, for two geometric reasons independent of room membership:

- **Wall zones between rooms.** Boundaries are most likely **wall centreline**
  (Revit `SpatialElementBoundaryLocation`) — CONFIRM against the pyRevit
  extractor, this one setting decides how honest "gross" is. At centreline,
  adjacent rooms tile edge-to-edge and a group unions into a clean polygon. Good
  — but the dissolved outline's area is still a property of the *polygon*, not of
  the child sum.
- **Filled holes.** Once interior voids (columns etc.) are filled per the
  decision above, the footprint area *includes* plan area that no room outline
  covered. That area exists in the dissolved polygon and in no child total.

Therefore: **area at every tier = measured area of that tier's actual dissolved
MultiPolygon.** Never "sum of child areas," never "parent minus the excluded
child's number" — both silently mishandle shared wall zones and filled voids.
(Earlier review wording said departments "overlap"; that was wrong — rooms never
overlap. The real cause is the wall zones and filled voids above.)

---

## Exclusions — two cases, one mechanism, two insertion points

The user gave one concrete case and one hypothetical; they are genuinely
different operations and compose differently up the chain. Model both as *where
in the two-stage pipeline the exclusion is applied*, so the union code stays a
dumb "dissolve these inputs" loop that never knows *why* an input is absent.

### Case A — exclude a whole group at a tier (the real one: outdoor areas)

Outdoor areas have their own department. The user wants them **out of the
building footprint** because they aren't part of it — but the outdoor department
still genuinely exists with its own area and its own plan view.

- **Applied at stage 2:** the outdoor group is computed normally, then
  **withheld from its parent's dissolve.**
- **Effect: bites at the tier where applied and every tier above.** Building no
  longer includes outdoor; outdoor's own department/sub-department footprints are
  **untouched**.
- The outdoor group is *real but categorically separate*, so the summary should
  still **show** it, visibly marked "not counted upward" — not vanish it. Same
  "surface the state as first-class" discipline as the `undefined` buckets and
  the validation report. This is a reporting variant worth building in: gross
  internal X / outdoor Y shown separately, **not summed** (and remember you can't
  sum them by subtracting a number anyway — see previous section).

### Case B — exclude specific rooms (the hypothetical)

Drop the room's loop **before it ever becomes geometry.**

- **Applied at stage 1:** the room never enters its group's union.
- **Effect: gone from every tier including its own lowest group** — the most
  destructive case, and it changes the bottom tier's own reported area, which
  Case A never does. The user flagged this asymmetry correctly.

### Settings shape

An exclusion is `{ tier, match, stage }` where the match is either a resolved
group (a tier code/value → Case A / stage 2) or individual rooms (a room id or
property → Case B / stage 1); the match kind implies the stage. Matching a group
reuses `classify_room`'s resolved path, so "exclude the outdoor department" is
expressed against the same tier values everything else resolves — no second
matching vocabulary.

Authored in the per-project TOML **beside `hierarchy`**, editable via
`settings.html`, added to `ProjectSettings` next to `hierarchy` /
`comparison_properties` — the same home as every other user-authored rule
(`colour_plans`, milestones). **Nothing about exclusions goes in the extractor**
(STRATEGY.md "Keep the extractor dumb on purpose").

---

## Endpoint & module shape

This is squarely the "Yes → own endpoint" case by STRATEGY-BROWSER.md's own test
(§ "Endpoints follow fetch lifecycle, not data type"): derived, more expensive
than a lookup, recomputed on a different trigger, consumed by a different view
than the room render. So:

- **`GET /projects/{id}/areas`** (name it for the noun, e.g. `areas` or
  `hierarchy-areas`) — **not** a field bolted onto `/rooms`.
- Returns, per tier per group: the dissolved MultiPolygon geometry (for the
  plan-view ask) **and** its measured area (for the table ask). The summary
  table is the same result *without* the geometry field — **one computation
  feeds both views, do not build two pipelines.** Respect existing query scoping
  (`?project=` / `?building=` / `?milestone=`) the way `/rooms` does; a milestone
  view reuses `assemble_rooms(.., Some(milestone))` for its room set exactly as
  `service::comparison` already does.
- New module **`service/areas.rs`** (transport-agnostic, never imports `axum` —
  CODING-CONVENTIONS.md "Dependency direction is the seam"), thin `handlers`
  adapter over it, same handler/service split as `rooms` / `validation` /
  `comparison`. If it can share the read logic, the MCP binary gets it for free
  the same way (STRATEGY-MCP.md).

---

## Browser (plan-view ask #1)

Mostly a viewer job and well inside SVG's comfort zone (STRATEGY-BROWSER.md
"Rendering: SVG today"). Server emits the MultiPolygon coordinates as data; the
viewer adds a mode toggle: draw per-tier dissolved polygons with the rooms below
ghosted or switched off. All client-side, same "axum stays a pure JSON API" line
that keeps CSV export and colour maths in the browser.

- Multipolygons with multiple exterior rings (islands) → multiple SVG shapes.
- Footprints are hole-free after stage 1, so `<polygon>` is enough and the
  even-odd `<path>` fill-rule dance is unnecessary — a small simplification the
  "discard holes" decision buys the front end for free.

---

## Naming / honesty (do not skip)

The number this produces is **aggregated room footprint**, wall-zone- and
filled-void-inclusive. It is *not* net room area and *not* a standards-based
gross (BOMA/IPMS). Name it so in the API field and the summary column so nobody
reads it as either. Consider having the summary report **both** the filled
footprint area *and* the summed net room area side by side — they now answer two
different questions, and their difference (wall zones + filled voids) is itself a
meaningful, legible number.

---

## Build order — start with the one risky piece, in isolation

The geometric risk is concentrated in stage 1. Slice it off first as a **pure
function** over `Vec<Room>` (or their loops) → group footprint MultiPolygon,
unit-tested inline (CODING-CONVENTIONS.md "Tests") with **no endpoint, no
settings, no browser** needed to prove it correct:

- Fixture: a square donut with a column-sized interior hole → assert the hole is
  gone and the exterior ring survives.
- Fixture: two disjoint room clusters in one group → assert **two** exterior
  rings survive (islands kept).
- Fixture: two adjacent rooms sharing a centreline edge → assert they dissolve to
  **one** ring (no sliver).

Only once that's green do the tier-dissolve loop, then exclusions (stage-2
withhold, then stage-1 room drop), then the endpoint, then the viewer mode. Each
layer is additive and independently testable.

### Dependency note

Needs a real geometry crate — do **not** hand-roll polygon union (holes, shared
vertices, collinear edges, Revit float noise are a genuine robustness trap). The
`geo` crate (`BooleanOps::union`, `MultiPolygon`, `Polygon::new(exterior,
interiors)`) is the standard fit and maps straight onto the existing
`loops[0]=outer, loops[1..]=holes` convention. It fetches fine under the current
network allowlist (`crates.io` / `static.crates.io` are allowed). `rayon` per
group/tier is available if measurement later shows it's warranted — but measure
first (STRATEGY.md "Parallelism has a threshold"): a few hundred rooms may be
faster single-threaded.

---

## Open questions to confirm before/while building

1. **Boundary location** — confirm the pyRevit extractor uses wall **centreline**
   (assumed). If it's finish-face, adjacent rooms float inside their walls and
   unions leave slivers everywhere; "gross footprint from union" then means
   something noticeably different and the naming caveats get sharper.
2. **Milestone/scoping parity** — does the areas endpoint need `?milestone=`
   from day one, or is "latest only" an acceptable first slice? (Reusing
   `assemble_rooms` makes milestone support nearly free, so probably include it.)
3. **Summary delivery** — is ask #2 a server-rendered stats page, or (consistent
   with the pure-JSON-API line) a browser view over the `/areas` JSON? The latter
   matches every existing precedent; confirm before anyone writes HTML server-side.
