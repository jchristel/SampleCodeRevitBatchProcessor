# HANDOVER — Units & Georeferencing

Adds two related pieces of metadata to a push and surfaces them in project
settings:

1. **Units** — every push declares the units its numbers are in, the server
   normalises everything to a fixed canonical (**metres**) at ingest, and
   stores/compares canonical. Geometry is never converted; only scalar
   properties are.
2. **Georeference** — an optional, advisory real-world datum (e.g.
   `"MGA2020-54"`) carried on the push and echoed into project settings. The
   server records it; it does no projection math.

Read this whole doc before writing code. The design decisions below were made
deliberately and each has a rejected alternative — don't re-litigate them in
code.

---

## The core mental model (read this first)

A single Revit push carries **two independent unit regimes at once**, and this
is the fact the whole design turns on:

- **Room polygons are ALWAYS feet.** The pyRevit exporter reads Revit internal
  units and does not convert. This is true regardless of the Revit project's
  display settings.
- **Room property values (Area, and any length/area parameter) are feet OR
  metric**, depending on the Revit project's unit settings — Revit hands these
  back already formatted in the project's display units. pyRevit pulls the raw
  strings **without checking units**, so the numbers alone are ambiguous
  (`25.5` could be ft² or m²; there is no reliable per-room heuristic).

Therefore a push needs **two declared units**, not one:

- `geometry_unit` — what the polygons are in (Feet for Revit, self-declared for
  IFC).
- `property_unit` — what the property values are in.

These are independent. A metric Revit project pushes **feet polygons and
metre-squared areas in the same payload.**

### Why the user declares `property_unit` at push time

pyRevit does **not** read the project's display-unit setting, and we are
**not** adding that. Reasons, in order:

- Units in Revit can vary *per parameter*, not just globally — there is no
  single project-level answer to read.
- A human at push time knows their own project.
- We make a wrong pick **discoverable** rather than trying to prevent it (see
  "Making a wrong pick loud" below). "He'll find out eventually" is acceptable
  *because* we make it fast to find out — it is not acceptable as silent
  corruption.

So: the push picker asks metric-vs-imperial, pyRevit forwards the human's
choice verbatim, the server never second-guesses the value but *does* sanity
-check its magnitude.

### Why canonical = metres, stored converted (not "store native")

We convert imperial pushes **in** to metres at ingest and store metres. The
rejected alternative was "store whatever the first push declared, convert the
minority source only at comparison time." Metres-canonical wins because:

- dRofus comparison and reporting are often metric already → trivial.
- The comparison layer (`numeric_match` / `elevation_match`) stays completely
  unit-blind: it only ever sees one unit. **Do not make it unit-aware.**
- One conversion at one trust boundary is easier to reason about than
  conversion scattered through comparison.

Cost accepted: a US/imperial shop's stored numbers are converted rather than
native. That's fine — raw pushes are kept in history untouched (see below), so
nothing is lost.

### Why geometry is never converted

The only cross-source comparisons that matter are **scalar** (Revit `Area` vs
dRofus `NetArea`, elevation). Nothing ever numerically diffs a Revit *polygon*
against a metric one — the viewer auto-fits, so absolute polygon units don't
matter for rendering either. Converting every `Point2D` would be a large blast
radius for zero benefit. **Convert three or four scalars per room; leave
geometry alone.**

This means: only `property_unit` drives conversion. `geometry_unit` is
recorded (for correctness of any future scale-bar / north-alignment / absolute
placement work — see STRATEGY-BROWSER "Coordinates and units") but does **not**
trigger any conversion today.

---

## What to build

### 1. `contract.rs` — the wire types

Add a `Unit` enum and a `GeoReference` struct, and put two unit fields + an
optional georeference on the envelope.

```rust
/// A unit that a pushed number can be expressed in. A CLOSED enum, not a free
/// string: the ingest boundary must reject a unit the normaliser can't convert
/// rather than storing an un-normalisable value that silently corrupts every
/// downstream comparison. Adding a unit is a deliberate code change here plus a
/// factor in `to_metres`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Unit {
    /// Revit internal units. The historical default — `Point2D` was feet-only,
    /// so this is what a pre-units producer means.
    Feet,
    Meters,
    Millimeters,
}

impl Unit {
    /// Metres-per-unit factor. Canonical storage unit is metres (see
    /// HANDOVER-units "canonical = metres"), so every scalar is multiplied by
    /// this at ingest. Meters is 1.0 (identity) by construction.
    pub fn metres_per_unit(self) -> f64 {
        match self {
            Unit::Feet => 0.3048,     // exact, by international definition
            Unit::Meters => 1.0,
            Unit::Millimeters => 0.001,
        }
    }
}

/// Default unit for a payload field that omits it. Feet, because the only
/// producer that predates this field is Revit, whose polygons are always feet —
/// so defaulting keeps every pre-units payload meaning exactly what it did.
fn default_unit() -> Unit {
    Unit::Feet
}

/// Optional geospatial datum tying a model's model-space origin to real-world
/// coordinates — e.g. "MGA2020 Zone 54". A free-form *label only*: the server
/// records and echoes it, it does NOT parse or project with it. `None` means
/// the model is ungeoreferenced (fine for auto-fit viewing; only matters once
/// footprints are aligned/moved across projects — see STRATEGY-SERVER "common
/// coordinate frame"). Its own struct, not a bare String, so a future datum
/// component (explicit rotation/offset) is an additive field here.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GeoReference {
    /// The datum/zone as the producer names it, e.g. "MGA2020-54". Opaque to
    /// the server.
    pub crs: String,
}
```

