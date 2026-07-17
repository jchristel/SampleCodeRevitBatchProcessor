# HANDOVER — Export views by level to a vector graphic (SVG) file

**Status:** design settled, not built. Reviewed against the current codebase
(`index.html`, 792 lines).
**Audience:** the next session (Claude Desktop) that implements this.
**One-line scope:** add a browser-side button that saves the current level's
floor plan — plain or with error highlighting — as a standalone `.svg` file.

---

## Decision: build it entirely client-side. No server endpoint.

This is the load-bearing architectural call, and it follows three shipped
precedents rather than inventing anything:

1. **SVG *is* the vector format, and the browser already holds it.**
   `renderLevel` (index.html:270) builds a complete SVG DOM in `#plan`. Exporting
   a "vector graphic file" is just serializing DOM the browser already rendered —
   the exact "presentation reshuffle of data the browser already has" argument
   that kept **Download CSV** off the server. Adding an `/export` route would
   break *"keep axum a pure JSON API — this is the load-bearing decision"*
   (STRATEGY-BROWSER.md).

2. **"Plain vs with errors" is already modeled.** The `showErrors` flag
   (index.html:189) and the `.room.error` class (index.html:110, applied at
   index.html:315) already exist. The export reuses this exact mechanism — no new
   error logic.

3. **"By level" is already the rendering grain.** `renderLevel(payload, levelId,
   …)` is per-level. Export targets the same call against a *detached* SVG node
   instead of `#plan`.

**Do NOT** add a Rust handler, a route in `main.rs`, or anything to the contract.
This is a pure `index.html` change.

---

## What changed since the last review (read this)

The codebase moved on since the feature was first reviewed. Two things to note:

- **A `milestoneSelect` picker was added** (index.html:134, state at
  index.html:181 `currentMilestone`). The plan can now be scoped by project /
  building / **milestone** / level. This does not change the export mechanism,
  but the **export filename should include the milestone** when one is active, so
  an exported file is self-describing. Use `currentMilestone` (null = "latest").
- Line numbers below are current as of the 792-line `index.html`. Re-verify
  before editing; a prior review used stale numbers.

Everything else the review assumed still holds: no SVG export exists yet
(`grep` for `buildLevelSvg|export|serializ|XMLSerial` finds nothing), and
`renderLevel` still hardcodes the global `plan` and mutates the module globals
`view` / `fitted`.

---

## The required refactor (do this first)

`renderLevel` currently:
- writes into the module-global `plan` node directly, and
- mutates the module globals `view` and `fitted` (index.html:276–289).

To export without disturbing the on-screen pan/zoom, extract a **pure builder**
that returns a fresh `<svg>` element and touches no globals:

```js
// Pure: builds and returns a detached <svg> for one level. No global reads
// beyond the payload passed in; no writes to `plan`, `view`, or `fitted`.
// `withErrors` is passed explicitly rather than read from the `showErrors`
// global, so an export's error state is independent of whether the panel is
// currently open on screen.
function buildLevelSvg(payload, levelId, { withErrors = false } = {}) { ... }
```

Then have the live renderer call the builder and adopt its children, so the two
paths can never drift:

```js
function renderLevel(payload, levelId, { refit = true } = {}) {
  // ...compute fitted/view exactly as today (this part still mutates globals,
  // which is correct for the on-screen view)...
  const built = buildLevelSvg(payload, levelId, { withErrors: showErrors });
  plan.replaceChildren(...built.childNodes);
}
```

**Why a pure builder, not "clone `#plan`":** cloning the live node inherits the
current `viewBox` — i.e. wherever the user has panned/zoomed to. An exported
floor plan almost certainly wants the **fitted** view (the whole level, framed),
not the user's current scroll position. Build fresh against the fitted bounds.
Make this a deliberate choice in code, commented.

---

## The four traps (in order of how likely they are to bite)

