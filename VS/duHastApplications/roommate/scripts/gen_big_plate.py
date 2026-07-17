#!/usr/bin/env python3
"""Generate a large synthetic floor-plate snapshot in the server's v5 contract.

Neither the raster JPEG nor the vector PDF of the hospital plan can be reliably
traced into labelled room polygons (walls aren't closed loops, and there's no
room->department mapping), so this builds a *structurally* similar plate instead:
one Building, a grid of Departments, each a grid of Rooms, on several levels.

It deliberately exercises the features that need scale:
  * hundreds/thousands of rooms per level -> the viewer's no-viewport-culling path
    (STRATEGY-BROWSER.md "No viewport culling on zoom");
  * a real Building/Department/SubDepartment hierarchy -> the /areas tier dissolve;
  * column holes in some rooms -> footprint > net (filled voids -> summary Delta > 0);
  * one empty courtyard block ringed by departments -> a hole that only appears
    when departments dissolve at the Building tier (the enclosed-space-counts case);
  * a detached wing -> islands (a MultiPolygon at the Department and Building tiers).

Rooms match `big-plate.toml`'s hierarchy: name properties Building / Department /
SubDepartment. Coordinates are in feet, Y-up (the viewer flips Y). Run:

    python scripts/gen_big_plate.py > data/big-plate-snapshot.json

then POST it to a running server:  curl -X POST --data-binary @data/big-plate-snapshot.json http://127.0.0.1:5151/rooms
"""
import argparse
import json
import sys

# --- knobs (defaults give ~1300 rooms across 3 levels; override via CLI) ---
# Culling stress lives in rooms-PER-LEVEL (the viewer renders one level's SVG at
# a time), so bump the grid dimensions, not just the level count. Example for a
# ~5000-rooms/level stress plate:
#   python scripts/gen_big_plate.py --dept-cols 9 --dept-rows 7 --room-cols 9 --room-rows 9 --levels 2
_p = argparse.ArgumentParser(description="Generate a synthetic floor-plate v5 snapshot.")
_p.add_argument("--levels", type=int, default=3)
_p.add_argument("--dept-cols", type=int, default=4)
_p.add_argument("--dept-rows", type=int, default=3)
_p.add_argument("--room-cols", type=int, default=6)
_p.add_argument("--room-rows", type=int, default=6)
_p.add_argument("--hole-every", type=int, default=7, help="~1 in N rooms gets a column hole")
_args = _p.parse_args()

LEVELS = _args.levels
DEPT_COLS, DEPT_ROWS = _args.dept_cols, _args.dept_rows   # departments per level
ROOM_COLS, ROOM_ROWS = _args.room_cols, _args.room_rows   # rooms per department
CELL_W, CELL_H = 16.0, 14.0          # feet, one room cell
HOLE_EVERY = _args.hole_every        # ~1 in N rooms gets a column hole
COURTYARD_DEPT = (1, 1)             # this department block is left empty (ringed void)

DEPARTMENTS = [
    "Emergency", "Surgery", "Imaging", "Wards A", "Wards B", "Outpatient",
    "Laboratory", "Pharmacy", "Administration", "Sterilisation", "ICU", "Maternity",
]
SUBS = ["North", "South", "East", "West"]  # 4 sub-departments per department, by quadrant


def rect(x0, y0, x1, y1):
    """A closed-open rectangle loop (Y-up), CCW."""
    return {"points": [{"x": x0, "y": y0}, {"x": x1, "y": y0},
                       {"x": x1, "y": y1}, {"x": x0, "y": y1}]}


def prop(v):
    return {"value": str(v), "storage_type": None}


def make_room(rid, name, level_id, x0, y0, x1, y1, building, dept, sub, hole):
    loops = [rect(x0, y0, x1, y1)]
    if hole:
        # a small centred column void; stage 1 fills it -> footprint > net
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        loops.append(rect(cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2))
    net = (x1 - x0) * (y1 - y0) - (5.76 if hole else 0.0)
    return {
        "id": rid, "name": name, "level_id": level_id, "loops": loops,
        "properties": {
            "Name": prop(name),
            "Building": prop(building),
            "Department": prop(dept),
            "SubDepartment": prop(sub),
            "Area": prop(round(net, 2)),
        },
    }


def build():
    rooms = []
    levels = []
    dept_w = ROOM_COLS * CELL_W
    dept_h = ROOM_ROWS * CELL_H
    next_id = 100000

    for lvl in range(LEVELS):
        level_id = f"L{lvl}"
        levels.append({"id": level_id, "name": f"Level {lvl:02d}", "elevation": float(lvl * 4000)})

        for dc in range(DEPT_COLS):
            for dr in range(DEPT_ROWS):
                if (dc, dr) == COURTYARD_DEPT:
                    continue  # leave an empty block ringed by its neighbours
                dept = DEPARTMENTS[(dc * DEPT_ROWS + dr) % len(DEPARTMENTS)]
                dx0 = dc * dept_w
                dy0 = dr * dept_h
                for rc in range(ROOM_COLS):
                    for rr in range(ROOM_ROWS):
                        x0 = dx0 + rc * CELL_W
                        y0 = dy0 + rr * CELL_H
                        sub = SUBS[(1 if rc >= ROOM_COLS // 2 else 0) + (2 if rr >= ROOM_ROWS // 2 else 0)]
                        hole = (next_id % HOLE_EVERY == 0)
                        rooms.append(make_room(
                            str(next_id), f"{dept[:3].upper()} {dc}{dr}-{rc}{rr}", level_id,
                            x0, y0, x0 + CELL_W, y0 + CELL_H, "Main", dept, sub, hole))
                        next_id += 1

        # A detached wing: its own department, offset to the right -> a separate
        # island at the Department and Building tiers.
        wing_x = DEPT_COLS * dept_w + 40.0
        for rc in range(4):
            for rr in range(6):
                x0 = wing_x + rc * CELL_W
                y0 = rr * CELL_H
                sub = SUBS[(1 if rc >= 2 else 0) + (2 if rr >= 3 else 0)]
                rooms.append(make_room(
                    str(next_id), f"WNG-{rc}{rr}", level_id,
                    x0, y0, x0 + CELL_W, y0 + CELL_H, "Main", "Plant Wing", sub, False))
                next_id += 1

    return {
        "schema_version": 5,
        "project": {"id": "big-plate", "name": "Large Floor Plate (synthetic)"},
        "model": {"id": "big-plate-model", "name": "BigPlate-ARCH", "source": "revit"},
        "snapshot": {"taken_at": "2026-07-17T09:00:00Z"},
        "levels": levels,
        "rooms": rooms,
    }


if __name__ == "__main__":
    payload = build()
    sys.stderr.write(f"generated {len(payload['rooms'])} rooms across {len(payload['levels'])} levels\n")
    json.dump(payload, sys.stdout)
