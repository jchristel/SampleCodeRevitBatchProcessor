# Handover: Colour Plans (persisted, ColorBrewer-based room colouring)

**For:** Claude Desktop, implementing in this Rust + vanilla-JS project.
**Status:** Design agreed. Nothing built yet. This document is the spec.

---

## 0. Code annotation directive (READ FIRST — applies to every file you touch)

This codebase has a distinctive, deliberate commenting style. **Match it. Do not
write thin restating comments; write comments that explain *why*, and that record
the decision and its alternatives.** Concretely:

- **Doc-comment every struct, enum, enum *variant*, and public fn** with `///`,
  explaining what it is *and why it exists / why it's shaped this way*. Look at
  `Settings`, `DrofusFieldConfig`, `FieldType`, `CompareMode` in `settings.rs` as
  the reference standard — e.g. the `drofus_fields` field carries a ~15-line
  comment covering type, QA override, and the "absence is fine" discipline.
- **Explain the road not taken.** Existing comments say things like "One
  declaration per column, not two separate lists — 'what is this column' shouldn't
  be answered in two places that can drift apart." Your new comments should do the
  same: when you pick a `Vec` over a map, a client-side computation over a
  server-side one, say why.
- **Record invariants and "absence is fine" defaults.** Every optional/defaulted
  field explains what omitting it means. Preserve this.
- **In the JS**, match the existing inline-comment density in `index.html`
  (see the `flip`, `bounds`, `levelsForPayload`, `renderLevel` region ~lines
  175–390). Explain coordinate math, fallbacks for older payloads, and any colour
  math.
- Keep comments truthful to the code. If you change behaviour, update the comment.

**This directive is not optional and not a nicety — annotation quality is a
first-class deliverable here, weighted equally with correctness.**

---

## 1. What we're building

Three room-colouring modes for the browser viewer, configured in the settings UI,
**persisted per project** in the existing settings file, applied **entirely
client-side** in the viewer.

1. **Hierarchy** — categorical hue per parent level, tint/shade per child level.
2. **Date range** — colour rooms by proximity of a date-typed property to a
   selected date: green = nearest, red = furthest, blue = in the future.
3. **Property comparison** — compare two room properties (A vs B) and colour by
   the result. This single mode supports three colouring styles under it:
   - **match/mismatch** — `|A−B| ≤ tolerance` → 2 colours (the dRofus-vs-Revit QA case);
   - **difference** — `A−B` mapped onto a diverging ramp, auto-scaled, centred on 0;
   - **bands** — user-defined cutoff→colour ranges.

### Two decisions already locked (build these, not alternatives)

- **Simplest persistence model:** a library of named plans (`Vec<ColourPlan>`),
  with **one marked active**. This mirrors the existing `milestones` pattern
  exactly. Do *not* build per-user or transient-only state.
- **Palettes: hand-picked JS constant.** Bundle a small set of ColorBrewer schemes
  as a JS object in the viewer. **Do NOT add `d3-scale-chromatic` or any npm
  dependency** — the browser layer is vanilla JS with no build step, and we're
  keeping it that way.

---

## 2. Architectural constraint (load-bearing — do not violate)

**The server stores and returns `colour_plans` verbatim and does nothing else with
it.** All parsing, comparison, colour computation, and palette lookup happen in the
browser, where room property values already live.

This is the same decision that kept CSV export and QA rendering client-side:
"axum stays a pure JSON API." The server MUST NOT compute colours, parse property
values for colouring, or grow a `/colour` endpoint. Adding server-side colour logic
would repeat the mistake the strategy docs explicitly warn against. If you find
yourself writing colour math in Rust, stop — it belongs in `index.html`.

Consequence: the Rust change is almost entirely **serde plumbing** — add the field,
let it round-trip, validate lightly. The real work is JS.

---

## 3. Rust side — `settings.rs` (+ validation, + a test)

### 3.1 Add one field to `Settings`

Following the `milestones` / `drofus_fields` precedent exactly:

```rust
/// User-authored colour plans for the viewer: named, persisted colouring
/// configs the user switches between. Lives in settings (not storage) for the
/// same reason milestones do — per-project user metadata with the same
/// lifecycle as hierarchy/room_label, riding this file's save pipeline
/// (validation, atomic install, hot-reload) for free.
///
/// The server treats this as opaque: it stores and serves it verbatim and
/// computes no colours. ALL colour math is client-side, where room property
/// values already live — the same "keep axum a pure JSON API" decision that
/// kept CSV export and QA rendering out of the server. A `Vec` (not a single
/// plan) so a project can keep a library of plans; exactly one is marked
/// active via `ColourPlan.active`. Empty if omitted — no plan, today's flat
/// fill.
#[serde(default)]
pub colour_plans: Vec<ColourPlan>,
```

### 3.2 New types (put them near `DrofusFieldConfig`, reuse its patterns)

