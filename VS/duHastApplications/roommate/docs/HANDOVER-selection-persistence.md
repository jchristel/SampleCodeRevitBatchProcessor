# Handover: URL + localStorage selection persistence

**For:** Claude Code
**Scope:** `index.html`, `settings.html`, `comparison.html`, plus one shared helper in `common.js`
**Goal:** Make each page's scope selection (which project, and on the viewer also building / milestone) survive navigation between the three pages, reloads, and bookmarking — **without** introducing a UI framework or build step.

---

## Why we're doing this

The three pages are independent static documents linked by plain `<a href>`. Today there is **zero** cross-navigation persistence: no `localStorage`, no `sessionStorage`, and `URLSearchParams` is used only to build *fetch* URLs, never to read/write `location.search`. Each page seeds its selection from `projects[0].id` when the current pick isn't found, so viewer → settings → back **resets the user's project pick** to the first available.

We are **not** adopting a framework. Per `STRATEGY-BROWSER.md`, the trigger for that is "manually writing the same state into several DOM places and watching them drift" — we're not there. This is a small, contained URL/`localStorage` fix.

## Design decisions (please honour these)

1. **URL is the source of truth for the current selection; `localStorage` is only the fallback seed.** On load, read the URL first; if absent, fall back to `localStorage`; if still absent, fall back to the existing `projects[0]` default. This keeps deep-links/bookmarks authoritative while still carrying a pick across a plain `<a href>` navigation that drops the query string.
2. **Write the URL with `history.replaceState`, never `pushState`.** Selecting a project is not a navigation; we don't want it to pile up Back-button entries.
3. **One shared `localStorage` key across all three pages** for the project id, so a pick on any page seeds the others. The viewer's building/milestone stay URL-only (they're viewer-specific and per-project; don't leak them into the other pages' seed).
4. **Validate against the server list before honouring a restored value.** A stored/URL project id that the server no longer lists must fall through to the existing default, exactly as an unknown pick does today. Never send a stale id to an endpoint.
5. **Keep it dependency-free and annotated.** Match the house style in these files: heavy explanatory comments on *why*, not *what*. See `CODING-CONVENTIONS.md`.
6. **Multi-zone caveat (viewer):** `index.html` supports multiple zones. Persist only the **first zone's** selection (`zones[0]`). Restoring N independent zone scopes from one URL is out of scope and not worth the complexity; a reload landing on a single restored zone is the accepted behaviour.

---

## Step 1 — Add shared helpers to `common.js`

`common.js` is loaded as a classic script before each page's own `<script>` in `settings.html` and `comparison.html`, exposing plain globals. **`index.html` does NOT currently load `common.js`** (it has its own `fetchJson`). You have two options; **prefer option A**:

- **Option A (preferred):** Add `<script src="common.js"></script>` before the main `<script>` in `index.html` too, so all three pages share these helpers. `common.js` only defines functions, so loading it in the viewer is harmless and de-duplicates the persistence logic.
- **Option B (fallback, only if adding the tag to `index.html` is undesirable):** duplicate the three small helpers inline in the viewer's script and note the duplication in a comment, mirroring how the `:root` tokens are currently duplicated across sibling pages.

Append to `common.js`:

