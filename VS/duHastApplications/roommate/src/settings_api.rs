//! Project-settings read/save API: the machinery behind the settings UI
//! (`static/settings.html`).
//!
//! Layout mirrors the codebase's handler/service split inside one module: a
//! transport-agnostic core at the top (plain functions over `projects_dir`,
//! typed `SettingsError` results), thin Axum adapters at the bottom. The MCP
//! binary reuses the core's *read* functions for its `list_project_settings`
//! / `get_project_settings` tools; **writes stay HTTP-only** — the MCP server
//! is a separate process, so a write from it could not hot-swap this
//! process's registry (instant split-brain), and mutation stays behind the
//! human UI per mcp.rs's read-only contract.
//!
//! The TOML files remain the single source of truth: reads parse them fresh
//! per call (no filename bookkeeping in `AppState`), and a save validates the
//! candidate through the exact startup pipeline (`bootstrap::load_project_bundle`)
//! before installing the file and hot-swapping the registry — a file this API
//! accepts can never fail the next boot. Access control is the server's
//! `127.0.0.1` bind, same trust model as ingest.

use std::path::{Path, PathBuf};
use std::sync::Mutex;

use axum::{
    extract::{Path as UrlPath, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};

use crate::bootstrap::{load_project_bundle, load_project_settings_dir};
use crate::drofus::load_drofus;
use crate::settings::{DrofusSource, Settings};
use crate::state::{is_path_safe_component, AppState, SettingsRegistry, Shared};

/// One project-settings file as the UI's list sees it. A file that fails to
/// parse still gets a row (with `error` set) rather than breaking the whole
/// list — the settings UI is exactly the tool you'd reach for to notice a
/// rotten file, so it must stay usable when one exists.
#[derive(Serialize)]
pub struct ProjectFileSummary {
    /// File name within the projects dir (not a full path).
    pub file: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub project_id: Option<String>,
    pub is_default: bool,
    pub drofus_configured: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Result of dry-running a dRofus CSV path — powers the UI's "check" button
/// and its drofus_fields label dropdown.
#[derive(Serialize)]
pub struct DrofusCheckResult {
    pub record_count: usize,
    pub link_property: String,
    pub labels: Vec<String>,
}

/// Typed failure for the core functions; each transport maps it itself
/// (HTTP below, MCP in `bin/mcp.rs`) — same seam discipline as `ServiceError`.
#[derive(Debug)]
pub enum SettingsError {
    /// The state wasn't built from a settings directory (in-memory tests).
    NotFileBacked,
    /// No settings file exists for the requested project id.
    NotFound(String),
    /// A create collides with an existing project id or file.
    Conflict(String),
    /// The candidate settings failed validation — message is the same loud
    /// text startup would print for the same mistake.
    Invalid(String),
    Internal(anyhow::Error),
}

/// Serialises every save end-to-end. Two concurrent admin saves are a
/// non-case in practice, but the lock makes the scan-then-write race
/// structurally impossible rather than merely unlikely.
static SAVE_LOCK: Mutex<()> = Mutex::new(());

/// Parse one settings file RAW — `toml::from_str`, no relative-path
/// resolution — so a dRofus path round-trips exactly as authored. (The
/// resolving parse, `load_settings`, is for *running* against a file; this
/// one is for *editing* it.)
fn read_raw(path: &Path) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)?;
    Ok(toml::from_str(&raw)?)
}

/// Every `*.toml` directly in the projects dir, sorted by file name.
fn settings_files(projects_dir: &Path) -> Result<Vec<PathBuf>, SettingsError> {
    let entries = std::fs::read_dir(projects_dir)
        .map_err(|e| SettingsError::Internal(anyhow::anyhow!("could not read {}: {e}", projects_dir.display())))?;
    let mut files: Vec<PathBuf> = entries
        .filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| p.extension().and_then(|e| e.to_str()) == Some("toml"))
        .collect();
    files.sort();
    Ok(files)
}

fn file_name(path: &Path) -> String {
    path.file_name().and_then(|n| n.to_str()).unwrap_or("?").to_string()
}

/// List every project-settings file with its headline facts (or its parse
/// error). Shared by `GET /api/settings/projects` and the MCP
/// `list_project_settings` tool.
pub fn list_project_files(projects_dir: &Path) -> Result<Vec<ProjectFileSummary>, SettingsError> {
    let mut out = Vec::new();
    for path in settings_files(projects_dir)? {
        match read_raw(&path) {
            Ok(settings) => out.push(ProjectFileSummary {
                file: file_name(&path),
                project_id: Some(settings.project_id),
                is_default: settings.is_default,
                drofus_configured: settings.sources.drofus.is_some(),
                error: None,
            }),
            Err(e) => out.push(ProjectFileSummary {
                file: file_name(&path),
                project_id: None,
                is_default: false,
                drofus_configured: false,
                error: Some(format!("{e:#}")),
            }),
        }
    }
    Ok(out)
}

