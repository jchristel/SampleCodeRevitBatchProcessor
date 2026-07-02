# Implementation Handoff — Steps 1–3 (properties, dRofus, classification)

**For:** Claude desktop, implementing against the existing `roommate` server
(`main.rs`, `Cargo.toml`, `index.html`).
**Source of truth:** STRATEGY.md "Next steps (committed order)". This doc is the
build order and the concrete shapes; STRATEGY.md holds the *why* for every call.

**Overall arc.** Three moves, in order, each depending on the one before:

1. **Room properties contract (v2 → v3).** Add an always-present properties block
   to every room: a typed built-in tier + an open custom-param bag.
2. **dRofus loader.** Read a two-header-row CSV at startup, key it, attach a
   `drofus` sub-object per room at `/rooms` assembly.
3. **Room classification hierarchy.** An n-tier `[[hierarchy]]` settings section
   that groups rooms by their property values, with `undefined`-fill for partial
   classification.

Steps 2 and 3 both read fields out of the step-1 properties block, so **do step 1
first** and don't shortcut it.

All three are **test implementations, no UI.** The viewer (`index.html`) keeps
working unchanged against `/rooms`; nothing here requires a front-end change.
Verify each step server-side (unit tests + a curl/POST round-trip) before moving
on.

---

## Ground rules that apply to all three

- **Keep the annotated style.** `main.rs` documents *why* on each type and
  function, not just *what*. Match it — the whole project's value is that the
  reasoning travels with the code.
- **Everything new is config-resolved at startup**, parsed from the TOML settings
  file, held in `AppState`. Fail fast on bad config (the `load_settings`
  contract already does this).
- **Store raw, derive late.** dRofus join and classification resolution happen at
  response assembly / on demand, not at load. `/rooms` stays the raw-geometry
  endpoint; the stored snapshot is never mutated by a join.
- **Ids are strings, always.** Revit `ElementId` is 64-bit; never parse an id to
  a machine int unless you explicitly need the number, and then use `i64`. This
  is a contract invariant, not a step-1-only concern.

---

## Step 1 — Room properties contract (v2 → v3)

### Goal

Every `Room` carries a `properties` block that is **always present** (not
`Option`), with two clearly separated tiers so no consumer branches on presence
and no consumer has to guess which tier a field lives in.

### Types

```rust
use std::collections::BTreeMap;

/// Everything known about a room's properties, split into two tiers.
/// ALWAYS present on a Room (never Option): the block is guaranteed, even when
/// `custom` is empty. Consumers read it without a presence check.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct RoomProperties {
    /// Revit built-ins — guaranteed to exist because Revit builds them in.
    /// Typed struct: the extractor can rely on these, so they get real fields.
    builtin: BuiltinProperties,

    /// Project-varying params (shared/project params). Shape is unknown at
    /// compile time, so an open bag. `#[serde(default)]` → an older/sparse
    /// payload deserializes to empty rather than failing.
    #[serde(default)]
    custom: BTreeMap<String, CustomValue>,
}

/// Built-in Revit properties. Add fields here as the extractor learns to send
/// them; each is a guaranteed value, not an Option, because Revit provides it.
/// NOTE: `id` / `name` / `level_id` stay on `Room` itself (they already exist
/// and the viewer reads them there) — this struct is for the *additional*
/// built-ins (number, area, perimeter, etc.) as they come online.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct BuiltinProperties {
    /// Room number as Revit reports it (distinct from the display name).
    #[serde(default)]
    number: String,
    /// Placed area, raw as extracted (units per the contract; not recomputed).
    #[serde(default)]
    area: f64,
    // Extend as the extractor sends more. Keep them raw — no derived fields.
}

/// One custom property: the raw string value plus an optional storage-type
/// HINT from Revit. Paired in one struct (not two parallel maps) so value and
/// type can't drift and an absent type degrades to "treat as string".
#[derive(Debug, Clone, Serialize, Deserialize)]
struct CustomValue {
    /// Raw value, always a string. Revit hands most params back as strings;
    /// any typing is deferred and done server-side, lazily.
    value: String,

