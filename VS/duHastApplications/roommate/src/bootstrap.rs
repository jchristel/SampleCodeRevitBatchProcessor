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

use crate::drofus::{load_drofus_from_bytes, load_drofus_from_path};
use crate::settings::{
    load_server_config, load_settings, validate_drofus_field_shapes, validate_drofus_fields,
    DrofusSource, ServerConfig,
};
use crate::state::{seed_if_test, AppState, ProjectSettings, Shared};
use crate::storage::{FsStore, MemStore, SnapshotStore};

/// Load and fully validate ONE project settings file into its runtime
/// bundle: parse TOML, load the dRofus data when configured (a `file` source
/// reads its CSV path; an `upload` source hydrates the latest stored CSV from
/// the snapshot store — which is why the store is a parameter), validate the
/// `drofus_fields` declarations against it. This is the single validation
/// pipeline for a project file — startup (`load_project_settings_dir`) and
/// the settings API's save both run exactly this, so a file the UI accepts
/// can never fail the next boot.
pub fn load_project_bundle(path: &Path, store: &dyn SnapshotStore) -> anyhow::Result<(String, bool, ProjectSettings)> {
    let settings = load_settings(&path.to_path_buf()).with_context(|| format!("bad settings file: {}", path.display()))?;

    // dRofus is optional per project: load and validate only when a
    // source is configured. `drofus_fields` declarations with *no* dRofus
    // source are a config mistake (they describe columns of a source that
    // isn't there) — fail loudly, same discipline as
    // `validate_drofus_fields`' unknown-label check.
    let drofus = match &settings.sources.drofus {
        Some(DrofusSource::File { path: csv_path }) => {
            let drofus = load_drofus_from_path(csv_path)
                .with_context(|| format!("bad dRofus source in {}", path.display()))?;

            // Can't validate this inside `load_settings`: the dRofus CSV (and its
            // label set) isn't loaded until the line above, one step later.
            validate_drofus_fields(&settings.drofus_fields, &drofus.all_labels)
                .with_context(|| format!("bad drofus_fields in {}", path.display()))?;
            Some(drofus)
        }
        Some(DrofusSource::Upload) => match store.get_latest_drofus(&settings.project_id)? {
            Some((taken_at, bytes)) => {
                // A stored CSV that fails to parse fails the boot loudly —
                // same discipline as a rotted `file` CSV. The upload endpoint
                // validates before storing, so this is only reachable by
                // hand-editing the store.
                let drofus = load_drofus_from_bytes(&bytes).with_context(|| {
                    format!(
                        "bad stored dRofus upload {} for project '{}' (referenced by {})",
                        taken_at,
                        settings.project_id,
                        path.display()
                    )
                })?;
                validate_drofus_fields(&settings.drofus_fields, &drofus.all_labels)
                    .with_context(|| format!("bad drofus_fields in {}", path.display()))?;
                Some(drofus)
            }
            // No upload yet: a legitimate "not configured yet" state, not an
            // error. The label set is unknowable, so only the label-free half
            // of the field validation can run.
            None => {
                validate_drofus_field_shapes(&settings.drofus_fields)
                    .with_context(|| format!("bad drofus_fields in {}", path.display()))?;
                None
            }
        },
        None => {
            if !settings.drofus_fields.is_empty() {
                anyhow::bail!(
                    "{} declares drofus_fields but no [sources.drofus] — \
                     remove the declarations or configure the source",
                    path.display()
                );
            }
            None
        }
    };

    let bundle = ProjectSettings {
        drofus,
        hierarchy: settings.hierarchy,
        builtin_properties: settings.builtin_properties,
        room_label: settings.room_label,
        drofus_fields: settings.drofus_fields,
        milestones: settings.milestones,
        comparison_key: settings.comparison_key,
        comparison_properties: settings.comparison_properties,
        hierarchy_exclusions: settings.hierarchy_exclusions,
    };
    Ok((settings.project_id, settings.is_default, bundle))
}