### 1. Styling lives in the page, not the SVG — the file will be blank/unstyled without inlining ⚠️ most important
There is **no external `.css` file** in this project. All styles live in a single
inline `<style>` block in `index.html`'s `<head>` (roughly lines 8–120): the CSS
custom properties in `:root` (index.html:8–16), then `.room`, `.room.error`,
`.hole`, `.label`, `.label .tag`, `.grid line`. The live `#plan` SVG is styled
only because it sits inside that page. **A `.svg` file saved and opened in
Illustrator / Inkscape / a bare browser tab carries none of `index.html`'s
`<style>` with it** — it will render as unstyled black shapes or nothing.
("External" throughout this doc means external *to the exported SVG file*, not a
separate stylesheet — there isn't one.)

Fix: embed a self-contained `<style>` element inside the exported `<svg>`, with
**the CSS variables resolved to literals**. The current values (index.html:9–15):

| variable        | value     | used by            |
|-----------------|-----------|--------------------|
| `--paper`       | `#f3efe6` | `.hole` fill, bg   |
| `--ink`         | `#1f2421` | strokes, labels    |
| `--rule`        | `#cfc7b4` | grid lines         |
| `--fill`        | `#e4ddc9` | `.room` fill       |
| `--fill-hover`  | `#d4c9a8` | (hover only — omit)|
| `--accent`      | `#b4541f` | `.label .tag`      |
| `--error`       | `#c98c86` | `.room.error` fill |

Don't hardcode these as a copy that will silently drift from `:root`. Read them
at export time with
`getComputedStyle(document.documentElement).getPropertyValue('--error')` and
inject the resolved values, OR add an explicit `<rect>` paper background plus a
generated `<style>` string built from those looked-up values. Either way, the
export must not depend on `index.html`'s `<style>` block being present.

Also add an opaque background `<rect>` covering the viewBox (fill `--paper`) as
the first child — otherwise the exported SVG is transparent, which surprises
people pasting it onto a white or dark surface.

### 2. Namespace + serialization for a standalone file
A freshly built node needs `xmlns="http://www.w3.org/2000/svg"` on the root
(the inline `#plan` sets it at index.html:139, but `document.createElementNS(SVG,
"svg")` on a detached node should carry it too). Serialize with
`XMLSerializer().serializeToString(svg)`. Optionally prepend
`<?xml version="1.0" encoding="UTF-8"?>` for a strict standalone document. Set an
explicit `viewBox` (the fitted bounds) and a `width`/`height` so it opens at a
sensible size outside a sized container.

### 3. "With errors" silently degrades if validation was never loaded
`errorRoomIds` (index.html:188) is only populated once the validation report has
been fetched (panel opened or Refresh pressed). If someone exports "with errors"
without ever loading validation, `errorRoomIds` is empty and the export silently
equals "plain."

Pick one and implement it deliberately (don't leave it a silent no-op):
- disable / hide the "with errors" export until `currentValidation` is loaded, or
- fetch validation on demand inside the export handler before building.

### 4. `vector-effect: non-scaling-stroke` won't behave the same standalone
The room/hole/grid strokes use `vector-effect: non-scaling-stroke`
(index.html:105, 107, 112) so line weight stays constant under the live
zoom/pan. In a static exported file there's no interactive zoom, so this is
mostly harmless — but if a downstream tool scales the SVG, non-scaling-stroke
keeps strokes at 1.5px regardless, which may look wrong at large print sizes.
Low priority; just be aware. If print output matters later, consider emitting
plain (scaling) strokes in the export path.

**Free bonus, no action needed:** the `<title>` tooltip elements (`titleEl`,
index.html:316/383+) carry into the exported SVG and remain as hover tooltips in
a browser. Leave them.

---

## UI wiring

Follow the **Download CSV** pattern exactly (the download plumbing already exists
and works):

- CSV button markup: index.html:149 (`validationDownload`).
- CSV download mechanics to copy: the `Blob` + `URL.createObjectURL` + synthetic
  `<a>.click()` + `revokeObjectURL` sequence in `downloadValidationCsv`
  (index.html ~577–589 region — re-verify line numbers).

Suggested minimal UI: a single **"Export SVG"** button in the header row (near
the pickers) or in the validation panel. Whether it exports plain or
with-errors:
- simplest: export **with-errors when the validation panel is open**
  (`showErrors === true`), **plain otherwise** — this reuses the existing mental
  model with zero new controls, and sidesteps trap #3 (if the panel is open,
  validation is loaded).
- or offer two buttons / a small menu ("Export plain" / "Export with errors").

Recommend starting with the first (one button, mode follows panel state) and
adding the split only if asked.

### Filename
Build a self-describing name from current scope state. Available globals:
`currentProjectId` (179), `currentBuildingKey` (180), `currentMilestone` (181),
`activeLevelId` (176), and the level's display `name` from the payload. Example:

```
roomplan_<project>_<level-name>[_<milestone>][_errors].svg
```

Sanitize to filesystem-safe characters. Fall back to `"project"` / `"level"` when
an id is null (mirrors `downloadValidationCsv`'s `currentProjectId || "project"`).

---

## Scope question to resolve before coding

**Current level only, or all levels?** "views by level" is ambiguous.
Recommendation: **current level only** to start — it matches the renderer's grain
(`renderLevel` is per-level) and is the smallest change. Treat "all levels"
(either a multi-file download or one SVG with a `<g>` layer per level) as a later
additive step. Confirm with the user before expanding, because all-levels changes
the UI (one button vs. a per-level selector or "export all").

---

## Definition of done

- [ ] `buildLevelSvg(payload, levelId, { withErrors })` extracted; pure; returns
      a detached `<svg>`; touches no globals.
- [ ] `renderLevel` refactored to call it (no behavior change on screen;
      pan/zoom/refit identical to today).
- [ ] Export uses the **fitted** view, not the current pan/zoom.
- [ ] Exported SVG is fully self-contained: embedded `<style>` with
      **resolved** color literals, `xmlns` set, background `<rect>`, explicit
      `viewBox` + `width`/`height`. Opens correctly in a bare browser tab AND
      Inkscape/Illustrator without `index.html`'s `<style>` present.
- [ ] "With errors" either loads validation on demand or is disabled until
      loaded — no silent empty-highlight export.
- [ ] Download wired via the existing Blob/`<a>`/`revokeObjectURL` pattern.
- [ ] Filename encodes project + level (+ milestone, + `errors` suffix).
- [ ] No server / `main.rs` / contract changes. `git diff` touches only
      `index.html` (and docs).

## Docs to update on completion
- **STRATEGY-BROWSER.md** — add a bullet under "Implemented" alongside the CSV
  export note, and add it to the SVG-rendering rationale (it's a second consumer
  of the same render path).

## Explicitly out of scope
Server-side rendering, PNG/PDF raster export, print stylesheets, all-levels
export (deferred), north-alignment / scale-bar (tracked separately in
STRATEGY-BROWSER.md "Open items").
