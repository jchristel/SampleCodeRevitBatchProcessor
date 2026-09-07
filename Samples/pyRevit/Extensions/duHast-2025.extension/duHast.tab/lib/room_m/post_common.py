"""
The parts of the wire contract that belong to no single entity.

Rooms and doors -- and windows and FF&E after them -- are separate contracts
that version independently, but they reach the same server over the same
transport, carry the same identity, and are read off the same duHast export
shapes. That common half lives here so each entity module owns only what is
genuinely its own: its endpoints, its schema version, its translation, and
its push.

Extracted from `post_rooms.py`, which is where all of this began and where a
second entity had to import it from. That worked, but it made the doors push
depend on the rooms module for reasons that had nothing to do with rooms, and
every further entity would have deepened that. Nothing here knows what a room
is.

What is shared, and why it must be shared rather than copied:

- **Transport** (`make_client`, `_post_content`, `unwrap_aggregate`). Two
  clients with different timeouts, or two different readings of what counts
  as a failed push, would be a difference nobody chose.
- **Identity** (`build_identity_envelope`, `SOURCE`). Every contract carries
  the same project/model/snapshot/phase block with the same validations. Two
  copies could drift on what counts as a valid identity, which is the exact
  failure those validations exist to catch.
- **duHast flattening** (`duhast_object_to_plain`, `duhast_objects_to_plain`)
  and the **property/geometry readers** (`find_property`, `properties_to_map`,
  `loop_to_points`). These read the shape duHast exports, not the shape any
  one entity has.
- **The NDJSON writer** (`write_ndjson_line`) and **the empty-push refusal**
  (`empty_push_refusal`), for the same reason: one wire format, one definition
  of "this push would have sent nothing".
- **The project registry** (`fetch_projects`) and the **placement transform**
  (`coordinate_system_to_affine`), which are facts about the run and the
  model rather than about anything being pushed.

Nothing here is Revit-facing: `coordinate_system_to_affine` takes numbers the
caller already read, and this module imports no Revit assembly. The extraction
side lives in `room_m.utils`.
"""

import json
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System import TimeSpan
from System.Net.Http import HttpClient
from System.Text import Encoding



# The settings endpoint, NOT /projects: a push target must be a *registered*
# project, and /projects lists only projects that already have stored
# snapshots -- which a project can only get by being pushed to first. See
# fetch_projects.
SERVER_URL_PROJECTS = "http://127.0.0.1:5151/api/settings/projects"


# Which producer this script feeds the server from. The server resolves
# canonical property names (Area, Number, ...) to this source's raw property
# names via its own settings -- this script only needs to say who it is.
SOURCE = "revit"


# Python 2 and 3 spell their string and number types differently, and this file
# runs on IronPython 2.7 as well as CPython 3.
try:
    _STRINGS = (str, unicode)  # noqa: F821 - IronPython 2.7
    _NUMBERS = (int, long, float)  # noqa: F821 - IronPython 2.7
except NameError:
    _STRINGS = (str,)
    _NUMBERS = (int, float)

# What lands in a field duHast could not convert. A string where a value was
# expected, so it survives the wire and shows up in QA as a property with a
# strange value -- visible -- rather than as an element that never arrived.
UNCONVERTIBLE = "<unconvertible>"