```js
// ---------------------------------------------------------------------------
// Selection persistence (shared by index / settings / comparison).
//
// The three pages are separate static documents linked by plain <a href>, so a
// navigation drops all in-memory state. To keep the user's scope pick across
// pages, reloads, and bookmarks we persist it in two places with a deliberate
// precedence: the URL query wins (so a bookmarked/deep-linked URL is
// authoritative), localStorage is only the cross-page fallback seed, and the
// caller's own default (projects[0]) is the last resort. localStorage carries
// ONLY the project id — it's the one selection every page shares; the viewer's
// building/milestone live in the URL alone (they're per-project and
// viewer-specific, so they must not seed the other pages).
//
// Callers MUST still validate a restored id against the live /projects list
// before using it: a stored id the server no longer lists falls through to the
// default, exactly as an unknown pick does today.
// ---------------------------------------------------------------------------

// The single localStorage key every page reads/writes for the project id.
const LS_PROJECT_KEY = "roommate.project";

// Read a query param from the current URL, or null if absent/empty.
function urlParam(name) {
  const v = new URLSearchParams(location.search).get(name);
  return v ? v : null;
}

// The restore precedence for the project id: URL query > localStorage > null.
// Returns a *candidate* only — the caller still checks it against the server
// list and falls back to its own default if the candidate isn't offered.
function seedProjectId() {
  const fromUrl = urlParam("project");
  if (fromUrl) return fromUrl;
  try {
    return localStorage.getItem(LS_PROJECT_KEY) || null;
  } catch (_) {
    // Private-mode / storage-disabled: treat as no stored seed. Never throw
    // out of a seed read — a blocked storage API must not break page load.
    return null;
  }
}

// Persist the chosen project id: mirror it into the URL (replaceState — this is
// a selection, not a navigation, so it must not add Back-button history) and
// into localStorage as the cross-page seed. Pass extra viewer-only scope in
// `extraParams` (e.g. { building, milestone }) to round-trip it in the URL
// WITHOUT storing it (those keys are dropped when null/empty). A null projectId
// clears both the query and the stored seed.
function persistSelection(projectId, extraParams = {}) {
  const url = new URL(location.href);
  const p = url.searchParams;

  if (projectId) p.set("project", projectId);
  else p.delete("project");

  // Viewer-only scope: present when set, removed when null/empty. These live in
  // the URL only, never in localStorage (they're per-project + viewer-specific).
  for (const [k, v] of Object.entries(extraParams)) {
    if (v) p.set(k, v);
    else p.delete(k);
  }

  history.replaceState(null, "", url);

  try {
    if (projectId) localStorage.setItem(LS_PROJECT_KEY, projectId);
    else localStorage.removeItem(LS_PROJECT_KEY);
  } catch (_) {
    // Storage blocked: the URL still carries the pick for this session, so
    // in-page persistence degrades to URL-only rather than failing.
  }
}
```

---

## Step 2 — `comparison.html` (simplest; do this first as the reference)

State field: `activeProjectId`. Boot calls `loadProjects()`, which seeds `projects[0]` when `activeProjectId` isn't in the list. Selection flows through `selectProject(projectId)`. The change handler is:
`$("projectSelect").addEventListener("change", (e) => selectProject(e.target.value));`

Changes:

**2a.** In `loadProjects()`, replace the seed block so a restored id is honoured when the server still offers it. Current code:

```js
  if (projects.length && !projects.some(p => p.id === activeProjectId)) {
    sel.value = projects[0].id;
    selectProject(projects[0].id);
  }
```

Replace with:

```js
  // Restore precedence: a valid URL/localStorage seed wins, else first project.
  // A seed the server no longer lists is ignored (falls to projects[0]), so we
  // never drive selectProject with a stale id.
  if (projects.length && !projects.some(p => p.id === activeProjectId)) {
    const seed = seedProjectId();
    const restored = seed && projects.some(p => p.id === seed) ? seed : projects[0].id;
    sel.value = restored;
    selectProject(restored);
  }
```

**2b.** At the end of `selectProject(projectId)`, after `activeProjectId = projectId;`, mirror the pick out. Comparison has no building/milestone scope to round-trip, so no extra params:

```js
  activeProjectId = projectId;
  persistSelection(activeProjectId); // URL + localStorage, so the pick survives navigation
```

That's the whole page. Verify: pick a non-default project, hit reload → same project; open `/settings.html` then come back → same project.

---

## Step 3 — `settings.html`

State field: `activeProjectId`. Selection flows through `selectProject(projectId)` (sets `activeProjectId = projectId;` near the top of that function). The list renderer is `loadProjectList()`; **note settings does NOT auto-select a project on load today** — it shows the list and waits for a click. Decide with this rule:

- **Do add auto-restore on load**, because that's the whole point: arriving at settings after picking a project elsewhere should open that project. But only when there's a real seed — don't auto-open `projects[0]` when there's no stored/URL pick (that would change existing "landing shows the list" behaviour for first-time users).

**3a.** In `selectProject(projectId)`, right after `activeProjectId = projectId;`, add:

```js
  activeProjectId = projectId;
  persistSelection(activeProjectId); // keep the pick in URL + localStorage across pages
```

**3b.** Also clear the seed when the user explicitly starts a new/unsaved project, so a later reload doesn't restore a project they navigated away from. In `newProject()`, after `activeProjectId = null;`, add:

```js
  activeProjectId = null;
  persistSelection(null); // no active project → clear the restored-pick seed
```

(When a new project is saved, `save()` already sets `activeProjectId` and calls `loadProjectList()`; add `persistSelection(activeProjectId);` right after the `activeProjectId = data.settings.project_id;` line there too, so a freshly-saved project becomes the seed.)

**3c.** Add a one-time restore in boot. Today boot is just `loadProjectList();`. `loadProjectList()` populates `#projectList` from `GET /api/settings` files; the option ids there are `item.project_id`. After it renders, if we have a seed that matches a listed project and no editor is open yet, open it. The cleanest place is at the very end of `loadProjectList()`, guarded so it only fires once:

```js
// module-level, near activeProjectId:
let didRestore = false; // one-shot: auto-open the seeded project on first list load

// ...at the end of loadProjectList(), after the list is rendered:
  // First render only: if a URL/localStorage seed names a project this list
  // actually contains, open it — that's how a pick made on another page lands
  // here. No seed, or a seed the list doesn't contain, leaves the "pick a
  // project" list untouched (unchanged first-run behaviour).
  if (!didRestore) {
    didRestore = true;
    const seed = seedProjectId();
    if (seed && !activeProjectId) {
      // selectProject here takes the project id used by /api/settings routes;
      // confirm the seed is present before calling so we never open a stale id.
      const items = /* the array loadProjectList just rendered from */ null;
      // Implementation note: reuse whatever local variable holds the parsed
      // file list in loadProjectList (the same one the .map/loop iterates).
      // Guard: only call selectProject(seed) if that list contains project_id === seed.
    }
  }
```

> **Claude Code:** open `loadProjectList()` and read how it iterates the file list (it builds `<li>`s with `class: item.project_id === activeProjectId ? "active" : ""`). Use that same in-scope list variable for the `contains(seed)` check, then call `selectProject(seed)`. Keep the one-shot `didRestore` guard so subsequent `loadProjectList()` refreshes (which happen after every save/select) don't re-trigger a restore and fight the user.

---

## Step 4 — `index.html` (viewer; most involved)

Per-zone state lives on the `zone` object built in `createZone(seed)`: `zone.projectId`, `zone.buildingKey`, `zone.milestone`. Boot ends with `createZone(null); setLayout(); tick(); setInterval(tick, 2000);`. Project resolution happens in `loadProjects(zone, projects)` (around the `if (!projects.some(p => p.id === zone.projectId))` block that falls back to `projects[0]`). Change handlers live in `wireZoneControls(zone)`.

**Only `zones[0]` is persisted** (see decision 6).

**4a.** If you took Option A in Step 1, add before the main `<script>`:

```html
<script src="common.js"></script>
<script>
```

**4b.** Seed the *first* zone from the URL/localStorage. In `createZone(seed)`, the initial project comes from `seed ? seed.projectId : null`. The boot call is `createZone(null)`, so the first zone starts `null` and later resolves to `projects[0]` inside `loadProjects`. Add restore in that resolver. Find in `loadProjects(zone, projects)`:

```js
  if (!projects.some(p => p.id === zone.projectId)) {
    zone.projectId = projects.length ? projects[0].id : null;
```

Change to honour a seed **only for the first zone, and only before its first resolve**:

