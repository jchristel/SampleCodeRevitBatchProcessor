//! Settings file path -> a running `Shared` state. The one place that knows
//! how to turn a TOML settings file into a live `AppState`: load settings,
//! load dRofus, validate `drofus_fields` against it, pick the storage
//! backend, and seed dev/test data. Shared verbatim by both binaries
//! (`main.rs`'s HTTP server and `bin/mcp.rs`'s MCP server) so they can't
//! drift on this wiring -- a change to how the store backend is chosen, for
//! instance, only has one call site to update.

use std::path::PathBuf;
use std::sync::Arc;

use anyhow::Context;

use crate::drofus::load_drofus;
use crate::settings::{load_settings, validate_drofus_fields, Settings};
use crate::state::{seed_if_test, AppState, Shared};
use crate::storage::{FsStore, MemStore, SnapshotStore};

pub fn build_state(settings_path: &PathBuf) -> anyhow::Result<Shared> {
    let settings = load_settings(settings_path)
        .with_context(|| format!("bad settings file: {}", settings_path.display()))?;

    tracing::info!("settings loaded from {}", settings_path.display());

    let Settings {
        sources,
        storage,
        test_data,
        hierarchy,
        builtin_properties,
        room_label,
        drofus_fields,
    } = settings;
    let drofus = load_drofus(&sources.drofus)?;

    // Can't validate this inside `load_settings`: the dRofus CSV (and its
    // label set) isn't loaded until the line above, one step later.
    validate_drofus_fields(&drofus_fields, &drofus.all_labels).context("bad drofus_fields in settings file")?;

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

    let state: Shared = Arc::new(AppState::new(
        store,
        drofus,
        hierarchy,
        builtin_properties,
        room_label,
        drofus_fields,
    ));

    seed_if_test(&state, test_data.as_ref())?;

    Ok(state)
}