def duhast_to_plain(value):
    """duHast data objects to plain JSON types, marking -- rather than dying on
    -- anything that will not convert.

    **duHast's own serializer cannot be used here, and the reason is narrow.**
    `serialize_utf` delegates to `Base.to_json`, which calls `json.dumps` with
    **no `default=` handler** over a `class_to_dict()` whose inner `serialize()`
    ends in `else: return obj`. So any CLR object duHast did not anticipate
    passes through untouched and then raises -- and the raise is not scoped to
    the field or even the element. It aborts the whole document's push.

    An UNHOSTED opening triggers it. Revit gives such an element an invalid
    `LevelId`; `get_level_data` calls `Element.Name.GetValue()` on nothing and
    gets a property descriptor back; `encode_utf8` returns a non-string argument
    UNCHANGED, so the descriptor lands in `level.name` with nothing complaining
    until serialization. Measured: one skylight in a house, two terrace sills in
    a facade file. Three elements, each of which cost its model's entire push.

    **Catching around `serialize_utf` would not have been enough**, which is why
    this walks. The failure fires inside `to_json` on a NESTED leaf, so a
    try/except one level up marks the whole element unconvertible -- dropping a
    real opening, with its id and properties and footprint, over one field. This
    recurses instead and marks only the leaf. `class_to_dict()` is still used
    for each duHast object: it is correct, it handles the .NET `Int64`
    conversion, and its only gap is the leaves it did not expect -- which the
    recursion below then catches.

    **Silent marking is acceptable here only because the server reports the
    consequence.** Such an element arrives with `level_id` of `-1`, nothing has
    an elevation for it, and QA answers `UnknownLevel` -- naming the element and
    the reason. If that report did not exist this would need its own channel.

    In `post_common` rather than in one entity's push, because the mechanism is
    duHast's and belongs to no entity: a hostless DOOR does exactly the same
    thing, and this should not have to be found twice."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, _NUMBERS) or isinstance(value, _STRINGS):
        return value

    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            out[key if isinstance(key, _STRINGS) else str(key)] = duhast_to_plain(item)
        return out

    if isinstance(value, (list, tuple)):
        return [duhast_to_plain(item) for item in value]

    to_dict = getattr(value, "class_to_dict", None)
    if callable(to_dict):
        try:
            return duhast_to_plain(to_dict())
        except Exception:
            return UNCONVERTIBLE

    # `__dict__` only when it holds something. An EMPTY one means the fallback
    # learned nothing, and emitting `{}` would quietly turn an unconvertible
    # field into an empty object -- which reads downstream as "present but
    # blank" rather than "could not be read". A CLR property descriptor, the
    # thing this was written for, is exactly that shape.
    attributes = getattr(value, "__dict__", None)
    if isinstance(attributes, dict) and attributes:
        return duhast_to_plain(attributes)

    return UNCONVERTIBLE


def duhast_objects_to_plain(json_data):
    """Flatten a whole duHast export to plain dicts so the translate step can
    walk it. Materializes the entire input -- fine for the buffered
    `post_payload` path; the streaming path uses `duhast_object_to_plain` per
    element instead so it never holds more than one at a time."""
    return duhast_to_plain(json_data)


def duhast_object_to_plain(obj):
    """Flatten ONE duHast object (or small structure), not the whole export, so
    peak memory stays at one element."""
    return duhast_to_plain(obj)


def unwrap_aggregate(e):
    """The real cause behind a CLR failure: `.Result` on a Task wraps any
    exception in an AggregateException whose message is a useless "One or
    more errors occurred" -- walk down to the innermost exception instead."""
    inner = getattr(e, "InnerException", None)
    while inner is not None:
        e = inner
        inner = getattr(e, "InnerException", None)
    return e


def make_client():
    """An HttpClient with an explicit timeout: the 100 s CLR default is too
    short for a large model push over a slow link; caller must Dispose()."""
    client = HttpClient()
    client.Timeout = TimeSpan.FromMinutes(5)
    return client


def find_property(instance_properties, prop_name):
    for prop in instance_properties.get("properties", []):
        if prop.get("name") == prop_name:
            return prop.get("value")
    return None


def loop_to_points(loop):
    return [{"x": float(pt[0]), "y": float(pt[1])} for pt in loop]


def coordinate_system_to_affine(rotation, translation):
    """Reduce duHast's shared-coordinate transform (as returned by
    ``get_coordinate_system_translation_and_rotation``) to the 2D affine
    ``[a, b, c, d, e, f]`` the server's ``ModelToShared`` carries, where
    ``shared_x = a*x + c*y + e`` and ``shared_y = b*x + d*y + f``.

    ``rotation`` is 3 basis-vector rows ``[BasisX, BasisY, BasisZ]`` (BasisX is
    the image of the model +X axis, BasisY of +Y); ``translation`` is the origin.
    So ``a,b = BasisX.x, BasisX.y`` and ``c,d = BasisY.x, BasisY.y``. Only the x
    and y of the first two basis rows and of the origin are read, so this is
    agnostic to 2D (3x2) vs 3D (3x3) serialization -- the z basis and any z
    translation are for elevation, not the plan placement.

    Carries NO unit conversion: this is a rigid-body placement (rotation +
    translation in feet), never a scale (HANDOVER-georeferencing.md)."""
    return [
        float(rotation[0][0]), float(rotation[0][1]),
        float(rotation[1][0]), float(rotation[1][1]),
        float(translation[0]), float(translation[1]),
    ]


