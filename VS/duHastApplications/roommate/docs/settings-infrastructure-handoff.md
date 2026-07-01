# Server Settings Infrastructure — Handoff Summary

**Project:** Rust/axum server for Revit room-outline visualization. Currently one endpoint: `/rooms`.

## Decisions

**1. External reference data (e.g. dRofus) → load via a startup settings file, not a push endpoint.**
Reasoning by the project's established principle — *endpoints follow fetch lifecycle, not data type*:
- dRofus is reference data joined onto rooms in the same render pass; it isn't recomputed on its own trigger or consumed independently → doesn't earn its own endpoint (same reason levels stayed in the payload).
- But it's *not* part of the Revit export — it comes from a separate source → it's config-resolved input wired in at startup, not payload data. That's the line: levels ride inside the POST; dRofus is wired via settings.

**2. Settings loaded once at startup from a `--settings <path>` CLI arg.** Fail fast on bad config rather than on first request.

**3. Sources sit behind a `#[serde(tag = "type")]` enum** so the future file→API swap is a new enum variant + loader change only — the settings contract, app state, and `/rooms` stay untouched.

**4. Optional `test_data` section** seeds a snapshot from disk at startup (dev convenience, skips manual push). Must feed the *same setter the push handler uses* so seed and push can't drift — the file is "a push that happens at boot." Field is `Option` + `#[serde(default)]` so prod config omits it and it can't ship as a live default. Kept as a separate section from `drofus` so removing the test seam later touches nothing else.

## Format: TOML for config, JSON for data

Settings file is **TOML** — it's hand-edited Rust config (matches `Cargo.toml` convention, supports comments, first-class serde support). The *data* it points at (snapshot, dRofus export) stays **JSON** — machine-generated payload, same shape a push sends. Split is deliberate: TOML for config a human edits, JSON for data a machine produces.

## Target settings shape

```toml
[sources.drofus]
type = "file"
path = "./data/drofus.txt"

# Dev only — omit in prod. Seeds a snapshot at startup, skips manual push.
[test_data]
snapshot_path = "./data/test_snapshot.json"
```

## Types (already drafted, annotated)

```rust
use serde::Deserialize;
use std::path::PathBuf;

/// Top-level server settings, parsed once at startup.
#[derive(Debug, Deserialize)]
pub struct Settings {
    pub sources: Sources,

    /// Optional: when present, a snapshot is loaded from disk at
    /// startup so the server has data without a manual push.
    /// `Option` = absent in prod config, present in test config.
    #[serde(default)]
    pub test_data: Option<TestData>,
}

/// External data sources joined onto the Revit snapshot.
#[derive(Debug, Deserialize)]
pub struct Sources {
    pub drofus: DrofusSource,
}

/// dRofus source. `#[serde(tag = "type")]` makes the JSON
/// `"type"` field pick the variant — the file→API swap later
/// is just a new variant, leaving every consumer untouched.
#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum DrofusSource {
    /// Current: read from a local text file.
    File { path: PathBuf },
    // Future: Api { url: String, api_key: String },
}

/// Dev-only seed data. Separate section from `drofus` so removing
/// the test seam later is a one-section deletion.
#[derive(Debug, Deserialize)]
pub struct TestData {
    /// Path to a pre-exported snapshot (same JSON shape a push sends).
    pub snapshot_path: PathBuf,
}
```

## Startup wiring (drafted, annotated)

```rust
use clap::Parser;

/// CLI args. One flag for now: where the settings file lives.
#[derive(Parser)]
struct Args {
    /// Path to the JSON settings file.
    #[arg(long)]
    settings: PathBuf,
}

/// Read + parse settings once. Fail fast at startup if config is bad,
/// rather than discovering it on the first request.
fn load_settings(path: &PathBuf) -> anyhow::Result<Settings> {
    let raw = std::fs::read_to_string(path)?;
    Ok(toml::from_str(&raw)?) // TOML — the `#[derive(Deserialize)]`
                              // types are format-agnostic, so only
                              // the parser call differs from JSON.
}

/// After settings load: if test_data is set, seed the app state with
/// the snapshot from disk. `if let` = no-op when the section is absent.
fn seed_if_test(state: &AppState, settings: &Settings) -> anyhow::Result<()> {
    if let Some(test) = &settings.test_data {
        let raw = std::fs::read_to_string(&test.snapshot_path)?;
        // Parse into the SAME type the push handler accepts, so seed
        // and push converge on one representation and can't drift.
        let snapshot: Snapshot = serde_json::from_str(&raw)?;
        state.set_snapshot(snapshot); // same setter the push uses
    }
    Ok(())
}
```

## To implement in desktop

- `clap` arg parsing for `--settings`, plus `load_settings()` (read + `serde_json::from_str`).
- `seed_if_test()`: `if let Some(test) = &settings.test_data` → read file → parse into the **same `Snapshot` type the push handler accepts** → call the shared setter on app state.
- Load dRofus data once at startup, hold resolved lookup in `Arc<AppState>`; `/rooms` reads already-joined data (keep the snapshot raw, do the join at response assembly).
- Add a STRATEGY.md note: when the real connector lands, `DrofusSource::Api` slots in beside `File`, loader-only change.
