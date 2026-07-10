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

use std::collections::HashMap;
use std::path::{Path, PathBuf};

use anyhow::Context;
use serde::Deserialize;

/// One project's settings, parsed once at startup from its own TOML file
/// (one of N files in the `--project-settings` directory — see
/// HANDOVER-per-project-settings.md). Server-wide config (`[storage]`,
/// `[test_data]`) lives separately in `ServerConfig`, loaded once from
/// `--server-settings` independent of this per-project loop.
#[derive(Debug, Deserialize)]
pub struct Settings {
    /// This bundle's project id — matched against `RoomPayload.project.id` to
    /// select which bundle applies to a given model. Must be non-empty
    /// (validated at load).
    pub project_id: String,

    /// When true, this bundle is also the explicit fallback for any project
    /// with no dedicated settings file (`AppState::settings_for`). At most
    /// one project file may set this — validated across the whole directory
    /// at load time, not here (a single file can't see its siblings).
    #[serde(default)]
    pub is_default: bool,

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
}

fn default_room_label() -> Vec<String> {
    vec!["$name".to_string(), "$id".to_string()]
}

/// One dRofus column's declared type/format, and optionally a QA override.
/// `label` matches row 1 of the dRofus CSV (the same key
/// `DrofusData::reconciliation`/`all_labels` use).
#[derive(Debug, Clone, Deserialize)]
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
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Deserialize)]
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
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CompareMode {
    /// Force exact string comparison even when both sides parse as numbers.
    Exact,
    /// Skip comparison and coverage reporting for this field entirely.
    Ignore,
}

/// Dry-run one strftime pattern so a typo (e.g. `%Q`) fails at startup, not
/// silently at compare time. `StrftimeItems` yields an `Item::Error` for any
/// specifier chrono doesn't know — walking the items is exactly the parse the
/// comparison will do later, minus a value.
fn validate_strftime(label: &str, which: &str, pattern: &str) -> anyhow::Result<()> {
    use chrono::format::{Item, StrftimeItems};
    if StrftimeItems::new(pattern).any(|item| matches!(item, Item::Error)) {
        anyhow::bail!(
            "drofus_fields entry '{}' has an invalid {} strftime pattern: '{}'",
            label,
            which,
            pattern
        );
    }
    Ok(())
}

/// Fail fast on a malformed dRofus field declaration — same "loud startup
/// error over a silent no-op" discipline as hierarchy tiers and builtin
/// properties:
/// - a `label` the dRofus CSV never declared. Can't run inside
///   `load_settings` itself: dRofus loads *after* settings in `main.rs`, so
///   the label set isn't known yet at that point — this runs as a separate
///   step once both are loaded.
/// - a `Date` field with no `format` — unusable without one.
/// - a `format`/`revit_format` given on a non-`Date` field — meaningless,
///   almost certainly a mistake rather than intentional.
/// - a `format`/`revit_format` that isn't a valid strftime pattern — it would
///   never parse any value, making the declaration a silent no-op.
pub fn validate_drofus_fields(fields: &[DrofusFieldConfig], all_labels: &[String]) -> anyhow::Result<()> {
    for field in fields {
        if !all_labels.iter().any(|l| l == &field.label) {
            anyhow::bail!("drofus_fields references unknown dRofus field label: '{}'", field.label);
        }
        match (field.field_type, &field.format) {
            (FieldType::Date, None) => {
                anyhow::bail!("drofus_fields entry '{}' has type = \"date\" but no format", field.label);
            }
            (other, Some(_)) if other != FieldType::Date => {
                anyhow::bail!("drofus_fields entry '{}' sets format but type is not \"date\"", field.label);
            }
            (FieldType::Date, Some(format)) => validate_strftime(&field.label, "format", format)?,
            _ => {}
        }
        if let Some(revit_format) = &field.revit_format {
            if field.field_type != FieldType::Date {
                anyhow::bail!(
                    "drofus_fields entry '{}' sets revit_format but type is not \"date\"",
                    field.label
                );
            }
            validate_strftime(&field.label, "revit_format", revit_format)?;
        }
    }
    Ok(())
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

pub fn load_server_config(path: &PathBuf) -> anyhow::Result<ServerConfig> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("could not read server settings file: {}", path.display()))?;
    let mut config: ServerConfig = toml::from_str(&raw).context("failed to parse server settings TOML")?;

    // Same base-dir discipline as `load_settings`: relative paths inside this
    // file resolve against the file's own directory, not the process cwd.
    let settings_dir = path.parent().filter(|p| !p.as_os_str().is_empty());
    if let Some(storage) = &mut config.storage {
        resolve_relative_to(&mut storage.root, settings_dir);
    }
    if let Some(test_data) = &mut config.test_data {
        resolve_relative_to(&mut test_data.snapshot_path, settings_dir);
    }

    Ok(config)
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
#[derive(Debug, Default, Deserialize)]
pub struct Sources {
    #[serde(default)]
    pub drofus: Option<DrofusSource>,
}

