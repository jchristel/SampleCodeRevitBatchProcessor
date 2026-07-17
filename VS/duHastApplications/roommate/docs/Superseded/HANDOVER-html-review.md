# HANDOVER — HTML best-practice review (index / settings / comparison)

**Status:** review complete on the copies available; **needs verification against
the live tree** before acting.
**Audience:** the next session (Claude Desktop), which has access to all three
files including `comparison.html`.
**Purpose:** hand over findings + a decision framework, and list exactly what to
re-check, because the review copy was missing one file.

---

## ⚠️ Read first: what this reviewer could and couldn't see

The review was done against the project snapshot in `/mnt/project/`. On that
snapshot **only two HTML files exist on disk**: `index.html` (791 lines, CRLF)
and `settings.html` (940 lines, LF). **`comparison.html` is listed in the project
manifest but was NOT present on disk**, so it was reviewed as *absent*.

Every recommendation below hinges on whether `comparison.html` is real and is a
**third page that copies the same design tokens / JS helpers**. That is the
single fact that flips the main recommendation from "leave inline" to "extract."
**Your first job is to resolve that.** See the checklist at the end.

---

## Overall verdict (for the two files seen)

Both files are **well-structured and not bloated.** They are long by line count,
but the length is inherent to the work — SVG floor-plan rendering + live-polling
viewer (`index.html`), and a full settings/dRofus editor (`settings.html`) — not
padding. Specifically:

- **Clear sectioning.** Both use banner comments (`// --- pan & zoom ---`,
  `// ---------- save ----------`) that make navigation easy.
- **Small, single-purpose functions.** ~34 functions in `index.html`, ~28 in
  `settings.html`; the largest (`renderLevel`, ~60 lines) is the core routine and
  earns its size.
- **Comments explain *why*, not *what*** (the two-pass label paint order, the
  level-dedup rationale). Above-average discipline.

This matches the project's own stated strategy in **STRATEGY-BROWSER.md**: *"Keep
axum a pure JSON API… Grow the vanilla JS until it actually hurts… adopting a
framework earlier is toolchain overhead for no payoff."* Judged against that
philosophy, the files are compliant, not sloppy. **Do not "modernize" into a
framework or split into many files on general principle** — that would fight a
deliberate, documented decision.

---

## Should there be an external CSS file?

**Currently defensible as-is. The duplication is already a conscious, documented
choice**, not an oversight: `settings.html`'s `:root` block carries the comment
*"the two pages are siblings, so the `:root` tokens are copied verbatim rather
than extracted."*

### What is actually duplicated
Only the **design tokens** — the `:root` custom-property block (`--paper`,
`--ink`, `--rule`, `--fill`, `--fill-hover`, `--accent`, `--error`, `--mono`;
`settings.html` adds `--ok`). ~8–9 near-identical lines per file. **The rest of
each file's CSS is page-specific** (`index.html`: `.room` / `.hole` / `.grid`;
`settings.html`: form + drop-zone styling) and does **not** belong in a shared
file.

### The rule of thumb
- **Two copies:** borderline — inline is fine, the comment already owns the
  tradeoff.
- **Three copies:** tips toward extraction. Three pages copy-pasting the palette
  makes "change the accent colour" a three-file edit that *will* drift.

`comparison.html`, if it exists and reuses the palette, is that third copy.

### If you extract
- Extract **only the shared `:root` tokens** into `static/tokens.css`; `<link>`
  it from all pages. Leave page-specific CSS inline.
- Cost is low: `static/` is already served by axum's `ServeDir` (main.rs:109), so
  one more static file is trivial to wire.
- **Independence from the SVG-export feature:** extracting tokens does NOT
  simplify the planned SVG export (see `HANDOVER-svg-export.md`). That export must
  inline **resolved colour literals** regardless, because the saved `.svg` leaves
  the page entirely and can't reference `tokens.css` either. Treat the two
  decisions as unrelated.

### Higher-value than CSS: shared JS
The stronger DRY signal is **JS helpers**, not CSS. `index.html` defines
`fetchJson`, `escapeHtml`, `csvEscape`. `settings.html` re-implements its own
`fetch` wrapper (around line 270) rather than sharing one. Overlap is minor today
(`settings.html` doesn't currently use `escapeHtml`), so it's **not urgent** — but
the same "third page" trigger applies, and *logic* drift causes bugs where
*palette* drift only causes cosmetic mismatch. If you extract anything, a tiny
`static/common.js` (`fetchJson` + `escapeHtml` + the blob-download helper) is the
higher-value move. Verify `comparison.html` doesn't add a *third* copy of these
before deciding.

---

## Concrete nits found (small, real, low-risk)

1. **Line-ending inconsistency.** `index.html` is **CRLF**, `settings.html` is
   **LF**. Normalise to one and add a `.gitattributes` (`*.html text eol=lf`) so
   this stops producing noisy whole-file diffs. **Check `comparison.html`'s
   endings too** and fold it into the same fix.
2. **Phantom `comparison.html`.** Manifest lists it; disk (in the review
   snapshot) didn't have it. Resolve the mismatch — deleted? renamed? uncommitted?
   Something references the name.
3. **One inline `style="..."` attribute** — the settings link in `index.html`
   line 138 (`style="margin-left:auto; color:var(--accent); font-size:0.72rem;
   text-decoration:none;"`). It's the *only* inline style in either file seen
   (`settings.html` has zero), so it breaks an otherwise-clean "styles live in
   `<style>`, not on elements" rule. Move it to a class. Trivial.

---

## Recommendation (decision tree for the next session)

```
Is comparison.html real AND does it reuse the :root palette / JS helpers?
├── NO  → Leave CSS inline. The 2-file duplication is documented and fine.
│         Still do the 3 nits above (endings, phantom-file, inline style).
└── YES → Extract shared :root tokens → static/tokens.css, <link> from all 3.
          Strongly consider static/common.js for fetchJson + escapeHtml +
          download-blob helper (verify comparison.html isn't a 3rd copy of
          these). Leave page-specific CSS/JS inline. Do the 3 nits too.
```

Either branch: **do not** split the page-specific CSS/JS out, and **do not**
introduce a build step or framework — both contradict STRATEGY-BROWSER.md.

---

## Verification checklist for Claude Desktop (against all 3 files)

- [ ] Confirm which HTML files actually exist. Resolve the `comparison.html`
      manifest-vs-disk mismatch (deleted / renamed / uncommitted?).
- [ ] Diff the `:root` blocks across all three. Confirm the token set is truly
      shared (and note any per-page additions like `settings.html`'s `--ok`).
- [ ] Check whether `comparison.html` re-implements `fetchJson` / `escapeHtml` /
      `csvEscape` / a download-blob helper — i.e. is it the "third copy" that
      justifies `common.js`?
- [ ] Confirm line endings per file; if mixed, normalise + add `.gitattributes`.
- [ ] Grep all three for inline `style="..."` attributes; move any to classes.
- [ ] Confirm each page's non-token CSS is genuinely page-specific (it should NOT
      be extracted) before touching anything.
- [ ] Re-confirm section-banner + small-function structure holds in
      `comparison.html` too; if it's the odd one out (giant functions, no
      sections), that's where cleanup effort should focus, not the two clean
      files.
- [ ] Sanity-check that any extraction still leaves the SVG-export feature
      inlining resolved colour literals (the two are independent — don't let a
      `tokens.css` lull the export into referencing it).

---

## Out of scope
Framework migration, build tooling, bundlers, splitting page-specific CSS/JS,
server-side templating. All contradict the committed "vanilla JS until it hurts /
axum stays a pure JSON API" strategy.
