#!/usr/bin/env python3
"""Generate synthetic floor-plate snapshots in the server's v5 contract.

Neither the raster JPEG nor the vector PDF of the hospital plan can be reliably
traced into labelled room polygons (walls aren't closed loops, and there's no
room->department mapping), so this builds *structurally* similar plates instead:
one Building, a grid of Departments, each a grid of Rooms.

Run directly, this produces a standalone `big-plate` project (N identical levels).
It also exposes `build_plate()` / `snapshot()` for other generators (e.g.
`gen_sample_plates.py`, which drops Medium + Large levels into the sample
project). Each plate deliberately exercises the features that need scale:
  * hundreds/thousands of rooms per level -> the viewer's viewport culling;
  * a Building/Department(/SubDepartment) hierarchy -> the /areas tier dissolve;
  * column holes in some rooms -> footprint > net (filled voids -> Delta > 0);
  * one empty courtyard block ringed by departments -> a hole that only appears
    when departments dissolve at the Building tier (enclosed-space-counts case);
  * a detached wing -> islands (a MultiPolygon at the Department/Building tiers).

Coordinates are in feet, Y-up (the viewer flips Y).
"""
import argparse
import json
import sys

CELL_W, CELL_H = 16.0, 14.0          # feet, one room cell
DEPARTMENTS = [
    "Emergency", "Surgery", "Imaging", "Wards A", "Wards B", "Outpatient",
    "Laboratory", "Pharmacy", "Administration", "Sterilisation", "ICU", "Maternity",
]
SUBS = ["North", "South", "East", "West"]  # 4 sub-departments per department, by quadrant


def rect(x0, y0, x1, y1):
    """A closed rectangle loop (Y-up), CCW."""
    return {"points": [{"x": x0, "y": y0}, {"x": x1, "y": y0},
                       {"x": x1, "y": y1}, {"x": x0, "y": y1}]}


def prop(v):
    return {"value": str(v), "storage_type": None}


def default_props(building, dept, sub):
    """Classification properties for the standalone `big-plate` project, whose
    hierarchy keys tiers on the name properties Building / Department / SubDepartment."""
    return {"Building": building, "Department": dept, "SubDepartment": sub}


def _room(rid, name, level_id, x0, y0, x1, y1, building, dept, sub, hole, props_fn):
    loops = [rect(x0, y0, x1, y1)]
    if hole:  # a small centred column void; stage 1 fills it -> footprint > net
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        loops.append(rect(cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2))
    net = (x1 - x0) * (y1 - y0) - (5.76 if hole else 0.0)
    props = {"Name": prop(name), "Area": prop(round(net, 2))}
    for k, v in props_fn(building, dept, sub).items():
        props[k] = prop(v)
    return {"id": rid, "name": name, "level_id": level_id, "loops": loops, "properties": props}


def build_plate(level_id, level_name, elevation, *, dept_cols, dept_rows, room_cols, room_rows,
                hole_every=7, first_id=100000, building="Main", props_fn=default_props,
                courtyard=(1, 1)):
    """Build one level's worth of rooms as a grid of departments of rooms, plus a
    detached wing. Returns (rooms, level, next_id) so a caller can pack several
    plates (each its own level id) into one snapshot without id collisions."""
    rooms = []
    next_id = first_id
    dept_w, dept_h = room_cols * CELL_W, room_rows * CELL_H

    for dc in range(dept_cols):
        for dr in range(dept_rows):
            if (dc, dr) == courtyard:
                continue  # leave an empty block ringed by its neighbours
            dept = DEPARTMENTS[(dc * dept_rows + dr) % len(DEPARTMENTS)]
            dx0, dy0 = dc * dept_w, dr * dept_h
            for rc in range(room_cols):
                for rr in range(room_rows):
                    x0, y0 = dx0 + rc * CELL_W, dy0 + rr * CELL_H
                    sub = SUBS[(1 if rc >= room_cols // 2 else 0) + (2 if rr >= room_rows // 2 else 0)]
                    hole = (next_id % hole_every == 0)
                    rooms.append(_room(str(next_id), f"{dept[:3].upper()} {dc}{dr}-{rc}{rr}", level_id,
                                       x0, y0, x0 + CELL_W, y0 + CELL_H, building, dept, sub, hole, props_fn))
                    next_id += 1

    # A detached wing: its own department, offset right -> a separate island.
    wing_x = dept_cols * dept_w + 40.0
    for rc in range(4):
        for rr in range(6):
            x0, y0 = wing_x + rc * CELL_W, rr * CELL_H
            sub = SUBS[(1 if rc >= 2 else 0) + (2 if rr >= 3 else 0)]
            rooms.append(_room(str(next_id), f"WNG-{rc}{rr}", level_id,
                               x0, y0, x0 + CELL_W, y0 + CELL_H, building, "Plant Wing", sub, False, props_fn))
            next_id += 1

    level = {"id": level_id, "name": level_name, "elevation": float(elevation)}
    return rooms, level, next_id


def snapshot(project_id, project_name, model_id, model_name, taken_at, plates):
    """Pack one or more (rooms, level) plates into one v5 snapshot for a model."""
    rooms, levels = [], []
    for plate_rooms, level in plates:
        rooms.extend(plate_rooms)
        levels.append(level)
    return {
        "schema_version": 5,
        "project": {"id": project_id, "name": project_name},
        "model": {"id": model_id, "name": model_name, "source": "revit"},
        "snapshot": {"taken_at": taken_at},
        "levels": levels,
        "rooms": rooms,
    }


def _main():
    p = argparse.ArgumentParser(description="Generate a standalone big-plate v5 snapshot.")
    p.add_argument("--levels", type=int, default=3)
    p.add_argument("--dept-cols", type=int, default=4)
    p.add_argument("--dept-rows", type=int, default=3)
    p.add_argument("--room-cols", type=int, default=6)
    p.add_argument("--room-rows", type=int, default=6)
    p.add_argument("--hole-every", type=int, default=7)
    a = p.parse_args()

    plates, next_id = [], 100000
    for lvl in range(a.levels):
        rooms, level, next_id = build_plate(
            f"L{lvl}", f"Level {lvl:02d}", lvl * 4000, first_id=next_id,
            dept_cols=a.dept_cols, dept_rows=a.dept_rows, room_cols=a.room_cols,
            room_rows=a.room_rows, hole_every=a.hole_every)
        plates.append((rooms, level))

    snap = snapshot("big-plate", "Large Floor Plate (synthetic)",
                    "big-plate-model", "BigPlate-ARCH", "2026-07-17T09:00:00Z", plates)
    sys.stderr.write(f"generated {len(snap['rooms'])} rooms across {len(snap['levels'])} levels\n")
    json.dump(snap, sys.stdout)


if __name__ == "__main__":
    _main()
