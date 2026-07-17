//! Startup configuration: the TOML settings file and everything parsed from it.
//!
//! Config a human hand-edits lives here (hence TOML, with comments); the *data*
//! it points at stays JSON. Everything is resolved once at startup and fails
//! fast on bad config — better a loud startup error than a surprise on the first
//! request. See `settings-infrastructure-handoff.md`.
//!
//! `DrofusSource` lives here (not in `drofus`) because it's part of the settings
//! contract; the `#[serde(tag = "type")]` enum is the seam that makes the future
//! file→API swap a loader-only change. `HierarchyTier` lives here too, as the
//! classification *definition*; `classify` consumes it but doesn't own its shape.
//!
//! Split across three files by concern, re-exported here so the public paths
//! (`crate::settings::Settings`, `::load_settings`, `::validate_drofus_fields`,
//! …) never move:
//! - **this file** — the config/domain types and their inherent `validate()`
//!   methods (part of each type's own API);
//! - **`validate`** — the standalone validation *functions* over those types;
//! - **`load`** — the TOML loaders and settings-file-relative path resolution.

use std::collections::HashMap;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};

mod load;
mod validate;

pub use load::{load_server_config, load_settings};
pub use validate::{validate_colour_plans, validate_drofus_field_shapes, validate_drofus_fields};

/// One project's settings, parsed once at startup from its own TOML file
/// (one of N files in the `--project-settings` directory — see
/// HANDOVER-per-project-settings.md). Server-wide config (`[storage]`,
/// `[test_data]`) lives separately in `ServerConfig`, loaded once from
/// `--server-settings` independent of this per-project loop.
///
/// Also derives `Serialize` (as do all the types it contains): the settings
/// API serves this exact shape as JSON and writes it back as TOML, so the
/// wire shape and the config-file shape can never drift.
#[derive(Debug, Deserialize, Serialize)]
pub struct Settings {
    /// This bundle's project id — matched against `RoomPayload.project.id` to
    /// select which bundle applies to a given model. Must be non-empty
    /// (validated at load).
    pub project_id: String,

    /// Human-readable project name, for display only — never matched against
    /// anything, so it stays freely editable in a way `project_id` (a storage
    /// path key) can't be. Producers read it from `/api/settings/projects` and
    /// send it as `RoomPayload.project.name`, which is what the store's
    /// `project.toml` manifest and the viewer's project picker then show; this
    /// file is where that name is *authored*.
    ///
    /// Optional, and absence is a normal state, not a defect: a project that
    /// never sets one is displayed under its id (every consumer falls back
    /// that way), which is exactly the behaviour before this field existed.
    /// Must be non-empty *when present* (validated at load) — a blank name is
    /// a mistake, and silently displaying an empty label is worse than saying
    /// so at startup.
    ///
    /// Declared here, adjacent to the other scalars and above `sources`,
    /// because TOML requires scalar keys to precede any table — serde emits
    /// fields in declaration order, so moving this below `sources` would write
    /// files that don't round-trip.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,

    /// When true, this bundle is also the explicit fallback for any project
    /// with no dedicated settings file (`AppState::settings_for`). At most
    /// one project file may set this — validated across the whole directory
    /// at load time, not here (a single file can't see its siblings).
    #[serde(default)]
    pub is_default: bool,

    /// The room property whose value identifies "the same room" when comparing
    /// milestones (see `service::comparison`). Its own concept, deliberately
    /// **not** the dRofus `link_property`: milestone comparison stands entirely
    /// on its own — a project may compare milestones with no dRofus configured
    /// at all — so the id key it matches rooms on is user-chosen and lives
    /// here, separate from anything dRofus. `None` (the default, and every
    /// project file predating this feature) is a real, reachable state: the
    /// comparison then has no way to match rooms across milestones and reports
    /// a "no comparison key configured" result rather than silently falling
    /// back to dRofus or to room `id`. Resolved per-room the same canonical/
    /// source way as every other property name, so a rename or a second source
    /// needs no change here.
    ///
    /// A scalar declared before any table field so the TOML serializer emits it
    /// ahead of `[sources]` etc. — the ordering footgun documented in
    /// CODING-CONVENTIONS.md.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub comparison_key: Option<String>,

