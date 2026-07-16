# Handover: Milestone Comparison Feature

## ⚠️ Read this first — code freshness

**The Rust code uploaded to this project is slightly out of date.** Whatever
source you (Claude Desktop) can see in the live workspace is the **current,
authoritative** version. Where the project-uploaded files and the live
workspace disagree, **the live workspace wins** — trust what's in front of you,
not the snapshot captured in this project. This handover describes *intent and
design*, not exact line numbers; verify signatures and module layout against
the live tree before editing.

---

## What we're building

The ability to **compare N milestones**. One milestone is chosen as the
**baseline**; every other selected milestone is compared against it. The output
is a *star*, not a mesh: baseline-vs-each-other, never all-pairs.

The report must cover, per compared milestone:
- **Rooms added / removed** relative to the baseline.
- **Property differences** on rooms present in both, over a **user-defined,
  persisted** set of properties.

### The room-linking key is user-defined AND optional

Rooms are matched across milestones by a **unique id field that the user
identifies**. This is the single most important thing to get right:

- **This key is its own concept — it is NOT the dRofus link property.** dRofus
  reconciliation has `link_property`, but that exists to join dRofus reference
  rows onto rooms. Milestone comparison needs its *own* user-chosen id
  property. Do not reach for `bundle.drofus...link_property` to satisfy this.
- **dRofus is optional in this context, so a unique id may not be defined at
  all.** A project may use milestone comparison with no dRofus configured
  whatsoever. The feature must stand entirely on its own. Design for the case
  where dRofus is absent as the *normal* case, not an edge case.
- Because the id is user-defined and optional, the comparison config must carry
  its **own** "which property is the link key" setting, separate from anything
  dRofus-related. When that setting is **unset**, the feature has no way to
  match rooms across milestones — handle this explicitly (a clear "no
  comparison key configured" state), don't silently fall back to dRofus or to
  room `id`.

### Property comparison rules

- The comparable property set is **user-defined** and **persistent** (chosen at
  export time, saved so it survives). It lives in **settings**, not storage —
  same home and lifecycle as `room_label` / `drofus_fields` / `milestones`,
  which buys validation + atomic save + hot-reload + the settings API for free.
- **Only properties that exist on the baseline may be compared.** Enumerate the
  property set from the **baseline's** rooms.
- If a comparable property is **missing from another milestone**, mark it as
  **`missing property`** (a distinct sentinel state), rather than treating it as
  a value difference.

---

## How this maps onto the existing code (verify against live tree)

Most machinery already exists — this feature is largely a **new consumer** of
two things that are already built. Reuse, don't reinvent.

1. **Milestone → resolved rooms** is already done by `assemble_rooms(state,
   project, building, milestone)` in `service/rooms.rs`. Given a milestone
   name, it resolves the pinned per-model snapshots and returns fully-joined
   `RoomResponse`s. Call it once per milestone (baseline + each other) and you
   have every milestone's room set with no new resolution logic. (dRofus join
   inside it is already optional and degrades to "not joined" — consistent with
   dRofus being optional here.)

2. **Property comparison** already exists in `service/validation.rs` (Revit vs
   dRofus). It has numeric-adaptive comparison, typed date comparison, an
   `exact` override, and presence-awareness. The milestone comparison is the
   *same comparison problem with a different pair of sides* (baseline value vs
   other-milestone value). Reuse its comparison helpers; do not write a second
   numeric/date comparator.

3. **Presence / "missing property"** — `property_presence` /
   `PropertyPresence` (Absent / Empty / Present) in `contract.rs` already
   encodes exactly the distinction you need. `Absent` on the other-milestone
   side is your **`missing property`** signal.

4. **Reading a property by name** — use `lookup_property` (in `contract.rs`) for
   the user-defined comparison key and for each comparable property, so a
   second source or a renamed property needs no change here.

5. **Added / removed rooms** — build a `BTreeSet` of the user-defined key values
   for baseline and for each other milestone, then diff the sets. This mirrors
   how `rooms_unmatched_in_drofus` is derived in `validation.rs`.

6. **Duplicate keys** — because the link key is user-chosen, two rooms may share
   a value. That makes the diff ambiguous. Guard it the same way
   `validation.rs` guards ambiguous dRofus keys (`DuplicateLinkValue`): exclude
   duplicated keys from the added/removed/changed logic and report them
   separately. This matters *more* here than in the dRofus path, because the key
   is arbitrary user config with no uniqueness guarantee.

### Suggested shape (confirm names against live code)

- New module `service/comparison.rs`, registered in `service/mod.rs` beside
  `validation`.
- A transport-agnostic core function, roughly:
  `compare_milestones(state, project, baseline: &str, others: &[String]) -> Result<ComparisonResponse, ServiceError>`
  — reading the comparable-property list and the user-defined link-key property
  from the project's settings bundle, not from arguments, since both are
  persisted config.
- Response as `Vec<MilestoneComparison>` (one entry per *other* milestone), each
  carrying `rooms_added`, `rooms_removed`, `property_differences`, plus a
  `missing_properties` / `missing property` marker per property, plus any
  `duplicate_key_values` guard list.
- A top-level "no comparison key configured" state for the dRofus-absent /
  key-unset case.

### Settings addition

Add the two persisted pieces to the per-project settings (`settings.rs`), each
`#[serde(default)]` so existing project files stay valid:
- the **comparison link-key property name** (optional — `Option<String>`,
  reflecting that it may be undefined), and
- the **ordered list of comparable property names**.

Follow the `drofus_fields` precedent for validation-at-load if any is warranted,
though "absence is fine" is the house style — an unresolvable property name
should contribute nothing rather than fail.

### Wiring

Add one HTTP handler (`handlers.rs`) and one MCP tool (`mcp.rs`), each a thin
adapter over the new service function — the same one-function-per-route pattern
every existing read route follows. Keep transport types out of
`service/comparison.rs`.

### Client

A separate client view is appropriate (parallels the settings page precedent):
pick baseline (radio) + others (checkboxes), edit the comparable-property list
and the link-key property, persist those via `settings_api.rs`, then call the
comparison endpoint. Surface the "no comparison key configured" state plainly,
since with dRofus optional it's a real, reachable state.

---

## Guardrails / house style to preserve

- Domain logic in `service/*` imports **no transport crate** (no `axum`, no
  `rmcp`, no `StatusCode`). `ServiceError` is the seam.
- Unknown/unregistered project → **soft empty success**, not an error (same as
  every other listing).
- Derived data (joins, comparisons) is assembled at response time and **never
  written back** into stored snapshots.
- Heavily annotate new Rust, matching the existing modules' comment density and
  "explain the reasoning, not just the rule" tone.