def properties_to_map(instance_properties):
    """Reshape duHast's [{name, value, storage_type}, ...] list into a flat
    {name: {value, storage_type}} map. One generic transform, no per-field
    logic -- which names count as "builtin" is a server-side settings concern
    (STRATEGY.md "source dimension"), not something decided here."""
    out = {}
    for prop in instance_properties.get("properties", []):
        name = prop.get("name")
        if not name:
            continue
        value = prop.get("value")
        out[name] = {
            "value": "" if value is None else str(value),
            "storage_type": prop.get("storage_type"),
        }
    return out


LEVEL_LIST_KEY = "building level"


def translate_levels(levels_source):
    """One model's duHast level export as the contract's `levels`, sorted by
    elevation.

    **Per model, and that is load-bearing.** A level id is a per-document
    `ElementId`, so two models' level lists cannot be merged -- "Level 1" in the
    architectural model and in the structural model are different ids naming the
    same floor, and the server dedups them across models on read. Stamping the
    list onto its own model's envelope block is what keeps that possible.

    Built before the identity check, as it always has been: a malformed level is
    a broken export too, and reordering the two would only change which complaint
    a reader sees first.

    **Shared rather than duplicated, because both entities stamp levels now.**
    Rooms always have; doors do too, so that a model pushing doors and NO rooms
    still declares the level set its `level_id`s point into -- without which the
    server cannot put those doors on an elevation axis and refuses to probe them
    at all. Two copies that could drift on what a level looks like would be
    worse than one import, the same terms `empty_push_refusal` is shared under.
    """
    levels = []
    for lvl in levels_source.get(LEVEL_LIST_KEY, []):
        levels.append({
            "id": str(lvl.get("id", "unknown")),
            "name": lvl.get("name", "Unknown Level"),
            "elevation": float(lvl.get("elevation", 0.0) or 0.0),
        })
    levels.sort(key=lambda l: l["elevation"])
    return levels


def build_identity_envelope(run_envelope, model_blocks, entity, schema_version):
    """The envelope fields EVERY entity's contract carries: schema_version,
    project, snapshot, phase, and the run's `models` list (each block stamped
    with its `source`).

    **One implementation, not one per entity.** The rooms and doors contracts
    differ in what each model block carries *around* identity -- levels and a
    boundary regime for rooms, nothing for doors -- but the identity block itself
    is the same validations and the same keys in both. Two copies of it could
    drift on what counts as a valid identity, which is precisely the failure
    these validations exist to catch, and each new entity (windows, FFE) would
    add another copy to keep in step.

    `entity` names the caller in the phase message; `schema_version` is the
    caller's because the contracts version independently -- a change to the room
    schema has nothing to say about doors.

    Identity is validated, never defaulted: a push missing project id, model id,
    or snapshot timestamp is broken input, and a loud ValueError here beats what
    the old `"unknown"`/`""` fallbacks did downstream (every default-identity
    push silently merged into one shared fake project, and an empty taken_at
    became a snapshot file literally named `.json`).
    `room_m.utils.post_envelope` always supplies all three, so only genuinely
    broken inputs fail.

    **A run with no models is refused here too.** The server refuses one as well,
    and this side says the same thing earlier -- a push exists because a run
    exported at least one document, so an empty list means the run driver lost
    every model without noticing.

    The server can now mint a snapshot id itself when a payload omits
    `snapshot.taken_at` (it answers with the resolved id) -- this producer
    deliberately keeps supplying its own: its timestamp says when the model
    was READ, which the server's receipt time can't know."""
    project = run_envelope.get("project")
    if not project or not project.get("id"):
        raise ValueError("push is missing its identity envelope: project.id")
    snapshot = run_envelope.get("snapshot")
    if not snapshot or not snapshot.get("taken_at"):
        raise ValueError("push is missing its identity envelope: snapshot.taken_at")

    # REQUIRED, unlike the per-model optional fields. Those are advisory model
    # facts the server can fall back on; this one says which phase the entities
    # were FILTERED to, and a push that omits it is refused -- rightly, because
    # unfiltered content is a mix of every phase and there is no safe default to
    # assume. Validated here rather than left to the server so the failure names
    # the producer's own bug instead of arriving as a 422.
    #
    # One phase for the whole run, so it is validated once rather than per model.
    phase = run_envelope.get("phase")
    if not phase or not str(phase).strip():
        raise ValueError(
            "push is missing its phase: {} must be filtered to one Revit "
            "phase before pushing (see room_m.utils.ui.choose_phase)".format(entity)
        )

    if not model_blocks:
        raise ValueError(
            "push declares no models: a {} push exists because a run exported at "
            "least one document".format(entity)
        )

    models = []
    for block in model_blocks:
        if not block or not block.get("id"):
            raise ValueError("push is missing its identity envelope: model.id")
        block = dict(block)
        block["source"] = SOURCE
        models.append(block)

    return {
        "schema_version": schema_version,
        "project": project,
        "snapshot": snapshot,
        "phase": str(phase).strip(),
        "models": models,
    }