    /// Ordered room property names compared across milestones, on rooms present
    /// in both a compared milestone and the baseline. Persisted here (not passed
    /// per request) with the same lifecycle as `room_label`/`milestones`, so it
    /// survives and rides the settings save pipeline. Enumeration is off the
    /// *baseline's* rooms at compare time (only properties on the baseline are
    /// comparable); a name that doesn't resolve on the other side is reported as
    /// a distinct "missing property" state, not a value difference. No startup
    /// validation — an unresolvable name simply contributes nothing, the house
    /// "absence is fine" discipline. Empty (the default) means no properties are
    /// compared, only room add/remove. A value array, declared before any table
    /// field for the same TOML-ordering reason as `comparison_key`.
    #[serde(default)]
    pub comparison_properties: Vec<String>,

    /// External sources joined onto this project's rooms. Defaulted so a
    /// project with no external sources at all is legal config — a project
    /// not using dRofus is normal, and the validation endpoint already
    /// reports it as `drofus_configured: false` rather than an error.
    #[serde(default)]
    pub sources: Sources,

    /// Ordered classification tiers, outermost first. Empty if the section is
    /// omitted (a project with no classification defined).
    #[serde(default)]
    pub hierarchy: Vec<HierarchyTier>,

    /// Canonical property names, each resolved to a source-specific raw
    /// property name. Lets a project retarget which raw property backs a
    /// canonical concept (e.g. "Area") without a Rust code change — the seam
    /// that matters once a second data source (e.g. IFC) can produce rooms
    /// alongside Revit, since the same canonical concept lives under a
    /// different raw name per source. Empty if the section is omitted, in
    /// which case `lookup_property` matches names verbatim (today's
    /// single-source behaviour).
    #[serde(default)]
    pub builtin_properties: Vec<BuiltinPropertyDef>,

    /// Ordered list of property names shown on a room's label in the viewer.
    /// `"$name"` / `"$id"` are intrinsic tokens referring to the room's own
    /// `name`/`id` fields (not resolvable via `lookup_property`, which only
    /// reads `room.properties`); anything else is a canonical property name
    /// resolved the same way dRofus/classification already are. Defaults to
    /// `["$name", "$id"]` — today's label — so omitting this section changes
    /// nothing. No startup validation: an unresolvable name just contributes
    /// nothing to that room's label, same "absence is fine" discipline as
    /// everywhere else here.
    #[serde(default = "default_room_label")]
    pub room_label: Vec<String>,

    /// User-defined milestones: named dates with data snapshots explicitly
    /// pinned to them, so the viewer can show the project as captured at a
    /// milestone instead of each model's latest push. Lives in settings (not
    /// storage) deliberately: milestones are per-project user-authored
    /// metadata with the same lifecycle as hierarchy/room_label, and riding
    /// this file buys the whole save pipeline — validation, atomic install,
    /// hot-reload — for free. Empty if omitted.
    #[serde(default)]
    pub milestones: Vec<Milestone>,

    /// Per-column declarations for dRofus CSV fields: what *type* of data a
    /// column holds, and, optionally, how QA comparison should treat it. One
    /// declaration per column, not two separate lists — "what is this
    /// column" shouldn't be answered in two places that can drift apart.
    /// `type` is read by any consumer that needs to know a column's shape:
    /// QA's date comparison parses a `Date`-declared column's values with the
    /// declared `format` and compares the parsed instants, so two renderings
    /// of the same moment no longer count as a mismatch (numeric-adaptive
    /// comparison still infers numeric-ness at compare time without needing a
    /// declaration). `qa` is the QA-specific override this used to be alone:
    /// `Exact` forces string comparison even when both sides parse as numbers
    /// or dates; `Ignore` excludes the field from comparison *and* the
    /// coverage report entirely — for a column that's mapped (present in the
    /// dRofus CSV's row 2) but expected to always differ. Empty if omitted,
    /// which is the default behavior for every column: treated as a string,
    /// numeric-adaptive comparison if both sides happen to parse as a number.
    #[serde(default)]
    pub drofus_fields: Vec<DrofusFieldConfig>,

