"""
POC bridge for ROOMS: take the duHast room + level exports, translate to the
viewer's v6 contract, and POST to the Rust server.

Everything here is rooms-specific. The transport, the identity envelope, the
duHast flattening and the NDJSON writer are shared with the other entity
pushes and live in `post_common.py` -- imported, never re-implemented, so no
two pushes can drift on how they talk to the server.

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
instead of a false "Finished". A push refused *here*, before the network (see
`post_common.empty_push_refusal`), reports through that same tuple with
`status = None`, so the caller needs no second failure channel to branch on.
"""

import json
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import StringContent, ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue
from System.Text import Encoding

from room_m.post_common import (
    LEVEL_LIST_KEY,
    build_identity_envelope,
    duhast_object_to_plain,
    duhast_objects_to_plain,
    empty_push_refusal,
    find_property,
    loop_to_points,
    properties_to_map,
    translate_levels,
    write_ndjson_line,
    _post_content,
)

from room_m.utils.phase_filter import (
    in_selected_phase,
)

SERVER_URL = "http://127.0.0.1:5151/rooms"
SERVER_URL_STREAM = "http://127.0.0.1:5151/rooms/stream"
SCHEMA_VERSION = 7


ROOM_LIST_KEY = "room"


def build_envelope(run_envelope, model_blocks):
    """Everything the v7 contract needs EXCEPT `rooms`: the run's shared identity
    plus its `models` list, each block already carrying this model's `levels` and
    (optionally) its `room_boundary`.

    Shared by the buffered `translate()` and the streaming path so both build
    identity the same way -- see contract.rs's `StreamEnvelope`, which is this
    dict's line-1 NDJSON counterpart server-side.

    The two rooms-only per-model fields are stamped by the caller rather than
    here: `room_boundary` by `room_m.utils.post_envelope.add_room_boundary` off
    the document, `levels` by `translate_levels` off the export. Both are
    optional to the server -- an absent regime falls back to the project's
    `[areas] boundary_location` and then to finish face, which is exactly what
    every push did before the field was sent."""
    return build_identity_envelope(run_envelope, model_blocks, "rooms", SCHEMA_VERSION)


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


def translate(run_envelope, entries):
    """Map a run's duHast exports onto the server's v7 contract as one whole
    payload. Used for the fully-buffered `/rooms` path and for regenerating
    `settings/test_snapshot.json` (see STRATEGY-SERVER.md).

    `entries` is `[(model_block, contribution), ...]` -- one per document in the
    run, as `room_m.exporters.rooms.export_model` builds them. Each
    `contribution` carries the model's raw room and level exports and its phase
    filter, so the per-model facts stay attached to the model they came from
    rather than being flattened into one heap this side of the wire."""
    blocks = []
    per_model_rooms = []
    for block, contribution in entries:
        levels_source = duhast_objects_to_plain(contribution["levels"])
        rooms_source = duhast_objects_to_plain(contribution["rooms"])
        block = dict(block)
        block["levels"] = translate_levels(levels_source)
        blocks.append(block)

        out_rooms = []
        for room in rooms_source.get(ROOM_LIST_KEY, []):
            out_room = translate_room(room)
            if out_room is not None and in_selected_phase(out_room, contribution["allowed_ids"]):
                out_rooms.append(out_room)
        per_model_rooms.append(out_rooms)

    contract = build_envelope(run_envelope, blocks)
    for model, out_rooms in zip(contract["models"], per_model_rooms):
        model["rooms"] = out_rooms
    return contract


