"""
POC bridge for DOORS: take the duHast door export, translate to the viewer's
v1 doors contract, and POST to the Rust server.

The sibling of `post_rooms.py`, and deliberately built on it rather than
beside it -- the transport (`make_client`, `_post_content`), the duHast
flattening (`duhast_object_to_plain`) and the NDJSON writer
(`write_ndjson_line`) are imported, not re-implemented, so the two pushes
cannot drift on how they talk to the server.

What is genuinely different, and why:

- **The doors schema versions independently of rooms**, starting at 1. A
  change to the room contract has nothing to say about doors.
- **No `levels` array.** A doors push targets a model that already has rooms
  (the server refuses otherwise), and that model's rooms snapshot already
  carries the level set a door's `level_id` points into. A second copy could
  only disagree.
- **The room references do not come from the export.** See
  `translate_door` -- they are read from the Revit API by `room_mate.py`,
  which is the only side that can ask the question correctly.
- **A degenerate footprint is dropped**, see `loops_from_polygon`. This is
  the one place this module actively discards data, and it has to: the bad
  value looks like real geometry.

Returns the same `(ok, status, text)` tuple shape as the room push, so the
caller's `Result` tracking is identical for both.
"""

import json

from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue

from post_rooms import (
    duhast_object_to_plain,
    loop_to_points,
    properties_to_map,
    write_ndjson_line,
    _post_content,
    SOURCE,
)

SERVER_URL = "http://127.0.0.1:5151/doors"
SERVER_URL_STREAM = "http://127.0.0.1:5151/doors/stream"

# Doors version independently of rooms (contract/doors.rs
# `SUPPORTED_DOOR_SCHEMA`). Sending the room schema here is refused, and the
# server's message names this number.
SCHEMA_VERSION = 1

DOOR_LIST_KEY = "door"

# Revit's *uninitialized* BoundingBoxXYZ: min +1e30, max -1e30. duHast returns
# one for a door family with no 3D geometry, and its own "did we get a box" and
# "is the loop non-empty" guards both pass -- so the bad value arrives looking
# like a real footprint rather than an absent one. Two of the 26 doors in the
# sample export are exactly this (both family type `2040x620x40`).
#
# Tested by magnitude rather than equality with 1e30: the value crosses a float
# round-trip, and the point is to catch the class rather than one bit pattern.
# There is no ambiguity to worry about -- a real model is measured in feet, so
# nothing legitimate is within twenty orders of magnitude of this.
SENTINEL_MAGNITUDE = 1e20


def is_degenerate(loop):
    """Whether a loop is the empty-bounding-box sentinel rather than geometry."""
    return any(abs(coord) >= SENTINEL_MAGNITUDE for point in loop for coord in point)


def loops_from_polygon(polygons):
    """Map a duHast door polygon onto the contract's `loops` -- the ROOM
    convention verbatim: `[0]` outer, `[1..]` holes, decimal feet, model space,
    Y up. One renderer and one `model_to_shared` transform then serve both
    entities.

    Returns `[]` for a door with no usable footprint, which the contract
    carries deliberately (`Door.loops`). **Not** `None`: unlike an unplaced
    room, which `translate_room` drops because there is nothing to draw, a
    geometry-less door still has properties and both room references, so it is
    a real door QA must see. Dropping it would silently lose a door->room link
    from the report that link exists for.

    The degenerate case is why this is a function rather than a field copy: a
    door family with no 3D geometry yields Revit's uninitialized bounding box,
    and pushing it would hand every consumer a polygon 1e30 feet across."""
    if not polygons:
        return []
    poly = polygons[0]
    outer = poly.get("outer_loop") or []
    if not outer or is_degenerate(outer):
        return []
    loops = [{"points": loop_to_points(outer)}]
    for inner in poly.get("inner_loops") or []:
        if inner and not is_degenerate(inner):
            loops.append({"points": loop_to_points(inner)})
    return loops


def build_envelope(doors_source):
    """Everything the v1 doors contract needs EXCEPT `doors`: schema_version,
    project, model (+ source), snapshot, phase, and the optional
    model_to_shared. The doors counterpart of `post_rooms.build_envelope`, and
    validated the same way -- identity is checked, never defaulted, because a
    payload missing project id, model id or snapshot timestamp is broken input
    and a loud ValueError here beats a 422 that names the wrong thing.

    No `levels`: see the module docstring."""
    project = doors_source.get("project")
    if not project or not project.get("id"):
        raise ValueError("export is missing its identity envelope: project.id")
    model = doors_source.get("model")
    if not model or not model.get("id"):
        raise ValueError("export is missing its identity envelope: model.id")
    snapshot = doors_source.get("snapshot")
    if not snapshot or not snapshot.get("taken_at"):
        raise ValueError("export is missing its identity envelope: snapshot.taken_at")

    # Required, exactly as for rooms, and refused by the server if absent: a
    # push carrying no phase was never filtered by the phase range test, so it
    # is unfiltered mixed-phase content. Doors are stricter than rooms on the
    # OTHER side of this check -- a phase that DISAGREES with the model is
    # refused rather than quarantined, because activating it would re-phase the
    # model while its rooms stayed behind.
    phase = doors_source.get("phase")
    if not phase or not str(phase).strip():
        raise ValueError(
            "export is missing its phase: doors must be filtered to one Revit "
            "phase before pushing (see room_mate.choose_phase)"
        )

    model = dict(model)
    model["source"] = SOURCE

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "model": model,
        "snapshot": snapshot,
        "phase": str(phase).strip(),
    }

    model_to_shared = doors_source.get("model_to_shared")
    if model_to_shared is not None:
        envelope["model_to_shared"] = model_to_shared

    return envelope