    /// User-authored colour plans for the viewer: named, persisted colouring
    /// configs the user switches between. Lives in settings (not storage) for
    /// the same reason `milestones` does — per-project user metadata with the
    /// same lifecycle as hierarchy/room_label, riding this file's save
    /// pipeline (validation, atomic install, hot-reload) for free.
    ///
    /// The server treats this as **opaque**: it stores and serves it verbatim
    /// and computes no colours. ALL colour math is client-side, where room
    /// property values already live — the same "keep axum a pure JSON API"
    /// decision that kept CSV export and QA rendering out of the server
    /// (see STRATEGY-BROWSER.md). A `Vec` (not a single plan) so a project can
    /// keep a library of plans; `ColourPlan.active` marks the one the viewer's
    /// colour picker defaults to (the picker's "None (flat)" always overrides,
    /// so `active` is a default, not a forced application). Empty if omitted —
    /// no plans, today's flat fill. The `#[serde(default)]` is the back-compat
    /// net: every already-saved project file (which has no `colour_plans` key)
    /// still deserializes to an empty `Vec`.
    #[serde(default)]
    pub colour_plans: Vec<ColourPlan>,

    /// Footprint exclusions for the hierarchy-areas feature (`service::areas`):
    /// rooms or whole groups withheld from the aggregated footprints. Empty (the
    /// default, and every file predating this feature) means nothing is excluded.
    /// `skip_serializing_if` so an empty list emits nothing — a trailing
    /// `hierarchy_exclusions = []` after the colour-plan tables would trip the
    /// TOML "value-after-table" ordering footgun (CODING-CONVENTIONS.md).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub hierarchy_exclusions: Vec<HierarchyExclusion>,
}

fn default_room_label() -> Vec<String> {
    vec!["$name".to_string(), "$id".to_string()]
}

/// One dRofus column's declared type/format, and optionally a QA override.
/// `label` matches row 1 of the dRofus CSV (the same key
/// `DrofusData::reconciliation`/`all_labels` use).
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DrofusFieldConfig {
    pub label: String,

    /// What kind of data this column holds. Defaults to `String` (today's
    /// implicit treatment of every column) when omitted.
    #[serde(default, rename = "type")]
    pub field_type: FieldType,

    /// Required when `field_type` is `Date`: a chrono strftime-style pattern
    /// describing how this column's raw string is laid out -- dRofus dates
    /// arrive as formatted text (e.g. `"6/29/2026 5:01:01 PM +10:00"`), not a
    /// structured value, so a parser needs to be told the shape rather than
    /// guessing it. Meaningless for any other `field_type`. Dry-run-validated
    /// at startup (a typo like `%Q` fails loudly rather than silently never
    /// parsing anything at compare time).
    #[serde(default)]
    pub format: Option<String>,

    /// Optional second strftime pattern for the *Revit* side of a date
    /// comparison, when the room property renders dates differently from the
    /// dRofus column. Absent (the common case) means `format` is used for
    /// both sides. Only legal on a `Date` field, same as `format`. Exists
    /// because the two sources format independently -- no real snapshot with
    /// a date-bearing room property existed when this was added, so rather
    /// than guess Revit's shape, a project can declare it when it shows up.
    #[serde(default)]
    pub revit_format: Option<String>,

    /// Optional QA comparison override for this column. `None` (the default)
    /// keeps today's behavior: numeric-adaptive comparison if both sides
    /// parse as a number, else exact string match.
    #[serde(default)]
    pub qa: Option<CompareMode>,
}

/// The kind of data a dRofus column holds. Not a closed set forever -- more
/// variants join as consumers need them (e.g. a `Numeric { unit }` case,
/// once real unit conversion rather than adaptive rounding is needed).
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum FieldType {
    #[default]
    String,
    Numeric,
    Date,
}

/// How one dRofus field's value is compared against Revit's, when the
/// default (numeric-adaptive if both sides parse as a number, else exact
/// string match) needs overriding.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum CompareMode {
    /// Force exact string comparison even when both sides parse as numbers.
    Exact,
    /// Skip comparison and coverage reporting for this field entirely.
    Ignore,
}

// ---------- colour plans ----------
//
// Persisted, per-project room-colouring configs for the viewer. The server is
// deliberately *opaque* to all of this: it round-trips these types verbatim
// and never computes a colour (see `Settings::colour_plans`). The types live
// here only so they persist through the settings save pipeline; every field's
// *meaning* is a browser concern, resolved in `index.html`.