def write_ndjson_line(gz, obj):
    """Serialize one object to a compact JSON line and write it (UTF-8) into
    the gzip stream, followed by '\n'. One object = one NDJSON line.

    `ensure_ascii` is False, and the CLR seam is the reason for it rather than
    an exception to it. Under IronPython 2.7 a .NET string arrives as a byte
    oriented `str`, so ensure_ascii=True has to DECODE it in order to escape a
    non-ASCII character -- using the system code page, which has no mapping for
    a lone 0xAE. One registered sign in a type property value (a plumbing
    fixture's "Smartflush(R) Suite") therefore aborted an entire FF&E push,
    and did so at serialization, far from the parameter that carried it.
    Encoding.UTF8.GetBytes below performs the same conversion correctly:
    measured on the wire as C2 AE, not a lone AE.

    Repairing duHast's encode_utf8 instead was tried and is worse. Despite its
    comment ("do encode and decode to avoid byte string") it returns the byte
    string unchanged here, and every variant that stopped the crash silently
    replaced the character with U+FFFD -- the harder failure to notice, and the
    one this codebase keeps paying for."""
    line = json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n"
    data = Encoding.UTF8.GetBytes(line)
    gz.Write(data, 0, data.Length)


def fetch_projects(url=SERVER_URL_PROJECTS):
    """GET the server's registered project list and report it as
    `(ok, status, text)`, the same tuple shape the post functions use so the
    caller branches uniformly. On success `text` is a list of `{"id", "name"}`
    dicts; on any failure it's an error string.

    A push must target a project the server has a registered settings bundle
    for (the server 422s otherwise -- see roommate's `validate_ingest`), so the
    authoritative set of ids a push can use is the set of settings files:
    `/api/settings/projects`. This deliberately does NOT use `/projects`, which
    answers a different question -- "which projects have rooms to look at" (it
    derives its list from stored snapshots, for the viewer's picker). Asking it
    here is a chicken-and-egg: a newly onboarded project has no snapshots, so
    it would never be offered, so it could never receive the first push that
    would make it appear.

    Settings files are the wire shape here, so this normalises them for the
    caller: `name` is the file's authored display name, falling back to the id
    when it sets none (absence is a normal state server-side, so the fallback
    is required, not defensive). That name is what the caller sends back as
    `project.name`, which the server writes into its storage manifest and the
    viewer shows -- so the settings file, not this script, is what names a
    project. Entries carrying a parse `error` have no readable `project_id` and
    so cannot be pushed to under any id -- they're dropped rather than offered
    as un-selectable noise.

    An empty list (`200 []`) is a *success* the caller interprets as "no
    project onboarded yet" (a hard stop for the producer), not a failure; a 2xx
    whose body isn't a JSON list is a genuine failure (unexpected server
    shape)."""
    client = make_client()
    try:
        response = client.GetAsync(url).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        if not (200 <= status < 300):
            return (False, status, "server returned {}: {}".format(status, text))
        try:
            files = json.loads(text)
        except ValueError as e:
            return (False, status, "could not parse {} response: {}".format(url, e))
        if not isinstance(files, list):
            return (False, status, "unexpected {} shape: {}".format(url, text))
        projects = [
            {"id": f["project_id"], "name": f.get("name") or f["project_id"]}
            for f in files
            if f.get("project_id")
        ]
        return (True, status, projects)
    except Exception as e:
        return (False, None, "could not reach {}: {}".format(url, unwrap_aggregate(e)))
    finally:
        client.Dispose()