    /// Revit's declared StorageType, forwarded as guidance only:
    /// "string" | "integer" | "double" | "elementid". Optional — absent means
    /// "treat as string". This is a HINT: declared type and parseable content
    /// can disagree (a String param holding "12.5", an empty Double), so any
    /// coercion keyed off it must fall back to `value` on failure.
    #[serde(default)]
    storage_type: Option<String>,
}
```

Wire it into the existing `Room`:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Room {
    id: String,
    name: String,
    level_id: String,
    loops: Vec<Loop>,

    /// Always present (see RoomProperties). `#[serde(default)]` lets a v2-shaped
    /// payload (no properties block) still deserialize, landing an empty block.
    #[serde(default)]
    properties: RoomProperties,
}
```

### Schema version

- Bump `const SUPPORTED_SCHEMA: u32 = 2;` → `3`.
- `ingest_rooms` already returns HTTP 422 on a version it doesn't speak — that
  behaviour is exactly what we want, so an old v2 producer fails loud, not
  silent. Leave that check as-is; just change the constant.
- **Decision to confirm with the developer:** do you want the server to also
  *accept* v2 (properties defaulted empty) during transition, or hard-require v3?
  The `#[serde(default)]` on `properties` makes v2 payloads deserializable, but
  the `SUPPORTED_SCHEMA` equality check will still 422 them. If a transition
  window is wanted, relax the check to `payload.schema_version > 3` (or a
  `2..=3` range). Default assumption: **hard-require v3** — simplest, loudest.

### Coercion helper (lazy, server-side)

Don't coerce at load. Provide a helper consumers call when they actually need a
typed read, so the raw string stays the source of truth:

```rust
impl CustomValue {
    /// Best-effort typed read guided by the storage-type hint, falling back to
    /// the raw string's natural parse, and never panicking. Returns None only
    /// when nothing sensible can be produced. Callers that just want the string
    /// read `.value` directly and ignore this.
    fn as_f64(&self) -> Option<f64> {
        // Hint steers intent, but content wins: try to parse regardless, since
        // the declared type can lie. This is deliberately forgiving.
        self.value.trim().parse::<f64>().ok()
    }
}
```

Keep this minimal for now — add typed accessors only as a consumer needs them.

### Verify

- Unit test: a v3 payload with a room carrying `builtin` + two `custom` entries
  round-trips through serde.
- Unit test: a v2-shaped room JSON (no `properties`) deserializes to an empty
  block (proves `#[serde(default)]` wiring), independent of whether the version
  check accepts it.
- Round-trip: POST a v3 snapshot, GET `/rooms`, confirm the block survives.

---

## Step 2 — dRofus loader (two-header-row CSV → keyed map → `drofus` sub-object)

### Goal

At startup, read the dRofus CSV named by `[sources.drofus]`, build a
`Map<String, DrofusRecord>` keyed by the dRofus id, hold it in `AppState`. At
`/rooms` assembly, attach a **separate `drofus` sub-object** to each room whose
linking property value hits the map. Never merge into `properties`; never mutate
the stored snapshot.

### CSV shape (recap)

```
DrofusRoomId,   NetArea,     Department,  ...   ← row 1: dRofus field names (labels)
RevitDrofusKey, d_net_area,  d_dept,      ...   ← row 2: matching Revit param names
<key value>,    <value>,     <value>,     ...   ← row 3+: data rows
```

- **Row 2, column 0** = the name of the Revit room property whose *value* is the
  dRofus id. This is the link. Read once; constant for the whole file.
- **Row 1** = dRofus field labels (for display). **Row 2 (cols 1+)** = the Revit
  param names those fields map to (kept for reconciliation).
- Link is a **direct value match**, dRofus ids are **unique** → flat map, one
  record per id, no collision handling.

### Dependency setup

Add a CSV reader to `Cargo.toml`:

```toml
csv = "1"
```

### Types + loader