/// dRofus source. `#[serde(tag = "type")]` lets the TOML `type` field pick the
/// variant — adding an `Api` variant later is a loader-only change; all
/// consumers of `AppState` stay untouched.
#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum DrofusSource {
    /// Current: load from a local file.
    File { path: PathBuf },
    // Future: Api { url: String, api_key: String },
}

/// Dev-only seed data. Kept separate from `drofus` so removing this test seam
/// later is a one-section deletion with no other changes.
#[derive(Debug, Deserialize)]
pub struct TestData {
    /// Path to a pre-exported snapshot (same JSON shape a POST sends).
    pub snapshot_path: PathBuf,
}

/// One tier of the classification hierarchy. A tier is keyed by a code and/or a
/// name property — at least one must be present (validated at startup), since a
/// tier naming neither is unkeyable.
#[derive(Debug, Clone, Deserialize)]
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

/// One canonical property definition: a stable name consumers (dRofus
/// `link_property`, hierarchy tier `code_property`/`name_property`) reference,
/// resolved per-source to whatever raw property name that source actually
/// uses. See `Settings::builtin_properties`.
#[derive(Debug, Clone, Deserialize)]
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

/// Resolve a path from the settings file relative to the settings file's own
/// directory, not the process's current working directory. Without this, a
/// relative path like `./settings/drofus.csv` only works when the binary
/// happens to be launched with cwd == crate root (e.g. via `cargo run`) —
/// running the compiled exe directly from anywhere else silently breaks it.
/// Absolute paths pass through unchanged.
fn resolve_relative_to(path: &mut PathBuf, settings_dir: Option<&Path>) {
    if path.is_absolute() {
        return;
    }
    if let Some(dir) = settings_dir {
        *path = dir.join(&path);
    }
}

