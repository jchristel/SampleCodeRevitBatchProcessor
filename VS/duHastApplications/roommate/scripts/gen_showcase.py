#!/usr/bin/env python3
"""Generate the 'showcase' project — a synthetic sample campus that exercises
every implemented feature: multiple **buildings**, the **hierarchy**
(Building/Department/SubDepartment), **colour plans** (all three modes),
**milestones** (two), and **milestone comparison**.

It emits TWO snapshots of one model ("campus-arch"), an earlier *Concept* and a
later *Design Freeze*, with deliberate differences (resized rooms, a department
reassignment, added and removed rooms) so the milestone comparison has something
to show. Rooms carry a stable `RoomNumber` (the comparison key) plus `Area`,
`TargetArea`, and `LastRenovated` (for the property-compare and date-range colour
plans). Every room has a **3x3 grid of columns** (nine square voids), so the
areas summary's footprint-vs-net delta is clearly non-zero.

    python scripts/gen_showcase.py            # writes data/showcase-concept.json + data/showcase-freeze.json
    # then POST concept first, then freeze (see the printed curl lines)

Pairs with settings/projects/showcase.toml, which defines the hierarchy, the
three colour plans, the two milestones (pinning the two snapshots below by their
taken_at), the comparison key, and the compared properties.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_big_plate import rect, prop  # noqa: E402

CELL_W, CELL_H = 16.0, 14.0
ROOM_COLS, ROOM_ROWS = 3, 3          # rooms per department
BUILDING_GAP = 30.0                  # feet between the two towers
COL_GRID, COL_SIZE = 3, 0.8          # a 3x3 grid of 0.8ft-square columns per room

CONCEPT_TS = "2026-01-15T09:00:00Z"
FREEZE_TS = "2026-06-30T09:00:00Z"

BUILDINGS = [
    ("North Tower", "NT", ["Emergency", "Radiology", "Surgery"]),
    ("South Tower", "ST", ["Wards", "Outpatient", "Pharmacy"]),
]
LEVELS = [("ground", "Ground", 0.0), ("level-1", "Level 1", 4000.0)]


def col_holes(x0, y0, x1, y1):
    """Nine column voids on a 3x3 grid inside the room, at 1/6, 1/2, 5/6."""
    w, h = x1 - x0, y1 - y0
    holes = []
    for i in range(COL_GRID):
        for j in range(COL_GRID):
            cx = x0 + w * (i + 0.5) / COL_GRID
            cy = y0 + h * (j + 0.5) / COL_GRID
            holes.append(rect(cx - COL_SIZE / 2, cy - COL_SIZE / 2, cx + COL_SIZE / 2, cy + COL_SIZE / 2))
    return holes


def a_room(rn, name, level_id, x0, y0, x1, y1, building, dept, sub, target, renov):
    net = (x1 - x0) * (y1 - y0) - COL_GRID * COL_GRID * COL_SIZE * COL_SIZE
    return {
        "id": rn,
        "name": name,
        "level_id": level_id,
        "loops": [rect(x0, y0, x1, y1)] + col_holes(x0, y0, x1, y1),
        "properties": {
            "Name": prop(name),
            "RoomNumber": prop(rn),
            "Building": prop(building),
            "Department": prop(dept),
            "SubDepartment": prop(sub),
            "Area": prop(round(net, 1)),
            "TargetArea": prop(target),
            "LastRenovated": prop(renov),
        },
    }


def base_layout():
    """Variant-agnostic room slots: identity + geometry. Diffs are applied per
    snapshot on top of this."""
    slots = []
    building_x = 0.0
    for bname, bcode, depts in BUILDINGS:
        bwidth = len(depts) * ROOM_COLS * CELL_W
        for lid, lname, _elev in LEVELS:
            for di, dept in enumerate(depts):
                dx = building_x + di * ROOM_COLS * CELL_W
                for rc in range(ROOM_COLS):
                    for rr in range(ROOM_ROWS):
                        idx = rc * ROOM_ROWS + rr
                        sub = "Ward A" if rr < 2 else "Ward B"
                        x0, y0 = dx + rc * CELL_W, rr * CELL_H
                        rn = f"{bcode}-{lid[0].upper()}-{dept[:3].upper()}{idx:02d}"
                        # a renovation date spread across years for the date colour plan
                        year = 2018 + (idx + di) % 8
                        slots.append({
                            "rn": rn, "name": f"{dept} {idx:02d}", "level_id": lid,
                            "x0": x0, "y0": y0, "x1": x0 + CELL_W, "y1": y0 + CELL_H,
                            "building": bname, "dept": dept, "sub": sub,
                            "target": round(CELL_W * CELL_H * 0.95, 1),
                            "renov": f"{year}-0{1 + idx % 9}-15",
                        })
        building_x += bwidth + BUILDING_GAP
    return slots


def levels():
    return [{"id": lid, "name": lname, "elevation": elev} for lid, lname, elev in LEVELS]


def concept(slots):
    return [a_room(s["rn"], s["name"], s["level_id"], s["x0"], s["y0"], s["x1"], s["y1"],
                   s["building"], s["dept"], s["sub"], s["target"], s["renov"]) for s in slots]


def freeze(slots):
    """Design Freeze = Concept with deliberate, legible changes so the milestone
    comparison reports resized (Area), reassigned (Department), added and removed
    rooms."""
    rooms = []
    for s in slots:
        # Remove: the last room of every Surgery/Pharmacy dept disappears.
        if s["rn"].endswith("08") and s["dept"] in ("Surgery", "Pharmacy"):
            continue
        x0, y0, x1, y1 = s["x0"], s["y0"], s["x1"], s["y1"]
        dept, sub = s["dept"], s["sub"]
        # Resize: room 00 of each dept shrinks 20% (Area changes).
        if s["rn"].endswith("00"):
            x1 = x0 + (x1 - x0) * 0.8
        # Reassign: Emergency room 04 becomes Radiology.
        if dept == "Emergency" and s["rn"].endswith("04"):
            dept = "Radiology"
        rooms.append(a_room(s["rn"], s["name"], s["level_id"], x0, y0, x1, y1,
                            s["building"], dept, sub, s["target"], s["renov"]))
    # Add: two brand-new rooms per tower on the ground floor (new RoomNumbers).
    for bname, bcode, _ in BUILDINGS:
        for k in range(2):
            x0 = 400.0 + k * CELL_W
            rooms.append(a_room(f"{bcode}-G-NEW{k:02d}", f"New Room {k}", "ground",
                               x0, 60.0, x0 + CELL_W, 60.0 + CELL_H, bname, "Outpatient",
                               "Ward A", round(CELL_W * CELL_H * 0.95, 1), "2026-05-01"))
    return rooms


def main():
    slots = base_layout()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # roommate/
    for variant, ts, builder in [("concept", CONCEPT_TS, concept), ("freeze", FREEZE_TS, freeze)]:
        rooms = builder(slots)
        snap = {
            "schema_version": 5,
            "project": {"id": "showcase", "name": "Sample Campus"},
            "model": {"id": "campus-arch", "name": "Campus-ARCH", "source": "revit"},
            "snapshot": {"taken_at": ts},
            "levels": levels(),  # shared levels; both buildings appear on each
            "rooms": rooms,
        }
        path = os.path.join(here, "data", f"showcase-{variant}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snap, f)
        sys.stderr.write(f"{variant}: {len(rooms)} rooms -> {os.path.relpath(path, here)} (taken_at {ts})\n")
    sys.stderr.write(
        "\nPush (concept first, then freeze):\n"
        "  curl -X POST --data-binary @data/showcase-concept.json http://127.0.0.1:5151/rooms\n"
        "  curl -X POST --data-binary @data/showcase-freeze.json  http://127.0.0.1:5151/rooms\n")


if __name__ == "__main__":
    main()
