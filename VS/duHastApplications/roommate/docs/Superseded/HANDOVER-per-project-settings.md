# HANDOVER: per-project settings

## Why

Today the server is booted with **one** TOML settings file (`--settings`) and
that single profile — `hierarchy`, `builtin_properties`, `room_label`,
`drofus_fields`, and the loaded dRofus dataset — is applied to **every** model,
regardless of which project it belongs to. Storage is already project-keyed and
happily accepts pushes for any project, but they all get classified/joined
through the one global profile.

The expected real-world usage is the opposite: **many people hit one central
server, each working on a different project**, and each project needs its own
classification rules and its own dRofus reference data. This doc describes
moving settings from **one-per-process** to **one-per-project**, staying on
hand-edited TOML.

## Guiding constraint

Stay with TOML. Settings remain **operator-provided files registered at
startup**, keyed by project id. Do **not** make settings something pushed or
stored alongside room data — that's a bigger, separate change. This keeps the
"settings are hand-edited TOML" model intact and is far less disruptive.

## What already makes this tractable

The architecture was written in anticipation of this (see the design note in
`STRATEGY-SERVER.md` about resolving hierarchy/properties per project in the
service layer rather than at startup):

- Settings-derived data lives as **read-only inputs on `AppState`**
  (`drofus`, `hierarchy`, `builtin_properties`, `room_label`, `drofus_fields`),
  never baked into the store, the contract, or the transport.
- The service layer already takes these as **plain arguments** off state:
  `classify_room(room, &state.hierarchy, source, &state.builtin_properties)`,
  `lookup_property(…, &state.builtin_properties)`, etc. It never reaches for a
  global.
- Storage (`storage.rs`) is already keyed by `(project_id, model_id)`
  independently of settings. **Do not touch it.**
- `assemble_rooms(state, project, building)` already receives the project id and
  already loops per-payload with `payload.project.id` in hand.

So this is a **focused refactor of load/registration + threading one more
argument through three service functions**, not a rewrite.

## Scope of change (do)

### 1. Introduce a per-project settings bundle

Create a struct bundling the five currently-flat read-only fields plus the
project's dRofus dataset:

```rust
pub struct ProjectSettings {
    pub drofus: Option<DrofusData>,
    pub hierarchy: Vec<HierarchyTier>,
    pub builtin_properties: Vec<BuiltinPropertyDef>,
    pub room_label: Vec<String>,
    pub drofus_fields: Vec<DrofusFieldConfig>,
}
```

`AppState` (in `state.rs`) changes from holding these five fields directly to
holding a registry:

```rust
pub struct AppState {
    store: Box<dyn SnapshotStore>,
    project_settings: HashMap<String, ProjectSettings>, // keyed by project id
    // consider a `default` / fallback bundle — see "Open decisions"
}
```

Add an accessor like `fn settings_for(&self, project_id: &str) -> Option<&ProjectSettings>`.

### 2. Load & register multiple settings files (`bootstrap.rs`)

`build_state` currently loads one file. It needs to load **N** project settings
files and register each under its project id. Two viable input shapes — pick one
in "Open decisions":

- a directory of `*.toml`, each carrying its own `project_id`, or
- a top-level "index" TOML listing `{ project_id, settings_path }` entries.

Each project's dRofus CSV is loaded per-project (so `load_drofus` runs once per
registered project), and `validate_drofus_fields` runs per-project against that
project's own labels — the same fail-fast discipline, just per bundle.

The store backend (`FsStore` vs `MemStore`) and the dev `test_data` seed stay
**server-wide**, not per-project — storage is one tree keyed by project id.

### 3. Thread the bundle through the service layer (`service/rooms.rs`)

The service functions must select the bundle by project instead of reading
`state.hierarchy` etc. directly:

- `assemble_room(state, room, source)` → needs the `ProjectSettings` for the
  owning payload's project. Simplest: pass `&ProjectSettings` in, so it stops
  reading `state.drofus` / `state.hierarchy` / `state.builtin_properties` /
  `state.room_label`.