pub fn load_settings(path: &PathBuf) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)
        .with_context(|| format!("could not read settings file: {}", path.display()))?;
    let mut settings: Settings = toml::from_str(&raw).context("failed to parse settings TOML")?;

    // Base dir for every relative path *inside* the settings file. `.filter`
    // turns a bare filename's empty parent ("") into None, which just means
    // "no base to prepend" — those paths fall back to cwd-relative, same as
    // before this fix.
    let settings_dir = path.parent().filter(|p| !p.as_os_str().is_empty());
    if let Some(DrofusSource::File { path: drofus_path }) = &mut settings.sources.drofus {
        resolve_relative_to(drofus_path, settings_dir);
    }

    if settings.project_id.trim().is_empty() {
        anyhow::bail!("settings file {} has an empty project_id", path.display());
    }

    // Fail fast on unkeyable or duplicate-named tiers — better a startup error
    // than a silent classification that groups every room under "undefined",
    // or a tier name lookup (e.g. "Building") silently picking the first of
    // two matches.
    let mut seen_tier_names = std::collections::HashSet::new();
    for tier in &settings.hierarchy {
        tier.validate()?;
        if !seen_tier_names.insert(tier.name.clone()) {
            anyhow::bail!("duplicate hierarchy tier name: '{}'", tier.name);
        }
    }
    // Fail fast on unmappable or duplicate builtin property definitions —
    // same discipline as hierarchy tiers.
    let mut seen_canonical = std::collections::HashSet::new();
    for def in &settings.builtin_properties {
        def.validate()?;
        if !seen_canonical.insert(def.canonical.clone()) {
            anyhow::bail!("duplicate builtin property canonical name: '{}'", def.canonical);
        }
    }
    Ok(settings)
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

    /// Two hierarchy tiers sharing a name fail `load_settings` at startup —
    /// otherwise a `.position(|t| t.name == "Building")` lookup would silently
    /// pick the first of two matches.
    #[test]
    fn test_duplicate_tier_names_fail_load_settings() {
        let dir = std::env::temp_dir().join(format!("roommate-dup-tier-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let drofus_path = dir.join("drofus.csv");
        std::fs::write(&drofus_path, "Id\nNumber\n").unwrap();

        let settings_path = dir.join("settings.toml");
        std::fs::write(
            &settings_path,
            format!(
                r#"
project_id = "p1"

[sources.drofus]
type = "file"
path = "{}"

[[hierarchy]]
name = "Building"
code_property = "a"

[[hierarchy]]
name = "Building"
code_property = "b"
"#,
                drofus_path.display().to_string().replace('\\', "/")
            ),
        )
        .unwrap();

        let result = load_settings(&settings_path);
        assert!(result.is_err());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A settings file with no `[sources]` section at all is legal — a
    /// project not using dRofus (or any external source) is a normal state,
    /// not a config error.
    #[test]
    fn test_settings_without_sources_loads() {
        let dir = std::env::temp_dir().join(format!("roommate-no-sources-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let settings_path = dir.join("settings.toml");
        std::fs::write(&settings_path, "project_id = \"p1\"\n").unwrap();

        let settings = load_settings(&settings_path).unwrap();
        assert!(settings.sources.drofus.is_none());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A minimal `DrofusFieldConfig` for tests that only care about one
    /// aspect of the declaration.
    fn field(label: &str) -> DrofusFieldConfig {
        DrofusFieldConfig {
            label: label.to_string(),
            field_type: FieldType::default(),
            format: None,
            revit_format: None,
            qa: None,
        }
    }

    /// A declaration referencing a label the dRofus CSV never declared fails
    /// startup rather than silently never applying.
    #[test]
    fn test_validate_drofus_fields_rejects_unknown_label() {
        let fields = vec![DrofusFieldConfig { qa: Some(CompareMode::Ignore), ..field("Nonexistent") }];
        let all_labels = vec!["NetArea".to_string(), "Department".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// A declaration referencing a real label, with only a `qa` override and
    /// no `type`, passes validation (today's shipped behavior, generalized).
    #[test]
    fn test_validate_drofus_fields_accepts_known_label() {
        let fields = vec![DrofusFieldConfig { qa: Some(CompareMode::Exact), ..field("NetArea") }];
        let all_labels = vec!["NetArea".to_string(), "Department".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_ok());
    }

    /// `type = "date"` with no `format` is unusable -- fails validation.
    #[test]
    fn test_validate_drofus_fields_date_without_format_fails() {
        let fields = vec![DrofusFieldConfig { field_type: FieldType::Date, ..field("LastSync") }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// `type = "date"` with a `format` passes validation.
    #[test]
    fn test_validate_drofus_fields_date_with_format_passes() {
        let fields = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%-m/%-d/%Y %-I:%M:%S %p %z".to_string()),
            ..field("LastSync")
        }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_ok());
    }

    /// A `format` on a non-date field is meaningless -- fails validation.
    #[test]
    fn test_validate_drofus_fields_format_on_non_date_fails() {
        let fields = vec![DrofusFieldConfig { format: Some("whatever".to_string()), ..field("NetArea") }];
        let all_labels = vec!["NetArea".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// A strftime typo (`%Q` is not a chrono specifier) fails at startup --
    /// otherwise the pattern would pass config validation and just silently
    /// never parse anything at compare time.
    #[test]
    fn test_validate_drofus_fields_malformed_strftime_fails() {
        let fields = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%Q/%-d/%Y".to_string()),
            ..field("LastSync")
        }];
        let all_labels = vec!["LastSync".to_string()];

        assert!(validate_drofus_fields(&fields, &all_labels).is_err());
    }

    /// `revit_format` follows `format`'s rules: legal (and dry-run-validated)
    /// on a date field, rejected on any other type.
    #[test]
    fn test_validate_drofus_fields_revit_format_rules() {
        let all_labels = vec!["LastSync".to_string(), "NetArea".to_string()];

        let good = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%-m/%-d/%Y %-I:%M:%S %p %z".to_string()),
            revit_format: Some("%Y-%m-%d %H:%M:%S".to_string()),
            ..field("LastSync")
        }];
        assert!(validate_drofus_fields(&good, &all_labels).is_ok());

        let on_non_date = vec![DrofusFieldConfig {
            revit_format: Some("%Y-%m-%d".to_string()),
            ..field("NetArea")
        }];
        assert!(validate_drofus_fields(&on_non_date, &all_labels).is_err());

        let malformed = vec![DrofusFieldConfig {
            field_type: FieldType::Date,
            format: Some("%Y-%m-%d".to_string()),
            revit_format: Some("%Q".to_string()),
            ..field("LastSync")
        }];
        assert!(validate_drofus_fields(&malformed, &all_labels).is_err());
    }
}