/// One named, persisted colouring configuration. `active` marks the plan the
/// viewer's colour picker defaults to — the picker also offers "None (flat)",
/// which always overrides, so `active` is a default selection, not a forced
/// application. `name` is user-facing only (the picker label). At most one plan
/// may be `active` (validated — see `validate_colour_plans`).
///
/// Scalar fields (`name`, `active`) are declared before `mode` (a sub-table)
/// so the TOML serializer emits them ahead of the `[colour_plans.mode]` table
/// — the same footgun documented for `Milestone.drofus_snapshot`.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ColourPlan {
    /// User-facing label shown in the viewer's colour picker.
    pub name: String,
    /// Whether this plan is the viewer picker's default selection. `false`
    /// (the default) means the plan is in the library but not the default —
    /// the picker starts on "None (flat)" unless some plan sets this.
    #[serde(default)]
    pub active: bool,
    /// The colouring strategy. Internally tagged on `kind` so the wire shape is
    /// self-describing and the browser switches on one field — the same tagged
    /// representation `DrofusSource` uses.
    pub mode: ColourMode,
}

/// The colouring strategies. Internally tagged on `kind` (like `DrofusSource`'s
/// `type`), so the browser branches on `mode.kind`. Every variant is a *struct*
/// variant, not a newtype/tuple: internally-tagged serde enums can't carry a
/// newtype variant that wraps a sequence, and struct variants keep the JSON/TOML
/// shape flat and self-describing.
///
/// All three modes are wired end-to-end in the viewer (`colourForRoom` in
/// `index.html` — see STRATEGY-BROWSER.md); an authored plan whose values don't
/// resolve (an unparseable property, a ratio-by-zero, a value between bands, an
/// undefined tier) degrades to a "no data" grey rather than erroring.
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "lowercase")]
pub enum ColourMode {
    /// Categorical hue per parent hierarchy tier, tint/shade per child tier.
    /// `tiers` names which hierarchy tiers participate, parent first (the
    /// browser reads each room's server-resolved `classification` path and
    /// matches by tier name); `scheme` names a bundled qualitative palette for
    /// the parent hues (child tint/shade is derived by lightening, no second
    /// scheme). One tier → hue only; a room whose parent tier is `undefined`
    /// renders "no data" grey.
    Hierarchy {
        tiers: Vec<String>,
        scheme: String,
    },

    /// Colour by proximity of a date-typed `property` to `near_date`: nearest
    /// green, furthest red, a date after `near_date` blue. `property` is a
    /// canonical/room property name resolved browser-side the same way labels
    /// are; `scheme` names a bundled diverging palette. `format` is the
    /// strftime pattern the room's date strings are in — the *same* pattern the
    /// dRofus date column uses (Revit room dates originate from dRofus), so an
    /// author reuses the `drofus_fields` `format` rather than inventing one;
    /// omitted means the browser falls back to native ISO-8601 parsing, and an
    /// unparseable value just renders "no data" grey. Validated as a real
    /// strftime pattern at load when present (see `validate_colour_plans`).
    DateRange {
        property: String,
        near_date: String,
        scheme: String,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        format: Option<String>,
    },

    /// Compare two room properties. `op` derives one number per room
    /// (difference or ratio of A and B); `colouring` maps that number to a
    /// colour. The two steps are kept deliberately separate: the number
    /// derivation is what a *future* `MilestoneCompare` mode (same property
    /// across two snapshots — current vs a `/rooms?milestone=`-pinned one)
    /// would swap out, reusing `Colouring` untouched. Property names that don't
    /// resolve on a given room aren't an error — that room just renders "no
    /// data" grey (the `room_label` "absence is fine" discipline).
    PropertyCompare {
        property_a: String,
        property_b: String,
        op: CompareOp,
        colouring: Colouring,
    },
}

/// How `PropertyCompare` reduces two property values to one number.
#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum CompareOp {
    /// `A − B`. The natural choice for match (`|A−B| ≤ tol`) and a
    /// zero-centred diverging ramp.
    Diff,
    /// `A / B`. For proportional comparisons; the browser guards division by
    /// zero (→ "no data" grey), so no server-side check is needed.
    Ratio,
}

