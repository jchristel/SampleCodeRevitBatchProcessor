# Handover: Viewer performance regression (zoom / general sluggishness)

**Status:** root cause NOT yet confirmed. This document gives a *leading
hypothesis* and two cheap, code-free tests to confirm it before writing any fix.
Please run the tests first — several earlier diagnoses in this investigation were
made from post-hoc flame-chart reading and turned out partly wrong. Measure, then
fix.

---

## Why the 2s poll exists, and the recommended fix (middle path)

**Purpose of the poll.** The data model is push-driven: an external producer
(pyRevit pushing room snapshots from Revit) sends new snapshots to the server;
the server holds the latest in memory; the viewer has **no other notification
channel**. So `tick()` polls `/rooms` every 2s to discover "has a newer snapshot
been pushed?" and re-renders on change. The same tick also refreshes the
project/building pickers so a newly-pushed project appears without a reload
(`index.html:1157-1158`). The 2s cadence is just "feels live enough." This is the
intended *live-monitoring* experience: keep the viewer open and watch rooms update
as the model is edited/re-pushed.

**The project already anticipated this exact cost.** `STRATEGY-BROWSER.md:261-264`
("Open items / things to watch") flags that re-stringifying the whole payload every
2s "may feel sluggish" on a big building, and names the cheap fixes: *a longer
interval* or *a small fingerprint (room count + hash)* instead of full stringify.
So this is a known, documented soft spot — not a mystery.

**Recommended fix — poll, but cheaply (keeps live-ness, removes the per-tick cost).**
Replace the full `JSON.stringify(payload)` change-detection (`index.html:975`) with
a lightweight fingerprint, and/or lengthen the interval. This preserves auto-update
and does **not** require changing the payload design — only the change-detection
stops round-tripping the whole payload. It is also the clean fix for the leading
hypothesis below (a volatile field in the payload forcing re-render every tick),
because you stop comparing volatile JSON.

⚠️ **Fingerprint caveat — check what field you actually have.** The obvious
"compare the snapshot id" approach has a snag here, verified against the code:

- The single-model **upload envelope** (`RoomPayload`) carries `snapshot.taken_at`
  (RFC3339 UTC) — but that is the *ingest* shape, not what the viewer receives.
- The viewer's `/rooms` response is `RoomsResult` (`rooms.rs:150-155`), which merges
  every stored model and exposes **only** `schema_version`, `levels`, `rooms`. It
  does **NOT** carry `taken_at` or any per-snapshot revision. So there is currently
  no ready-made stable id on the viewer payload to compare.

Two ways to get a stable fingerprint, pick one:

1. **Client-side stable hash (no server change).** Build the compare key from only
   the fields that affect rendering, explicitly excluding anything volatile:
   e.g. hash `rooms.length` + each room's `[id, level_id, loops, properties-that-
   render]`. Cheaper than full stringify if you hash incrementally, and immune to
   volatile fields by construction. Simplest if you can't touch the server.
2. **Server adds a revision to `RoomsResult` (cleaner, preferred).** Add a stable
   field the merge can compute — e.g. the max `taken_at` across contributing models,
   or a content hash, or a monotonic counter bumped on each push. Then the client
   compares one value. This is the "add the field where the merge already knows the
   answer" option and avoids the client hashing 390 rooms at all. Note `RoomsResult`
   merges N models, so a *single* `taken_at` isn't enough — it must summarize all
   contributing snapshots (max, or a hash of the set).

**If live auto-update turns out NOT to be needed** (workflow is push-then-open, not
watch-live), a manual **Refresh** button (or refresh-on-window-focus) is even
simpler and drops idle cost to zero. This is a product/workflow call the user
should confirm: *is the viewer meant to update live while someone re-pushes from
Revit, or is it open-inspect-close?* The cheap-poll fix above is the safe default
if live-ness is wanted or unknown.

---

## What is actually established (high confidence)

These are conclusions backed by evidence gathered this session, not guesses:

1. **The problem is long-standing and version-independent.** The user profiled
   older `index.html` versions (including pre-"zoning"/multi-zone builds) and the
   slowness is present there too. → Multi-zone/"zoning" did NOT introduce it.

2. **The multi-zone tick did NOT cause it, but it amplifies it.** `tick()`
   (`index.html:1160`) loops zones **serially** with `await loadProjects(zone);
   await poll(zone)` and re-fetches the global `/projects` list once per zone per
   tick. With N zones that's N× the work, serially, every 2s. This is a real
   inefficiency that makes a pre-existing cost N× worse, but it is not the origin.

3. **Two changes made earlier this session are NOT the cause** (they postdate the
   user's original report). One of them, however, is a *current-profile* cost and
   should be reverted regardless — see "Cleanup" below.

4. **Bottom-up profile (zoomed-in, current build) top self-times:**
   - `Recalculate style` — 168ms, 27%
   - `poll` (`index.html:1004`ish, the poll fn) — 159ms, 25.6%
   - `Paint` — 58ms
   - `setViewBox`, `get clientWidth`, `Layout` — ~40ms each
   The two dominant buckets are **style recalc** and **poll**.

5. **Labels are NOT the bottleneck.** Hiding all `.label` elements
   (`document.querySelectorAll('.label').forEach(l=>l.style.display='none')`) left
   frame times at 200–383ms. Do not spend effort on label culling as a fix.

---

## Leading hypothesis (UNCONFIRMED — confirm via the two tests below)

**The viewer performs a full teardown-and-rebuild re-render on every 2s tick,
because per-tick change-detection sees the payload as "changed" every time.**

Mechanism, by line:

- `poll` (`index.html:969`) fetches `/rooms`, then does
  `const incoming = JSON.stringify(payload)` (`:975`) and compares to
  `zone.lastPayloadJson` (`:976`). This is O(payload) every tick, every zone —
  that alone plausibly explains `poll`'s 25.6% self-time (stringifying ~390 rooms
  × N zones every 2s).
- On *any* detected difference it calls `ingest` (`:678`), which calls
  `renderLevel(..., { refit: true })` (`:688`). `renderLevel` does
  `plan.replaceChildren()` (`:542`) and rebuilds every polygon + label from
  scratch. That full rebuild is the likely source of the `Recalculate style` /
  `Layout` / `Paint` costs.
- **If the payload contains anything volatile** (a server-side generated-at
  timestamp, a "last sync"/wall-clock field, or non-deterministic JSON key order),
  then `incoming !== lastPayloadJson` is **true every tick even when nothing real
  changed**, so the full re-render fires every 2s forever, in every version. The
  header meta line shows a wall-clock time ("11:04:46 am") and a "v5" revision —
  suggesting the payload may well carry volatile fields.

Why this fits all the evidence:
- Version-independent: this code path exists in every version.
- Worsens over time without code changes: payload has grown richer (dRofus join,
  more fields) and room counts are high, so the per-tick stringify + rebuild got
  heavier even though the logic didn't change.
- N×-amplified by zoning: the serial per-zone tick multiplies it.
- Felt "zoom-related": if a 2s re-render lands mid-gesture it janks the zoom, and
  `refit: true` (`:688`) even snaps the view back to `zone.fitted` — so a spurious
  re-render also **resets the zoom level**, which the user may perceive as
  zoom-specific stutter.

---

## Confirm BEFORE fixing — two code-free tests

### Test A — Is the payload volatile? (the smoking gun)
In the viewer's console, capture two consecutive `/rooms` responses on a quiet
system (no edits, no interaction) and diff them:

```js
const u = document.querySelector('svg.plan') && location.origin; // sanity
async function grab(){ const r = await fetch('/rooms',{cache:'no-store'}); return await r.text(); }
const a = await grab(); await new Promise(r=>setTimeout(r,2500)); const b = await grab();
console.log('identical:', a === b);
if (a !== b) {
  // find first differing region
  let i=0; while(i<a.length && a[i]===b[i]) i++;
  console.log('first diff at', i, JSON.stringify(a.slice(i-40,i+80)), '\\n vs \\n', JSON.stringify(b.slice(i-40,i+80)));
}
```
- `identical: true` → payload is stable; hypothesis about *volatility* is wrong,
  but the per-tick `JSON.stringify` cost (Test B) may still be the issue.
- `identical: false` → **confirmed**: the diff region names the volatile field
  (expect a timestamp / sync-time / generated-at). This is the root cause.

*(Note: an older client build may hit the current server; the payload shape is the
server's, so this test is valid on any client version.)*

### Test B — Is the tick the cost at all? (isolation)
Neuter the poll so no re-render happens, then interact:

```js
poll = async () => {};   // stops per-tick fetch+stringify+re-render
```
Then zoom/pan for ~10s.
- Smooth now → the tick re-render path is the dominant cost. Combined with Test A,
  you know whether it's *volatility* (A=false) or just *stringify weight*
  (A=true) driving it.
- Still janky → there is a genuine **per-frame gesture cost** independent of the
  tick. Re-profile the wheel path; suspect the viewBox-change → style/layout on
  `.room` strokes (this is where the reverted `--sw` change and the original
  `non-scaling-stroke` both live — see Cleanup).

Run A and B together: they form a 2×2 that uniquely identifies the cause.

| Test A (payload) | Test B (neuter poll) | Conclusion |
|---|---|---|
| differs | becomes smooth | **Volatile payload → spurious full re-render every tick.** Fix change-detection. |
| identical | becomes smooth | Payload stable but per-tick stringify+rebuild too heavy. Fix change-detection cost. |
| either | still janky | Per-frame gesture render cost. See **"Zoom-dependent cost: no viewport culling"** below — investigate that before stroke/viewBox style recalc. |

---

## Investigate: zoom-dependent cost — no viewport culling (option)

**This is a distinct, independent cost from the poll, and it's the best current
explanation for a specific user observation the poll story does NOT explain:**

> Zoomed **out** (lots of geometry on screen) → OK, slight stutter. Zoomed **in**
> (less on screen) → really slow.

If the poll re-render were the only cost, zoom level wouldn't matter — rebuilding
390 polygons costs the same wherever the viewBox sits. So the zoom-dependence
points at a **second, per-frame, zoom-sensitive** cost. Leading explanation:

**SVG clips; it does not cull.** Every room polygon, hole, and grid line stays in
the DOM at all times (`renderLevel` appends all of them; nothing removes off-screen
ones on view change). Zooming in does **not** reduce the element count the browser
must process each frame — it still walks all ~390+ elements, transforms each by the
viewBox, and then clips the off-screen majority away. Clipping is not free, and two
things make it *worse* when zoomed in, not better:

1. **The grid.** `renderLevel` (~`index.html:588`) draws grid lines across the full
   `zone.fitted` bounds at a fixed `step = 5` — a fixed line count regardless of
   zoom. Zoomed in, each line becomes enormous in device space (thousands of
   screen-px long, mostly off-screen) and must still be rasterized/clipped every
   frame. Long strokes overhanging the viewport are a classic zoomed-in cost.
2. **Stroke geometry.** With `non-scaling-stroke` (the original, post-Cleanup
   state), the on-screen width stays constant but the browser recomputes the stroke
   in device space on every viewBox change, over polygon edges whose device-space
   extents are now huge.

So the user's culling intuition is right, just inverted: the problem is that there
is **no** culling, so zoom-in doesn't shed work, and the geometry left in the DOM
gets more expensive to process the deeper you zoom. Labels being ruled out earlier
is still consistent — they're a *constant* chunk, not the *zoom-scaling* one.

### Confirm (all console-only, no code)

1. **Element count is constant across zoom** (confirms no culling). In Elements,
   count `svg.plan` children zoomed out vs zoomed in — expect the same ~390+.
   Or: `console.log(document.querySelector('svg.plan').childElementCount)` at each
   zoom.
2. **Grid experiment** (isolates the grid, ~10s):
   ```js
   document.querySelectorAll('.grid').forEach(g => g.style.display='none');
   ```
   Then zoom in and pan. If zoomed-in smoothness jumps noticeably → oversized
   off-screen grid lines are a real contributor.
3. **Culling experiment** (isolates rooms — the actual fix test): while zoomed in,
   hide rooms whose bbox is outside the current viewBox and see if pan/zoom smooths.
   Rough version:
   ```js
   const z = window.zones?.[0]; const vb = document.querySelector('svg.plan').viewBox.baseVal;
   document.querySelectorAll('.room').forEach(p => {
     const b = p.getBBox();
     const off = b.x+b.width < vb.x || b.x > vb.x+vb.width || b.y+b.height < vb.y || b.y > vb.y+vb.height;
     p.style.display = off ? 'none' : '';
   });
   ```
   (Note `getBBox` itself forces layout — this is a one-off probe, not the real
   implementation.) If hiding off-screen rooms at high zoom smooths interaction →
   culling is the fix.

### If confirmed — fix direction
- **Viewport-cull DOM elements on view change:** hide (or don't append) rooms/holes
  whose bounding box is outside the current viewBox, recomputed on pan/zoom. Store
  each room's precomputed bbox at build time (avoid per-frame `getBBox`, which
  forces layout). Throttle the cull to `requestAnimationFrame` so a burst of wheel
  events does one cull per frame, not one per event.
- **Cap grid extent to the visible region** rather than the full `fitted` bounds —
  regenerate grid lines for the current viewBox on view change (throttled), or
  clip the grid group. Removes the oversized off-screen grid-line cost.
- These are per-frame-render fixes and are **independent of** the poll/fingerprint
  fix — a full solution likely needs both: fingerprint kills the periodic stutter
  (zoomed out and in), culling kills the zoomed-in stall.

⚠️ Culling changes render behavior (elements leave/re-enter the DOM on pan/zoom);
verify hover/label/colour-plan behavior still works for elements that re-appear.

---

## Fix directions (apply only what the tests point to)

**If Test A shows a volatile payload (most likely):**
- Apply the cheap-fingerprint fix from the **"Why the 2s poll exists"** section
  above (client-side stable hash, or a server-added revision on `RoomsResult`).
  That section has the important caveat: `RoomsResult` (`rooms.rs:150-155`) exposes
  only `schema_version`/`levels`/`rooms` — there is **no** `taken_at`/revision on
  the viewer payload today, so you either hash a stable subset client-side or add a
  field server-side. Do not assume a snapshot id is already there to compare.
- Whichever you pick, the point is the same: stop feeding volatile JSON into the
  change gate at `index.html:975`, so a quiet system triggers no re-render.

**If Test B still janky (per-frame cost):**
- **First**, work the **"Zoom-dependent cost: no viewport culling"** section above —
  especially if the jank scales with zoom-in. Viewport culling + capping grid
  extent is the most likely lever, not stroke recalc.
- Avoid `refit: true` on tick re-renders so a re-render never resets the user's
  zoom (`ingest:688` → pass `refit:false` when the level/scope is unchanged; only
  refit on an actual level/project switch). This alone removes the zoom-reset
  symptom even if a re-render still fires.
- Only after the above, investigate stroke/viewBox style recalc on the gesture.

**Independent of the tests — reduce the amplifier (`tick`, `:1160`):**
- Fetch `/projects` **once per tick**, not once per zone.
- Run zones' `poll` **concurrently** (`await Promise.all(zones.map(poll))`) instead
  of serially. Reduces the N× serial stall zoning introduced.

---

## Cleanup: revert an earlier-session change (do this regardless)

Earlier this session a stroke-scaling change was added to *this working copy* to
try to fix zoom cost: a `--sw` CSS custom property with
`stroke-width: calc(1.5 * var(--sw))` on `.room`/`.hole`/grid, plus a
`setStrokeScale(zone)` that reads `svg.clientWidth` inside `setViewBox`.

- It did **not** address the real (pre-existing) problem, and in the current
  profile it is itself a cost: the `clientWidth` read forces a synchronous
  **Layout**, and writing `--sw` invalidates the `calc()` stroke-width on every
  polygon → the 27% **Recalculate style**.
- **Revert it**: restore `vector-effect: non-scaling-stroke` on `.grid line`,
  `.room`, `.hole` (was at `index.html:104,107,112`), and remove `setStrokeScale`,
  the `--sw` var, and the `clientWidth` read from `setViewBox`. `non-scaling-stroke`
  was in every historical version and was never shown to be the bottleneck.

⚠️ This working copy in outputs ALSO contains the (good) colour-picker fix and the
tick-refresh guard from a separate handover (`HANDOVER-colour-picker-fix.md`). When
reverting the stroke change, keep the colour-picker changes. Safest path: re-apply
the colour-picker fix onto a clean current `index.html` rather than shipping this
copy, so the unrelated stroke experiment doesn't ride along.

---

## Key line references (current upload)
- `index.html:969-983` — `poll`; `:975` the `JSON.stringify` compare; `:976` the change gate.
- `index.html:678-690` — `ingest`; `:688` `renderLevel(..., {refit:true})` (rebuild + zoom reset).
- `index.html:540-542` — `renderLevel` / `plan.replaceChildren()` full teardown.
- `index.html:1160-1165` — `tick` (serial, per-zone, re-fetches `/projects`).
- `index.html:1194` — `setInterval(tick, 2000)`.
- `index.html:104,107,112` — strokes (revert target for the `--sw` cleanup).
- Meta line shows "v5" + wall-clock time → candidate volatile/revision fields for Test A / the fix.

## Verification once fixed
- Test A re-run: with the new change-detection, a quiet system triggers **no**
  `ingest`/`renderLevel` between real changes (add a temporary
  `console.count('re-render')` in `ingest` and confirm it stays flat while idle).
- Idle profile: no periodic 200–383ms tick spikes in the Frames track.
- Zoom holds: zooming in and waiting through several ticks does NOT snap the view
  back to fitted.
- Multi-zone: with 3 zones, idle tick cost is roughly flat vs 1 zone (parallelized
  + single `/projects` fetch), not 3×.