```rust
use std::collections::BTreeMap;

/// One dRofus row, resolved. `fields` is dRofus-field-label → value (row 1
/// labels as keys). Kept as strings — same raw discipline as custom props.
#[derive(Debug, Clone, Serialize)]
struct DrofusRecord {
    fields: BTreeMap<String, String>,
}

/// The whole dRofus dataset, resolved once at startup.
struct DrofusData {
    /// Which Revit room property holds the linking id (row 2, col 0).
    /// Read the room's property of THIS name to get its dRofus key.
    link_property: String,

    /// dRofus id → record. Direct value match; ids unique, so a plain map.
    by_id: BTreeMap<String, DrofusRecord>,
}

/// Read the two-header-row CSV into DrofusData. Fail fast (startup) on a
/// malformed file — same contract as load_settings.
fn load_drofus(source: &DrofusSource) -> anyhow::Result<DrofusData> {
    let DrofusSource::File { path } = source; // only variant today
    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(false) // BOTH header rows are data to us; we parse them by hand
        .from_path(path)
        .with_context(|| format!("could not open dRofus CSV: {}", path.display()))?;

    let mut records = rdr.records();

    // Row 1: dRofus field labels.
    let labels = records
        .next()
        .context("dRofus CSV missing row 1 (field labels)")??;
    // Row 2: Revit param names. Col 0 is the link property.
    let revit_names = records
        .next()
        .context("dRofus CSV missing row 2 (Revit param names)")??;

    let link_property = revit_names
        .get(0)
        .context("dRofus CSV row 2 col 0 (link property) is empty")?
        .to_string();

    // Data rows: col 0 is the dRofus id (the key), cols 1+ are values keyed by
    // the row-1 label at the same column index.
    let mut by_id = BTreeMap::new();
    for row in records {
        let row = row?;
        let id = match row.get(0) {
            Some(id) if !id.is_empty() => id.to_string(),
            _ => continue, // skip blank-key rows rather than fail the whole load
        };
        let mut fields = BTreeMap::new();
        for col in 1..labels.len() {
            if let (Some(label), Some(val)) = (labels.get(col), row.get(col)) {
                fields.insert(label.to_string(), val.to_string());
            }
        }
        by_id.insert(id, DrofusRecord { fields });
    }

    tracing::info!(
        "loaded {} dRofus record(s); link property = {}",
        by_id.len(),
        link_property
    );
    Ok(DrofusData { link_property, by_id })
}
```

### AppState wiring

`AppState` currently holds `drofus: Option<DrofusSource>`. Replace the *source*
with the *resolved data* — the source has done its job once loaded:

```rust
struct AppState {
    latest: Mutex<Option<RoomPayload>>,

    /// Resolved dRofus data, loaded once at startup. `Option` because a config
    /// could omit the source later; today it's always Some.
    drofus: Option<DrofusData>,
}
```

In `main`, load before building state:

```rust
let Settings { sources, test_data, hierarchy } = settings; // hierarchy from step 3
let drofus = load_drofus(&sources.drofus)?;                 // fail fast at startup
let state: Shared = Arc::new(AppState::new(drofus));
```

### Join at `/rooms` assembly (NOT at load)

`get_rooms` currently clones and returns the stored payload. Change it to build a
*response* that layers dRofus on top, leaving the stored snapshot untouched:

```rust
/// A room as sent to the viewer: the stored room plus any attached dRofus data.
/// Separate response type so the join never mutates the stored snapshot, and so
/// dRofus stays a distinct sub-object (its own lifecycle — it will later refresh
/// on its own trigger, so it must not be fused into the room's own properties).
#[derive(Serialize)]
struct RoomResponse {
    #[serde(flatten)]
    room: Room,
    /// Present only when the room's link value matched a dRofus record.
    /// Absent (skipped) otherwise — an unmatched key is a signal, not an error.
    #[serde(skip_serializing_if = "Option::is_none")]
    drofus: Option<DrofusRecord>,
}

async fn get_rooms(State(state): State<Shared>) -> Result<Json<serde_json::Value>, StatusCode> {
    let payload = match state.latest.lock().unwrap().clone() {
        Some(p) => p,
        None => return Err(StatusCode::NO_CONTENT),
    };

    let rooms: Vec<RoomResponse> = payload
        .rooms
        .iter()
        .map(|room| {
            let drofus = state.drofus.as_ref().and_then(|d| {
                // Read the linking property off the room's custom bag (or
                // built-ins, depending on where the project put it — see note).
                let key = room.properties.custom.get(&d.link_property).map(|v| &v.value);
                key.and_then(|k| d.by_id.get(k)).cloned()
            });
            RoomResponse { room: room.clone(), drofus }
        })
        .collect();

    // Re-emit levels + rooms; keep schema_version so the viewer's check holds.
    Ok(Json(serde_json::json!({
        "schema_version": payload.schema_version,
        "levels": payload.levels,
        "rooms": rooms,
    })))
}
```

