# Handover — RoomMate module-length refactor

**Project:** `roommate` (Rust, edition 2024, axum server). Revit → Rust → browser room-data pipeline.

## Purpose of this handover
A module-length / structure review was completed in Claude (chat). This documents the findings and the agreed plan so the work can continue in Claude Desktop with the full repo checked out.

## Context
- Total Rust: ~7,600 lines across 20 modules.
- Convention in this repo: unit tests live inline as `mod tests` at the bottom of each file (idiomatic — keep it). Judge module size by **non-test** lines.

## Findings — modules over 500 lines

| Module | Total | Impl (pre-`mod tests`) | Verdict |
|---|---|---|---|
| storage.rs | 968 | ~610 | **Split** |
| rooms.rs | 911 | ~373 | Fine (but long fn — see below) |
| settings_api.rs | 840 | ~480 | Borderline — leave for now |
| settings.rs | 760 | ~515 | **Split** (mixed concerns) |
| validation.rs | 755 | ~357 | Fine (but long fn) |
| contract.rs | 628 | ~354 | Fine — pure type/contract module |
| handlers.rs | 557 | ~377 | Fine |

## Agreed plan (priority order)

### 1. Split `storage.rs` (clearest win)
Two full trait impls in one file. Target layout:
- `storage/mod.rs` — `SnapshotStore` trait + `ProjectManifest`, `ModelEntry` types
- `storage/fs.rs` — `FsStore` (currently lines ~156–568; the `impl SnapshotStore for FsStore` block at 272–568 is ~300 lines and the real weight)
- `storage/mem.rs` — `MemStore` (~569–666)
Move each type's tests into the sub-module with the code it tests.

### 2. Split `settings.rs` (three concerns in one file)
Currently mixes: config/domain types, validation free-functions, and loaders. Target:
- `settings/mod.rs` — types (`Settings`, `ServerConfig`, `Storage`, `Sources`, `Milestone`, `HierarchyTier`, `BuiltinPropertyDef`, enums)
- `settings/validate.rs` — `validate_strftime`, `validate_drofus_fields`, `validate_drofus_field_shapes`
- `settings/load.rs` — `load_settings`, `load_server_config`, `resolve_relative_to`

### 3. Break up long functions (bigger smell than module size)
- `assemble_rooms` — rooms.rs ~174–373 (~200 lines)
- `compute_validation` — validation.rs ~190–342 (~150 lines)
- Long `impl SnapshotStore for FsStore` methods in storage.rs

Enable the lint to surface them:
```toml
[lints.clippy]
too_many_lines = "warn"   # flags fns > 100 lines
```

### Not doing
- `settings_api.rs` — mixes HTTP DTOs with service logic but still cohesive; revisit only if it grows.
- `rooms.rs`, `validation.rs`, `contract.rs`, `handlers.rs` — single-responsibility, under ~380 real lines. Leave.

## Housekeeping
- `settings.rs` uses `\r\n` line endings while other modules use `\n`. Normalize via `.gitattributes` (`*.rs text eol=lf`) to avoid noisy diffs — do this **before** the split so the diff stays clean.

## Suggested first step in Desktop
Run `cargo clippy` with the `too_many_lines` lint on to get an authoritative list of long functions, then start the `storage.rs` split. Add annotations/doc-comments as you go (per project preference for well-annotated Rust).