def translate_door(door, room_references):
    """Map one duHast door object onto the v1 `Door` shape, or return None when
    it carries no id (nothing downstream could key on it).

    `room_references` is `{door id: (from_room_id, to_room_id)}`, built by
    `room_mate.door_room_references` from the Revit API. **The export's own
    `from_room`/`to_room` are deliberately ignored**, for two reasons:

    1. They are arrays holding one entry per phase, tagged with a `phase_id`
       that appears nowhere else in the file and cannot be resolved against
       anything on the wire -- the blocker STRATEGY-ENTITIES records.
    2. `FamilyInstance.FromRoom[phase]` takes the phase and answers exactly one
       room, so asking Revit is both correct and simpler than reconciling an
       array against a phase table that isn't there.

    A door absent from `room_references` gets `None` on both sides rather than
    raising: that is the honest reading (nothing was resolved) and the server's
    QA reports it as a door with no room reference, which is exactly where a
    reader should see it."""
    instance = door.get("instance_properties") or {}
    door_id = instance.get("id")
    if door_id is None:
        return None
    door_id = str(door_id)

    type_props = door.get("type_properties") or {}
    level = door.get("level") or {}
    from_room, to_room = room_references.get(door_id, (None, None))

    return {
        "id": door_id,
        "level_id": str(level.get("id", "unknown")),
        "loops": loops_from_polygon(door.get("polygon")),
        "from_room": from_room,
        "to_room": to_room,
        "type_id": str(type_props.get("id", "unknown")),
        "type_name": type_props.get("name", "Unknown Type"),
        "properties": properties_to_map(instance),
        "type_properties": properties_to_map(type_props),
    }


def in_selected_phase(out_door, allowed_door_ids):
    """Whether a translated door survives the phase filter. `None` means no
    filter was supplied and every door passes.

    The test itself lives in `room_mate.elements_in_phase`, which has the
    document's phase ordering; this module stays free of the Revit assembly,
    exactly as the room path does."""
    if allowed_door_ids is None:
        return True
    return out_door["id"] in allowed_door_ids


def translate(doors_source, room_references, allowed_door_ids=None):
    """Map the duHast door export onto the v1 contract as one whole payload.
    The buffered counterpart of `post_doors_stream`, kept for the same reasons
    `post_rooms.translate` is: small manual pushes and fixture generation."""
    envelope = build_envelope(doors_source)
    out_doors = []
    for door in doors_source.get(DOOR_LIST_KEY, []):
        out_door = translate_door(door, room_references)
        if out_door is not None and in_selected_phase(out_door, allowed_door_ids):
            out_doors.append(out_door)
    envelope["doors"] = out_doors
    return envelope


def post_doors_stream(json_formatted_doors, room_references, url=SERVER_URL_STREAM, allowed_door_ids=None):
    """Gzip-compress an NDJSON stream (line 1 = envelope, one line per door) to
    the server's streaming doors ingest, translating one door at a time as it
    is read off the raw export.

    Doors are far fewer than rooms per model, so this is not load-bearing the
    way the room stream is. It is used anyway so one transport serves both
    pushes -- a producer that streamed rooms and buffered doors would be two
    code paths to keep working for no gain. Returns `(ok, status, text)`."""
    door_meta = dict(
        (key, value) for key, value in json_formatted_doors.items() if key != DOOR_LIST_KEY
    )
    envelope = build_envelope(duhast_object_to_plain(door_meta))

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for door in json_formatted_doors.get(DOOR_LIST_KEY, []):
            out_door = translate_door(duhast_object_to_plain(door), room_references)
            if out_door is not None and in_selected_phase(out_door, allowed_door_ids):
                write_ndjson_line(gz, out_door)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)


def post_doors(json_formatted_doors, room_references, url=SERVER_URL, allowed_door_ids=None):
    """Buffered counterpart of `post_doors_stream`. Returns `(ok, status, text)`."""
    contract = translate(duhast_object_to_plain(json_formatted_doors), room_references, allowed_door_ids)
    from System.Net.Http import StringContent
    from System.Text import Encoding

    return _post_content(url, StringContent(json.dumps(contract), Encoding.UTF8, "application/json"))
