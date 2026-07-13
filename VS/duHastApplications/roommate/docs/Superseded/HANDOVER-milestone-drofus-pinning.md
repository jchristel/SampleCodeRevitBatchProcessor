# HANDOVER — Pinning dRofus snapshots to milestones

## What this is

Milestones already pin **model** snapshots: a named date carries an
`attachments` map (`model id → snapshot taken_at`), and `/rooms?milestone=`
serves each pinned model's *pinned* snapshot instead of its latest push. This
task closes the one documented gap in that feature: the dRofus data joined onto
a milestone view is still the project's **current** CSV, not the CSV as it stood
at the milestone. dRofus snapshots now exist in the store — they're just not
pinnable yet.

The strategy docs already call this out as the deferred slot:

- `STRATEGY-SERVER.md`, Deferred: *"milestone pinning of dRofus snapshots (the
  snapshots themselves now exist … but `attachments` still pins only model
  snapshots and the milestone view still joins the current dRofus)."*
- `settings.rs`, `Milestone` doc comment: *"dRofus is deliberately NOT pinnable
  yet … when it becomes an uploaded, snapshotted source … its pins join
  `attachments` without a redesign; that's the slot future sources fill."*

dRofus is now exactly that uploaded, snapshotted source. This is the promised
"join without a redesign."

## The shape of the change

Two independent moving parts, then the wiring:

1. **A milestone needs to record a dRofus pin.** Today `attachments` is a flat
   `model id → taken_at`. dRofus is project-scoped, not per-model, so it can't
   just be another entry in that map without colliding with a model whose id
   happened to equal a reserved word. Add a **separate, optional** field.
2. **`assemble_rooms` must join the pinned dRofus CSV**, not `bundle.drofus`.
   Right now `assemble_room` reads `bundle.drofus` unconditionally. Under an
   active milestone with a dRofus pin, it must instead load that snapshot's CSV
   from the store, parse it, and join against *that*.
3. **Read-path plumbing** so the resolved dRofus dataset flows from
   `assemble_rooms` down into `assemble_room`.

Everything else — level dedup, the building filter, classification — already
composes because the milestone substitution happens *before* those steps and
this change stays on the same seam.

## Step 1 — the settings field

In `settings.rs`, `struct Milestone` currently has `name`, `date`,
`attachments`. Add:

```rust
/// Optional dRofus snapshot pinned to this milestone: the `taken_at` id of
/// one uploaded dRofus CSV in the store, joined onto this milestone's rooms
/// instead of the project's current dRofus data. `None` (the common case,
/// and every milestone authored before this field existed) means the
/// milestone view keeps joining the *current* dRofus — the pre-pinning
/// behaviour, unchanged. dRofus is project-scoped, so this is a single id,
/// not a per-model map like `attachments`.
///
/// Like an `attachments` pin, existence of the snapshot is a read-time
/// concern (skip + warn, fall back to current), NOT validated here — settings
/// can't see the store. Its *shape* (a valid RFC3339-UTC snapshot id) is
/// validated in `validate()` below, same as an `attachments` value.
#[serde(default, skip_serializing_if = "Option::is_none")]
pub drofus_snapshot: Option<String>,
```

Then extend `Milestone::validate()`. It already loops `attachments` values
through `contract::validate_snapshot_id` (or whatever the existing per-pin
check is — confirm against the current body, the test
`test_milestone_validate` exercises it). Add the same check for
`drofus_snapshot` when `Some`:

```rust
if let Some(id) = &self.drofus_snapshot {
    // Same rule as an attachments pin: a valid RFC3339-UTC snapshot id.
    // Existence is not checkable here (settings can't see storage).
    crate::contract::validate_snapshot_id(id)
        .with_context(|| format!("milestone '{}' has an invalid drofus_snapshot id", self.name))?;
}
```

**Watch the TOML footgun** documented in `STRATEGY-SERVER.md` (the
`room_label` note): `drofus_snapshot` is a scalar key on a `[[milestones]]`
table entry, so it must sit *under* its `[[milestones]]` header alongside
`name`/`date`, before any nested `[milestones.attachments]` sub-table opens.
A `[[milestones]]` entry in TOML looks like:

```toml
[[milestones]]
name = "Design Freeze"
date = "2026-06-30"
drofus_snapshot = "2026-06-29T17:00:00Z"   # <-- new, a bare scalar, before attachments

[milestones.attachments]
"model-guid-A" = "2026-06-29T09:00:00Z"
```

## Step 2 — propagate the field through the runtime bundle

