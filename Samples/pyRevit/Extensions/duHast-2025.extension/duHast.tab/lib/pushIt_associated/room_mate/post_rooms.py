"""
POC bridge: take the duHast room + level exports, translate to the viewer's
v5 contract, and POST to the Rust server.

Large FFE exports run >100 MB uncompressed (see roommate's
HANDOVER-gzip.md / HANDOVER-streaming.md / HANDOVER-streaming-sender.md), so
the actual push (`post_payload_stream`) gzip-compresses a line-delimited
(NDJSON) stream rather than building one giant JSON string -- envelope first,
then one line per room, each room flattened and translated individually as
it's read off the export. Honest memory profile: peak is one room's dict
plus the *compressed* body (a `MemoryStream` the whole gzip output
accumulates in before the POST -- gzip shrinks these payloads ~10-20x, so
that buffer is tens of MB at worst; streaming it to the network as well is
deferred until that's actually a problem). `post_payload`/`translate()` (the
older, fully-buffered path) stay around only because
`settings/settings.toml`'s `test_data` seed and the dev test fixture
(`test_snapshot.json`) are generated from `translate()`'s whole-payload
output.

Both post functions return `(ok, status, text)` rather than printing and
swallowing failures -- the caller (room_mate.py) records per-model failures
on its `Result`, so a run with a dead server or a rejected payload ends red
instead of a false "Finished".
"""

import json
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System import TimeSpan
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import HttpClient, StringContent, ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue
from System.Text import Encoding

from duHast.Utilities.files_json import serialize_utf

SERVER_URL = "http://127.0.0.1:5151/rooms"
SERVER_URL_STREAM = "http://127.0.0.1:5151/rooms/stream"
# The settings endpoint, NOT /projects: a push target must be a *registered*
# project, and /projects lists only projects that already have stored
# snapshots -- which a project can only get by being pushed to first. See
# fetch_projects.
SERVER_URL_PROJECTS = "http://127.0.0.1:5151/api/settings/projects"
SCHEMA_VERSION = 5

# Which producer this script feeds the server from. The server resolves
# canonical property names (Area, Number, ...) to this source's raw property
# names via its own settings -- this script only needs to say who it is.
SOURCE = "revit"


LEVEL_LIST_KEY = "building level"
ROOM_LIST_KEY = "room"


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


def build_envelope(rooms_source, levels_source):
    """Everything the v5 contract needs EXCEPT `rooms`: schema_version,
    project, model (+ source), snapshot, levels. Shared by the buffered
    `translate()` and the streaming path so both build identity the same
    way -- see contract.rs's `StreamEnvelope`, which is this dict's line-1
    NDJSON counterpart server-side.

    Identity is validated, never defaulted: a payload missing project id,
    model id, or snapshot timestamp is broken input, and a loud ValueError
    here beats what the old `"unknown"`/`""` fallbacks did downstream (every
    default-identity push silently merged into one shared fake project, and
    an empty taken_at became a snapshot file literally named `.json`).
    room_mate.py always supplies all three, so only genuinely broken inputs
    fail.

    The server can now mint a snapshot id itself when a payload omits
    `snapshot.taken_at` (it answers with the resolved id) -- this producer
    deliberately keeps supplying its own: its timestamp says when the model
    was READ, which the server's receipt time can't know."""
    levels = []
    for lvl in levels_source.get(LEVEL_LIST_KEY, []):
        levels.append({
            "id": str(lvl.get("id", "unknown")),
            "name": lvl.get("name", "Unknown Level"),
            "elevation": float(lvl.get("elevation", 0.0) or 0.0),
        })
    levels.sort(key=lambda l: l["elevation"])

    project = rooms_source.get("project")
    if not project or not project.get("id"):
        raise ValueError("export is missing its identity envelope: project.id")
    model = rooms_source.get("model")
    if not model or not model.get("id"):
        raise ValueError("export is missing its identity envelope: model.id")
    snapshot = rooms_source.get("snapshot")
    if not snapshot or not snapshot.get("taken_at"):
        raise ValueError("export is missing its identity envelope: snapshot.taken_at")

    model = dict(model)
    model["source"] = SOURCE

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "model": model,
        "snapshot": snapshot,
        "levels": levels,
    }

    # The model->shared placement transform (see contract.rs `ModelToShared`) is
    # a model-level fact stamped onto the envelope by room_mate.py, so it is
    # forwarded verbatim rather than derived here. Optional: absent on an
    # un-placed model, which the server renders via auto-fit exactly as before.
    # It rides the envelope, so the streaming path (which builds this from
    # `room_meta`, minus the room list) carries it with no per-room scan.
    model_to_shared = rooms_source.get("model_to_shared")
    if model_to_shared is not None:
        envelope["model_to_shared"] = model_to_shared

    return envelope