/// The number→colour step, factored *out* of `PropertyCompare` on purpose: it's
/// the reusable half, so a future mode that derives a per-room number
/// differently (e.g. `MilestoneCompare`) reuses these three styles without
/// change. Internally tagged on `style`; struct variants only (see
/// `ColourMode` for why).
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "style", rename_all = "lowercase")]
pub enum Colouring {
    /// Two colours: within `tolerance` of zero (a match) vs. not. This is the
    /// dRofus-vs-Revit QA case. Reuses the *philosophy* of `CompareMode`'s
    /// numeric-adaptive comparison (both sides parse as numbers → numeric
    /// compare with tolerance, else exact) rather than inventing a second one —
    /// the actual comparison runs browser-side against string property values.
    Match { tolerance: f64 },
    /// Map the number onto a diverging palette centred on zero, auto-scaled to
    /// the level's data extent (computed per-render in the browser). `scheme`
    /// names a bundled diverging palette.
    Diverging { scheme: String },
    /// Map the number through user-defined cutoff→colour `bands`. A struct
    /// variant (`{ bands }`), not a newtype `Bands(Vec<Band>)`, because
    /// internally-tagged enums can't wrap a sequence in a newtype variant.
    Bands { bands: Vec<Band> },
}

/// One band of a `Bands` colouring: the half-open interval `[lo, hi)` gets
/// `colour`. `lo`/`hi` are `Option` so the first/last band can be open-ended
/// (`None` = −∞ / +∞). Bands are validated at load to be sorted and disjoint
/// (see `validate_colour_plans`), which is what lets the browser do a simple
/// ordered first-match scan with no overlap-resolution logic. A value that
/// falls in a *gap* between bands (allowed) renders as "no data" grey — a
/// deliberate gap, not a bug.
///
/// `colour` is a CSS colour string (e.g. `"#b4541f"`); the server never parses
/// it — validating colour syntax is a browser concern, and an unparseable one
/// just renders as the browser's fallback.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Band {
    /// Inclusive lower bound; `None` = open (−∞).
    #[serde(default)]
    pub lo: Option<f64>,
    /// Exclusive upper bound; `None` = open (+∞).
    #[serde(default)]
    pub hi: Option<f64>,
    /// CSS colour string applied to rooms whose value lands in `[lo, hi)`.
    pub colour: String,
}

/// Server-wide settings, parsed once at startup from the `--server-settings`
/// file — separate from per-project `Settings` because storage and dev
/// seeding are properties of the running server, not of any one project.
#[derive(Debug, Deserialize)]
pub struct ServerConfig {
    /// Where model snapshots are persisted on disk. When present, pushes are
    /// written under this root (project-guid/model-guid/snapshot.json) and
    /// survive restarts. When absent, storage stays purely in-memory (dev/test).
    #[serde(default)]
    pub storage: Option<Storage>,

    /// Dev-only: when present, seeds the server with a snapshot from disk at
    /// startup so no manual POST is needed. Omit in prod.
    #[serde(default)]
    pub test_data: Option<TestData>,
}

/// On-disk snapshot storage config. Its own section (not under `[sources]`):
/// a source *supplies* join data, storage *persists* the snapshots themselves —
/// different kind of thing. Kept as an `Option` on `ServerConfig` so omitting
/// it is a clean fallback to the in-memory store, no other change.
#[derive(Debug, Deserialize)]
pub struct Storage {
    /// Root directory holding one sub-dir per project (named by project GUID).
    /// Created on first push if missing; must be writable.
    pub root: PathBuf,
}

/// External data sources joined onto the Revit snapshot. Every source is
/// optional: which sources a project uses is that project's choice, and an
/// absent source degrades to "not configured" downstream (e.g.
/// `ValidationResponse.drofus_configured: false`), never an error.
#[derive(Debug, Default, Deserialize, Serialize)]
pub struct Sources {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drofus: Option<DrofusSource>,
}

/// dRofus source. `#[serde(tag = "type")]` lets the TOML `type` field pick the
/// variant — adding an `Api` variant later is a loader-only change; all
/// consumers of `AppState` stay untouched.
#[derive(Debug, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum DrofusSource {
    /// Load from a local file path, once at startup.
    File { path: PathBuf },
    /// Data arrives via `POST /projects/{id}/drofus` uploads, stored as
    /// timestamped snapshots in the `SnapshotStore`; the latest one is
    /// hydrated at startup (and hot-swapped in after each upload). A project
    /// with this source but no upload yet is legitimately "not configured
    /// yet" downstream — not a startup error.
    Upload,
    // Future: Api { url: String, api_key: String },
}

