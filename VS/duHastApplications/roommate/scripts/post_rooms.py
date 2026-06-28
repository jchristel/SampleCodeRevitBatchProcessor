"""
POC bridge: read the IronPython room export and POST it to the Rust viewer
in the schema the server expects.

Usage: just run it. Adjust ROOMS_FILE and SERVER_URL below if needed.
"""

import json
import urllib.request
import urllib.error

# --- POC config: hardcoded paths for now ---
ROOMS_FILE = r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET8\VS\duHastApplications\roommate\scripts\rooms.json"        # <-- point this at your export
SERVER_URL = "http://127.0.0.1:5151/rooms"
SCHEMA_VERSION = 1


def find_property(instance_properties, prop_name):
    """Pull a single named value out of the flat properties list."""
    for prop in instance_properties.get("properties", []):
        if prop.get("name") == prop_name:
            return prop.get("value")
    return None


def loop_to_points(loop):
    """Convert [[x, y], ...] pairs into the server's [{x, y}, ...] objects."""
    return [{"x": float(pt[0]), "y": float(pt[1])} for pt in loop]


def translate(source):
    """Map the IronPython export structure onto the server's contract."""
    out_rooms = []

    for room in source.get("room", []):
        polygons = room.get("polygon", [])
        if not polygons:
            continue
        poly = polygons[0]

        outer = poly.get("outer_loop", [])
        if not outer:
            # Unplaced room (empty outline) — nothing to draw, skip it.
            continue

        loops = [{"points": loop_to_points(outer)}]
        for inner in poly.get("inner_loops", []):
            if inner:
                loops.append({"points": loop_to_points(inner)})

        props = room.get("instance_properties", {})
        room_id = str(props.get("id", "unknown"))
        # "Number" is the room's user-facing tag; fall back to the name property.
        number = find_property(props, "Number")
        name = find_property(props, "Name") or "Room"
        label = f"{name} {number}".strip() if number not in (None, "") else name

        out_rooms.append({"id": room_id, "name": label, "loops": loops})

    return {"schema_version": SCHEMA_VERSION, "rooms": out_rooms}


def main():
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        source = json.load(f)

    payload = translate(source)
    print(f"Translated {len(payload['rooms'])} room(s) with geometry.")

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SERVER_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Server responded {resp.status}: {resp.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Server rejected it ({e.code}): {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"Could not reach {SERVER_URL} — is the server running? ({e.reason})")


if __name__ == "__main__":
    main()