def translate_room(room):
    """Map one duHast room object onto the v5 `Room` shape, or return None for
    an unplaced room (no outer loop -- nothing to draw). Pulled out of
    `translate()` so the streaming path can translate-and-write one room at a
    time instead of building a second full list alongside `rooms_source`."""
    polygons = room.get("polygon", [])
    if not polygons:
        return None
    poly = polygons[0]

    outer = poly.get("outer_loop", [])
    if not outer:
        return None  # unplaced room, nothing to draw

    loops = [{"points": loop_to_points(outer)}]
    for inner in poly.get("inner_loops", []):
        if inner:
            loops.append({"points": loop_to_points(inner)})

    props = room.get("instance_properties", {})
    room_id = str(props.get("id", "unknown"))
    number = find_property(props, "Number")
    name = find_property(props, "Name") or "Room"
    label = "{} {}".format(name, number).strip() if number not in (None, "") else name

    lvl = room.get("level", {}) or {}
    level_id = str(lvl.get("id", "unknown"))

    return {
        "id": room_id,
        "name": label,
        "level_id": level_id,
        "loops": loops,
        "properties": properties_to_map(props),
    }


def translate(rooms_source, levels_source):
    """Map the two duHast exports onto the server's v5 contract as one whole
    payload. Used for the fully-buffered `/rooms` path and for regenerating
    `settings/test_snapshot.json` (see STRATEGY-SERVER.md) -- kept producing
    the exact same shape as before this module's streaming refactor."""
    envelope = build_envelope(rooms_source, levels_source)
    out_rooms = []
    for room in rooms_source.get(ROOM_LIST_KEY, []):
        out_room = translate_room(room)
        if out_room is not None:
            out_rooms.append(out_room)
    envelope["rooms"] = out_rooms
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


def post_payload(json_formatted_room, json_formatted_level, url=SERVER_URL):
    """Flatten both duHast exports, translate, and POST the whole v5 contract
    as one buffered JSON body. Retained for the `settings/settings.toml`
    dev-seed fixture and small/manual pushes; the live Revit export path
    (`room_mate.py`) uses `post_payload_stream` instead -- see module
    docstring. Returns `(ok, status, text)`."""
    rooms_source = duhast_objects_to_plain(json_formatted_room)
    levels_source = duhast_objects_to_plain(json_formatted_level)
    contract = translate(rooms_source, levels_source)
    body = json.dumps(contract)

    content = StringContent(body, Encoding.UTF8, "application/json")
    return _post_content(url, content)


def post_payload_stream(json_formatted_room, json_formatted_level, url=SERVER_URL_STREAM):
    """Gzip-compress an NDJSON stream (line 1 = envelope, one line per room)
    to the server's streaming ingest. Each room is flattened, translated,
    and written into the gzip stream individually as it's read off the raw
    export -- no whole-export `json.dumps` round-trip and no second full
    rooms list, so peak memory on the translation side is one room's dict.
    The compressed body does still accumulate in a `MemoryStream` before the
    POST (see the module docstring for why that's acceptable). This is the
    path `room_mate.py` calls for a live Revit export. Returns
    `(ok, status, text)`."""
    # The metadata around the room list (identity envelope, file header) is
    # small -- flatten it in one go, leaving the (potentially huge) room list
    # untouched as raw duHast objects to be flattened one at a time below.
    room_meta = dict(
        (key, value) for key, value in json_formatted_room.items() if key != ROOM_LIST_KEY
    )
    envelope = build_envelope(
        duhast_object_to_plain(room_meta),
        duhast_object_to_plain(json_formatted_level),
    )

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for room in json_formatted_room.get(ROOM_LIST_KEY, []):
            out_room = translate_room(duhast_object_to_plain(room))
            if out_room is not None:
                write_ndjson_line(gz, out_room)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)