/// Find and parse the settings file whose `project_id` matches. Shared by
/// `GET /api/settings/projects/{id}` and the MCP `get_project_settings` tool.
/// Returns the file name alongside so the UI can show where the project lives.
pub fn get_project_file(projects_dir: &Path, project_id: &str) -> Result<(String, Settings), SettingsError> {
    for path in settings_files(projects_dir)? {
        if let Ok(settings) = read_raw(&path) {
            if settings.project_id == project_id {
                return Ok((file_name(&path), settings));
            }
        }
    }
    Err(SettingsError::NotFound(format!("no settings file declares project_id '{project_id}'")))
}

/// Dry-run a dRofus CSV path (relative paths resolve against the projects
/// dir, exactly as they would from a settings file there) and report what it
/// contains — record count for the UI's sanity line, the label set for the
/// drofus_fields dropdown.
pub fn check_drofus(projects_dir: &Path, path: &str) -> Result<DrofusCheckResult, SettingsError> {
    if path.trim().is_empty() {
        return Err(SettingsError::Invalid("dRofus path is empty".to_string()));
    }
    let mut resolved = PathBuf::from(path);
    if resolved.is_relative() {
        resolved = projects_dir.join(resolved);
    }
    let data = load_drofus(&DrofusSource::File { path: resolved }).map_err(|e| SettingsError::Invalid(format!("{e:#}")))?;
    Ok(DrofusCheckResult {
        record_count: data.by_id.len(),
        link_property: data.link_property,
        labels: data.all_labels,
    })
}

/// Save one project's settings: validate through the startup pipeline, write
/// the file atomically, hot-swap the running registry. `existing_id` is
/// `Some` for an update (`PUT`) and `None` for a create (`POST`).
///
/// Ordering is deliberate: nothing is installed until the candidate passed
/// the exact validation startup runs, and the registry is only swapped from a
/// full, successful re-load of the whole directory — the running server can
/// never observe a half-updated state, and a file this function accepts can
/// never fail the next boot.
pub fn save_project(state: &AppState, existing_id: Option<&str>, settings: Settings) -> Result<Settings, SettingsError> {
    let projects_dir = state.projects_dir().ok_or(SettingsError::NotFileBacked)?.clone();
    let _guard = SAVE_LOCK.lock().unwrap();

    let id = settings.project_id.clone();
    if !is_path_safe_component(&id) {
        return Err(SettingsError::Invalid(format!(
            "project_id {id:?} is empty or contains characters unsafe for file names"
        )));
    }

    // Resolve the target file. Update: the file that currently declares this
    // id (the id is the identity — renaming is a new project, not an edit).
    // Create: a fresh `<id>.toml`, rejecting a collision with any existing
    // declaration or file.
    let target = match existing_id {
        Some(existing) => {
            if existing != id {
                return Err(SettingsError::Invalid(format!(
                    "project_id cannot change ('{existing}' -> '{id}'): the id is the project's identity — create a new project instead"
                )));
            }
            let (file, _) = get_project_file(&projects_dir, existing)?;
            projects_dir.join(file)
        }
        None => {
            if let Ok((file, _)) = get_project_file(&projects_dir, &id) {
                return Err(SettingsError::Conflict(format!("project '{id}' already exists (in {file})")));
            }
            let target = projects_dir.join(format!("{id}.toml"));
            if target.exists() {
                return Err(SettingsError::Conflict(format!(
                    "file {} already exists but declares a different project",
                    file_name(&target)
                )));
            }
            target
        }
    };

    // Cross-file checks against every OTHER file: a second `is_default` is
    // the same startup-loud error `load_project_settings_dir` raises.
    // (Duplicate project_id is already excluded by the create path above and
    // impossible on update, where the id equals the target file's own.)
    if settings.is_default {
        for path in settings_files(&projects_dir)? {
            if path == target {
                continue;
            }
            if let Ok(other) = read_raw(&path) {
                if other.is_default {
                    return Err(SettingsError::Invalid(format!(
                        "another settings file already sets is_default = true: {} ('{}')",
                        file_name(&path),
                        other.project_id
                    )));
                }
            }
        }
    }

    // Serialize and stage the candidate as a temp file IN the projects dir
    // (so relative dRofus paths resolve exactly as they will at startup) with
    // a non-.toml extension (so a crash mid-save can't leave a file the next
    // startup scan would pick up).
    let toml_text =
        toml::to_string_pretty(&settings).map_err(|e| SettingsError::Invalid(format!("settings do not serialize to TOML: {e}")))?;
    let temp = projects_dir.join(format!(".{id}.candidate.tmp"));
    std::fs::write(&temp, &toml_text)
        .map_err(|e| SettingsError::Internal(anyhow::anyhow!("could not write candidate file: {e}")))?;

    // Full standalone validation — the same pipeline startup runs, so the
    // rejection message is the same loud text a bad boot would print.
    if let Err(e) = load_project_bundle(&temp) {
        std::fs::remove_file(&temp).ok();
        return Err(SettingsError::Invalid(format!("{e:#}")));
    }

    // Atomic install (std::fs::rename replaces an existing target on both
    // Unix and Windows), then rebuild the registry from the whole directory
    // and swap it in. A reload failure here means some OTHER file rotted
    // underneath us — surface it loudly and keep serving the old registry.
    std::fs::rename(&temp, &target)
        .map_err(|e| SettingsError::Internal(anyhow::anyhow!("could not install settings file: {e}")))?;

    match load_project_settings_dir(&projects_dir) {
        Ok((by_project, default)) => {
            state.swap_registry(SettingsRegistry { by_project, default });
            tracing::info!("settings saved and applied: {} ({})", id, file_name(&target));
            Ok(settings)
        }
        Err(e) => Err(SettingsError::Internal(anyhow::anyhow!(
            "settings file installed, but reloading the directory failed (another file may be broken): {e:#} — \
             the running server keeps its previous settings until this is fixed"
        ))),
    }
}

