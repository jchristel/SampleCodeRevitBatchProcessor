"""
POC bridge for DOORS: take the duHast door export, translate to the viewer's
v1 doors contract, and POST to the Rust server.

The sibling of `post_rooms.py`, and built alongside it on a shared base rather
than on it -- the transport (`_post_content`), the duHast flattening
(`duhast_object_to_plain`), the NDJSON writer (`write_ndjson_line`) and the
identity envelope (`build_identity_envelope`) all come from `post_common.py`,
imported and never re-implemented, so the two pushes cannot drift on how they
talk to the server or on what they claim to be. This module holds only what is
doors-specific, and knows nothing about rooms.

What is genuinely different, and why:

- **The doors schema versions independently of rooms**, starting at 1. A
  change to the room contract has nothing to say about doors.
- **No `levels` array.** A doors push targets a model that already has rooms
  (the server refuses otherwise), and that model's rooms snapshot already
  carries the level set a door's `level_id` points into. A second copy could
  only disagree.
- **The room references, the position and the direction do not come from the
  export.** See `translate_door` -- all four are read from the Revit API by
  `room_m.utils.doors.door_placements`, in one pass, which is the only side
  that can ask the questions correctly and the only way they are guaranteed to
  agree.
- **A degenerate footprint is dropped**, see `loops_from_polygon`. This is
  the one place this module actively discards data, and it has to: the bad
  value looks like real geometry.
- **An empty doors push is refused here, though the server accepts one.**
  Deliberately stricter than `handlers.rs`, and the asymmetry is the point.
  The server must allow zero doors, because it cannot tell a shell or a
  pre-fit-out phase from a broken export. This side is not answering that
  question -- it is answering "someone asked for a doors push and there are no
  doors to push", which is worth stopping whichever of the two it turns out to
  be. The cost is real and accepted: a model that genuinely has no doors can no
  longer record that fact through this producer.

Returns the same `(ok, status, text)` tuple shape as the room push, so the
caller's `Result` tracking is identical for both.
"""

import json

from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue

from room_m.post_common import (
    build_identity_envelope,
    duhast_object_to_plain,
    empty_push_refusal,
    loop_to_points,
    properties_to_map,
    write_ndjson_line,
    _post_content,
)

