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

from duHast.Utilities.files_json import serialize_utf


# The settings endpoint, NOT /projects: a push target must be a *registered*
# project, and /projects lists only projects that already have stored
# snapshots -- which a project can only get by being pushed to first. See
# fetch_projects.
SERVER_URL_PROJECTS = "http://127.0.0.1:5151/api/settings/projects"


# Which producer this script feeds the server from. The server resolves
# canonical property names (Area, Number, ...) to this source's raw property
# names via its own settings -- this script only needs to say who it is.
SOURCE = "revit"


def duhast_objects_to_plain(json_data):
    """Serialize duHast data objects (default=serialize_utf), then parse back
    into plain dicts so the translate step can walk them. Materializes the
    WHOLE input as a string and again as a dict tree -- fine for the buffered
    `post_payload` path; the streaming path uses `duhast_object_to_plain`
    per room instead so it never holds more than one room at a time."""
    json_string = json.dumps(json_data, indent=None, default=serialize_utf, ensure_ascii=False)
    return json.loads(json_string)


def duhast_object_to_plain(obj):
    """Flatten ONE duHast object (or small structure) to plain dicts, not the
    whole export -- the dumps/loads round-trip exists only because duHast data
    objects aren't plain dicts, so scoping it to one object keeps peak memory
    at one room instead of the entire export."""
    return json.loads(json.dumps(obj, default=serialize_utf, ensure_ascii=False))


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


def build_identity_envelope(source, entity, schema_version):
    """The envelope fields EVERY entity's contract carries: schema_version,
    project, model (+ source), snapshot, phase, and the optional
    model_to_shared.

    **One implementation, not one per entity.** The rooms and doors contracts
    differ in what they carry *around* identity -- levels and a boundary regime
    for rooms, nothing for doors -- but the identity block itself is the same
    four validations and the same five keys in both. Two copies of it could
    drift on what counts as a valid identity, which is precisely the failure
    these validations exist to catch, and each new entity (windows, FFE) would
    add another copy to keep in step.

    `entity` names the caller in the phase message; `schema_version` is the
    caller's because the contracts version independently -- a change to the room
    schema has nothing to say about doors.

    Identity is validated, never defaulted: a payload missing project id,
    model id, or snapshot timestamp is broken input, and a loud ValueError
    here beats what the old `"unknown"`/`""` fallbacks did downstream (every
    default-identity push silently merged into one shared fake project, and
    an empty taken_at became a snapshot file literally named `.json`).
    `room_m.utils.post_envelope.build_model_envelope` always supplies all three,
    so only genuinely broken inputs fail.

    The server can now mint a snapshot id itself when a payload omits
    `snapshot.taken_at` (it answers with the resolved id) -- this producer
    deliberately keeps supplying its own: its timestamp says when the model
    was READ, which the server's receipt time can't know."""
    project = source.get("project")
    if not project or not project.get("id"):
        raise ValueError("export is missing its identity envelope: project.id")
    model = source.get("model")
    if not model or not model.get("id"):
        raise ValueError("export is missing its identity envelope: model.id")
    snapshot = source.get("snapshot")
    if not snapshot or not snapshot.get("taken_at"):
        raise ValueError("export is missing its identity envelope: snapshot.taken_at")

    # REQUIRED, unlike model_to_shared below and the callers' own optional
    # fields. Those are advisory model facts the server can fall back on; this
    # one says which phase the entities were FILTERED to, and a push that omits
    # it is refused -- rightly, because unfiltered content is a mix of every
    # phase and there is no safe default to assume. Validated here rather than
    # left to the server so the failure names the producer's own bug instead of
    # arriving as a 422.
    phase = source.get("phase")
    if not phase or not str(phase).strip():
        raise ValueError(
            "export is missing its phase: {} must be filtered to one Revit "
            "phase before pushing (see room_m.utils.ui.choose_phase)".format(entity)
        )

    model = dict(model)
    model["source"] = SOURCE

    envelope = {
        "schema_version": schema_version,
        "project": project,
        "model": model,
        "snapshot": snapshot,
        "phase": str(phase).strip(),
    }

    # The model->shared placement transform (see contract.rs `ModelToShared`) is
    # a model-level fact stamped onto the envelope by
    # `room_m.utils.post_envelope.build_model_envelope`, so it is forwarded
    # verbatim rather than derived here. Optional: absent on an un-placed model,
    # which the server renders via auto-fit exactly as before. It rides the
    # envelope, so the streaming paths (which build this from the export's
    # metadata, minus the entity list) carry it with no per-entity scan.
    model_to_shared = source.get("model_to_shared")
    if model_to_shared is not None:
        envelope["model_to_shared"] = model_to_shared

    return envelope


def write_ndjson_line(gz, obj):
    """Serialize one object to a compact JSON line and write it (UTF-8) into
    the gzip stream, followed by '\n'. One object = one NDJSON line.
    `ensure_ascii` stays at its default (True) deliberately: pure-ASCII bytes
    are the safer choice across the CLR seam, and it's the wire-format
    convention for this module (the `ensure_ascii=False` in the flatten
    helpers is internal -- that output is parsed right back)."""
    line = json.dumps(obj, separators=(",", ":")) + "\n"  # compact, no spaces
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
    has the export in hand, so it can report that the model held 26 rooms and
    name where each one went, which is the difference between "0 rooms" sending
    someone to read server logs and a message that points at the phase picker.

    Shared with `post_doors` rather than reimplemented there, on the same terms
    as the transport helpers: two guards that could drift on what "empty" means
    would be worse than none.

    `dropped` is `[(count, why), ...]` -- the fates that account for the missing
    entries, printed in order and skipping the zeroes. It is allowed to be empty
    (the buffered paths translate in one call and so cannot break the loss down;
    the streaming paths, which are what a live Revit push uses, do).

    Note the two halves say different things and mean to. An export that held
    entries and kept none is a *filter* fault and says so. An export that held
    none never had anything to filter, and blaming the phase for that would send
    a reader hunting the wrong thing."""
    project = (envelope.get("project") or {}).get("id", "unknown")
    model = (envelope.get("model") or {}).get("id", "unknown")
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
        "refusing to push {} for {}/{} in phase '{}': {}. Nothing was sent.{}".format(
            entity, project, model, phase, detail, advice)
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
