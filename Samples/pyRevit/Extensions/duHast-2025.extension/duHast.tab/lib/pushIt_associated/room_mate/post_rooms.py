"""
POC bridge: take the duHast room + level exports, translate to the viewer's
v5 contract, and POST to the Rust server.

Large FFE exports run >100 MB uncompressed (see roommate's
HANDOVER-gzip.md / HANDOVER-streaming.md / HANDOVER-streaming-sender.md), so
the actual push (`post_payload_stream`) gzip-compresses a line-delimited
(NDJSON) stream rather than building one giant JSON string -- envelope first,
then one line per room, written straight into the gzip stream as each room is
translated. `post_payload`/`translate()` (the older, fully-buffered path) stay
around only because `settings/settings.toml`'s `test_data` seed and the dev
test fixture (`test_snapshot.json`) are generated from `translate()`'s whole-
payload output.
"""

import json
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import HttpClient, StringContent, ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue
from System.Text import Encoding

from duHast.Utilities.files_json import serialize_utf

SERVER_URL = "http://127.0.0.1:5151/rooms"
SERVER_URL_STREAM = "http://127.0.0.1:5151/rooms/stream"
SCHEMA_VERSION = 5

# Which producer this script feeds the server from. The server resolves
# canonical property names (Area, Number, ...) to this source's raw property
# names via its own settings -- this script only needs to say who it is.
SOURCE = "revit"


LEVEL_LIST_KEY = "building level"
ROOM_LIST_KEY = "room"


def duhast_objects_to_plain(json_data):
    """Serialize duHast data objects (default=serialize_utf), then parse back
    into plain dicts so the translate step can walk them."""
    json_string = json.dumps(json_data, indent=None, default=serialize_utf, ensure_ascii=False)
    return json.loads(json_string)


def find_property(instance_properties, prop_name):
    for prop in instance_properties.get("properties", []):
        if prop.get("name") == prop_name:
            return prop.get("value")
    return None


def loop_to_points(loop):
    return [{"x": float(pt[0]), "y": float(pt[1])} for pt in loop]


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
    NDJSON counterpart server-side."""
    levels = []
    for lvl in levels_source.get(LEVEL_LIST_KEY, []):
        levels.append({
            "id": str(lvl.get("id", "unknown")),
            "name": lvl.get("name", "Unknown Level"),
            "elevation": float(lvl.get("elevation", 0.0) or 0.0),
        })
    levels.sort(key=lambda l: l["elevation"])

    model = dict(rooms_source.get("model", {"id": "unknown", "name": "unknown"}))
    model["source"] = SOURCE

    return {
        "schema_version": SCHEMA_VERSION,
        "project": rooms_source.get("project", {"id": "unknown", "name": "unknown"}),
        "model": model,
        "snapshot": rooms_source.get("snapshot", {"taken_at": ""}),
        "levels": levels,
    }


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
    the gzip stream, followed by '\n'. One object = one NDJSON line."""
    line = json.dumps(obj, separators=(",", ":")) + "\n"  # compact, no spaces
    data = Encoding.UTF8.GetBytes(line)
    gz.Write(data, 0, data.Length)


def post_payload(json_formatted_room, json_formatted_level, url=SERVER_URL):
    """Flatten both duHast exports, translate, and POST the whole v5 contract
    as one buffered JSON body. Retained for the `settings/settings.toml`
    dev-seed fixture and small/manual pushes; the live Revit export path
    (`room_mate.py`) uses `post_payload_stream` instead -- see module docstring."""
    rooms_source = duhast_objects_to_plain(json_formatted_room)
    levels_source = duhast_objects_to_plain(json_formatted_level)
    contract = translate(rooms_source, levels_source)
    body = json.dumps(contract)

    client = HttpClient()
    content = StringContent(body, Encoding.UTF8, "application/json")
    try:
        response = client.PostAsync(url, content).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        print("Server responded {}: {}".format(status, text))
    except Exception as e:
        print("Could not reach {} - is the server running? ({})".format(url, e))
    finally:
        client.Dispose()


def post_payload_stream(json_formatted_room, json_formatted_level, url=SERVER_URL_STREAM):
    """Flatten both duHast exports, then gzip-compress an NDJSON stream (line 1
    = envelope, one line per room) straight to the server's streaming ingest.
    Never builds a second full `rooms` list or one giant `json.dumps` string
    -- each room is translated and written as it's read off `rooms_source`, so
    peak memory here is one room, not the whole export (see
    HANDOVER-streaming-sender.md). This is the path `room_mate.py` calls for
    a live Revit export.
    """
    rooms_source = duhast_objects_to_plain(json_formatted_room)
    levels_source = duhast_objects_to_plain(json_formatted_level)
    envelope = build_envelope(rooms_source, levels_source)

    out = MemoryStream()
    # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
    gz = GZipStream(out, CompressionMode.Compress)
    write_ndjson_line(gz, envelope)
    for room in rooms_source.get(ROOM_LIST_KEY, []):
        out_room = translate_room(room)
        if out_room is not None:
            write_ndjson_line(gz, out_room)
    gz.Close()  # MUST close to flush the gzip footer; do NOT skip
    body = out.ToArray()

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    client = HttpClient()
    try:
        response = client.PostAsync(url, content).Result
        status = int(response.StatusCode)
        text = response.Content.ReadAsStringAsync().Result
        print("Server responded {}: {}".format(status, text))
    except Exception as e:
        print("Could not reach {} - is the server running? ({})".format(url, e))
    finally:
        client.Dispose()