/// Dev-only seed data. Kept separate from `drofus` so removing this test seam
/// later is a one-section deletion with no other changes.
#[derive(Debug, Deserialize)]
pub struct TestData {
    /// Path to a pre-exported snapshot (same JSON shape a POST sends).
    pub snapshot_path: PathBuf,
}

/// One user-defined milestone: a named date with data snapshots explicitly
/// pinned to it (`attachments`: model id → snapshot `taken_at`). The *name*
/// is the milestone's identity — unique per project, and what
/// `/rooms?milestone=` matches on; the date is display/ordering metadata.
/// A milestone can also pin one dRofus snapshot (`drofus_snapshot`), so the
/// milestone view joins the reference data as it stood at the milestone
/// rather than the project's current dRofus — the slot that was reserved for
/// "future sources" now that dRofus is an uploaded, snapshotted source.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Milestone {
    /// Identity: unique per project, non-empty (validated at load).
    pub name: String,
    /// Display/order date: `YYYY-MM-DD` or a full RFC3339 date-time
    /// (validated at load).
    pub date: String,
    /// Optional dRofus snapshot pinned to this milestone: the `taken_at` id of
    /// one uploaded dRofus CSV in the store, joined onto this milestone's rooms
    /// instead of the project's current dRofus. `None` (the common case, and
    /// every milestone authored before this field existed) keeps the pre-
    /// pinning behaviour — the milestone view joins the *current* dRofus.
    /// dRofus is project-scoped, so this is a single id, not a per-model map
    /// like `attachments`. Like an `attachments` pin, whether the snapshot
    /// still *exists* is a read-time concern (skip + warn, fall back to
    /// current); only its *shape* (a valid RFC3339-UTC snapshot id) is
    /// validated here. Declared before `attachments` so the TOML serializer
    /// emits it as a scalar ahead of the `[milestones.attachments]` sub-table.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drofus_snapshot: Option<String>,
    /// Explicit pins: model id → snapshot id (`taken_at`). A model with no
    /// entry simply doesn't appear in this milestone's view. Whether a pinned
    /// snapshot still *exists* is a read-time concern (skip + warn), not
    /// validated here — settings can't see storage.
    #[serde(default)]
    pub attachments: std::collections::BTreeMap<String, String>,
}

impl Milestone {
    /// Startup-loud checks on one milestone's own fields (uniqueness across
    /// milestones is checked in `load_settings`, which can see the siblings).
    pub fn validate(&self) -> anyhow::Result<()> {
        if self.name.trim().is_empty() {
            anyhow::bail!("a milestone has an empty name");
        }
        let date_ok = chrono::NaiveDate::parse_from_str(&self.date, "%Y-%m-%d").is_ok()
            || chrono::DateTime::parse_from_rfc3339(&self.date).is_ok();
        if !date_ok {
            anyhow::bail!(
                "milestone '{}' has an invalid date {:?} (expected YYYY-MM-DD or RFC3339)",
                self.name,
                self.date
            );
        }
        for (model_id, taken_at) in &self.attachments {
            if model_id.trim().is_empty() {
                anyhow::bail!("milestone '{}' has an attachment with an empty model id", self.name);
            }
            crate::contract::validate_snapshot_id(taken_at).map_err(|e| {
                anyhow::anyhow!("milestone '{}', attachment for model '{}': {}", self.name, model_id, e)
            })?;
        }
        // Same rule as an attachments pin: a valid RFC3339-UTC snapshot id.
        // Existence is not checkable here (settings can't see storage).
        if let Some(id) = &self.drofus_snapshot {
            crate::contract::validate_snapshot_id(id)
                .map_err(|e| anyhow::anyhow!("milestone '{}', drofus_snapshot: {}", self.name, e))?;
        }
        Ok(())
    }
}

/// One tier of the classification hierarchy. A tier is keyed by a code and/or a
/// name property — at least one must be present (validated at startup), since a
/// tier naming neither is unkeyable.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct HierarchyTier {
    /// Human label for the tier ("Building", "Department").
    pub name: String,
    /// Room property holding this tier's code. Optional per-tier.
    #[serde(default)]
    pub code_property: Option<String>,
    /// Room property holding this tier's display name. Optional per-tier.
    #[serde(default)]
    pub name_property: Option<String>,
}