// ---------- Axum adapters ----------

fn to_http(err: SettingsError) -> (StatusCode, String) {
    match err {
        SettingsError::NotFileBacked => (
            StatusCode::NOT_FOUND,
            "this server has no --project-settings directory (settings editing unavailable)".to_string(),
        ),
        SettingsError::NotFound(msg) => (StatusCode::NOT_FOUND, msg),
        SettingsError::Conflict(msg) => (StatusCode::CONFLICT, msg),
        SettingsError::Invalid(msg) => (StatusCode::UNPROCESSABLE_ENTITY, msg),
        SettingsError::Internal(e) => {
            tracing::error!("settings API internal error: {e:#}");
            (StatusCode::INTERNAL_SERVER_ERROR, e.to_string())
        }
    }
}

fn require_dir(state: &AppState) -> Result<PathBuf, (StatusCode, String)> {
    state.projects_dir().cloned().ok_or_else(|| to_http(SettingsError::NotFileBacked))
}

/// `GET /api/settings/projects`
pub async fn http_list_projects(State(state): State<Shared>) -> Result<Json<Vec<ProjectFileSummary>>, (StatusCode, String)> {
    let dir = require_dir(&state)?;
    list_project_files(&dir).map(Json).map_err(to_http)
}

/// Wire shape of one project's settings: the parsed `Settings` plus which
/// file it lives in.
#[derive(Serialize)]
pub struct ProjectSettingsResponse {
    pub file: String,
    pub settings: Settings,
}

/// `GET /api/settings/projects/{id}`
pub async fn http_get_project(
    State(state): State<Shared>,
    UrlPath(project_id): UrlPath<String>,
) -> Result<Json<ProjectSettingsResponse>, (StatusCode, String)> {
    let dir = require_dir(&state)?;
    let (file, settings) = get_project_file(&dir, &project_id).map_err(to_http)?;
    Ok(Json(ProjectSettingsResponse { file, settings }))
}

/// Save response: the settings as installed, plus the hot-reload confirmation
/// the UI shows ("saved & applied live").
#[derive(Serialize)]
pub struct SaveResponse {
    pub applied: bool,
    pub settings: Settings,
}

/// `POST /api/settings/projects` (create)
pub async fn http_create_project(
    State(state): State<Shared>,
    Json(settings): Json<Settings>,
) -> Result<Json<SaveResponse>, (StatusCode, String)> {
    let settings = save_project(&state, None, settings).map_err(to_http)?;
    Ok(Json(SaveResponse { applied: true, settings }))
}

