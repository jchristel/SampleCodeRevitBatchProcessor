//! In-memory `SnapshotStore` — the volatile, latest-only impl kept for
//! `[storage]`-less dev/test configs. See the module doc in `mod.rs` for the
//! trait contract; the one thing that differs here is history: there is none
//! (latest-only, by design), so replacement is the normal upsert.

use std::collections::BTreeMap;
use std::sync::Mutex;

use anyhow::Result;

use super::SnapshotStore;
use crate::contract::RoomPayload;
use crate::state::ModelKey;

/// In-memory store: the pre-persistence behaviour, kept for tests and for a
/// `[storage]`-less config. Latest-only per model (no history) — history is a
/// disk affordance, not worth reproducing in the volatile store.
#[derive(Default)]
pub struct MemStore {
    latest: Mutex<BTreeMap<ModelKey, RoomPayload>>,
    /// Latest uploaded dRofus CSV per project id: `(taken_at, bytes)`.
    /// Latest-only like `latest` — history is a disk affordance.
    drofus: Mutex<BTreeMap<String, (String, Vec<u8>)>>,
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

    fn list_snapshot_ids(&self, key: &ModelKey) -> Result<Vec<String>> {
        // Latest-only store, so "all snapshot ids" is at most the one current
        // id — honest about the fact that MemStore keeps no history.
        Ok(self
            .latest
            .lock()
            .unwrap()
            .get(key)
            .map(|p| vec![p.snapshot.taken_at.clone()])
            .unwrap_or_default())
    }

    fn get_snapshot(&self, key: &ModelKey, taken_at: &str) -> Result<Option<RoomPayload>> {
        // Latest-only store: an id can only be answered when it IS the
        // current latest; anything older is genuinely gone.
        Ok(self
            .latest
            .lock()
            .unwrap()
            .get(key)
            .filter(|p| p.snapshot.taken_at == taken_at)
            .cloned())
    }

    fn put_drofus(&self, project_id: &str, taken_at: &str, csv: &[u8]) -> Result<bool> {
        // Latest-only: replacement is the normal upsert (same stance as
        // `put`), so the duplicate-skip rule doesn't apply here.
        self.drofus
            .lock()
            .unwrap()
            .insert(project_id.to_string(), (taken_at.to_string(), csv.to_vec()));
        Ok(true)
    }

    fn list_drofus_snapshot_ids(&self, project_id: &str) -> Result<Vec<String>> {
        Ok(self
            .drofus
            .lock()
            .unwrap()
            .get(project_id)
            .map(|(id, _)| vec![id.clone()])
            .unwrap_or_default())
    }

    fn get_drofus(&self, project_id: &str, taken_at: &str) -> Result<Option<Vec<u8>>> {
        Ok(self
            .drofus
            .lock()
            .unwrap()
            .get(project_id)
            .filter(|(id, _)| id == taken_at)
            .map(|(_, bytes)| bytes.clone()))
    }

    fn get_latest_drofus(&self, project_id: &str) -> Result<Option<(String, Vec<u8>)>> {
        Ok(self.drofus.lock().unwrap().get(project_id).cloned())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contract::{Model, Project, Snapshot};

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

    /// MemStore keeps no history: its snapshot id list is just the current
    /// latest.
    #[test]
    fn test_mem_store_lists_only_latest_snapshot_id() {
        let store = MemStore::new();
        store.put(&payload("p", "m", "2026-01-01T10:00:00Z")).unwrap();
        store.put(&payload("p", "m", "2026-01-02T10:00:00Z")).unwrap();

        let key = ModelKey { project_id: "p".into(), model_id: "m".into() };
        assert_eq!(store.list_snapshot_ids(&key).unwrap(), vec!["2026-01-02T10:00:00Z".to_string()]);
    }

    /// MemStore dRofus: latest-only, replacement is the normal upsert.
    #[test]
    fn test_mem_store_drofus_latest_only() {
        let store = MemStore::new();
        assert!(store.get_latest_drofus("p").unwrap().is_none());

        store.put_drofus("p", "2026-01-01T10:00:00Z", b"one").unwrap();
        store.put_drofus("p", "2026-01-02T10:00:00Z", b"two").unwrap();

        assert_eq!(store.list_drofus_snapshot_ids("p").unwrap(), vec!["2026-01-02T10:00:00Z".to_string()]);
        let (id, bytes) = store.get_latest_drofus("p").unwrap().unwrap();
        assert_eq!(id, "2026-01-02T10:00:00Z");
        assert_eq!(bytes, b"two");
        assert!(store.get_drofus("p", "2026-01-01T10:00:00Z").unwrap().is_none());
        assert_eq!(store.get_drofus("p", "2026-01-02T10:00:00Z").unwrap().unwrap(), b"two");
    }
}
