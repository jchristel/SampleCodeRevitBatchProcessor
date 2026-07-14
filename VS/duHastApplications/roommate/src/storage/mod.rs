//! Snapshot persistence, behind a trait so the backing store is swappable.
//!
//! The whole point of this module is the `SnapshotStore` trait: handlers and
//! `AppState` talk to *it*, never to the filesystem directly. Today the impl is
//! `FsStore` (a directory tree); tomorrow it could be a database — a new impl,
//! no change to callers. Same seam discipline as `DrofusSource`.
//!
//! The two impls live in their own files behind this module — `fs` (`FsStore`)
//! and `mem` (`MemStore`) — re-exported here so `crate::storage::FsStore` /
//! `crate::storage::MemStore` stay the public paths regardless of the split.
//! The trait, the manifest types, and the reserved-dir constant stay here,
//! since both impls depend on them.
//!
//! On-disk layout (STRATEGY.md project → model → snapshot):
//!
//! ```text
//! <root>/
//!   <project-guid>/
//!     project.toml          authoritative: project name + known models
//!     drofus/               reserved (never a model id): uploaded dRofus CSVs
//!       <snapshot-ts>.csv   one file per upload — history kept, never overwritten
//!     <model-guid>/
//!       <snapshot-ts>.json  one file per push — history kept, never overwritten
//! ```
//!
//! `project.toml` is **authoritative and two-way**: the server reads it to know
//! what exists and rewrites it on every push (upsert). A push for an unknown
//! project or model *creates* the structure rather than rejecting it — the store
//! grows from pushes.
//!
//! History is kept: every snapshot lands in its own timestamped file. Pruning is
//! a future UI concern (select-and-delete), not an ingest-time decision.

use std::collections::BTreeMap;

use anyhow::Result;
use serde::{Deserialize, Serialize};

use crate::contract::RoomPayload;
use crate::state::ModelKey;

mod fs;
mod mem;

pub use fs::FsStore;
pub use mem::MemStore;

/// Reserved subdirectory name inside a project dir for uploaded dRofus CSVs.
/// Never treated as a model dir — `list_models` skips it explicitly. (Model
/// ids are Revit GUIDs in practice, so a real collision is implausible; the
/// skip makes it impossible.)
pub const DROFUS_DIR: &str = "drofus";

// ---------- project.toml ----------

/// The authoritative per-project manifest, one `project.toml` per project dir.
/// Lists the project's display name and every model seen under it. Rewritten on
/// each push so it always reflects the models actually on disk.
///
/// It intentionally duplicates the `name` the snapshot envelope also carries:
/// the manifest is the *index* (readable without opening any snapshot), the
/// envelope is the per-push record. On conflict the latest push wins and updates
/// the manifest.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProjectManifest {
    /// Project display name (mutable; the GUID dir name is the stable identity).
    pub name: String,
    /// Known models under this project, keyed by model GUID.
    #[serde(default)]
    pub models: BTreeMap<String, ModelEntry>,
    /// Snapshot ids (raw `taken_at` values) of uploaded dRofus CSVs, ascending.
    /// Project-scoped, not model-scoped: dRofus is reference data joined onto
    /// every model's rooms, so it hangs off the manifest directly rather than
    /// a `ModelEntry`. Same index role (and same `default` back-compat rule)
    /// as `ModelEntry::snapshots`.
    #[serde(default)]
    pub drofus_snapshots: Vec<String>,
}

/// One model's entry in a `ProjectManifest`.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ModelEntry {
    /// Model display name (mutable; the GUID dir name is the stable identity).
    pub name: String,
    /// Snapshot ids (raw `taken_at` values) stored for this model, ascending.
    /// The manifest's index role extended to snapshots: listing a model's
    /// history reads this, never the (possibly >100 MB) snapshot JSONs.
    /// `default` keeps manifests written before this field existed parseable —
    /// their history is recovered from the directory instead (filesystem wins,
    /// see `list_snapshot_ids`).
    #[serde(default)]
    pub snapshots: Vec<String>,
}

// ---------- the trait ----------

/// Abstract snapshot store. Callers depend only on this; the concrete backend
/// (filesystem now, a database later) is chosen once at startup.
///
/// `put` is an **upsert**: it creates whatever project/model structure is
/// missing, then stores the snapshot. It never rejects an unknown id — a push
/// defines new structure. On a duplicate `taken_at`, a history-keeping store
/// (`FsStore`) **skips with a warning** rather than overwrite — a re-sent
/// payload must not silently destroy the record it duplicates. `MemStore`
/// keeps no history at all (latest-only, by design), so replacement *is* its
/// normal upsert and the skip rule doesn't apply.
pub trait SnapshotStore: Send + Sync {
    /// Persist one pushed payload, creating project/model structure as needed.
    fn put(&self, payload: &RoomPayload) -> Result<()>;

    /// Latest snapshot for a model, if any. (Latest = newest by snapshot key.)
    fn get_latest(&self, key: &ModelKey) -> Result<Option<RoomPayload>>;

    /// Every model key the store knows about — the index question. For
    /// `FsStore` this is answered by the `project.toml` manifests (the
    /// manifest is the index, snapshots are the record), reconciled against
    /// the directory tree.
    fn list_models(&self) -> Result<Vec<ModelKey>>;

    /// Every model's latest snapshot, for the merge that `/rooms` currently does.
    fn all_latest(&self) -> Result<Vec<(ModelKey, RoomPayload)>>;

    /// Every snapshot id (`taken_at`) stored for one model, ascending — so the
    /// latest is the last element. Empty when the model is unknown or has no
    /// snapshots yet. A history-less store (`MemStore`) reports just its
    /// current latest.
    fn list_snapshot_ids(&self, key: &ModelKey) -> Result<Vec<String>>;

    /// One specific stored snapshot by its id (`taken_at`), or `None` when no
    /// such snapshot exists — the milestone read path. A history-less store
    /// (`MemStore`) can only answer for its current latest.
    fn get_snapshot(&self, key: &ModelKey, taken_at: &str) -> Result<Option<RoomPayload>>;

    /// Store one uploaded dRofus CSV against a project. Returns `false` when
    /// a dRofus snapshot with this `taken_at` already exists — skipped with a
    /// warning, never overwritten, same duplicate rule as `put`. The caller
    /// is expected to have *validated the CSV before storing it*: a stored
    /// CSV is hydrated at every boot, so a bad one stored here fails the next
    /// startup loudly.
    fn put_drofus(&self, project_id: &str, taken_at: &str, csv: &[u8]) -> Result<bool>;

    /// Every dRofus snapshot id (`taken_at`) stored for one project,
    /// ascending — latest is the last element. Empty when the project is
    /// unknown or has no uploads yet. A history-less store (`MemStore`)
    /// reports just its current latest.
    fn list_drofus_snapshot_ids(&self, project_id: &str) -> Result<Vec<String>>;

    /// One stored dRofus CSV by its snapshot id, or `None`.
    fn get_drofus(&self, project_id: &str, taken_at: &str) -> Result<Option<Vec<u8>>>;

    /// The newest stored dRofus CSV with its id — the bootstrap hydration
    /// read that turns an `Upload`-sourced project's stored data into its
    /// in-memory `DrofusData`.
    fn get_latest_drofus(&self, project_id: &str) -> Result<Option<(String, Vec<u8>)>>;
}
