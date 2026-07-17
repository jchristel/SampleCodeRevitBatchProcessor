# Handover: Viewer colour-plan picker not appearing

## TL;DR
The viewer's colour-plan `<select>` never shows because the viewer fetches colour
plans using the **payload project id** (`130486`) against an endpoint that matches
strictly on the **settings `project_id`** (`"Rouse Hill Hospital Health Services"`).
Those are two different id spaces. The fetch 404s, `zone.colourPlans` falls to `[]`,
and `populateColourSelect` hides the select.

**Confirmed empirically** in the browser console:
```js
fetch('/api/settings/projects/Rouse%20Hill%20Hospital%20Health%20Services').then(r => console.log(r.status)); // 200
fetch('/api/settings/projects/130486').then(r => console.log(r.status));                                      // 404
```

This is NOT stale state — resetting/re-pushing the project will reproduce it (the
push mints a payload id that won't equal the settings `project_id`). Do not reset
as a fix.

## Root cause (server)
- `/projects` returns `id = payload.project.id` → `130486` (see `projects.rs:76`,
  `list_projects`).
- Every normal endpoint resolves that id through
  `SettingsRegistry::settings_for` (`state.rs:131`), which does
  `by_project.get(id).or(default)`. Your `RHH.toml` has `is_default = true`, so
  `130486` resolves to the default bundle. That's why room data, buildings,
  milestones, validation all work.
- BUT the settings read endpoint `GET /api/settings/projects/{id}`
  (`settings_api.rs:416 http_get_project` → `get_project_file` at
  `settings_api.rs:144`) matches strictly on `settings.project_id == project_id`
  with **no default fallback**. So `130486` → 404.
- Extra wrinkle: colour plans are client-only. `ProjectSettings` (the live
  registry bundle, `state.rs:66`) does NOT carry `colour_plans`. So the fix
  cannot serve colour plans out of `settings_for`'s bundle — the viewer genuinely
  needs the settings *file* read. The mapping payload-id → file must re-read files
  with default-fallback semantics.

## Constraint that shapes the fix
`GET /api/settings/projects/{id}` is shared by THREE callers:
- `index.html:715` (viewer) — passes the **payload id**, read-only, needs fallback.
- `settings.html:362` and `comparison.html:254` (editors) — pass the **real
  settings `project_id`**, and also PUT to the same path (`settings.html:1154`,
  `comparison.html:312`). These MUST stay strict: a silent default-fallback on the
  editor's GET/PUT could load or overwrite the wrong file.

So: do **not** change `http_get_project` / `get_project_file` behavior globally.
Keep strict for the editors; give the viewer a separate resolving read path.

## Work already done (in the read-only project copy — REDO in the real repo)

### 1. index.html (viewer) — the tick-refresh bug (do keep this)
There were actually two independent problems. The first: `loadColourPlansForProject`
was only reachable on a code path that runs at most once, below an early-return
guard. Fix applied to a copy at `/mnt/user-data/outputs/index.html`:

- Hoisted the colour-plan load in `loadProjects(zone)` to run BEFORE the
  `if (ids === zone.lastProjectIds) return;` early return (that guard fires every
  tick once the project list is stable, making anything after it unreachable in
  steady state).
- Guarded it with a new `zone.colourPlansProjectId` field so it fetches once per
  project change, not every 2s tick.
- Added `colourPlansProjectId: null` to the zone init object (~`index.html:1128`).
- Kept `zone.colourPlansProjectId` in sync in the manual project-change handler
  (~`index.html:1065`).

⚠️ This fix is necessary but NOT sufficient on its own — even reachable, the fetch
still 404s until the server side is fixed (or the viewer resolves the id itself).

The edited viewer is at `/mnt/user-data/outputs/index.html` if useful as reference,
but re-apply against your live `static/index.html` rather than trusting the copy.

### 2. settings_api.rs — resolving reader (half-done, FINISH THIS)
Added a new fn `resolve_project_file` next to `get_project_file`
(`settings_api.rs`, just above `check_drofus`). It tries an exact
`get_project_file` first, then falls back to the file with `is_default = true`.
This mirrors `settings_for`'s semantics but returns the file+parsed `Settings`
(so `colour_plans` come along).

**STILL TODO** (was interrupted here):
1. Add a viewer-facing handler, e.g. `http_get_project_resolved`, identical to
   `http_get_project` but calling `resolve_project_file` instead of
   `get_project_file`. Returns the same `ProjectSettingsResponse`.
2. Register a new route in `main.rs` (~line 110), e.g.
   `.route("/api/settings/resolve/{id}", get(http_get_project_resolved))`
   Keep the existing `/api/settings/projects/{id}` untouched.
3. Point the viewer at the new route: in `index.html:715` change
   `/api/settings/projects/${…}` → `/api/settings/resolve/${…}`.
   (The viewer is the ONLY caller that should use the resolving route.)

### Alternative (viewer-only, no server change)
If you'd rather not touch the server: in `loadColourPlansForProject`, first GET
`/api/settings/projects` (the list — returns `project_id` + `is_default` per
file), find the summary whose `project_id` equals `projectId` OR, failing that,
the one with `is_default === true`, then GET
`/api/settings/projects/<that project_id>`. This duplicates the fallback logic the
server already owns and is more fragile, but it's a one-file change. The server
route is the cleaner option.

## Verification checklist
- [ ] `cargo build` / `cargo test` green. Add a unit test for
      `resolve_project_file`: (a) exact match wins, (b) unknown id falls back to
      the `is_default` file, (c) unknown id with no default → `NotFound`. Mirror
      the style of existing tests in `settings_api.rs` (see the ones around
      `test_settings_without_colour_plans_defaults_empty`).
- [ ] With server running, in console:
      `fetch('/api/settings/resolve/130486').then(r=>console.log(r.status))` → 200,
      and the JSON's `settings.colour_plans` has your 3 plans.
- [ ] Reload the viewer (hard reload — `ServeDir` may 304; Cmd/Ctrl+Shift+R). The
      colour picker appears within ~2s and defaults to the active plan
      ("Designed vs Briefed").
- [ ] Editors unaffected: settings.html and comparison.html still load/save via
      the strict `/api/settings/projects/{id}` route.

## Serving note (why "reload" alone may have looked like nothing changed)
The viewer is static, served from disk via `ServeDir::new("static")`
(`main.rs:113`), relative to the server's **working directory**, not the source
tree. Editing a source copy does nothing unless the file lands in the running
server's `static/` dir. No server restart is needed for an HTML change (ServeDir
reads disk per request), but you DO need the new file in the right `static/` and a
cache-busting hard reload. A `cargo` rebuild IS needed for the Rust changes above.

## Key file/line references
- `projects.rs:61-76` — `list_projects`, source of the payload id.
- `state.rs:131-133` — `settings_for` fallback (the semantics to mirror).
- `state.rs:66-106` — `ProjectSettings` (note: no `colour_plans` field).
- `settings_api.rs:144-153` — strict `get_project_file` (leave as-is).
- `settings_api.rs` (new) — `resolve_project_file` (added; finish wiring it).
- `settings_api.rs:415-423` — `http_get_project` (template for the new handler).
- `main.rs:109-110` — settings routes (add the resolve route).
- `index.html:713-724` — `loadColourPlansForProject` (repoint the fetch URL).
- `index.html:694-708` — `populateColourSelect` (hides select when `plans.length===0`).