def empty_push_refusal(entity, envelope, raw_count, dropped):
    """The `(ok, status, text)` a push reports when it would have sent nothing.

    Refused **client-side, before the POST**, even though the server refuses an
    empty rooms push itself (`handlers.rs::reject_empty_rooms`). The server's
    422 is the backstop and stays the authority; this exists because the
    producer can say something the server cannot. The server sees one number --
    zero -- and can only guess that a phase filter is behind it. This side still
    has the export in hand, so it can report that the run held 26 rooms and
    name where each one went, which is the difference between "0 rooms" sending
    someone to read server logs and a message that points at the phase picker.

    Shared with `post_doors` rather than reimplemented there, on the same terms
    as the transport helpers: two guards that could drift on what "empty" means
    would be worse than none.

    **Scoped to the RUN, not to one model** -- which is what the multi-model
    push fixed rather than a detail of it. The question a producer can answer is
    "someone asked for a push and there is nothing to send"; asked per model it
    turned a rooms-only document in a multiselect run into a failed doors push
    and a red run, which was routine and wrong. Asked once per run it is the
    question it was always meant to be. The server keeps its own per-model rooms
    guard, and the two are answering different things rather than disagreeing.

    `dropped` is `[(count, why), ...]` -- the fates that account for the missing
    entries, printed in order and skipping the zeroes. It is allowed to be empty
    (the buffered paths translate in one call and so cannot break the loss down;
    the streaming paths, which are what a live Revit push uses, do).

    Note the two halves say different things and mean to. An export that held
    entries and kept none is a *filter* fault and says so. An export that held
    none never had anything to filter, and blaming the phase for that would send
    a reader hunting the wrong thing."""
    project = (envelope.get("project") or {}).get("id", "unknown")
    models = ", ".join(m.get("id", "unknown") for m in envelope.get("models") or []) or "no models"
    phase = envelope.get("phase", "unknown")

    if raw_count == 0:
        detail = "the export holds no {} at all".format(entity)
        advice = ""
    else:
        why = ", ".join("{} {}".format(n, reason) for n, reason in dropped if n)
        # Both entity names are regular plurals, so the singular is the plural
        # minus its 's' -- worth the two lines because this message is read by
        # someone already unsure whether the export or the filter is at fault,
        # and "held 1 rooms" reads as a bug in the tool telling them so.
        noun = entity if raw_count != 1 else entity[:-1]
        detail = "the export held {} {}, and none survived{}".format(
            raw_count, noun, ": " + why if why else "")
        advice = " Check that the phase filter matched something before pushing."

    message = (
        "refusing to push {} for {} ({}) in phase '{}': {}. Nothing was sent.{}".format(
            entity, project, models, phase, detail, advice)
    )
    print(message)
    return (False, None, message)


def _post_content(url, content):
    """POST prepared content and report the outcome as `(ok, status, text)`:
    `ok` is HTTP 2xx, `status` is the code (None when the server was never
    reached), `text` is the response body or the underlying failure. The
    print stays for the interactive pyRevit console; the tuple is for the
    caller's `Result` tracking -- a failure must end the run red, not vanish
    into the console scrollback."""
    client = make_client()
    try:
        response = client.PostAsync(url, content).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        print("Server responded {}: {}".format(status, text))
        return (200 <= status < 300, status, text)
    except Exception as e:
        message = "could not reach {}: {}".format(url, unwrap_aggregate(e))
        print(message)
        return (False, None, message)
    finally:
        client.Dispose()
