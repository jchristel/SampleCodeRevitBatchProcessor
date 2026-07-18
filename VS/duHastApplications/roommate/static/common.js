// Shared browser helpers for the roommate pages. Kept tiny and dependency-free
// (STRATEGY-BROWSER.md: vanilla JS, no build step). Served from static/ by
// axum's ServeDir and loaded as a classic <script> BEFORE each page's own
// <script>, so these are plain globals — no module wiring.
//
// settings.html and comparison.html both talk to the same settings API in the
// same shape, so the two helpers below were byte-identical copies in each page.
// index.html keeps its own `fetchJson` (a GET-only variant with a different
// error message) and does not use these.

// GET JSON with no-store caching; throws the server's error text (falling back
// to "<url> -> <status>") on a non-2xx so callers surface it verbatim.
async function apiGet(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text() || `${url} -> ${res.status}`);
  return res.json();
}

// Send JSON (POST/PUT/…). Returns { ok, status, text } WITHOUT throwing, so the
// caller can show the server's 422 validation text verbatim.
async function apiSend(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  return { ok: res.ok, status: res.status, text };
}

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
