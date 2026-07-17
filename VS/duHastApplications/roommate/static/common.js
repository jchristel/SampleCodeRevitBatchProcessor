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