def post_payload(run_envelope, entries, url=SERVER_URL):
    """Flatten a run's duHast exports, translate, and POST the whole v7 contract
    as one buffered JSON body. Retained for the `settings/settings.toml`
    dev-seed fixture and small/manual pushes; the live Revit export path
    (`room_mate.py`) uses `post_payload_stream` instead -- see module
    docstring. Returns `(ok, status, text)`."""
    contract = translate(run_envelope, entries)

    # Guarded on the way OUT, not inside `translate`: `translate` also generates
    # the `settings/test_snapshot.json` fixture and the `test_data` seed, and a
    # fixture generator has no business refusing to produce an empty document.
    # What is a fault is *pushing* one.
    #
    # Counted across the RUN, matching the streaming path and
    # `empty_push_refusal`'s own scope: a run that sent nothing is the fault, and
    # one rooms-less document among several is not.
    written = sum(len(model["rooms"]) for model in contract["models"])
    if not written:
        raw = sum(
            len(duhast_objects_to_plain(c["rooms"]).get(ROOM_LIST_KEY, [])) for _, c in entries
        )
        return empty_push_refusal("rooms", contract, raw, [])

    # ensure_ascii=False for the reason `write_ndjson_line` records: under
    # IronPython 2.7 escaping a non-ASCII character means decoding a byte
    # oriented str with the system code page first, which fails on bytes like
    # 0xAE and takes the whole push with it. StringContent below encodes as
    # UTF-8 correctly instead.
    body = json.dumps(contract, ensure_ascii=False)

    content = StringContent(body, Encoding.UTF8, "application/json")
    return _post_content(url, content)


def post_payload_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Gzip-compress an NDJSON stream (line 1 = envelope, one line per room) to
    the server's streaming ingest. Each room is flattened, translated, and
    written into the gzip stream individually as it's read off the raw export --
    no whole-export `json.dumps` round-trip and no second full rooms list, so
    peak memory on the translation side is one room's dict. The compressed body
    does still accumulate in a `MemoryStream` before the POST (see the module
    docstring for why that's acceptable). This is the path `room_mate.py` calls
    for a live Revit export. Returns `(ok, status, text)`.

    `entries` is `[(model_block, contribution), ...]` -- the whole run. **Every
    room line names its own model**, rather than the stream switching models on a
    marker line: a dropped or reordered line would otherwise file rooms under the
    wrong model, and a room id is unique only within a model, so the result would
    resolve against real-looking rooms instead of failing. The id costs a few
    bytes gzip removes anyway.

    Sends nothing when the translation keeps no rooms across the whole run
    (`empty_push_refusal`). The count is taken *as the stream is written* rather
    than by pre-scanning the export, because the two questions differ: the phase
    filter says what it keeps, and `translate_room` independently drops unplaced
    rooms, so only the write loop knows how many rooms actually reached the wire.
    The body is built and then discarded in that case -- cheap, since there was
    nothing in it, and it buys a single unambiguous count instead of two
    estimates that could disagree."""
    # The metadata around each model's room list (file header) is small --
    # flatten it in one go, leaving the (potentially huge) room lists untouched
    # as raw duHast objects to be flattened one at a time below. `levels` is
    # small too and is needed whole, on the model block it belongs to.
    blocks = []
    for block, contribution in entries:
        block = dict(block)
        block["levels"] = translate_levels(duhast_object_to_plain(contribution["levels"]))
        blocks.append(block)
    envelope = build_envelope(run_envelope, blocks)

    raw = 0
    unplaced = 0
    out_of_phase = 0
    written = 0

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for block, (_, contribution) in zip(blocks, entries):
            model_id = block["id"]
            for room in contribution["rooms"].get(ROOM_LIST_KEY, []):
                raw += 1
                out_room = translate_room(duhast_object_to_plain(room))
                if out_room is None:
                    unplaced += 1
                    continue
                if not in_selected_phase(out_room, contribution["allowed_ids"]):
                    out_of_phase += 1
                    continue
                written += 1
                out_room["model_id"] = model_id
                write_ndjson_line(gz, out_room)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    if written == 0:
        return empty_push_refusal("rooms", envelope, raw, [
            (unplaced, "unplaced (no boundary loop)"),
            (out_of_phase, "outside phase '{}'".format(envelope["phase"])),
        ])

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)
