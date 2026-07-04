//! Shared application state.
//!
//! State no longer owns the store's *mechanism* — it holds a
//! `Box<dyn SnapshotStore>` and delegates. Whether snapshots live on disk
//! (`FsStore`) or in memory (`MemStore`) is chosen once at startup from config;
//! nothing here or in the handlers changes when that choice changes. A database
//! backend later is a third impl, same seam.
//!
//! `ModelKey` lives here (not in `storage`) because it's the shared identity
//! both state and storage key on; keeping it here avoids a state↔storage import
//! cycle.

use std::sync::Arc;

use anyhow::Context;

use crate::contract::RoomPayload;
use crate::drofus::DrofusData;
use crate::settings::{BuiltinPropertyDef, HierarchyTier, TestData};
use crate::storage::SnapshotStore;

/// Composite key identifying one storage bucket: a model within a project.
///
/// Keyed on the *ids* (immutable, machine-chosen — the Revit GUID and the
/// project's stable key), never the display names, so renaming in Revit can't
/// fork the record. Room ids are only unique *within* a model, which is exactly
/// why the model half of this key must exist — it disambiguates the same raw
/// room id appearing in two linked models.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct ModelKey {
    pub project_id: String,
    pub model_id: String,
}

impl ModelKey {
    /// Pull the key out of a payload's identity envelope. Centralised so every
    /// call site keys the same way — state and storage agree on "the key".
    pub fn from_payload(payload: &RoomPayload) -> Self {
        Self {
            project_id: payload.project.id.clone(),
            model_id: payload.model.id.clone(),
        }
    }
}

/// Shared application state: the snapshot store plus the read-only join/classify
/// inputs resolved at startup.
pub struct AppState {
    /// The snapshot store, behind the trait so the backend is swappable.
    store: Box<dyn SnapshotStore>,

    /// Resolved dRofus data, loaded once at startup. Joined onto rooms at
    /// response assembly — a stored snapshot is never mutated by the join.
    pub drofus: Option<DrofusData>,

    /// Classification tiers loaded from settings. Resolved per-room inside
    /// `/rooms` assembly; not cached (see classify_room).
    pub hierarchy: Vec<HierarchyTier>,

    /// Canonical → per-source raw property name mappings loaded from
    /// settings. Passed to `lookup_property` alongside each room's source so
    /// dRofus join and classification resolve names consistently regardless
    /// of which producer the room came from.
    pub builtin_properties: Vec<BuiltinPropertyDef>,
}

impl AppState {
    pub fn new(
        store: Box<dyn SnapshotStore>,
        drofus: DrofusData,
        hierarchy: Vec<HierarchyTier>,
        builtin_properties: Vec<BuiltinPropertyDef>,
    ) -> Self {
        Self { store, drofus: Some(drofus), hierarchy, builtin_properties }
    }

    /// Store a pushed payload. Upsert semantics live in the store impl; state
    /// just forwards. Shared by the push handler and the startup seed so the two
    /// paths can't drift.
    pub fn set_snapshot(&self, payload: RoomPayload) -> anyhow::Result<()> {
        self.store.put(&payload)
    }

    /// Every model's latest snapshot, for the `/rooms` merge.
    pub fn all_snapshots(&self) -> anyhow::Result<Vec<(ModelKey, RoomPayload)>> {
        self.store.all_latest()
    }
}

pub type Shared = Arc<AppState>;

pub fn seed_if_test(state: &AppState, test_data: Option<&TestData>) -> anyhow::Result<()> {
    if let Some(test) = test_data {
        let raw = std::fs::read_to_string(&test.snapshot_path).with_context(|| {
            format!(
                "could not read test snapshot: {}",
                test.snapshot_path.display()
            )
        })?;
        // Parse into the same type the push handler accepts — seed and push
        // converge on one representation and can never drift.
        let snapshot: RoomPayload =
            serde_json::from_str(&raw).context("failed to parse test snapshot JSON")?;
        state.set_snapshot(snapshot)?;
        tracing::info!("seeded snapshot from {}", test.snapshot_path.display());
    }
    Ok(())
}