impl HierarchyTier {
    /// A tier must name at least one property or it can't be keyed. Validated
    /// at startup so a misconfigured tier is a loud error, not a silent
    /// "undefined" for every room.
    pub fn validate(&self) -> anyhow::Result<()> {
        if self.code_property.is_none() && self.name_property.is_none() {
            anyhow::bail!(
                "hierarchy tier '{}' names neither code_property nor name_property",
                self.name
            );
        }
        Ok(())
    }
}

/// A footprint exclusion for the hierarchy-areas feature (`service::areas`). The
/// match kind implies WHERE in the two-stage pipeline it applies — the handover's
/// "the match kind implies the stage":
///
/// - `group` — Case A, applied at **stage 2**: a resolved group at `tier` whose
///   value matches is computed normally but WITHHELD from its parent's dissolve,
///   so it drops out of that tier and every tier above while its own footprints
///   stay. Still reported, flagged "not counted upward" (outdoor areas: real,
///   with their own plan, but not part of the building footprint).
/// - `rooms` — Case B, applied at **stage 1**: the listed room ids never enter
///   any union, so they vanish from every tier including their own bottom group.
///
/// Matching a group reuses the resolved tier value everything else classifies
/// against — no second matching vocabulary; `value` matches the tier's resolved
/// code OR name. Internally tagged on `match`, the same self-describing shape
/// `DrofusSource`/`ColourMode` use.
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "match", rename_all = "lowercase")]
pub enum HierarchyExclusion {
    Group { tier: String, value: String },
    Rooms { ids: Vec<String> },
}

/// One canonical property definition: a stable name consumers (dRofus
/// `link_property`, hierarchy tier `code_property`/`name_property`) reference,
/// resolved per-source to whatever raw property name that source actually
/// uses. See `Settings::builtin_properties`.
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct BuiltinPropertyDef {
    /// The stable name consumers reference (e.g. "Area").
    pub canonical: String,
    /// Source key (e.g. "revit") → that source's raw property name.
    pub by_source: HashMap<String, String>,
}

impl BuiltinPropertyDef {
    /// A definition with no source mappings can never resolve to anything —
    /// fail fast rather than silently never matching at request time.
    pub fn validate(&self) -> anyhow::Result<()> {
        if self.by_source.is_empty() {
            anyhow::bail!(
                "builtin property '{}' has no by_source mappings",
                self.canonical
            );
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A HierarchyTier with neither property fails validation.
    #[test]
    fn test_unkeyable_tier_fails_validation() {
        let tier = HierarchyTier {
            name: "Ghost".to_string(),
            code_property: None,
            name_property: None,
        };
        assert!(tier.validate().is_err());
    }

    fn milestone(name: &str, date: &str) -> Milestone {
        Milestone {
            name: name.to_string(),
            date: date.to_string(),
            drofus_snapshot: None,
            attachments: Default::default(),
        }
    }

    /// A milestone's own checks: empty name, unparseable date, and an
    /// attachment whose snapshot id isn't an RFC3339 UTC date-time all fail;
    /// both accepted date shapes pass.
    #[test]
    fn test_milestone_validate() {
        assert!(milestone("Design Freeze", "2026-06-30").validate().is_ok());
        assert!(milestone("Design Freeze", "2026-06-30T10:00:00Z").validate().is_ok());

        assert!(milestone("  ", "2026-06-30").validate().is_err(), "empty name");
        assert!(milestone("M", "sometime in June").validate().is_err(), "bad date");

        let mut bad_pin = milestone("M", "2026-06-30");
        bad_pin.attachments.insert("model-1".to_string(), "not-a-snapshot-id".to_string());
        assert!(bad_pin.validate().is_err(), "attachment id must be a valid snapshot id");

        let mut good_pin = milestone("M", "2026-06-30");
        good_pin.attachments.insert("model-1".to_string(), "2026-06-29T10:00:00.123456Z".to_string());
        assert!(good_pin.validate().is_ok());

        // A dRofus pin follows the same snapshot-id rule as an attachment.
        let mut bad_drofus = milestone("M", "2026-06-30");
        bad_drofus.drofus_snapshot = Some("not-a-snapshot-id".to_string());
        assert!(bad_drofus.validate().is_err(), "drofus_snapshot must be a valid snapshot id");

        let mut good_drofus = milestone("M", "2026-06-30");
        good_drofus.drofus_snapshot = Some("2026-06-29T17:00:00Z".to_string());
        assert!(good_drofus.validate().is_ok());
    }
}