/// Load and validate every `*.toml` file directly inside `projects_dir` (not
/// recursive) into a project-id-keyed registry, plus the explicit default
/// bundle if exactly one file sets `is_default = true`. Fails the whole
/// startup on: a malformed file, a duplicate `project_id` across files, or
/// more than one file claiming `is_default` -- same "loud startup error over
/// a silent no-op" discipline `load_settings` already uses for hierarchy
/// tiers and builtin properties. Also re-run by the settings API after a
/// save, to build the registry it hot-swaps in.
pub fn load_project_settings_dir(
    projects_dir: &Path,
    store: &dyn SnapshotStore,
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

        let (project_id, is_default, bundle) = load_project_bundle(&path, store)?;
        tracing::info!("project settings loaded from {} (project_id = {})", path.display(), project_id);

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

    // Pick the backend from config: a `[storage]` root → persistent FsStore,
    // otherwise the volatile MemStore (dev/test). Both satisfy SnapshotStore, so
    // this is the only line that knows which one is running. Constructed BEFORE
    // the project bundles load, because an `upload`-sourced project hydrates
    // its dRofus data from this store.
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

    let (project_settings, default_settings) = load_project_settings_dir(projects_dir, store.as_ref())
        .with_context(|| format!("bad project settings directory: {}", projects_dir.display()))?;

    if project_settings.is_empty() && default_settings.is_none() {
        tracing::warn!("no project settings files found in {} -- every read/ingest will be rejected/skipped until one is added", projects_dir.display());
    }

    let state: Shared = Arc::new(
        AppState::new(store, project_settings, default_settings).with_projects_dir(projects_dir.clone()),
    );

    seed_if_test(&state, test_data.as_ref())?;

    Ok(state)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp_projects_dir(tag: &str) -> std::path::PathBuf {
        let dir = std::env::temp_dir().join(format!("roommate-bootstrap-{}-{}", tag, std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    /// A project with no `[sources]` at all registers with `drofus: None` —
    /// the state `compute_project_validation` reports as
    /// `drofus_configured: false`.
    #[test]
    fn test_project_without_sources_registers_with_no_drofus() {
        let dir = temp_projects_dir("no-sources");
        std::fs::write(dir.join("p1.toml"), "project_id = \"p1\"\n").unwrap();

        let (registry, _default) = load_project_settings_dir(&dir, &MemStore::new()).unwrap();
        assert!(registry.get("p1").unwrap().drofus.is_none());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// `drofus_fields` declarations without a dRofus source are a config
    /// mistake — declarations for a source that isn't there — and must fail
    /// startup loudly, not be silently carried along.
    #[test]
    fn test_drofus_fields_without_source_fails_startup() {
        let dir = temp_projects_dir("fields-no-source");
        std::fs::write(
            dir.join("p1.toml"),
            "project_id = \"p1\"\n\n[[drofus_fields]]\nlabel = \"NetArea\"\nqa = \"exact\"\n",
        )
        .unwrap();

        let msg = match load_project_settings_dir(&dir, &MemStore::new()) {
            Err(err) => format!("{err:#}"),
            Ok(_) => panic!("expected startup failure for drofus_fields without a source"),
        };
        assert!(msg.contains("drofus_fields"), "message names the problem: {msg}");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// An `upload`-sourced project with no upload yet registers with
    /// `drofus: None` — a legitimate not-configured-yet state — and its
    /// `drofus_fields` are accepted on their label-free shape checks alone.
    #[test]
    fn test_upload_source_with_empty_store_registers_without_drofus() {
        let dir = temp_projects_dir("upload-empty");
        std::fs::write(
            dir.join("p1.toml"),
            "project_id = \"p1\"\n\n[sources.drofus]\ntype = \"upload\"\n\n[[drofus_fields]]\nlabel = \"NetArea\"\nqa = \"exact\"\n",
        )
        .unwrap();

        let (registry, _default) = load_project_settings_dir(&dir, &MemStore::new()).unwrap();
        let bundle = registry.get("p1").unwrap();
        assert!(bundle.drofus.is_none());
        assert_eq!(bundle.drofus_fields.len(), 1, "field declarations carried along for later");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// An `upload`-sourced project's shape checks still run with no data: a
    /// `date` field without a `format` is rejectable without knowing labels.
    #[test]
    fn test_upload_source_shape_validation_runs_without_data() {
        let dir = temp_projects_dir("upload-shape");
        std::fs::write(
            dir.join("p1.toml"),
            "project_id = \"p1\"\n\n[sources.drofus]\ntype = \"upload\"\n\n[[drofus_fields]]\nlabel = \"Updated\"\ntype = \"date\"\n",
        )
        .unwrap();

        let msg = match load_project_settings_dir(&dir, &MemStore::new()) {
            Err(err) => format!("{err:#}"),
            Ok(_) => panic!("expected failure: date field with no format"),
        };
        assert!(msg.contains("format"), "message names the problem: {msg}");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// An `upload`-sourced project with a stored CSV hydrates it as its
    /// dRofus data, and `drofus_fields` labels are validated against it.
    #[test]
    fn test_upload_source_hydrates_latest_stored_csv() {
        let dir = temp_projects_dir("upload-hydrate");
        std::fs::write(
            dir.join("p1.toml"),
            "project_id = \"p1\"\n\n[sources.drofus]\ntype = \"upload\"\n\n[[drofus_fields]]\nlabel = \"NetArea\"\nqa = \"exact\"\n",
        )
        .unwrap();

        let store = MemStore::new();
        store
            .put_drofus("p1", "2026-01-01T10:00:00Z", b"DrofusRoomId,NetArea\nNumber,Area\n1,25.5\n")
            .unwrap();

        let (registry, _default) = load_project_settings_dir(&dir, &store).unwrap();
        let drofus = registry.get("p1").unwrap().drofus.as_ref().expect("hydrated");
        assert_eq!(drofus.link_property, "Number");
        assert_eq!(drofus.by_id["1"].fields.get("NetArea"), Some(&"25.5".to_string()));

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A stored CSV whose labels don't cover the declared `drofus_fields`
    /// fails the load loudly — same discipline as a `file` source.
    #[test]
    fn test_upload_source_label_mismatch_fails_loudly() {
        let dir = temp_projects_dir("upload-mismatch");
        std::fs::write(
            dir.join("p1.toml"),
            "project_id = \"p1\"\n\n[sources.drofus]\ntype = \"upload\"\n\n[[drofus_fields]]\nlabel = \"NoSuchColumn\"\nqa = \"exact\"\n",
        )
        .unwrap();

        let store = MemStore::new();
        store
            .put_drofus("p1", "2026-01-01T10:00:00Z", b"DrofusRoomId,NetArea\nNumber,Area\n1,25.5\n")
            .unwrap();

        let msg = match load_project_settings_dir(&dir, &store) {
            Err(err) => format!("{err:#}"),
            Ok(_) => panic!("expected failure: drofus_fields label not in stored CSV"),
        };
        assert!(msg.contains("NoSuchColumn"), "message names the label: {msg}");

        std::fs::remove_dir_all(&dir).ok();
    }
}