Add to **both** `RoomPayload` **and** `StreamEnvelope` (they must stay in
lockstep — a streamed push and a whole push carry identical identity/metadata;
the only difference is where `rooms` come from):

```rust
    /// Unit the room POLYGON coordinates are in. Always Feet for the Revit
    /// source (the exporter does not convert internal units); self-declared for
    /// IFC. Recorded but NOT converted — geometry is stored as-pushed (see
    /// HANDOVER-units "geometry is never converted"). `#[serde(default)]` →
    /// Feet keeps pre-units payloads valid and unchanged in meaning.
    #[serde(default = "default_unit")]
    pub geometry_unit: Unit,

    /// Unit the room PROPERTY values (Area + any length/area parameter) are in
    /// — INDEPENDENT of `geometry_unit`. Revit returns these already formatted
    /// in the project's display units, so a metric Revit project sends feet
    /// polygons but m² areas in one payload. pyRevit forwards the user's
    /// push-time metric/imperial choice here without inspecting the values.
    /// This is the ONLY field that drives ingest conversion.
    #[serde(default = "default_unit")]
    pub property_unit: Unit,

    /// Optional real-world datum for this model. Absent on ungeoreferenced
    /// pushes. Advisory: recorded into project settings and echoed, never used
    /// for math.
    #[serde(default)]
    pub geo_reference: Option<GeoReference>,