**Note on where the link property lives.** The linking property might be a
custom param *or* a built-in (STRATEGY.md step 1). The snippet above reads
`custom` only; if the project's key is a built-in, add a small resolver that
checks built-ins first, then custom, by property name. Confirm with the
developer which tier holds the key for the test dataset and make the lookup
handle both.

### Verify

- Unit test `load_drofus` against a small fixture CSV: correct `link_property`,
  correct record count, a spot-checked record's fields.
- Round-trip: seed a snapshot (via `test_data`) whose rooms carry the link
  property, GET `/rooms`, confirm matched rooms show a `drofus` object and
  unmatched rooms omit it.
- Confirm the stored snapshot is unchanged after a GET (join is response-only).

---

## Step 3 — Room classification hierarchy

### Goal

An **n-tier** classification (e.g. Building → Department → Sub-department →
Functional Group) defined in the settings file as an ordered `[[hierarchy]]`
array. Load + validate at startup. Resolve each room to a **full-depth path**
where missing tiers are an explicit `undefined` (not a truncated path, not a
dropped room). No endpoint yet — resolve in memory; a `/hierarchy` endpoint comes
with the UI.

### Settings shape

```toml
# Own top-level section — NOT under [sources]. A source supplies values; this
# defines structure over values already on the room. Array-of-tables so tier
# ORDER is encoded for free: outermost (Building) first.
[[hierarchy]]
name = "Building"
code_property = "d_building_code"
name_property = "d_building_name"

[[hierarchy]]
name = "Department"
code_property = "d_dept_code"
name_property = "d_dept_name"
# ... n tiers deep
```

Per-project: the server is already started with a specific `--settings <path>`,
so a different project is just a different settings file. No mechanism change.

### Types + validation

```rust
/// One tier of the classification hierarchy. A tier is keyed by a code and/or a
/// name property — at least one must be present (validated at startup), since a
/// tier naming neither is unkeyable.
#[derive(Debug, Clone, Deserialize)]
struct HierarchyTier {
    /// Human label for the tier ("Building", "Department").
    name: String,
    /// Room property holding this tier's code. Optional per-tier.
    #[serde(default)]
    code_property: Option<String>,
    /// Room property holding this tier's display name. Optional per-tier.
    #[serde(default)]
    name_property: Option<String>,
}

impl HierarchyTier {
    /// A tier must name at least one property or it can't be keyed.
    fn validate(&self) -> anyhow::Result<()> {
        if self.code_property.is_none() && self.name_property.is_none() {
            anyhow::bail!(
                "hierarchy tier '{}' names neither code_property nor name_property",
                self.name
            );
        }
        Ok(())
    }
}
```

Add to `Settings`:

```rust
#[derive(Debug, Deserialize)]
struct Settings {
    sources: Sources,
    #[serde(default)]
    test_data: Option<TestData>,

    /// Ordered classification tiers, outermost first. Empty if the section is
    /// omitted (a project with no classification defined).
    #[serde(default)]
    hierarchy: Vec<HierarchyTier>,
}
```

Validate in `load_settings` (fail fast, consistent with the rest of settings):

```rust
fn load_settings(path: &PathBuf) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("could not read settings file: {}", path.display()))?;
    let settings: Settings = toml::from_str(&raw).context("failed to parse settings TOML")?;
    for tier in &settings.hierarchy {
        tier.validate()?; // unkeyable tier is a startup error, not a runtime surprise
    }
    Ok(settings)
}
```

### Resolution (full-depth path with `undefined` fill)