All derive `Debug, Clone, Deserialize, Serialize`. Enums use
`#[serde(rename_all = "lowercase")]` and/or tagged representations consistent with
`FieldType`/`CompareMode`. **Annotate every variant.**

```rust
/// One named, persisted colouring configuration. `active` picks the single
/// plan the viewer applies; more than one `active: true` is a config error
/// (validated — see `validate_colour_plans`). `name` is user-facing only.
pub struct ColourPlan {
    pub name: String,
    #[serde(default)]
    pub active: bool,
    pub mode: ColourMode,
}

/// The three colouring strategies. Tagged enum (serde adjacently/internally
/// tagged — match whichever the JS is easiest to branch on; internally tagged
/// on a "kind" field is recommended) so the wire shape is self-describing and
/// the browser can switch on one field.
pub enum ColourMode {
    /// Categorical hue per parent hierarchy tier, tint/shade per child. Which
    /// tiers participate and which qualitative scheme is used are the payload.
    Hierarchy { /* tiers: Vec<...>, scheme: String */ },

    /// Proximity of a date-typed property to `near_date`: nearest = green,
    /// furthest = red, future = blue. `property` is a canonical property name
    /// (resolved browser-side the same way labels are). `scheme` names a
    /// bundled diverging/sequential palette.
    DateRange { /* property: String, near_date: String, scheme: String */ },

    /// Compare two properties A and B. `op` derives one number per room
    /// (difference or ratio); `colouring` maps that number to a colour. This
    /// one variant carries all three colouring styles (match / diverging /
    /// bands) because they share the same A,B,parse,compute pipeline and only
    /// differ in the final number→colour step.
    PropertyCompare {
        /* property_a: String, property_b: String,
           op: CompareOp,          // Diff | Ratio
           colouring: Colouring,   // Match{tolerance} | Diverging{scheme} | Bands(Vec<Band>)
        */
    },
}
```

Fill in the commented-out fields as real fields. Keep every one documented. For the
numeric-parse-with-tolerance behaviour, **reuse the existing dRofus comparison
philosophy** (numeric-adaptive if both sides parse, else exact) rather than
inventing a second one — cross-reference `CompareMode` in your comments.

### 3.3 Validation (mirror `validate_drofus_fields`)

Add `validate_colour_plans(...)` in the same "loud startup error over silent no-op"
style as the existing validators. Check at minimum:

- **At most one `active` plan** across the `Vec` (like the cross-file `is_default`
  check, but within one file so it can run in the normal validation step).