/// `PUT /api/settings/projects/{id}` (update)
pub async fn http_update_project(
    State(state): State<Shared>,
    UrlPath(project_id): UrlPath<String>,
    Json(settings): Json<Settings>,
) -> Result<Json<SaveResponse>, (StatusCode, String)> {
    let settings = save_project(&state, Some(&project_id), settings).map_err(to_http)?;
    Ok(Json(SaveResponse { applied: true, settings }))
}

#[derive(Deserialize)]
pub struct DrofusCheckRequest {
    pub path: String,
}

/// `POST /api/settings/drofus-check`
pub async fn http_drofus_check(
    State(state): State<Shared>,
    Json(req): Json<DrofusCheckRequest>,
) -> Result<Json<DrofusCheckResult>, (StatusCode, String)> {
    let dir = require_dir(&state)?;
    check_drofus(&dir, &req.path).map(Json).map_err(to_http)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::MemStore;
    use std::collections::HashMap;

    fn temp_dir(tag: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("roommate-settings-api-{}-{}", tag, std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    fn file_backed_state(dir: &Path) -> AppState {
        AppState::new(Box::new(MemStore::new()), HashMap::new(), None).with_projects_dir(dir.to_path_buf())
    }

    fn minimal_settings(id: &str) -> Settings {
        toml::from_str(&format!("project_id = \"{id}\"\n")).unwrap()
    }

    /// A `Settings` value survives serialize-to-TOML → parse — proves the new
    /// `Serialize` derives and toml's table ordering handle the full shape
    /// (values, tables, arrays-of-tables interleaved in struct order).
    #[test]
    fn test_settings_toml_round_trip() {
        let source: Settings = toml::from_str(
            r#"
project_id = "p1"
is_default = true
room_label = ["$name", "Area"]

[sources.drofus]
type = "file"
path = "drofus.csv"

[[hierarchy]]
name = "Building"
code_property = "bldg_code"

[[builtin_properties]]
canonical = "Area"
by_source = { revit = "Area" }

[[milestones]]
name = "Design Freeze"
date = "2026-06-30"
[milestones.attachments]
"model-guid" = "2026-06-29T10:00:00Z"

[[drofus_fields]]
label = "LastSync"
type = "date"
format = "%Y-%m-%d"
qa = "ignore"
"#,
        )
        .unwrap();

        let text = toml::to_string_pretty(&source).unwrap();
        let reparsed: Settings = toml::from_str(&text).unwrap();

        assert_eq!(reparsed.project_id, "p1");
        assert!(reparsed.is_default);
        assert_eq!(reparsed.room_label, vec!["$name".to_string(), "Area".to_string()]);
        assert!(matches!(reparsed.sources.drofus, Some(DrofusSource::File { .. })));
        assert_eq!(reparsed.hierarchy.len(), 1);
        assert_eq!(reparsed.builtin_properties.len(), 1);
        assert_eq!(reparsed.drofus_fields.len(), 1);
        assert_eq!(reparsed.milestones.len(), 1);
        assert_eq!(reparsed.milestones[0].name, "Design Freeze");
        assert_eq!(reparsed.milestones[0].attachments["model-guid"], "2026-06-29T10:00:00Z");
    }

    /// Create → list → get round-trip through the core, and the saved project
    /// is immediately resolvable via the hot-swapped registry (no restart).
    #[test]
    fn test_save_applies_live_and_reads_back() {
        let dir = temp_dir("save-live");
        let state = file_backed_state(&dir);

        assert!(state.settings().settings_for("p1").is_none(), "not registered before save");

        save_project(&state, None, minimal_settings("p1")).unwrap();

        assert!(state.settings().settings_for("p1").is_some(), "registered without a restart");
        let list = list_project_files(&dir).unwrap();
        assert_eq!(list.len(), 1);
        assert_eq!(list[0].project_id.as_deref(), Some("p1"));
        let (file, settings) = get_project_file(&dir, "p1").unwrap();
        assert_eq!(file, "p1.toml");
        assert_eq!(settings.project_id, "p1");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Creating an id that already exists is a conflict, not an overwrite.
    #[test]
    fn test_create_duplicate_id_conflicts() {
        let dir = temp_dir("dup-id");
        let state = file_backed_state(&dir);
        save_project(&state, None, minimal_settings("p1")).unwrap();

        match save_project(&state, None, minimal_settings("p1")) {
            Err(SettingsError::Conflict(msg)) => assert!(msg.contains("p1")),
            other => panic!("expected Conflict, got {other:?}"),
        }

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A second `is_default` is rejected with the file that already claims it
    /// named — same rule startup enforces, caught before anything is written.
    #[test]
    fn test_second_default_rejected() {
        let dir = temp_dir("second-default");
        let state = file_backed_state(&dir);
        let mut first = minimal_settings("p1");
        first.is_default = true;
        save_project(&state, None, first).unwrap();

        let mut second = minimal_settings("p2");
        second.is_default = true;
        match save_project(&state, None, second) {
            Err(SettingsError::Invalid(msg)) => assert!(msg.contains("is_default") && msg.contains("p1")),
            other => panic!("expected Invalid, got {other:?}"),
        }
        assert!(get_project_file(&dir, "p2").is_err(), "nothing was written for the rejected save");

        std::fs::remove_dir_all(&dir).ok();
    }

    /// An invalid candidate (here: drofus_fields without a source — the same
    /// startup-loud rule) leaves the existing file byte-identical on disk and
    /// the registry unswapped.
    #[test]
    fn test_invalid_update_leaves_file_intact() {
        let dir = temp_dir("invalid-update");
        let state = file_backed_state(&dir);
        save_project(&state, None, minimal_settings("p1")).unwrap();
        let before = std::fs::read_to_string(dir.join("p1.toml")).unwrap();

        let bad: Settings = toml::from_str(
            "project_id = \"p1\"\n\n[[drofus_fields]]\nlabel = \"X\"\nqa = \"exact\"\n",
        )
        .unwrap();
        match save_project(&state, Some("p1"), bad) {
            Err(SettingsError::Invalid(msg)) => assert!(msg.contains("drofus_fields")),
            other => panic!("expected Invalid, got {other:?}"),
        }

        assert_eq!(std::fs::read_to_string(dir.join("p1.toml")).unwrap(), before, "file untouched");
        assert!(
            !dir.join(".p1.candidate.tmp").exists(),
            "candidate temp file cleaned up"
        );

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Updating may not change the project id — the id is the identity.
    #[test]
    fn test_update_cannot_rename() {
        let dir = temp_dir("no-rename");
        let state = file_backed_state(&dir);
        save_project(&state, None, minimal_settings("p1")).unwrap();

        match save_project(&state, Some("p1"), minimal_settings("p2")) {
            Err(SettingsError::Invalid(msg)) => assert!(msg.contains("identity")),
            other => panic!("expected Invalid, got {other:?}"),
        }

        std::fs::remove_dir_all(&dir).ok();
    }

    /// Updating an unknown id is NotFound; a path-unsafe id never touches disk.
    #[test]
    fn test_update_unknown_and_unsafe_ids() {
        let dir = temp_dir("unknown-unsafe");
        let state = file_backed_state(&dir);

        assert!(matches!(
            save_project(&state, Some("ghost"), minimal_settings("ghost")),
            Err(SettingsError::NotFound(_))
        ));
        assert!(matches!(
            save_project(&state, None, minimal_settings("a/b")),
            Err(SettingsError::Invalid(_))
        ));
        assert!(settings_files(&dir).unwrap().is_empty());

        std::fs::remove_dir_all(&dir).ok();
    }

    /// The dRofus dry-run reports records and labels; a bogus path is the
    /// same loud error a bad startup source would raise.
    #[test]
    fn test_check_drofus() {
        let dir = temp_dir("drofus-check");
        std::fs::write(dir.join("d.csv"), "DrofusRoomId,NetArea\nNumber,Area\n1,25.5\n2,30.0\n").unwrap();

        let ok = check_drofus(&dir, "d.csv").unwrap();
        assert_eq!(ok.record_count, 2);
        assert_eq!(ok.link_property, "Number");
        assert_eq!(ok.labels, vec!["NetArea".to_string()]);

        assert!(matches!(check_drofus(&dir, "missing.csv"), Err(SettingsError::Invalid(_))));

        std::fs::remove_dir_all(&dir).ok();
    }

    /// A file that fails to parse still appears in the list, carrying its
    /// error — the settings UI stays usable when one file is broken.
    #[test]
    fn test_list_reports_broken_file() {
        let dir = temp_dir("broken-file");
        std::fs::write(dir.join("good.toml"), "project_id = \"p1\"\n").unwrap();
        std::fs::write(dir.join("bad.toml"), "this is not toml [[").unwrap();

        let list = list_project_files(&dir).unwrap();
        assert_eq!(list.len(), 2);
        let bad = list.iter().find(|s| s.file == "bad.toml").unwrap();
        assert!(bad.error.is_some());
        let good = list.iter().find(|s| s.file == "good.toml").unwrap();
        assert_eq!(good.project_id.as_deref(), Some("p1"));

        std::fs::remove_dir_all(&dir).ok();
    }
}