`Milestone` is carried verbatim into `ProjectSettings.milestones` in
`bootstrap::load_project_bundle` (`milestones: settings.milestones`), so the
new field rides along for free — no bootstrap change. Confirm nothing
constructs `Milestone { .. }` with all fields named positionally that would now
fail to compile; the test helpers in `milestones.rs`, `rooms.rs`, and
`settings.rs` build `Milestone` with explicit fields, so add
`drofus_snapshot: None` (or `..Default::default()` if you give it a `Default`)
to each. Grep for `Milestone {` across the crate and the tests.

## Step 3 — join the pinned dRofus in `assemble_rooms`

This is the substance. In `rooms.rs`, `assemble_rooms` currently, under a
milestone filter, replaces each model's latest payload with the pinned
snapshot, then falls through to the shared loop that calls `assemble_room`.
`assemble_room` reads `bundle.drofus` directly.

The join needs to read a *different* `DrofusData` for the milestone-pinned
case. The cleanest seam that respects the existing "resolve once per request"
discipline:

- Resolve the effective `DrofusData` for the milestone **once**, up front,
  right where the milestone is matched (the `Some(wanted) => { … }` arm that
  already looks up `ms`). A milestone is project-scoped and one request is one
  project's worth of milestone, so this is a single resolution, not per-model.
- Thread that resolved data down to `assemble_room` as an override.

Concretely:

**(a)** Give `assemble_room` an explicit dRofus argument instead of reading
`bundle.drofus` itself:

```rust
fn assemble_room(
    bundle: &ProjectSettings,
    drofus: Option<&DrofusData>,   // was: read bundle.drofus inside
    room: &Room,
    source: &str,
) -> RoomResponse {
    let drofus = drofus.and_then(|d| {
        lookup_property(room, &d.link_property, source, &bundle.builtin_properties)
            .and_then(|key| d.by_id.get(&key).cloned())
    });
    // classification + label unchanged
    ...
}
```

The default (non-milestone) call passes `bundle.drofus.as_ref()` — identical
behaviour to today.

**(b)** In `assemble_rooms`, compute the milestone dRofus override once. When a
milestone is active and defines a `drofus_snapshot`, load + parse that CSV;
otherwise the override is just `bundle.drofus`. Load through the same
store method the dRofus read side already uses — `state.get_drofus(project_id,
taken_at)` returns `Option<Vec<u8>>` — and parse with
`drofus::load_drofus_from_bytes` (the exact function `bootstrap` uses to
hydrate an upload; it strips the BOM). A pin whose snapshot is missing or
fails to parse **skips + warns and falls back to the current dRofus**, matching
the dangling-`attachments`-pin stance ("a signal, not an error").

Because the override is per-milestone (project-scoped) but the assembly loop is
per-model, resolve it into a variable the loop closes over. Rough sketch,
slotting into the existing milestone arm and loop:

```rust
// Resolved once: the DrofusData a milestone view should join against.
// Owned, because a parsed pinned CSV is a fresh value with no home in the
// bundle. `None` here means "no dRofus at all" (project has none configured);
// Some(Owned)/Some(borrowed-from-bundle) both flow to assemble_room as &.
let mut milestone_drofus: Option<DrofusData> = None;   // only set when a pin resolves

if let Some(wanted) = milestone {
    // (inside the existing `find(|m| m.name == wanted)` success path,
    //  where you already have `ms`)
    if let Some(pin) = &ms.drofus_snapshot {
        match state.get_drofus(&payload.project.id, pin).map_err(ServiceError::Internal)? {
            Some(bytes) => match crate::drofus::load_drofus_from_bytes(&bytes) {
                Ok(data) => milestone_drofus = Some(data),
                Err(e) => tracing::warn!(
                    "milestone '{}' pins dRofus snapshot {:?} for project {}, but it failed to parse ({e:#}) — falling back to current dRofus",
                    wanted, pin, payload.project.id
                ),
            },
            None => tracing::warn!(
                "milestone '{}' pins dRofus snapshot {:?} for project {}, but no such snapshot exists — falling back to current dRofus",
                wanted, pin, payload.project.id
            ),
        }
    }
}
```

Then at the `assemble_room` call site in the loop, pick the override when set,
else the bundle's own:

```rust
let effective_drofus = milestone_drofus.as_ref().or(bundle.drofus.as_ref());
// ...
let mut response = assemble_room(bundle, effective_drofus, room, &payload.model.source);
```