- A `DateRange`/`PropertyCompare` referencing property names is *not* hard-failed
  for unknown names — follow the `room_label` precedent ("an unresolvable name just
  contributes nothing"), because properties are source-native and vary. Document
  this choice explicitly.
- **`Bands` cutoffs MUST NOT overlap** — hard-fail at load with a loud error
  (same discipline as the other validators), naming the offending plan and the two
  overlapping bands. Bands must form a sorted, disjoint partition of the value line:
  each band is a half-open interval `[lo, hi)`, and band *n*'s `hi` must be `<=`
  band *n+1*'s `lo`. Reject overlaps *and* out-of-order bands here rather than
  silently picking a winner at colour time — an overlap is a config mistake, and
  "first match wins" would hide it. (Gaps between bands are allowed and render as
  the "no data"/grey fill — document that so a deliberate gap isn't mistaken for a
  bug.)

Wire it into wherever `validate_drofus_fields` is called (check `main.rs` load
sequence — dRofus validation runs *after* settings+dRofus are both loaded; colour
validation only needs settings, so it can run earlier, alongside hierarchy).

### 3.4 Test (mirror `test_v5_room_properties_round_trip`)

Add a serde round-trip test proving a `Settings` with `colour_plans` survives
TOML/JSON round-trip intact, **and** that a `Settings` with no `colour_plans` key
still deserializes to an empty `Vec` (the `#[serde(default)]` guarantee — this is
the backward-compat safety net for every already-saved project file).

### 3.5 What you do NOT touch on the server

`settings_api.rs` needs **no change** — `http_get_project` / `http_update_project`
already serve and accept the whole `Settings` struct as JSON. The new field rides
along automatically. Confirm this by reading those two handlers; do not add routes.

---

## 4. Browser side — `index.html` (the real work)

### 4.1 Bundled palette constant (hand-picked, no dependency)

Add a JS constant near the top with a handful of ColorBrewer schemes as literal hex
arrays. Suggested minimum set:

- `RdYlGn` (diverging) — date proximity & difference. Note: green=near means you may
  apply it reversed; document the direction.
- `RdBu` (diverging) — signed difference centred on zero.
- `Greens`, `Blues` (sequential single-hue) — hierarchy child tint/shade ramps.
- `Set2` or `Paired` (qualitative) — hierarchy parent hues.

Comment each array with its ColorBrewer name and intended use. Include a short
helper to sample a scheme at position `t ∈ [0,1]` (piecewise-linear across the hex
stops) and one for picking the k-th qualitative colour.

### 4.2 Colour function

Write a pure `colourForRoom(room, plan, context)` that branches on `plan.mode.kind`
and returns a fill hex (or the "no data" grey). `context` carries per-render
precomputed scale info (min/max difference across the level, active date, hierarchy
tier→hue assignment) so the per-room call is cheap. Key behaviours to implement and
**comment heavily**:

- **String values.** `room.properties[name].value` is a string like
  `"1.49999935417"`. Parse with tolerance for numeric modes; this is the same
  precision issue logged as a known bug. Non-numeric properties support only
  match/mismatch, not difference — detect and degrade gracefully.
- **Missing property / unparseable** → return the defined "no data" grey, never
  drop the room or throw.
- **Diverging scales centre on zero**; auto-scale extent to the level's data.
- **Bands are pre-validated as sorted and non-overlapping** (see §3.3), so the JS
  can do a simple ordered scan and return the first band whose `[lo, hi)` contains
  the value — no overlap-resolution logic needed. A value in a gap between bands, or
  outside all bands, returns the "no data" grey. Comment that this simplicity is
  *earned by* the server-side validation, so nobody later adds redundant handling.
- **Date mode**: parse dates (reuse the strftime/format thinking from dRofus date
  fields where relevant), ignore time-of-day, future→blue branch is separate from
  the green→red ramp.

### 4.3 Wire into `renderLevel`

`renderLevel(payload, levelId, …)` (~line 270) currently sets each room polygon's
class to `"room"` / `"room error"` (~line 315), and fill comes from CSS vars
(`--fill`, `--error`). For colour plans, when a plan is active, set the polygon's
`fill` **presentation attribute** directly from `colourForRoom(...)`, overriding the
CSS class fill. Preserve the existing hover/error behaviour when no plan is active
(don't regress the current look). Comment the precedence clearly: active plan fill >
error highlight > default `--fill`.

Precompute the per-level `context` once before the room loop, not per room.

### 4.4 Reading the active plan

The viewer already fetches settings-derived data; read `colour_plans`, pick the one
with `active: true` (first wins if somehow several — but validation should prevent
that), and pass it to the render path. If none active or list empty → today's
behaviour unchanged.

---

## 5. Settings UI — `settings.html`

Add a `<section class="block">` titled "Colour plans", following the **Milestones**
section pattern exactly (`settings.html` ~line 230: a `.rows` container +
`+ colour plan` button, rows built by the same `el(...)` helper, saved by the same
`apiSend("PUT", …)` path that persists the whole `Settings` object).

Each plan row: name input, active radio (radio, not checkbox — enforces single
active in the UI), mode dropdown, and mode-specific controls:

- **Hierarchy**: tier multiselect + qualitative scheme dropdown.
- **Date range**: property dropdown (date-typed) + date input + scheme dropdown.
- **Property compare**: property A dropdown, property B dropdown, op (diff/ratio),
  then colouring sub-mode (match → tolerance field; diverging → scheme dropdown;
  bands → editable cutoff→colour rows, add/remove like milestone rows).

Property dropdowns populate from the union of property keys seen in the current
project's rooms (same source the label/QA config uses). Persistence is free: it's
all one `Settings` PUT.

---

## 6. Build order (suggested)

1. Rust: add `colour_plans` field + types + `#[serde(default)]` + round-trip test.
   Confirm `settings_api` untouched. **Get the round-trip test green first** — it
   proves persistence end-to-end before any UI exists.
2. Rust: `validate_colour_plans` + wire into load sequence.
3. JS: palette constant + `colourForRoom` + unit-check the colour math in isolation.
4. JS: wire into `renderLevel` with correct fill precedence.
5. `settings.html`: the editor section (start with Property-compare/match, since it
   serves the real QA need, then add the other modes/styles).

Each step is independently testable. Steps 1–2 are pure serde/validation; 3 is pure
function; only 4–5 touch live rendering.

---

## 7. Known adjacent bugs (do NOT fix here, just don't trip over them)

- Property values are strings with float noise (`1.49999935417` vs `1.5`) — your
  tolerance parse must handle this, but the underlying precision bug is separate and
  already logged.
- Level duplication across files exists — hierarchy mode may surface it; don't try
  to fix level dedup as part of this feature.

---

## 8. Definition of done

- A named colour plan created in `settings.html` persists across reload (saved in the
  project settings file, round-trips through serde).
- Exactly one plan is active; the viewer colours the current level accordingly.
- All three modes work; property-compare supports match / difference / bands.
- Missing/unparseable data renders grey, never errors.
- Server has no colour logic and no new routes.
- **Every new struct, enum, variant, fn, and non-trivial JS block is annotated to
  the standard of §0.**
