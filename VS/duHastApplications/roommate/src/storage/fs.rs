//! Filesystem-backed `SnapshotStore` — the persistent, history-keeping impl.
//! See the module doc in `mod.rs` for the on-disk layout and the
//! manifest-is-index / snapshots-are-record discipline this file implements.

use std::fs;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

use super::{DROFUS_DIR, ProjectManifest, SnapshotStore};
use crate::contract::RoomPayload;
use crate::state::ModelKey;

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

    fn drofus_dir(&self, project_id: &str) -> PathBuf {
        self.project_dir(project_id).join(DROFUS_DIR)
    }

    /// dRofus CSV filename from a snapshot id — same `:` sanitisation as
    /// `snapshot_filename` (so lexical-max-is-newest holds for `.csv` files
    /// exactly as for `.json`), different extension.
    fn drofus_filename(taken_at: &str) -> String {
        format!("{}.csv", taken_at.replace(':', "-"))
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

    /// Best-effort reverse of `snapshot_filename` for a snapshot file the
    /// manifest doesn't index (a pre-`snapshots`-field store, or a manifest
    /// that lost an entry): restore the `:` separators the sanitiser
    /// replaced. Only the positions that are unambiguously time separators in
    /// an RFC3339 id are restored — the two inside the time-of-day and the
    /// one in a `+hh-mm` offset tail; anything unrecognisable stays as the
    /// raw stem. Warning-path fallback only, never the primary index.
    fn id_from_file_stem(stem: &str) -> String {
        let mut bytes = stem.as_bytes().to_vec();
        // "YYYY-MM-DDTHH-MM-SS…": bytes 13 and 16 are sanitised colons.
        if bytes.len() >= 19 && bytes[10] == b'T' && bytes[13] == b'-' && bytes[16] == b'-' {
            bytes[13] = b':';
            bytes[16] = b':';
        }
        // A "+hh-mm" numeric-offset tail (e.g. "+00-00"): its '-' was a ':'.
        if let Some(plus) = bytes.iter().rposition(|&b| b == b'+') {
            if plus + 5 == bytes.len() - 1 && bytes[plus + 3] == b'-' {
                bytes[plus + 3] = b':';
            }
        }
        String::from_utf8(bytes).unwrap_or_else(|_| stem.to_string())
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
        //    insert this model if absent (`or_default` = the unknown-model case),
        //    update its name, and index this snapshot id (insert-if-absent, kept
        //    sorted so ascending == chronological for RFC3339-UTC ids). Rewritten
        //    every push so the manifest always mirrors what's on disk — which
        //    also backfills a pre-`snapshots`-field manifest one push at a time.
        let mut manifest = self.read_manifest(project_id)?;
        manifest.name = payload.project.name.clone();
        let entry = manifest.models.entry(model_id.clone()).or_default();
        entry.name = payload.model.name.clone();
        if !entry.snapshots.contains(&payload.snapshot.taken_at) {
            entry.snapshots.push(payload.snapshot.taken_at.clone());
            entry.snapshots.sort();
        }
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
                if model_id == DROFUS_DIR {
                    continue; // reserved dRofus upload dir, never a model
                }
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

    fn list_snapshot_ids(&self, key: &ModelKey) -> Result<Vec<String>> {
        // The manifest's `snapshots` list is the index; the directory is the
        // record. Same reconciliation stance as `list_models`: on
        // disagreement the filesystem wins — a file the manifest doesn't
        // index is included (with a best-effort id recovered from its name,
        // since the sanitised filename lost its `:`), and a manifest id with
        // no file behind it is dropped. Both are warned about, so drift is
        // noticeable rather than silent.
        let indexed = self
            .read_manifest(&key.project_id)?
            .models
            .get(&key.model_id)
            .map(|m| m.snapshots.clone())
            .unwrap_or_default();

        let dir = self.model_dir(&key.project_id, &key.model_id);
        let mut on_disk: Vec<String> = Vec::new();
        if dir.exists() {
            for entry in fs::read_dir(&dir)
                .with_context(|| format!("could not read model dir: {}", dir.display()))?
            {
                let path = entry?.path();
                if path.extension().and_then(|e| e.to_str()) == Some("json") {
                    if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                        on_disk.push(name.to_string());
                    }
                }
            }
        }

        let mut ids = Vec::new();
        for id in indexed {
            let filename = Self::snapshot_filename(&id);
            if let Some(pos) = on_disk.iter().position(|f| *f == filename) {
                on_disk.swap_remove(pos);
                ids.push(id);
            } else {
                tracing::warn!(
                    "manifest lists snapshot {:?} for {}/{} but no file exists — dropping it (filesystem wins)",
                    id, key.project_id, key.model_id
                );
            }
        }
        for filename in on_disk {
            let stem = filename.strip_suffix(".json").unwrap_or(&filename);
            let id = Self::id_from_file_stem(stem);
            tracing::warn!(
                "snapshot file {}/{}/{} is missing from project.toml — including it as {:?} (filesystem wins)",
                key.project_id, key.model_id, filename, id
            );
            ids.push(id);
        }
        ids.sort();
        Ok(ids)
    }

    fn get_snapshot(&self, key: &ModelKey, taken_at: &str) -> Result<Option<RoomPayload>> {
        let path = self
            .model_dir(&key.project_id, &key.model_id)
            .join(Self::snapshot_filename(taken_at));
        if !path.exists() {
            return Ok(None);
        }
        Ok(Some(Self::read_payload(&path)?))
    }

    fn put_drofus(&self, project_id: &str, taken_at: &str, csv: &[u8]) -> Result<bool> {
        // Same upsert shape as `put`: ensure the dir, index the id in the
        // manifest, then write the file — skipping (never overwriting) a
        // duplicate `taken_at`.
        let dir = self.drofus_dir(project_id);
        fs::create_dir_all(&dir)
            .with_context(|| format!("could not create dRofus dir: {}", dir.display()))?;

        let mut manifest = self.read_manifest(project_id)?;
        if !manifest.drofus_snapshots.iter().any(|id| id == taken_at) {
            manifest.drofus_snapshots.push(taken_at.to_string());
            manifest.drofus_snapshots.sort();
        }
        self.write_manifest(project_id, &manifest)?;

        let file = dir.join(Self::drofus_filename(taken_at));
        if file.exists() {
            tracing::warn!("dRofus snapshot already exists, skipping: {}", file.display());
            return Ok(false);
        }
        fs::write(&file, csv)
            .with_context(|| format!("could not write dRofus snapshot: {}", file.display()))?;

        tracing::info!("stored dRofus snapshot {} @ {}", project_id, taken_at);
        Ok(true)
    }

    fn list_drofus_snapshot_ids(&self, project_id: &str) -> Result<Vec<String>> {
        // Same manifest-vs-directory reconciliation as `list_snapshot_ids`:
        // the manifest is the index, the files are the record, filesystem
        // wins on disagreement, both directions warned.
        let indexed = self.read_manifest(project_id)?.drofus_snapshots;

        let dir = self.drofus_dir(project_id);
        let mut on_disk: Vec<String> = Vec::new();
        if dir.exists() {
            for entry in fs::read_dir(&dir)
                .with_context(|| format!("could not read dRofus dir: {}", dir.display()))?
            {
                let path = entry?.path();
                if path.extension().and_then(|e| e.to_str()) == Some("csv") {
                    if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                        on_disk.push(name.to_string());
                    }
                }
            }
        }

        let mut ids = Vec::new();
        for id in indexed {
            let filename = Self::drofus_filename(&id);
            if let Some(pos) = on_disk.iter().position(|f| *f == filename) {
                on_disk.swap_remove(pos);
                ids.push(id);
            } else {
                tracing::warn!(
                    "manifest lists dRofus snapshot {:?} for {} but no file exists — dropping it (filesystem wins)",
                    id, project_id
                );
            }
        }
        for filename in on_disk {
            let stem = filename.strip_suffix(".csv").unwrap_or(&filename);
            let id = Self::id_from_file_stem(stem);
            tracing::warn!(
                "dRofus file {}/{}/{} is missing from project.toml — including it as {:?} (filesystem wins)",
                project_id, DROFUS_DIR, filename, id
            );
            ids.push(id);
        }
        ids.sort();
        Ok(ids)
    }

    fn get_drofus(&self, project_id: &str, taken_at: &str) -> Result<Option<Vec<u8>>> {
        let path = self.drofus_dir(project_id).join(Self::drofus_filename(taken_at));
        if !path.exists() {
            return Ok(None);
        }
        Ok(Some(fs::read(&path)
            .with_context(|| format!("could not read dRofus snapshot: {}", path.display()))?))
    }

    fn get_latest_drofus(&self, project_id: &str) -> Result<Option<(String, Vec<u8>)>> {
        // Latest = last of the reconciled ascending list (RFC3339-UTC ids, so
        // lexical max is newest). Going through the reconciliation instead of
        // a raw directory scan means an un-indexed file still wins its way in
        // and a phantom manifest id can't name a file that isn't there.
        let Some(id) = self.list_drofus_snapshot_ids(project_id)?.pop() else {
            return Ok(None);
        };
        match self.get_drofus(project_id, &id)? {
            Some(bytes) => Ok(Some((id, bytes))),
            None => Ok(None), // racing delete; treat as no data
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Model, Project, Snapshot};
    use crate::storage::{MemStore, ModelEntry};
    use std::collections::BTreeMap;

    fn payload(project: &str, model: &str, ts: &str) -> RoomPayload {
        RoomPayload {
            schema_version: 5,
            project: Project { id: project.into(), name: "P".into() },
            model: Model { id: model.into(), name: "M".into(), source: "revit".into() },
            snapshot: Snapshot { taken_at: ts.into() },
            model_to_shared: None,
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
            models: BTreeMap::from([(
                "modelA".to_string(),
                ModelEntry { name: "M".to_string(), snapshots: vec!["2026-01-01T10:00:00Z".to_string()] },
            )]),
            drofus_snapshots: vec![],
        };
        std::fs::write(&manifest_path, toml::to_string_pretty(&manifest).unwrap()).unwrap();

        let mut keys: Vec<String> = store.list_models().unwrap().into_iter().map(|k| k.model_id).collect();
        keys.sort();
        assert_eq!(keys, vec!["modelA".to_string(), "modelB".to_string()]);

        let all = store.all_latest().unwrap();
        assert_eq!(all.len(), 2, "the un-manifested model still appears");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Each push indexes its snapshot id in the manifest, and
    /// `list_snapshot_ids` reads them back ascending regardless of push
    /// order — never opening a snapshot JSON.
    #[test]
    fn test_fs_store_lists_snapshot_ids_ascending() {
        let dir = std::env::temp_dir().join(format!("roommate-snap-ids-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();
        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        assert_eq!(
            store.list_snapshot_ids(&key).unwrap(),
            vec!["2026-01-01T10:00:00Z".to_string(), "2026-01-02T10:00:00Z".to_string()]
        );

        // Unknown model: empty, not an error.
        let unknown = ModelKey { project_id: "p".into(), model_id: "nope".into() };
        assert!(store.list_snapshot_ids(&unknown).unwrap().is_empty());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Reconciliation, filesystem wins both ways: a snapshot file the
    /// manifest doesn't index (a store written before the `snapshots` field
    /// existed) is included with its id recovered from the sanitised
    /// filename, and a manifest id with no file behind it is dropped.
    #[test]
    fn test_fs_store_snapshot_ids_filesystem_wins_over_manifest() {
        let dir = std::env::temp_dir().join(format!("roommate-snap-rec-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();

        // Sabotage the manifest: drop the first id (as if written pre-field)
        // and add a phantom id whose file doesn't exist.
        let manifest_path = dir.join("p").join("project.toml");
        let manifest = ProjectManifest {
            name: "P".to_string(),
            models: BTreeMap::from([(
                "m".to_string(),
                ModelEntry {
                    name: "M".to_string(),
                    snapshots: vec!["2026-01-02T10:00:00Z".to_string(), "2026-01-03T10:00:00Z".to_string()],
                },
            )]),
            drofus_snapshots: vec![],
        };
        std::fs::write(&manifest_path, toml::to_string_pretty(&manifest).unwrap()).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        assert_eq!(
            store.list_snapshot_ids(&key).unwrap(),
            vec!["2026-01-01T10:00:00Z".to_string(), "2026-01-02T10:00:00Z".to_string()],
            "un-indexed file recovered (with its ':' restored), phantom id dropped"
        );

        std::fs::remove_dir_all(&dir).ok();
    }

    /// `get_snapshot` answers a specific historic id (not just the latest),
    /// and `None` for an id that was never stored.
    #[test]
    fn test_fs_store_get_snapshot_by_id() {
        let dir = std::env::temp_dir().join(format!("roommate-get-snap-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        let old = store.get_snapshot(&key, "2026-01-01T10:00:00Z").unwrap().unwrap();
        assert_eq!(old.snapshot.taken_at, "2026-01-01T10:00:00Z");
        assert!(store.get_snapshot(&key, "2026-03-01T10:00:00Z").unwrap().is_none());

        // MemStore can only answer for its current latest.
        let mem = MemStore::new();
        mem.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        mem.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();
        assert!(mem.get_snapshot(&key, "2026-01-02T10:00:00Z").unwrap().is_some());
        assert!(mem.get_snapshot(&key, "2026-01-01T10:00:00Z").unwrap().is_none());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// dRofus uploads: put/list/get/latest round-trip, ascending ids,
    /// duplicate `taken_at` skipped with the original bytes preserved.
    #[test]
    fn test_fs_store_drofus_round_trip() {
        let dir = std::env::temp_dir().join(format!("roommate-drofus-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        assert!(store.get_latest_drofus("p").unwrap().is_none());
        assert!(store.list_drofus_snapshot_ids("p").unwrap().is_empty());

        assert!(store.put_drofus("p", "2026-01-02T10:00:00Z", b"csv-two").unwrap());
        assert!(store.put_drofus("p", "2026-01-01T10:00:00Z", b"csv-one").unwrap());

        assert_eq!(
            store.list_drofus_snapshot_ids("p").unwrap(),
            vec!["2026-01-01T10:00:00Z".to_string(), "2026-01-02T10:00:00Z".to_string()]
        );
        assert_eq!(store.get_drofus("p", "2026-01-01T10:00:00Z").unwrap().unwrap(), b"csv-one");
        assert!(store.get_drofus("p", "2026-03-01T10:00:00Z").unwrap().is_none());

        // Latest is the lexical max — the older backfill did not displace it.
        let (id, bytes) = store.get_latest_drofus("p").unwrap().unwrap();
        assert_eq!(id, "2026-01-02T10:00:00Z");
        assert_eq!(bytes, b"csv-two");

        // Duplicate taken_at: skipped (false), original bytes preserved.
        assert!(!store.put_drofus("p", "2026-01-02T10:00:00Z", b"CHANGED").unwrap());
        assert_eq!(store.get_drofus("p", "2026-01-02T10:00:00Z").unwrap().unwrap(), b"csv-two");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// The reserved `drofus/` dir must never surface as a phantom model in
    /// `list_models` — the single most likely silent regression of adding a
    /// non-model subdirectory to the project dir.
    #[test]
    fn test_fs_store_drofus_dir_is_not_a_model() {
        let dir = std::env::temp_dir().join(format!("roommate-drofus-dir-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        store.put_drofus("p", "2026-01-01T11:00:00Z", b"csv").unwrap();

        let keys = store.list_models().unwrap();
        assert_eq!(keys.len(), 1);
        assert_eq!(keys[0].model_id, "m");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// dRofus reconciliation, filesystem wins both ways: an un-indexed file
    /// is included with its id recovered from the sanitised filename, a
    /// manifest id with no file behind it is dropped.
    #[test]
    fn test_fs_store_drofus_ids_filesystem_wins_over_manifest() {
        let dir = std::env::temp_dir().join(format!("roommate-drofus-rec-{}", std::process::id()));
        let store = FsStore::new(dir.clone()).unwrap();

        store.put_drofus("p", "2026-01-01T10:00:00Z", b"one").unwrap();
        store.put_drofus("p", "2026-01-02T10:00:00Z", b"two").unwrap();

        // Sabotage the manifest: drop the first id, add a phantom one.
        let manifest_path = dir.join("p").join("project.toml");
        let manifest = ProjectManifest {
            name: String::new(),
            models: BTreeMap::new(),
            drofus_snapshots: vec!["2026-01-02T10:00:00Z".to_string(), "2026-01-03T10:00:00Z".to_string()],
        };
        std::fs::write(&manifest_path, toml::to_string_pretty(&manifest).unwrap()).unwrap();

        assert_eq!(
            store.list_drofus_snapshot_ids("p").unwrap(),
            vec!["2026-01-01T10:00:00Z".to_string(), "2026-01-02T10:00:00Z".to_string()],
            "un-indexed file recovered (with its ':' restored), phantom id dropped"
        );

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
