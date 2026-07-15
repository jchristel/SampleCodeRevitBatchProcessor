//! The TOML loaders and settings-file-relative path resolution. Split from the
//! type definitions in `mod.rs` so the *parsing + startup validation* pass
//! reads on its own. Re-exported from `mod.rs`, so callers still use
//! `crate::settings::load_settings` / `::load_server_config`.

use std::path::{Path, PathBuf};

use anyhow::Context;

use super::{DrofusSource, ServerConfig, Settings};

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

    // A present-but-blank name is a mistake, not a way to say "no name":
    // omitting the key is. Caught here rather than tolerated, since the
    // alternative is every consumer rendering an empty label.
    if let Some(name) = &settings.name {
        if name.trim().is_empty() {
            anyhow::bail!(
                "settings file {} has an empty name — omit the key to display the project under its id",
                path.display()
            );
        }
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
    // Fail fast on malformed or duplicate-named milestones — the name is the
    // identity `/rooms?milestone=` matches on, so two milestones sharing one
    // would silently resolve to the first.
    let mut seen_milestones = std::collections::HashSet::new();
    for milestone in &settings.milestones {
        milestone.validate()?;
        if !seen_milestones.insert(milestone.name.clone()) {
            anyhow::bail!("duplicate milestone name: '{}'", milestone.name);
        }
    }
    // Fail fast on a malformed colour-plan library (>1 active, overlapping
    // bands). Colour plans need no dRofus labels, so — unlike
    // `validate_drofus_fields` which runs later in `bootstrap` — this belongs
    // here alongside the other settings-only validators.
    super::validate_colour_plans(&settings.colour_plans)?;
    Ok(settings)
}

#[cfg(test)]
mod tests {
    use super::*;

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

    /// A settings file with no `name` is legal — the project is then displayed
    /// under its id by every consumer, which is the behaviour that predates
    /// the field.
    #[test]
    fn test_settings_without_name_loads() {
        let dir = std::env::temp_dir().join(format!("roommate-no-name-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let settings_path = dir.join("settings.toml");
        std::fs::write(&settings_path, "project_id = \"p1\"\n").unwrap();

        let settings = load_settings(&settings_path).unwrap();
        assert!(settings.name.is_none());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A present-but-blank `name` fails load: omitting the key is how you say
    /// "no name", so a blank one is a mistake — and tolerating it would have
    /// every consumer render an empty label.
    #[test]
    fn test_blank_name_fails_load_settings() {
        let dir = std::env::temp_dir().join(format!("roommate-blank-name-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let settings_path = dir.join("settings.toml");
        std::fs::write(&settings_path, "project_id = \"p1\"\nname = \"   \"\n").unwrap();

        let result = load_settings(&settings_path);
        assert!(result.is_err());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// `name` survives a TOML round-trip in a position TOML accepts: serde
    /// emits fields in declaration order, so a scalar declared below a table
    /// (`sources`) would serialize into a file that no longer parses.
    #[test]
    fn test_name_round_trips_through_toml() {
        let dir = std::env::temp_dir().join(format!("roommate-name-rt-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let settings_path = dir.join("settings.toml");
        std::fs::write(&settings_path, "project_id = \"p1\"\nname = \"Sample Hospital Job\"\n").unwrap();

        let settings = load_settings(&settings_path).unwrap();
        assert_eq!(settings.name.as_deref(), Some("Sample Hospital Job"));

        let written = toml::to_string_pretty(&settings).unwrap();
        std::fs::write(&settings_path, &written).unwrap();
        let reloaded = load_settings(&settings_path).unwrap();
        assert_eq!(reloaded.name.as_deref(), Some("Sample Hospital Job"));

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Two milestones sharing a name fail `load_settings` — the name is what
    /// `/rooms?milestone=` matches on, so a duplicate would silently resolve
    /// to the first.
    #[test]
    fn test_duplicate_milestone_names_fail_load_settings() {
        let dir = std::env::temp_dir().join(format!("roommate-dup-ms-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let settings_path = dir.join("settings.toml");
        std::fs::write(
            &settings_path,
            r#"
project_id = "p1"

[[milestones]]
name = "Freeze"
date = "2026-06-30"

[[milestones]]
name = "Freeze"
date = "2026-07-30"
"#,
        )
        .unwrap();

        let msg = format!("{:#}", load_settings(&settings_path).unwrap_err());
        assert!(msg.contains("duplicate milestone name"), "message names the problem: {msg}");

        std::fs::remove_dir_all(&dir).ok();
    }
}