**Scoping caveat to get right:** `assemble_rooms` already handles multiple
projects in one unscoped merge (each payload carries its own `bundle`). A
milestone `drofus_snapshot` belongs to one project. If you resolve
`milestone_drofus` in the per-payload loop that builds `scoped`, key it per
project (e.g. a `BTreeMap<String, DrofusData>` project_id → resolved data, or
resolve lazily per project) so project A's pinned dRofus never leaks onto
project B's rooms. The single-project case (`/rooms?project=…&milestone=…`,
the realistic milestone call) is the simple one; don't let the multi-project
merge path silently cross-join. Simplest safe structure: resolve the override
inside the final assembly loop keyed on `payload.project.id`, memoised, rather
than a single top-level `Option`.

## Step 4 — the join is read-only, so nothing else moves

- **Validation report** (`service::validation`) stays latest-based, exactly as
  the milestone view's model side already does. Do **not** wire the pinned
  dRofus into `compute_validation` in this task — `STRATEGY-SERVER.md` lists
  the latest-based validation report as a deliberate v1 milestone limit, and
  the validation path resolves its own dRofus link independently (the
  "deferred gap" noted in the Service layer bullet). Leave it.
- **No schema bump.** This is settings-file surface, not the wire contract
  (`schema_version` 5). A milestone without `drofus_snapshot` means exactly
  what it meant before, so every existing project file stays valid — same
  "pure relaxation, not a bump" reasoning as the omittable-snapshot change.
- **Settings UI** (`static/settings.html` + `settings_api.rs`): the milestone
  editor round-trips `Milestone` as JSON. Because `drofus_snapshot` is
  `#[serde(default, skip_serializing_if = "Option::is_none")]`, the API keeps
  working untouched; a nice-to-have (not required for this task) is a dropdown
  populated from `GET /projects/{id}/drofus/snapshots` so an author picks a
  real id instead of typing one. Flag it as follow-up if you don't build it.

## Tests to add

Mirror the existing milestone tests in `rooms.rs`
(`test_assemble_rooms_milestone_serves_pinned_snapshot` is the template — it
uses `FsStore` because pinning to history needs a store that keeps history):

1. **Pinned dRofus is joined.** Upload two dRofus CSVs (old + new) via
   `store.put_drofus`, differing in one field value for the same link id. Pin
   the milestone's model snapshot AND set `drofus_snapshot` to the *old* CSV's
   id. Assert the milestone view's room carries the **old** dRofus field value
   while the default view carries the **new** one. This is the whole feature in
   one test.
2. **Missing dRofus pin falls back, doesn't error.** Set `drofus_snapshot` to
   an id that was never uploaded. Assert the milestone view still returns rooms
   (joined against current dRofus), i.e. `Ok(Some(..))` with the room present —
   the skip-and-warn path, parallel to
   `test_assemble_rooms_milestone_excludes_unpinned_and_unknown`'s dangling-pin
   stance but falling back rather than dropping (dRofus is a join, not the room
   itself).
3. **No dRofus pin = current behaviour.** A milestone with model pins but no
   `drofus_snapshot` joins the current dRofus — guards the default path.
4. **`Milestone::validate` rejects a malformed `drofus_snapshot`.** Extend
   `test_milestone_validate` in `settings.rs`: a non-RFC3339 `drofus_snapshot`
   fails, a valid one passes.
5. **Multi-project isolation** (if you took the merge path): project A's pinned
   dRofus does not appear on project B's rooms in an unscoped
   `?milestone=`-only merge.

## Files you'll touch

- `settings.rs` — `Milestone` field + `validate()` + test.
- `rooms.rs` — `assemble_room` signature, `assemble_rooms` override
  resolution, tests. **The core of the change.**
- Test helpers constructing `Milestone { .. }` in `milestones.rs`, `rooms.rs`,
  `settings.rs` — add the new field.
- `settings.html` / `settings_api.rs` — only if you build the picker dropdown
  (optional).
- `STRATEGY-SERVER.md` — move the "milestone pinning of dRofus snapshots" line
  out of **Deferred** into the Milestones bullet as shipped; update the
  Milestones bullet's "two deliberate v1 limits" to note the dRofus pin now
  exists (validation staying latest-based remains the one carried-over limit).
- `settings.rs` `Milestone` doc comment — it currently says dRofus is "NOT
  pinnable yet"; rewrite to describe the shipped pin.

## The one thing not to get wrong

The whole design intent (per both strategy docs) is that milestone substitution
happens **before** the join/classify/filter steps so they compose unchanged.
Keep the dRofus override on that same seam: resolve *which* `DrofusData` to use
up front, then let the existing assembly run. Don't reach into classification
or the building filter — they neither know nor care which dRofus snapshot fed
the join. If you find yourself special-casing a downstream step for milestones,
step back: the substitution should have already made that step's input correct.