from room_m.utils.phase_filter import (
    in_selected_phase,
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
    """Everything the v1 doors contract needs EXCEPT `doors`.

    Which is the shared identity block and nothing else -- no `levels`, no
    `room_boundary` (see the module docstring for both). That is why this is a
    single delegating call rather than a body: what a doors envelope carries is
    exactly what every entity's envelope carries, so the *only* doors-specific
    facts left here are the schema version and the noun in the phase message.

    Kept as a named function rather than inlined into its two callers, on the
    same terms as the transport helpers: the doors schema version is then stated
    once, and the streaming and buffered paths cannot end up building different
    envelopes.

    Doors are stricter than rooms on the far side of the phase check -- a phase
    that DISAGREES with the model is refused rather than quarantined, because
    activating it would re-phase the model while its rooms stayed behind. That
    is the server's rule, not this envelope's; what happens here is identical
    for both entities."""
    return build_identity_envelope(doors_source, "doors", SCHEMA_VERSION)


def translate_door(door, placements):
    """Map one duHast door object onto the v1 `Door` shape, or return None when
    it carries no id (nothing downstream could key on it).

    `placements` is `{door id: {"from_room", "to_room", "insertion_point",
    "normal"}}`, built by `room_m.utils.doors.door_placements` from the Revit
    API.
    **Everything in it is read from Revit rather than from the export**, and for
    two different reasons.

    The room references, because the export's own are unusable:

    1. They are arrays holding one entry per phase, tagged with a `phase_id`
       that appears nowhere else in the file and cannot be resolved against
       anything on the wire -- the blocker STRATEGY-ENTITIES records.
    2. `FamilyInstance.FromRoom[phase]` takes the phase and answers exactly one
       room, so asking Revit is both correct and simpler than reconciling an
       array against a phase table that isn't there.

    The position and direction, because they must agree with those references.
    `through_wall_normal` points from the from-room to the to-room, and it is
    `FacingOrientation` -- the same orientation `ToRoom` itself follows. Read
    from one API pass over one phase, the four values cannot describe different
    states of the same door.

    A door absent from `placements` gets `None` for all four rather than
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
    placement = placements.get(door_id) or {}

    return {
        "id": door_id,
        "level_id": str(level.get("id", "unknown")),
        "loops": loops_from_polygon(door.get("polygon")),
        "from_room": placement.get("from_room"),
        "to_room": placement.get("to_room"),
        # Both are sent even when null. The contract accepts their absence (old
        # snapshots predate them) but this producer states what it found either
        # way -- "Revit had no plan direction for this door" and "this producer
        # is too old to have looked" are different facts, and a key that is
        # simply missing cannot tell them apart.
        "insertion_point": placement.get("insertion_point"),
        "through_wall_normal": placement.get("normal"),
        "type_id": str(type_props.get("id", "unknown")),
        "type_name": type_props.get("name", "Unknown Type"),
        "properties": properties_to_map(instance),
        "type_properties": properties_to_map(type_props),
    }


def translate(doors_source, placements, allowed_door_ids=None):
    """Map the duHast door export onto the v1 contract as one whole payload.
    The buffered counterpart of `post_doors_stream`, kept for the same reasons
    `post_rooms.translate` is: small manual pushes and fixture generation."""
    envelope = build_envelope(doors_source)
    out_doors = []
    for door in doors_source.get(DOOR_LIST_KEY, []):
        out_door = translate_door(door, placements)
        if out_door is not None and in_selected_phase(out_door, allowed_door_ids):
            out_doors.append(out_door)
    envelope["doors"] = out_doors
    return envelope


def post_doors_stream(json_formatted_doors, placements, url=SERVER_URL_STREAM, allowed_door_ids=None):
    """Gzip-compress an NDJSON stream (line 1 = envelope, one line per door) to
    the server's streaming doors ingest, translating one door at a time as it
    is read off the raw export.

    Doors are far fewer than rooms per model, so this is not load-bearing the
    way the room stream is. It is used anyway so one transport serves both
    pushes -- a producer that streamed rooms and buffered doors would be two
    code paths to keep working for no gain. Returns `(ok, status, text)`.

    Sends nothing when no door reaches the wire, counted as the stream is
    written for the same reason the room path counts there -- see the module
    docstring for why this is stricter than the server."""
    door_meta = dict(
        (key, value) for key, value in json_formatted_doors.items() if key != DOOR_LIST_KEY
    )
    envelope = build_envelope(duhast_object_to_plain(door_meta))

    raw = 0
    no_id = 0
    out_of_phase = 0
    written = 0

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for door in json_formatted_doors.get(DOOR_LIST_KEY, []):
            raw += 1
            out_door = translate_door(duhast_object_to_plain(door), placements)
            if out_door is None:
                no_id += 1
                continue
            if not in_selected_phase(out_door, allowed_door_ids):
                out_of_phase += 1
                continue
            written += 1
            write_ndjson_line(gz, out_door)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    if written == 0:
        return empty_push_refusal("doors", envelope, raw, [
            (no_id, "carrying no element id"),
            (out_of_phase, "outside phase '{}'".format(envelope["phase"])),
        ])

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)


def post_doors(json_formatted_doors, placements, url=SERVER_URL, allowed_door_ids=None):
    """Buffered counterpart of `post_doors_stream`. Returns `(ok, status, text)`."""
    doors_source = duhast_object_to_plain(json_formatted_doors)
    contract = translate(doors_source, placements, allowed_door_ids)

    # Guarded here rather than in `translate`, matching `post_rooms.post_payload`:
    # translating an empty door set is a legitimate thing to ask for, pushing one
    # is not.
    if not contract["doors"]:
        return empty_push_refusal(
            "doors", contract, len(doors_source.get(DOOR_LIST_KEY, [])), [])

    from System.Net.Http import StringContent
    from System.Text import Encoding

    return _post_content(url, StringContent(json.dumps(contract), Encoding.UTF8, "application/json"))
