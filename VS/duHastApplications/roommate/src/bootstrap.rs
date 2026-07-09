//! Settings file paths -> a running `Shared` state. The one place that knows
//! how to turn a server-settings file plus a directory of per-project
//! settings files into a live `AppState`: load each project's settings, load
//! its dRofus data, validate its `drofus_fields` against it, register it
//! under its project id, pick the storage backend, and seed dev/test data.
//! Shared verbatim by both binaries (`main.rs`'s HTTP server and
//! `bin/mcp.rs`'s MCP server) so they can't drift on this wiring -- a change
//! to how the store backend is chosen, for instance, only has one call site
//! to update.
//!
//! See HANDOVER-per-project-settings.md: settings moved from one-per-process
//! to one-per-project, while `[storage]`/`[test_data]` (server-wide, not tied
//! to any one project) stayed behind in their own `ServerConfig` file.

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::Context;

use crate::drofus::load_drofus;
use crate::settings::{load_server_config, load_settings, validate_drofus_fields, ServerConfig};
use crate::state::{seed_if_test, AppState, ProjectSettings, Shared};
use crate::storage::{FsStore, MemStore, SnapshotStore};

/// Load and validate every `*.toml` file directly inside `projects_dir` (not
/// recursive) into a project-id-keyed registry, plus the explicit default
/// bundle if exactly one file sets `is_default = true`. Fails the whole
/// startup on: a malformed file, a duplicate `project_id` across files, or
/// more than one file claiming `is_default` -- same "loud startup error over
/// a silent no-op" discipline `load_settings` already uses for hierarchy
/// tiers and builtin properties.
fn load_project_settings_dir(
    projects_dir: &Path,
) -> anyhow::Result<(HashMap<String, ProjectSettings>, Option<ProjectSettings>)> {
    let mut registry = HashMap::new();
    let mut default_bundle: Option<(String, ProjectSettings)> = None;

    let entries = std::fs::read_dir(projects_dir)
        .with_context(|| format!("could not read project settings directory: {}", projects_dir.display()))?;

    for entry in entries {
        let entry = entry.with_context(|| format!("could not read entry in {}", projects_dir.display()))?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("toml") {
            continue; // not a settings file (e.g. a stray drofus.csv sitting alongside)
        }

        let settings = load_settings(&path).with_context(|| format!("bad settings file: {}", path.display()))?;
        tracing::info!("project settings loaded from {} (project_id = {})", path.display(), settings.project_id);

        let drofus = load_drofus(&settings.sources.drofus)
            .with_context(|| format!("bad dRofus source in {}", path.display()))?;

        // Can't validate this inside `load_settings`: the dRofus CSV (and its
        // label set) isn't loaded until the line above, one step later.
        validate_drofus_fields(&settings.drofus_fields, &drofus.all_labels)
            .with_context(|| format!("bad drofus_fields in {}", path.display()))?;

        let project_id = settings.project_id.clone();
        let is_default = settings.is_default;
        let bundle = ProjectSettings {
            drofus: Some(drofus),
            hierarchy: settings.hierarchy,
            builtin_properties: settings.builtin_properties,
            room_label: settings.room_label,
            drofus_fields: settings.drofus_fields,
        };

        if is_default {
            if let Some((other_id, _)) = &default_bundle {
                anyhow::bail!(
                    "more than one project settings file sets is_default = true: '{}' and '{}'",
                    other_id,
                    project_id
                );
            }
            default_bundle = Some((project_id.clone(), bundle.clone()));
        }

        if registry.insert(project_id.clone(), bundle).is_some() {
            anyhow::bail!("duplicate project_id across settings files: '{}'", project_id);
        }
    }

    Ok((registry, default_bundle.map(|(_, b)| b)))
}

pub fn build_state(server_settings: &PathBuf, projects_dir: &PathBuf) -> anyhow::Result<Shared> {
    let ServerConfig { storage, test_data } = load_server_config(server_settings)
        .with_context(|| format!("bad server settings file: {}", server_settings.display()))?;
    tracing::info!("server settings loaded from {}", server_settings.display());

    let (project_settings, default_settings) = load_project_settings_dir(projects_dir)
        .with_context(|| format!("bad project settings directory: {}", projects_dir.display()))?;

    if project_settings.is_empty() && default_settings.is_none() {
        tracing::warn!("no project settings files found in {} -- every read/ingest will be rejected/skipped until one is added", projects_dir.display());
    }

    // Pick the backend from config: a `[storage]` root → persistent FsStore,
    // otherwise the volatile MemStore (dev/test). Both satisfy SnapshotStore, so
    // this is the only line that knows which one is running.
    let store: Box<dyn SnapshotStore> = match storage {
        Some(cfg) => {
            tracing::info!("persistent storage at {}", cfg.root.display());
            Box::new(FsStore::new(cfg.root)?)
        }
        None => {
            tracing::info!("no [storage] configured — using in-memory store");
            Box::new(MemStore::new())
        }
    };

    let state: Shared = Arc::new(AppState::new(store, project_settings, default_settings));

    seed_if_test(&state, test_data.as_ref())?;

    Ok(state)
}
