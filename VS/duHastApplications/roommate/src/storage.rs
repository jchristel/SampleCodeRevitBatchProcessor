//! Snapshot persistence, behind a trait so the backing store is swappable.
//!
//! The whole point of this module is the `SnapshotStore` trait: handlers and
//! `AppState` talk to *it*, never to the filesystem directly. Today the impl is
//! `FsStore` (a directory tree); tomorrow it could be a database — a new impl,
//! no change to callers. Same seam discipline as `DrofusSource`.
//!
//! On-disk layout (STRATEGY.md project → model → snapshot):
//!
//! ```text
//! <root>/
//!   <project-guid>/
//!     project.toml          authoritative: project name + known models
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
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

use crate::contract::RoomPayload;
use crate::state::ModelKey;

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
}

/// One model's entry in a `ProjectManifest`.
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ModelEntry {
    /// Model display name (mutable; the GUID dir name is the stable identity).
    pub name: String,
}

// ---------- the trait ----------

/// Abstract snapshot store. Callers depend only on this; the concrete backend
/// (filesystem now, a database later) is chosen once at startup.
///
/// `put` is an **upsert**: it creates whatever project/model structure is
/// missing, then stores the snapshot. It never rejects an unknown id — a push
/// defines new structure. A snapshot that already exists for the same
/// `taken_at` is **skipped with a warning**, never overwritten: history is
/// kept, and a re-sent payload must not silently destroy the record it
/// duplicates.
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
}

// ---------- filesystem impl ----------

/// Filesystem-backed store rooted at a configured directory.
///
/// Stateless beyond the root path: every call recomputes paths and touches disk,
/// so the on-disk tree is the single source of truth (no in-memory cache to keep
/// in sync). Fine at single-user scale; a caching layer is a later optimisation
/// if disk reads on `/rooms` ever bite.
pub struct FsStore {
    root: PathBuf,
}

impl FsStore {
    /// Bind to a root dir, creating it if absent. Fail fast on an unwritable
    /// root — same startup-loud contract as the rest of config.
    pub fn new(root: PathBuf) -> Result<Self> {
        fs::create_dir_all(&root)
            .with_context(|| format!("could not create storage root: {}", root.display()))?;
        Ok(Self { root })
    }

    fn project_dir(&self, project_id: &str) -> PathBuf {
        self.root.join(project_id)
    }

    fn manifest_path(&self, project_id: &str) -> PathBuf {
        self.project_dir(project_id).join("project.toml")
    }

    fn model_dir(&self, project_id: &str, model_id: &str) -> PathBuf {
        self.project_dir(project_id).join(model_id)
    }

    /// Read a project's manifest, or a default (empty) one if it doesn't exist
    /// yet — an absent manifest just means "first push for this project".
    fn read_manifest(&self, project_id: &str) -> Result<ProjectManifest> {
        let path = self.manifest_path(project_id);
        if !path.exists() {
            return Ok(ProjectManifest::default());
        }
        let raw = fs::read_to_string(&path)
            .with_context(|| format!("could not read manifest: {}", path.display()))?;
        toml::from_str(&raw).with_context(|| format!("malformed manifest: {}", path.display()))
    }

    fn write_manifest(&self, project_id: &str, manifest: &ProjectManifest) -> Result<()> {
        let path = self.manifest_path(project_id);
        let toml = toml::to_string_pretty(manifest).context("could not serialise manifest")?;
        fs::write(&path, toml)
            .with_context(|| format!("could not write manifest: {}", path.display()))
    }

    /// Snapshot filename from the payload's timestamp. The `taken_at` is an
    /// ISO-8601 string; `:` is illegal on some filesystems, so sanitise it to a
    /// safe, still-sortable form before using it as a filename.
    fn snapshot_filename(taken_at: &str) -> String {
        format!("{}.json", taken_at.replace(':', "-"))
    }

    /// The most recent snapshot file in a model dir, by lexical name order.
    /// Timestamp filenames sort chronologically, so lexical-max = newest.
    fn latest_snapshot_file(dir: &Path) -> Result<Option<PathBuf>> {
        if !dir.exists() {
            return Ok(None);
        }
        let mut newest: Option<PathBuf> = None;
        for entry in fs::read_dir(dir)
            .with_context(|| format!("could not read model dir: {}", dir.display()))?
        {
            let path = entry?.path();
            // Only snapshot files count; skips anything non-`.json` in the dir.
            if path.extension().and_then(|e| e.to_str()) == Some("json") {
                // Keep the lexically-largest path. `map_or(true, …)` seeds the
                // first match (None → take it), then compares subsequent paths.
                if newest.as_ref().map_or(true, |n| path > *n) {
                    newest = Some(path);
                }
            }
        }
        Ok(newest)
    }