```js
  if (!projects.some(p => p.id === zone.projectId)) {
    // Restore the first zone's project from URL/localStorage on first resolve;
    // additional zones (and later re-resolves) keep the plain projects[0]
    // default. A seed the server no longer lists falls through to projects[0].
    let fallback = projects.length ? projects[0].id : null;
    if (zone === zones[0] && !zone._seeded && projects.length) {
      zone._seeded = true; // one-shot, so a later project deletion re-defaults cleanly
      const seed = seedProjectId();
      if (seed && projects.some(p => p.id === seed)) fallback = seed;
    }
    zone.projectId = fallback;
```

Add `_seeded: false,` to the zone object literal in `createZone` (near `projectId`), with a comment: `// one-shot guard: first-zone URL/localStorage restore has run`.

> Also restore `building`/`milestone` for the first zone from the URL here, *after* `zone.projectId` is set and its buildings/milestones have loaded. The simplest correct spot: after the existing `await loadBuildingsForProject(...)` / `await loadMilestonesForProject(...)` calls that follow project resolution, read `urlParam("building")` / `urlParam("milestone")` and assign them to `zone.buildingKey` / `zone.milestone` **only if** the freshly-loaded option lists contain them (guard against stale scope, same as project). Gate this on the same `zone === zones[0] && restore-not-yet-done` condition — reuse a second one-shot flag (e.g. `zone._seededScope`) so the 2s poll's repeated building/milestone refreshes don't clobber a user's later manual change.

**4c.** Persist on change. In `wireZoneControls(zone)`, the project, building, and milestone `change` handlers each mutate `zone.*` and set `zone.lastRevision = null`. Add persistence, but **only when this is the first zone**, so a second zone's picker doesn't overwrite the URL:

At the end of the `projectSelect` change handler:
```js
    if (zone === zones[0]) persistSelection(zone.projectId, { building: zone.buildingKey, milestone: zone.milestone });
```

At the end of the `buildingSelect` change handler:
```js
    if (zone === zones[0]) persistSelection(zone.projectId, { building: zone.buildingKey, milestone: zone.milestone });
```

At the end of the `milestoneSelect` change handler:
```js
    if (zone === zones[0]) persistSelection(zone.projectId, { building: zone.buildingKey, milestone: zone.milestone });
```

(Building/milestone go in the URL only; `persistSelection` won't store them in `localStorage`. When they're `null` — e.g. right after a project change resets them — the helper drops those params, which is what we want.)

---

## Testing checklist

Run the server and exercise all three pages:

1. **Deep-link:** open `/comparison.html?project=<id>` for a real id → that project is selected on load. Same for `/settings.html?project=<id>` and `/?project=<id>` (viewer, first zone).
2. **Cross-page carry:** pick a non-default project on the viewer → open `settings` (plain link, no query) → the seeded project opens. Then `compare` → same project preselected.
3. **Reload:** after any pick, reload → same selection (URL carries it).
4. **Stale id:** hand-edit the URL to `?project=does-not-exist` → page falls back to the default (`projects[0]` on viewer/comparison; list-with-no-editor on settings), no failed fetch to a bad id.
5. **New-project clears seed (settings):** start a new project, navigate away and back → does not auto-reopen a phantom project.
6. **Back button:** changing the project must **not** add history entries (we used `replaceState`) — pressing Back should leave the page, not step through prior selections.
7. **Multi-zone (viewer):** add a second zone, change its project → URL reflects only the first zone; reload restores the first zone only. No error from the second zone's handler.
8. **Storage blocked:** in a private window with storage disabled, nothing throws; URL-based persistence still works within a session.

## Out of scope (do not implement)

- Persisting per-zone scope for multiple viewer zones.
- Persisting colour-plan / validation-panel / areas-mode UI toggles (transient view state, not scope).
- Any server-side change — this is entirely client-side, keeping axum a pure JSON API per `STRATEGY-BROWSER.md`.
- A framework, router, or build step.
