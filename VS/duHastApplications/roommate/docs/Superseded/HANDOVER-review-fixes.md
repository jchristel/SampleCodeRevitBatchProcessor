# HANDOVER — Code-review fixes (items 1–6)

Context: a review of the codebase looked for design changes implemented as
afterthoughts — places where the design moved (service-layer extraction,
per-project settings, multi-project merge) but the code only partially
followed. Six findings, ordered here by how to tackle them: the two
behavioral bugs first (they change output), then the structural cleanups.
Item 7 (dead `ServiceError` variants, unused `get_latest`, duplicated ingest
checks, mixed line endings) is deliberately out of scope.

Every fix below preserves the codebase's existing disciplines: loud startup
errors over silent no-ops, transport types never below `handlers`/`mcp`,
derived data never written back to state, and doc comments that carry the
*why*.

---

## Fix 4 (do first) — Level dedup merges levels across projects

**File:** `service/rooms.rs`, `assemble_rooms`.

**Problem.** The level-dedup pass predates per-project settings: it iterates
the whole `scoped` list and collapses any two levels with the same
`(name, elevation)` — even when they belong to *different projects*. In an
unscoped call, two unrelated projects that both have "Level 1" @ 0.0 collapse
to one canonical level id, and rooms from project B get remapped onto a level
id minted from project A's model. The comment above `scoped` even says "an
unscoped merge is now inherently per-project", but the dedup loop never got
that memo. Level identity is only meaningful *within* a project (the dedup
exists for linked models of one job, per its own doc comment).

**Fix.** Make the dedup group key include the project. Two equivalent
shapes; prefer (a) as the smaller diff:

(a) Key `level_remap` and the canonical-levels lookup by project:

```rust
// canonical levels per project, not one flat list
let mut canonical_levels: BTreeMap<String, Vec<Level>> = BTreeMap::new(); // project_id -> levels
// remap key grows a project dimension
let mut level_remap: BTreeMap<(String, String, String), String> = BTreeMap::new(); // (project_id, model_id, level_id) -> canonical
```

In the dedup loop, look up/push within `canonical_levels.entry(key.project_id.clone())`,
and insert into `level_remap` with the 3-tuple. In the emit loop, read the
remap with the 3-tuple. `ModelKey` already carries `project_id`, so both
loops have it in hand — no signature changes.

(b) Alternative: restructure `assemble_rooms` to process one project at a
time (group `scoped` by project id first). Cleaner long-term, but a larger
diff; only take this if you're touching the function heavily anyway.

**Note on `emitted_level_ids`:** it stays a flat set — canonical ids are
model-local `Level.id`s and could in principle collide across projects. If
you take shape (a), also key `emitted_level_ids` by `(project_id, canonical_id)`
so a collision can't suppress another project's level. Cheap insurance, same
loop.

**Tests to add (rooms.rs tests module):**
- Two payloads in *different* projects, each with "Level 1" @ 0.0 →
  unscoped `assemble_rooms` returns **two** levels, and each project's room
  keeps a level id from its own project.
- Existing `test_assemble_rooms_dedups_levels_by_name_and_elevation`
  (same-project case) must stay green unchanged.

---

## Fix 5 — Building filter leaks rooms from tier-less projects

**File:** `service/rooms.rs`, `assemble_rooms`.

**Problem.** When `?building=X` is given, a project whose hierarchy has no
"Building" tier hits the `else` branch (`payload.rooms.iter().collect()`) and
contributes **all** its rooms — into a response the caller believes is
filtered to one building of some *other* project. The "graceful degrade"
(no tier → filter is a no-op) was written when there was one settings bundle
for the whole server; it's wrong once projects with different hierarchies
coexist in one merge.

**Fix.** When a building filter is requested and the payload's bundle has no
Building tier, the model matches nothing — skip it:

```rust
let matching_rooms: Vec<&Room> = match (building, building_idx) {
    (Some(wanted), Some(idx)) => /* existing classify-and-filter path */,
    (Some(_), None) => Vec::new(), // filter requested, project can't answer it: contributes nothing
    (None, _) => payload.rooms.iter().collect(),
};
```

And treat the filter as "active" whenever `building.is_some()`, so the
levels-skip rule (`building_filter_active && matching_rooms.is_empty()`)
also drops that project's levels:

```rust
let building_filter_active = building.is_some();
```

**Semantics decision, made deliberately:** this changes single-project
behavior too — previously, `?project=p1&building=X` where p1 has no Building
tier returned everything; now it returns empty. That's the correct reading:
the caller asked for a building, p1 has no notion of one, and `list_buildings`
already tells the caller `tier_configured: false` so a well-behaved client
never sends this combination. An empty result is honest; a silently ignored
filter is not. Update the `assemble_rooms` doc comment (the "no-op rather
than an error" paragraph) to say exactly this.

**Tests to add:**
- Project A with a Building tier and a room in building X; project B with
  *no* hierarchy and one room. Unscoped `assemble_rooms(_, None, Some(keyX))`
  → only A's room, and only A's levels.
- Scoped: `assemble_rooms(_, Some("B"), Some(keyX))` → empty rooms/levels,
  `store_empty: false`.

**MCP note:** no code change in `mcp.rs` (its `get_rooms` just forwards to
`assemble_rooms`), but update the `#[tool(description = ...)]` text to state
the new rule — a project with no "Building" tier matches nothing under a
building filter — since an LLM client acts on that description literally.
This is the only Fix-5 touch outside `service/rooms.rs`. (For the record:
`mcp.rs` needs no update for the per-project settings architecture itself —
it shares `bootstrap::build_state` with the HTTP binary, so the two entry
points can't drift on registration, default bundle, or store selection.)

---

## Fix 1 — `store_empty` smuggles a transport concern through the domain

**File:** `service/rooms.rs`, `handlers.rs`, `bin/mcp.rs` (mcp.rs in this
project's flat copy).

**Problem.** `RoomsResult.store_empty` exists only so the HTTP adapter can
emit 204; the handler then hand-builds `json!` to strip the field off the
wire, while the MCP path serializes it anyway. The service layer extraction
happened, but the 204 signal never got a proper home — it's a bool bolted
onto the domain result.

**Fix.** Let the type say it:

```rust
/// `None` = nothing has ever been pushed (the HTTP adapter's 204 case).
/// A filter matching nothing is still `Some` with empty vecs.
pub fn assemble_rooms(...) -> Result<Option<RoomsResult>, ServiceError>
```

- Drop `store_empty` from `RoomsResult`. Early-return `Ok(None)` where
  `store_empty` was set; return `Ok(Some(result))` otherwise.
- `handlers::get_rooms`: `None` → `StatusCode::NO_CONTENT`. With
  `store_empty` gone, the hand-built `json!` is no longer needed —
  `RoomsResult` already derives `Serialize`, so return `Json(result)`
  directly. (Field order changes in the JSON; the viewer keys by name, so
  this is safe — but grep `index.html` for any positional assumptions
  before deleting the `json!`.)
- `mcp.rs::get_rooms`: MCP has no 204. Map `None` to an explicit empty
  result so the tool's output shape stays self-describing, e.g. serialize
  `{ "store_empty": true }`… no — keep it simpler and *more* honest than
  today: return a `CallToolResult` with a short text block like
  `"no snapshots have been pushed to this server yet"` for `None`, and the
  plain serialized `RoomsResult` for `Some`. Update the tool's doc comment
  (it currently documents the `store_empty` field).

**Tests to update:** the two handler tests
(`test_get_rooms_returns_204_when_store_empty`,
`test_get_rooms_empty_filter_result_is_200_not_204`) keep their assertions,
only the plumbing changes. Service tests swap `result.store_empty`
assertions for `is_none()` / `is_some()`.

---

## Fix 2 — `ProjectSettings.drofus` is an `Option` that can never be `None`

**Files:** `state.rs`, `settings.rs`, `bootstrap.rs`, `service/validation.rs`.

**Problem.** `Settings.sources.drofus` is required in every project TOML and
`bootstrap` always loads it, so every registered bundle has `Some(drofus)` —
yet `compute_project_validation` carefully handles `None` ("a project not
using dRofus is normal"). The Option is a vestige of the per-project
retrofit: a state the docs describe as normal is actually unreachable.

**Fix — pick one direction and commit.** Recommended: **make the state
real**, since "a project not using dRofus is normal" is the better product
answer and the handling code already exists:

- `settings.rs`: make dRofus optional in config —
  `pub struct Sources { #[serde(default)] pub drofus: Option<DrofusSource> }`,
  and make the whole `sources` section `#[serde(default)]` on `Settings`
  (a project with no external sources is now legal). Derive/impl `Default`
  for `Sources`.
- `bootstrap.rs::load_project_settings_dir`: load dRofus only when
  configured; skip `validate_drofus_fields` when it isn't — but **fail
  loudly** if `drofus_fields` is non-empty while no dRofus source exists
  (declarations for a source that isn't there are a config mistake, same
  discipline as `validate_drofus_fields`' unknown-label check).
- `load_settings`: the `match &mut settings.sources.drofus` path-resolution
  becomes `if let Some(DrofusSource::File { path }) = ...`.
- `state.rs` / `validation.rs`: unchanged — the `Option` and its `None`
  handling finally earn their keep.

(The other direction — making the field non-optional everywhere — is a
smaller diff but forecloses the "project without dRofus" case the validation
endpoint already advertises via `drofus_configured: false`. Don't take it.)

**Tests to add:**
- A settings TOML with no `[sources]` at all loads successfully; its
  project's `/rooms` works and `/projects/{id}/validation` returns
  `drofus_configured: false`.
- A settings TOML with `drofus_fields` entries but no dRofus source fails
  startup with a clear message.

---

## Fix 3 — `project.toml` manifest is authoritative in docs, write-only in code

**File:** `storage.rs`.

**Problem.** The module doc calls the manifest "authoritative: the server
reads it to know what exists", but no read path consumes it — `all_latest`
walks the directory tree; `read_manifest` is only called inside `put` to
upsert itself. Design intent and implementation disagree.

**Fix — align the code with the stated design** (the manifest is genuinely
useful: it's the only place a project/model *display name* survives without
opening a snapshot, and it's the natural hook for future pruning/metadata):

- Add to the trait: `fn list_models(&self) -> Result<Vec<ModelKey>>` — the
  index question the manifest was built to answer.
- `FsStore::list_models`: read each project dir's `project.toml` and emit
  one `ModelKey` per manifest `models` entry. A model dir *not* in the
  manifest is a manifest bug — log a warning and include it anyway
  (filesystem truth wins; the warning makes the drift visible instead of
  silent).
- Rewrite `FsStore::all_latest` as: `list_models()`, then `get_latest` per
  key — the manifest becomes the index, snapshots stay the record, exactly
  as the module doc claims. `get_latest` finally gains a production caller
  (partially retiring one item-7 note for free).
- `MemStore::list_models`: keys of the map.

If instead you decide the manifest isn't worth keeping — delete
`ProjectManifest`, `read_manifest`, `write_manifest`, and the doc paragraph,
and shrink `put` to dir + snapshot file. Valid, but you lose the readable
display-name index and the pruning hook; only do this if the team confirms
nothing external reads `project.toml`.

**Tests to add:**
- A push creates a manifest whose `models` entry round-trips through
  `all_latest` (i.e. the returned key came *via* the manifest — easiest to
  prove by hand-editing a name in the manifest and asserting the warning
  path on a missing entry).
- A model dir present on disk but absent from the manifest still appears in
  `all_latest` (filesystem-wins rule).

---

## Fix 6 — `FieldType::Date`/`format` is validated config with no consumer

**File:** `settings.rs`, `service/validation.rs`.

**Problem.** `type = "date"` + `format` is parsed and strictly validated at
startup, but nothing consumes it — QA explicitly falls back to string
comparison for date-labeled fields. Config surface shipped ahead of its
feature: an operator can be forced to fix a `format` string that then does
nothing.

**Fix — make the declaration earn its validation** by implementing the one
consumer the comments keep promising: typed date comparison in QA.

- Add `chrono` to `Cargo.toml` (it's the format dialect the settings doc
  already names).
- Startup: extend `validate_drofus_fields` to *dry-run the format* —
  `chrono::format::StrftimeItems` parse (or format a fixed date with it) so
  a typo like `%Q` fails at startup, same loud-config discipline. Today an
  invalid pattern would pass validation and only surface later.
- `compute_validation`, `Present(room_value)` arm: before the numeric/string
  ladder, if the field's declaration is `FieldType::Date` (and `qa` isn't
  `Exact`), parse both sides with the declared `format`
  (`chrono::DateTime::parse_from_str`, falling back to
  `NaiveDateTime`/`NaiveDate` for patterns without a timezone). Both parse →
  compare the parsed instants; either side fails to parse → fall back to
  the existing string path (same "hint, not truth" stance as
  `CustomValue.storage_type`). Keep the change inside a small
  `date_match(a, b, format) -> Option<bool>` helper next to
  `numeric_match`, mirroring its `None = fall back` contract.
- One open question to resolve before writing the Revit-side comparison:
  what format does the *room* side of a date arrive in? The settings only
  declare the dRofus column's format. If Revit's side has its own shape,
  the declaration needs a second optional pattern (e.g. `revit_format`) —
  check a real snapshot before committing to single-format parsing.
- Update the `Settings.drofus_fields` doc comment: the "a future feature …
  needs to actually parse the value" paragraph becomes present-tense.

Fallback option if typed comparison is explicitly not wanted yet: strip
`FieldType`/`format` from `DrofusFieldConfig` entirely (keep only
`label` + `qa`) and reintroduce them with their consumer. Do not keep the
middle state — validated-but-unused config is the afterthought being fixed.

**Tests to add:**
- `date_match` with the shipped pattern `"%-m/%-d/%Y %-I:%M:%S %p %z"`:
  equal instants in different renderings → `Some(true)`; different instants
  → `Some(false)`; unparseable side → `None`.
- `compute_validation`: a date field where the two sides differ textually
  but denote the same instant produces no mismatch; `qa = "exact"` on the
  same field forces the textual mismatch to be reported.
- `validate_drofus_fields` rejects a malformed strftime pattern at startup.

---

## Suggested order & interactions

1. **Fix 4** then **Fix 5** — both live in `assemble_rooms`; do them
   together in one pass over the function, tests for both before moving on.
2. **Fix 1** — touches the same file's return type; doing it after 4/5
   avoids rebasing the dedup changes over a signature change.
3. **Fix 2** — isolated to settings/bootstrap; independent of the above.
4. **Fix 3** — storage only; note it organically resolves the
   "`get_latest` has no caller" item-7 observation.
5. **Fix 6** — largest; needs the `revit_format` question answered first.

After each fix: `cargo test` (existing suites in rooms.rs, handlers.rs,
validation.rs, settings.rs, storage.rs must stay green except where a test
encodes the old, now-wrong semantics — Fix 5 changes one documented
behavior; update the doc comments in the same commit as the code).

---

# Part 2 — Python push-side fixes (post_rooms.py / room_mate.py)

Same review lens applied to the client scripts that feed the server. Four
fixes (P1–P4) plus minors. Constraint to keep in mind throughout: this code
runs under IronPython/pyRevit inside Revit — CLR types, no CPython-only
libraries, and the UI thread is precious.

---

## Fix P1 — `post_payload_stream` doesn't actually stream

**File:** `post_rooms.py`.

**Problem.** The function's docstring claims "peak memory here is one room,
not the whole export," but the pipeline buffers everything twice before any
per-room work starts, and once more after:

1. `duhast_objects_to_plain(json_formatted_room)` — `json.dumps` of the
   **entire** export into one string, then `json.loads` back into a full
   dict tree. The whole export is materialized as both a string and a
   parsed structure before the "streaming" loop begins.
2. The gzip output accumulates in a `MemoryStream`, and `out.ToArray()`
   copies the complete compressed body into a second buffer for
   `ByteArrayContent`. Nothing streams to the network.

The only genuine saving is that no single uncompressed JSON string of the
*translated* payload is built — but step 1 builds an equivalent-sized string
of the *untranslated* payload anyway. Streaming was bolted onto a pipeline
whose first step is a whole-export buffer.

**Fix — two stages, take them in order:**

*Stage 1 (small, real win): kill the dumps/loads round-trip.*
`duhast_objects_to_plain` exists only because duHast data objects aren't
plain dicts. Replace it with a per-object flatten at the point of use:

```python
def duhast_object_to_plain(obj):
    """Flatten ONE duHast object to plain dicts, not the whole export."""
    return json.loads(json.dumps(obj, default=serialize_utf, ensure_ascii=False))
```

Then in `post_payload_stream`, flatten the level export and the room
export's envelope/metadata parts once (they're small), and flatten each
room **inside the loop**:

```python
for room in rooms_raw:  # still duHast objects
    out_room = translate_room(duhast_object_to_plain(room))
    if out_room is not None:
        write_ndjson_line(gz, out_room)
```

Peak memory drops to one room's dict plus the compressed buffer — the
docstring's claim becomes true on the translation side. (Check what
`build_json_for_file` returns: if the room list is already reachable
without serializing the container, iterate it directly; only the envelope
extraction in `build_envelope` needs the flattened top level.)

*Stage 2 (optional, only if compressed-body size ever bites): stream the
HTTP body too.* Replace `MemoryStream` + `ByteArrayContent` with a
`StreamContent` reading from the gzip stream via
`System.IO.Pipelines`-free plumbing: simplest CLR-compatible shape is an
anonymous pipe (`AnonymousPipeServerStream`/`ClientStream`) or a custom
`HttpContent` subclass whose `SerializeToStreamAsync` writes the NDJSON
lines through a `GZipStream` wrapping the network stream directly. This
removes the compressed buffer and the `ToArray()` copy. Note gzip typically
shrinks these payloads ~10–20×, so the compressed buffer is usually tens of
MB at worst — defer Stage 2 until that's actually a problem, and say so in
the docstring instead of overclaiming.

**Docstring:** whichever stage you stop at, rewrite the module and function
docstrings to state the *actual* memory profile. The current text is the
afterthought being fixed.

**Verification:** push the large FFE export before/after and compare
IronPython process peak working set; assert byte-identical server-side
snapshots (same `taken_at` re-push to a scratch storage root, diff the two
JSON files).

---

## Fix P2 — Push failures are swallowed; `Result` reports success anyway

**Files:** `post_rooms.py`, `room_mate.py`.

**Problem.** Both post functions catch every exception, `print`, and return
`None`. A 422 (schema mismatch, unregistered project id), a 500, or a
server-not-running all leave `room_mate.py`'s `Result` tracker untouched —
the user exports five models, two silently fail, and the run ends with
"Finished" and a success `Result`.

**Fix.**

- `post_payload` / `post_payload_stream` return `(ok, status, text)`:

```python
    try:
        response = client.PostAsync(url, content).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        return (200 <= status < 300, status, text)
    except Exception as e:
        return (False, None, "could not reach {}: {}".format(url, unwrap_aggregate(e)))
    finally:
        client.Dispose()
```

  (`unwrap_aggregate` — see Fix P4 — so the message isn't a useless
  "One or more errors occurred".)

- `room_mate.py` consumes it per model and records failure without
  aborting the remaining models:

```python
    ok, status, text = post_payload_stream(json_formatted_room, json_formatted_level)
    if ok:
        return_value.append_message("{}: server accepted ({})".format(selected_doc.Title, text))
    else:
        return_value.update_sep(False, "{}: push failed ({}): {}".format(selected_doc.Title, status, text))
```

  `update_sep(False, ...)` flips the overall status while keeping the loop
  going — one bad model shouldn't discard the others' successful pushes,
  but the run must end red.

- Keep the `print` for the interactive pyRevit console; the `Result` is
  for the caller.

**Tests:** hard to unit-test under IronPython; minimum bar is a manual
matrix — server down, wrong `schema_version`, unregistered project id, and
a good push — confirming the final `Result` status and per-model messages
for each.

---

## Fix P3 — Identity defaults paper over the envelope retrofit

**Files:** `post_rooms.py` (`build_envelope`), `room_mate.py` (envelope
construction), plus one server-side note.

**Problem.** `build_envelope` fills gaps with sentinels:
`project/model → {"id": "unknown", ...}`, `snapshot → {"taken_at": ""}`.
Consequences downstream:

- Every default-identity push merges into one shared fake "unknown"
  project — silently, across unrelated models.
- An empty `taken_at` becomes a snapshot file literally named `.json`
  (FsStore builds the filename from it), and lexical latest-ordering is
  garbage from then on.
- These defaults exist because the identity envelope was retrofitted onto
  exports that might predate it — but a payload without identity is
  exactly the "loud error over silent no-op" case the server enforces
  everywhere else.

**Fix (client):** validate, don't default. In `build_envelope`, require
`project.id`, `model.id`, and a non-empty `snapshot.taken_at`; raise
`ValueError` naming the missing field. Remove the `.get(..., {"id":
"unknown"...})` fallbacks. `room_mate.py` always supplies all three, so the
live path is unaffected; only genuinely broken inputs now fail — loudly,
and (after Fix P2) visibly in the `Result`.

**Fix (server-side note — add to Part 1's backlog):** `payload.project.id`
and `payload.model.id` flow **unsanitized into filesystem paths**
(`FsStore::model_dir` does `root.join(project_id).join(model_id)`). With
`room_mate.py` sending `selected_doc.Title` as the model id, a title
containing `/`, `\`, or `..` is a path traversal out of the storage root.
Ingest must reject (422) any project/model id containing path separators,
`..`, or characters illegal in filenames — same startup-loud spirit,
applied at the trust boundary. One validation fn shared by both ingest
handlers, tested with `"../escape"` and `"a/b"`.

**Also (room_mate.py, same area):** `project.id = Number or Title` and
`model.id = Title` remain the acknowledged GUID stopgap. Two additional
consequences worth a comment where the envelope is built: two different
files sharing a Title collide into one model record, and renaming a file
forks its history. If duHast ever exposes
`Document.CreationGUID`/worksharing GUIDs, switch; until then the comment
should name the collision risk, not just the rename risk.

---

## Fix P4 — Second-resolution timestamps overwrite history

**Files:** `room_mate.py` (`taken_at`), one server-side note.

**Problem.** `taken_at` is formatted `%Y-%m-%dT%H:%M:%SZ`. Two pushes of
the same model within one second produce the same FsStore filename — the
second push silently overwrites the first, defeating storage's "history
kept, never overwritten" contract. Easy to hit when re-running a script
back-to-back after a small fix.

**Fix (client):** sub-second precision:

```python
"taken_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
```

Microseconds keep the string lexically sortable (fixed width), so
FsStore's lexical-max = newest rule is untouched. (`utcnow()` is fine
under IronPython; don't chase the CPython deprecation here.)

**Fix (server-side note — add to Part 1's backlog):** `FsStore::put`
currently `fs::write`s over an existing snapshot file without noticing.
Even with client-side precision, a genuinely identical `taken_at` (e.g. a
re-sent payload) should not silently destroy history: either make it a
no-op-with-log ("snapshot already exists, skipping") or suffix the
filename. Pick one and document it on `SnapshotStore::put`'s upsert
contract.

---

## Python minors (fix opportunistically, no dedicated pass)

- **`.Result` blocks the pyRevit UI thread** and wraps failures in
  `AggregateException`. Full async isn't worth it in IronPython; do add an
  `unwrap_aggregate(e)` helper (walk `e.InnerException` /
  `e.InnerExceptions[0]`) so error messages are the real cause, and set
  `client.Timeout` explicitly (e.g. 5 min for large pushes — the 100 s
  default may genuinely be too short for a big model on Stage-2 streaming).
- **Cancel granularity:** `pb.cancelled` is only checked after a full
  export+post; a cancel during a large model does nothing. Check it once
  more between `get_all_room_data` and the post.
- **`MemoryStream` never disposed** in `post_payload_stream` — wrap in
  try/finally with `out.Dispose()` (goes away entirely under P1 Stage 2).
- **`ensure_ascii` inconsistency:** `duhast_objects_to_plain` uses
  `ensure_ascii=False`, `write_ndjson_line` and `post_payload` use the
  default (`True`). Both emit valid JSON; standardize on `True` for the
  wire (pure-ASCII bytes are the safer choice across the CLR seam) and
  say so in `write_ndjson_line`'s docstring.
- **Shared envelope dict:** `dic_room_data.update(envelope)` and
  `dic_level_data.update(envelope)` share nested dict instances; if
  `build_json_for_file` ever mutates its input, the two exports
  cross-contaminate. Cheap insurance: `copy.deepcopy(envelope)` for the
  second use, or build it twice.

---

## Combined order (Rust + Python)

Python fixes are independent of the Rust ones except where noted:

- **P2** first — it's small and makes every subsequent manual verification
  trustworthy (failures become visible).
- **P3 client + P4 client** together — both touch the envelope.
- **P3/P4 server notes** fold into the Rust work: ingest id validation
  pairs naturally with Fix 1's handler touch-up; the duplicate-`taken_at`
  policy belongs with Fix 3's storage pass.
- **P1 Stage 1** any time; **Stage 2** only when measured need appears.