    fn read_payload(path: &Path) -> Result<RoomPayload> {
        let raw = fs::read_to_string(path)
            .with_context(|| format!("could not read snapshot: {}", path.display()))?;
        serde_json::from_str(&raw)
            .with_context(|| format!("malformed snapshot: {}", path.display()))
    }
}

impl SnapshotStore for FsStore {
    fn put(&self, payload: &RoomPayload) -> Result<()> {
        // Upsert: one path handles all three cases — unknown project, unknown
        // model under a known project, or a re-push of a known model. `create_dir_all`
        // and the manifest `entry(...).or_default()` are each idempotent, so no
        // branching on "does this exist yet" is needed.
        let project_id = &payload.project.id;
        let model_id = &payload.model.id;

        // 1. Ensure the model dir exists. `create_dir_all` also makes the parent
        //    project dir when the project is brand new — the unknown-project case.
        let model_dir = self.model_dir(project_id, model_id);
        fs::create_dir_all(&model_dir)
            .with_context(|| format!("could not create model dir: {}", model_dir.display()))?;

        // 2. Upsert the authoritative manifest: refresh the project display name,
        //    and insert this model if absent (`or_default` = the unknown-model
        //    case) before updating its name. Rewritten every push so the manifest
        //    always mirrors what's on disk.
        let mut manifest = self.read_manifest(project_id)?;
        manifest.name = payload.project.name.clone();
        manifest
            .models
            .entry(model_id.clone())
            .or_default()
            .name = payload.model.name.clone();
        self.write_manifest(project_id, &manifest)?;

        // 3. Write the snapshot under its own timestamped filename — never
        //    overwriting a prior one, so the model dir accumulates full history.
        //    A same-`taken_at` re-push is skipped, not overwritten: the client
        //    stamps sub-second precision, so a collision means a genuinely
        //    re-sent payload, and even that must not silently destroy history.
        let file = model_dir.join(Self::snapshot_filename(&payload.snapshot.taken_at));
        if file.exists() {
            tracing::warn!("snapshot already exists, skipping: {}", file.display());
            return Ok(());
        }
        let json = serde_json::to_string_pretty(payload).context("could not serialise snapshot")?;
        fs::write(&file, json)
            .with_context(|| format!("could not write snapshot: {}", file.display()))?;

        tracing::info!(
            "stored snapshot {}/{} @ {}",
            project_id,
            model_id,
            payload.snapshot.taken_at
        );
        Ok(())
    }

    fn get_latest(&self, key: &ModelKey) -> Result<Option<RoomPayload>> {
        let dir = self.model_dir(&key.project_id, &key.model_id);
        match Self::latest_snapshot_file(&dir)? {
            Some(path) => Ok(Some(Self::read_payload(&path)?)),
            None => Ok(None),
        }
    }

    fn list_models(&self) -> Result<Vec<ModelKey>> {
        let mut out = Vec::new();
        if !self.root.exists() {
            return Ok(out);
        }
        for project in fs::read_dir(&self.root)? {
            let project_dir = project?.path();
            if !project_dir.is_dir() {
                continue;
            }
            // Dir name *is* the project GUID — display names live in the
            // manifest, identity lives in the path.
            let project_id = match project_dir.file_name().and_then(|n| n.to_str()) {
                Some(id) => id.to_string(),
                None => continue, // non-UTF-8 dir name: not one of ours, skip
            };

            // The manifest is the index: one key per `models` entry. But the
            // snapshots are the record, so a model dir the manifest doesn't
            // list is a manifest bug, not invisible data — warn (making the
            // drift noticeable) and include it anyway: filesystem truth wins.
            let manifest = self.read_manifest(&project_id)?;
            let mut model_ids: Vec<String> = manifest.models.keys().cloned().collect();
            for model in fs::read_dir(&project_dir)? {
                let model_dir = model?.path();
                if !model_dir.is_dir() {
                    continue; // skips project.toml (a file, not a model dir)
                }
                let model_id = match model_dir.file_name().and_then(|n| n.to_str()) {
                    Some(id) => id.to_string(),
                    None => continue,
                };
                if !manifest.models.contains_key(&model_id) {
                    tracing::warn!(
                        "model dir {}/{} is missing from project.toml — including it anyway (filesystem wins)",
                        project_id,
                        model_id
                    );
                    model_ids.push(model_id);
                }
            }

            out.extend(model_ids.into_iter().map(|model_id| ModelKey { project_id: project_id.clone(), model_id }));
        }
        Ok(out)
    }

    fn all_latest(&self) -> Result<Vec<(ModelKey, RoomPayload)>> {
        // The manifest-backed index supplies the keys, `get_latest` reads each
        // key's newest snapshot — the manifest is the index, the snapshots the
        // record, exactly as the module doc claims. A manifest entry whose dir
        // holds no snapshots yet (or was deleted by hand) simply yields
        // nothing for that key.
        let mut out = Vec::new();
        for key in self.list_models()? {
            if let Some(payload) = self.get_latest(&key)? {
                out.push((key, payload));
            }
        }
        Ok(out)
    }
}