- `assemble_rooms` already loops `for (key, payload) in &scoped` — look up
  `state.settings_for(&payload.project.id)` **inside the loop** and pass it to
  `assemble_room`, `classify_room`, and the building-filter's `classify_room`
  call (line ~198).

**The one subtlety — the unfiltered merge (`project: None`).** Today an
unscoped `/rooms` classifies every model with the single global profile. Once
settings are per-project, an unscoped merge must classify **each model with its
own project's bundle**. This is clean because the loop is already per-payload
with `payload.project.id` available — but every `state.<field>` read in that
loop becomes a `bundle.<field>` read on the per-payload bundle. Decide what
happens for a payload whose project has **no** registered settings (skip? empty
bundle? see "Open decisions").

### 4. Ingest registration check (`handlers.rs`, `ingest_rooms` + `ingest_rooms_stream`)

Currently ingest accepts any project blindly (schema-version check only, lines
~34–42). With per-project settings, decide whether a push for an **unregistered**
project should:

- **422 / 400** reject ("no settings configured for project X"), or
- **lazily accept** and store it (served with a fallback/empty bundle).

Put the check right after the schema-version check, before `set_snapshot`. Both
ingest handlers need it (the streaming one assembles its `RoomPayload` before
storing — add the check once the envelope's project id is known).

### 5. MCP binary (`bin/mcp.rs`)

**Free.** It reads the same `Shared` state through the same `service` functions,
so it inherits per-project resolution with no change beyond whatever the service
signatures become.

## Out of scope (do NOT touch)

- `storage.rs` / on-disk layout — already project-keyed.
- The JSON contract (`contract.rs`), `ModelKey`, `SUPPORTED_SCHEMA`.
- Level-dedup logic in `assemble_rooms`.
- Transport adapter response shapes.
- Settings-as-data (pushed/stored settings) — explicitly deferred.

## Open decisions (resolve before/while coding)

1. **Multi-file input shape**: directory-of-tomls vs an index toml. Directory
   is simpler operationally; index gives explicit project→file mapping. The CLI
   `--settings` currently takes one `PathBuf` (`main.rs` `Args`, and `mcp.rs`'s
   own arg parser) — whichever shape you pick, update **both** binaries' arg
   parsing, since `build_state` is shared.
2. **Unregistered project on read**: skip that payload from the merge, or serve
   it through an empty/default bundle (rooms present but unclassified, no dRofus).
   Skipping is cleaner; empty-bundle is more forgiving.
3. **Unregistered project on ingest**: reject (422) vs lazily accept. Rejecting
   pairs naturally with "skip on read"; lazy-accept pairs with "empty bundle".
   Pick one policy and apply it consistently on both axes.
4. **Fallback/default bundle**: whether to keep a server-wide default profile
   for unregistered projects at all. If yes, `AppState` holds an
   `Option<ProjectSettings>` default alongside the map.

## Suggested order of work

1. `ProjectSettings` struct + `AppState` registry + `settings_for` accessor
   (mechanical; keep the old five-arg `AppState::new` shape working for tests or
   update the tests in the same pass — `rooms.rs` and `handlers.rs` test modules
   both call `AppState::new` with the five fields).
2. `bootstrap.rs` multi-file load + per-project dRofus load/validate.
3. Thread bundle through `service/rooms.rs` (`assemble_room`, `assemble_rooms`,
   both `classify_room` sites, `resolve_label_fields`).
4. Ingest registration policy in both `handlers.rs` ingest paths.
5. CLI arg update in `main.rs` and `bin/mcp.rs`.
6. Update tests (the `AppState::new` call sites in `rooms.rs`, `handlers.rs`,
   `storage.rs` test modules).

## Rough sizing

A few days of careful work with test updates. The bulk of the effort is in
load/registration (step 2) and per-project dRofus loading; the service-layer
threading (step 3) is largely mechanical because the per-payload loop already
exists. No storage, contract, or transport-shape changes.
