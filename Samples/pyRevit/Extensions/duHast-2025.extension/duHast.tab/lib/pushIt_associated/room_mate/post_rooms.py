"""
POC bridge: take the duHast room + level exports, translate to the viewer's
v2 contract, and POST to the Rust server.
"""

import json
import clr
clr.AddReference("System.Net.Http")
from System.Net.Http import HttpClient, StringContent
from System.Text import Encoding

from duHast.Utilities.files_json import serialize_utf

SERVER_URL = "http://127.0.0.1:5151/rooms"
SCHEMA_VERSION = 2


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


def translate(rooms_source, levels_source):
    """Map the two duHast exports onto the server's v2 contract."""
    # levels from the dedicated level export
    levels = []
    for lvl in levels_source.get(LEVEL_LIST_KEY, []):
        levels.append({
            "id": str(lvl.get("id", "unknown")),
            "name": lvl.get("name", "Unknown Level"),
            "elevation": float(lvl.get("elevation", 0.0) or 0.0),
        })
    levels.sort(key=lambda l: l["elevation"])

    # rooms, each tagged with its level id
    out_rooms = []
    for room in rooms_source.get(ROOM_LIST_KEY, []):
        polygons = room.get("polygon", [])
        if not polygons:
            continue
        poly = polygons[0]

        outer = poly.get("outer_loop", [])
        if not outer:
            continue  # unplaced room, nothing to draw

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

        out_rooms.append({
            "id": room_id,
            "name": label,
            "level_id": level_id,
            "loops": loops,
        })

    return {"schema_version": SCHEMA_VERSION, "levels": levels, "rooms": out_rooms}


def post_payload(json_formatted_room, json_formatted_level, url=SERVER_URL):
    """Flatten both duHast exports, translate, and POST the v2 contract."""
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