```

**Schema version: do NOT bump `SUPPORTED_SCHEMA` (stays 5).** All three fields
default, so every existing v5 payload stays valid and means exactly what it did
(feet, feet, no georef). This is a pure relaxation — identical reasoning to
`taken_at` becoming omittable. Update the `SUPPORTED_SCHEMA` doc comment to note
units were added as a compatible relaxation.

Do the TOML-footgun check (CODING-CONVENTIONS "TOML footgun"): wherever these
land in a *serialized* struct, scalar fields (`geometry_unit`, `property_unit`)
must precede any map/sub-table field, and `geo_reference` (a sub-table) must
come after all scalars.

### 2. The normaliser — convert scalars in, at ingest

A small, pure, well-tested function that takes a room's property map + the
`property_unit` and returns a map with the length/area scalars converted to
metres. This is the one place conversion happens.

Key subtleties to get right and test:

- **Only length/area properties convert.** A Department string, a room number,
  a name must pass through untouched. You need a definition of "which
  properties are dimensional." The safest source is the same
  canonical-name/`BuiltinPropertyDef` machinery `lookup_property` already uses:
  convert the properties that resolve to known dimensional canonicals (`Area`,
  and any configured length/area field), leave everything else. **Do not
  convert by guessing from the value.** Confirm the exact set with the project
  owner — at minimum `Area`; elevation lives on `Level`, see next point.
- **`Level.elevation` is a length** and is part of the property regime (it's a
  Revit dimensional value), so it converts by `property_unit` too. Don't forget
  it — `elevation_match` compares it.
- **Area is a length², not a length.** If `Area` is expressed in ft² its factor
  is `0.3048²`, not `0.3048`. Make the normaliser aware of dimension
  (length vs area) per property, or you will be off by ~10.76×. This is the
  single easiest bug to introduce here — test it explicitly.
- Conversion happens **after** `ensure_taken_at` and the other envelope
  resolution, at the same ingest trust boundary. After normalisation, nothing
  downstream ever sees non-metres.

### 3. Project settings — establish + guard the unit

The project record must remember the unit it was established in (store
`property_unit`; also store `geometry_unit` and `geo_reference` for display).
The `settings` module isn't in the file set I was working from — locate the
project record type (tracked the way `source` is) and add the fields there,
plus their surface in `settings.html` and the settings API read path (and the
MCP `get_project_settings` read tool, which reuses the settings-API core).

Then add the **consistency guard** at ingest:

```rust
/// A push's declared property unit must match what the project was first
/// established in. First push SETS the project unit; a later mismatch is a hard
/// 422 rather than letting the store mix regimes. This is the fast path by
/// which a wrong push-time metric/imperial pick surfaces — the next push of a
/// normally-correct project rejects the day it's fat-fingered. Geometry unit is
/// recorded but not guarded (it doesn't drive comparison). Georeference is
/// advisory: it updates, it never rejects.
pub fn check_unit_consistency(
    established: Option<Unit>,
    incoming: Unit,
) -> Result<(), String> {
    match established {
        Some(u) if u != incoming => Err(format!(
            "project is registered in {u:?}; this push declares {incoming:?}. \
             Repush in the project's units or change the project's unit in \
             settings — the server does not convert between established units."
        )),
        _ => Ok(()),
    }
}
```

Note: the *stored* numbers are always metres regardless; this guard is about
the *declared* unit matching, so a project doesn't silently flip regime between
pushes. Establishing-on-first-push mirrors how the store already grows from
pushes (mod.rs: "project.toml is authoritative and two-way... a push for an
unknown project creates the structure").

### 4. Making a wrong pick loud — the first-push sanity band

The consistency guard (#3) catches every push **after** the first. The first
push (or a project deliberately re-declared) has no prior unit to diff against,
so the only signal is the magnitudes themselves. Add a **soft warning** (per
CODING-CONVENTIONS "Signal, not error" — this is fall-back+warn, NOT a
rejection; we promised not to second-guess the user's value):

- At the **whole-model** level, feet² and metre² totals differ by ~10.76×. Sum
  the room areas; if the declared unit implies a total that's implausible for a
  building (or wildly inconsistent with the declared unit's expected range),
  emit a warning into the **validation report** — not a 422.
- This is deliberately whole-model, not per-room: a single small room is
  genuinely ambiguous between ft² and m², but a whole building's total is not.
- Keep the band wide and dumb. Its only job is to catch the exact mistake we're
  tolerating (user picked the wrong radio button), at the one moment the hard
  guard can't. False positives here are worse than a few misses, because a
  false positive teaches users to ignore the warning.

Surface it wherever validation signals already surface (the validation report
the MCP `get_validation` tool and the browser read).

### 5. Raw history stays raw

The store keeps every push in its own timestamped file, never overwritten
(mod.rs). **Keep storing the raw pushed payload as-is** (feet, whatever the
user declared) in that history file — do the metres normalisation on the
*read/serve/compare* path, or store a normalised derived copy alongside, but do
not lose the original. Reason: if a user discovers a wrong metric/imperial pick
three pushes later, the fix must be re-interpreting stored history, not asking
them to re-export a model that may have moved on. Decide with the project owner
whether normalisation is store-time-derived or read-time; either is fine as
long as the raw push survives.

---

## Open questions to resolve with the project owner before/while coding

1. **The dimensional-property set.** Exactly which canonical properties convert,
   beyond `Area`? Any length parameters (perimeter, height, clear width)? This
   determines the normaliser's conversion table. Anything not on the list passes
   through untouched.
2. **dRofus units.** Is the dRofus CSV (`NetArea`) always metric by convention,
   or should it declare its unit too? Current CSV (`DrofusRoomId,NetArea,
   Department` → `1,113.89,Cardiology`) states no unit. If dRofus is assumed
   canonical-metric, the compare is direct; if not, dRofus needs its own
   declared unit and the same normalisation. **Confirm before writing the
   compare path** — it decides whether the dRofus join needs a unit field.
3. **Normalise at store-time or read-time?** (see #5 above). Pick one.
4. **IFC's `geometry_unit`.** Out of scope to *implement* now (no IFC source
   yet), but confirm the enum covers the likely IFC units (m, mm — both
   present). Add others only when a real IFC file needs them.

---

## Conventions to follow (from CODING-CONVENTIONS.md)

- **Inline tests** at the bottom of each touched file. The normaliser deserves
  thorough unit tests: feet→m, mm→m, m→m identity, **area uses the squared
  factor**, non-dimensional properties untouched, elevation converts.
- **Annotate the "why"**, not the what — every field and function above has its
  rationale in the doc comment; keep that density.
- **Loud startup / loud ingest**: the consistency guard is a specific 422
  message, the sanity band is a specific validation warning.
- **Dependency direction**: conversion + guard logic is transport-agnostic
  (`service`-side); handlers and mcp.rs stay thin adapters.
- **Don't make the comparison layer unit-aware.** Its whole simplicity is that
  it sees one unit. Normalise before it, never inside it.
- Module-length rule: if `contract.rs` or the settings module crosses ~500
  non-test lines with these additions, split per the `foo/` + `mod.rs`
  re-export pattern.