```rust
/// One tier's resolved value for a room. `undefined` is a REPRESENTED value, not
/// an absence — every room gets one of these at every tier, so the grouping tree
/// is uniform-depth and a viewer can render "undefined Sub-department" as its own
/// group rather than dropping the room.
#[derive(Debug, Clone, Serialize)]
struct TierValue {
    tier: String,
    /// None when this tier (or a tier above it) had no data — i.e. undefined.
    #[serde(skip_serializing_if = "Option::is_none")]
    code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    /// True once classification has fallen through to undefined at this tier.
    undefined: bool,
}

/// Resolve one room to a full-depth classification path.
/// RULE: assign the room to the highest tier it has data for; once a tier is
/// missing its data, that tier AND every tier below are `undefined`. (A room
/// missing tier 1 is undefined all the way down — still visualizable.)
fn classify_room(room: &Room, tiers: &[HierarchyTier]) -> Vec<TierValue> {
    let mut path = Vec::with_capacity(tiers.len());
    let mut fell_through = false;

    for tier in tiers {
        // Read code/name off the room's properties (custom bag here; extend to
        // built-ins if a tier's property is a built-in — same note as step 2).
        let code = tier
            .code_property
            .as_ref()
            .and_then(|p| room.properties.custom.get(p))
            .map(|v| v.value.clone())
            .filter(|s| !s.is_empty());
        let name = tier
            .name_property
            .as_ref()
            .and_then(|p| room.properties.custom.get(p))
            .map(|v| v.value.clone())
            .filter(|s| !s.is_empty());

        // A tier has data if at least one of its referenced properties resolved.
        let has_data = code.is_some() || name.is_some();

        if fell_through || !has_data {
            fell_through = true; // once undefined, stay undefined downward
            path.push(TierValue { tier: tier.name.clone(), code: None, name: None, undefined: true });
        } else {
            path.push(TierValue { tier: tier.name.clone(), code, name, undefined: false });
        }
    }
    path
}
```

### Where it runs

- **For now:** resolve in memory. Simplest is to compute the path per room inside
  the `/rooms` assembly (same place the dRofus join happens) and include it on
  `RoomResponse` as a `classification: Vec<TierValue>` field, OR keep it separate
  and log/inspect it in a test. Either is fine for a no-UI test implementation —
  pick per what's easiest to eyeball.
- **Hold the tiers in `AppState`** (loaded from settings, alongside dRofus) so
  the resolver has them.
- **No `/hierarchy` endpoint yet.** When the UI arrives it gets its own endpoint
  (grouping is derived, differently-triggered data) — leave the seam, don't build
  it now.

### Staleness note (leave a comment in the code)

The resolved classification is a cache over (static definition + current
snapshot). If you resolve it once and store it, it must be recomputed whenever a
new snapshot is pushed or dRofus is re-polled. Computing it fresh inside
`/rooms` assembly sidesteps this entirely for now — prefer that until there's a
measured reason to cache.

### Verify

- Unit test: a fully-classified room → full path, no `undefined`.
- Unit test: a room missing the sub-department property → Building + Department
  resolved, Sub-department and everything below `undefined`.
- Unit test: a room missing tier 1 → `undefined` all the way down.
- Startup test: a `[[hierarchy]]` tier with neither property → `load_settings`
  errors.

---

## Suggested commit sequence

1. Step 1 types + schema bump + serde round-trip tests. (No behaviour change to
   the join or classification yet.)
2. Step 2 CSV loader + `AppState` change + `/rooms` join + tests.
3. Step 3 settings section + validation + resolver + tests.
4. STRATEGY.md: tick the three items and note any decisions made (v2 acceptance
   window, where the link/tier properties live per-tier).

## Open decisions to confirm with the developer before/while building

- **v2 acceptance:** hard-require v3, or accept v2 with empty properties during
  transition? (Affects the `SUPPORTED_SCHEMA` check.)
- **Link/tier property tier:** for the test dataset, do the dRofus link property
  and the classification tier properties live in the built-in struct or the
  custom bag? Determines whether the lookup needs to check both tiers. Safest is
  to write a small `lookup_property(&room, name)` that checks built-ins then
  custom, and use it in both step 2 and step 3.
- **CSV crate vs hand-parse:** the `csv` crate is suggested; a hand-split is
  possible but handles quoting/escaping worse. Prefer the crate.