// ---------- in-memory impl ----------

/// In-memory store: the pre-persistence behaviour, kept for tests and for a
/// `[storage]`-less config. Latest-only per model (no history) — history is a
/// disk affordance, not worth reproducing in the volatile store.
#[derive(Default)]
pub struct MemStore {
    latest: Mutex<BTreeMap<ModelKey, RoomPayload>>,
}

impl MemStore {
    pub fn new() -> Self {
        Self::default()
    }
}

impl SnapshotStore for MemStore {
    fn put(&self, payload: &RoomPayload) -> Result<()> {
        let key = ModelKey::from_payload(payload);
        self.latest.lock().unwrap().insert(key, payload.clone());
        Ok(())
    }

    fn get_latest(&self, key: &ModelKey) -> Result<Option<RoomPayload>> {
        Ok(self.latest.lock().unwrap().get(key).cloned())
    }

    fn list_models(&self) -> Result<Vec<ModelKey>> {
        Ok(self.latest.lock().unwrap().keys().cloned().collect())
    }

    fn all_latest(&self) -> Result<Vec<(ModelKey, RoomPayload)>> {
        Ok(self
            .latest
            .lock()
            .unwrap()
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Model, Project, RoomPayload, Snapshot};

    fn payload(project: &str, model: &str, ts: &str) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project.into(), name: "P".into() },
            model: Model { id: model.into(), name: "M".into(), source: "revit".into() },
            snapshot: Snapshot { taken_at: ts.into() },
            levels: vec![],
            rooms: vec![],
        }
    }

    /// Two models under one project don't overwrite; each keeps its own latest.
    #[test]
    fn test_fs_store_keeps_models_separate() {
        let dir = std::env::temp_dir().join(format!("roommate-test-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("proj1", "modelA", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("proj1", "modelB", "2026-01-01T11:00:00Z")).unwrap();

        let all = store.all_latest().unwrap();
        assert_eq!(all.len(), 2);

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A newer snapshot is returned as latest, older one still on disk (history).
    #[test]
    fn test_fs_store_latest_wins_history_kept() {
        let dir = std::env::temp_dir().join(format!("roommate-hist-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        let latest = store.get_latest(&key).unwrap().unwrap();
        assert_eq!(latest.snapshot.taken_at, "2026-01-02T10:00:00Z");

        // Both snapshot files present — history not overwritten.
        let files = std::fs::read_dir(dir.join("p").join("m")).unwrap().count();
        assert_eq!(files, 2);

        std::fs::remove_dir_all(&dir).ok();
    }

    /// The manifest is the read index: a model dir present on disk but
    /// missing from `project.toml` must still appear in `all_latest`
    /// (filesystem truth wins over a buggy manifest), alongside the
    /// manifest-listed model.
    #[test]
    fn test_fs_store_filesystem_wins_over_manifest() {
        let dir = std::env::temp_dir().join(format!("roommate-manifest-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("proj1", "modelA", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("proj1", "modelB", "2026-01-01T11:00:00Z")).unwrap();

        // Sabotage the manifest: drop modelB from it, as if a push had
        // crashed between snapshot write and manifest write.
        let manifest_path = dir.join("proj1").join("project.toml");
        let manifest = ProjectManifest {
            name: "P".to_string(),
            models: BTreeMap::from([("modelA".to_string(), ModelEntry { name: "M".to_string() })]),
        };
        std::fs::write(&manifest_path, toml::to_string_pretty(&manifest).unwrap()).unwrap();

        let mut keys: Vec<String> = store.list_models().unwrap().into_iter().map(|k| k.model_id).collect();
        keys.sort();
        assert_eq!(keys, vec!["modelA".to_string(), "modelB".to_string()]);

        let all = store.all_latest().unwrap();
        assert_eq!(all.len(), 2, "the un-manifested model still appears");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A re-push with an identical `taken_at` is skipped, not overwritten —
    /// history must never be silently destroyed by a duplicate timestamp.
    #[test]
    fn test_fs_store_duplicate_taken_at_does_not_overwrite() {
        let dir = std::env::temp_dir().join(format!("roommate-dup-ts-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        let first = payload("p", "m", "2026-01-01T10:00:00Z");
        store.put(&first).unwrap();

        // Same taken_at, different content — must NOT replace the original.
        let mut second = payload("p", "m", "2026-01-01T10:00:00Z");
        second.project.name = "CHANGED".to_string();
        store.put(&second).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        let latest = store.get_latest(&key).unwrap().unwrap();
        assert_eq!(latest.project.name, "P", "the original snapshot survives a duplicate-timestamp re-push");

        std::fs::remove_dir_all(&dir).ok();
    }
}
