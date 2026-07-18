#!/usr/bin/env python3
"""Add two synthetic test levels to the SAMPLE project for UI testing.

Emits a v5 snapshot for a new model ("Synthetic Plates") under `sample-project`,
carrying two extra levels — a Medium plate (~300 rooms) and a Large plate
(~5000 rooms) — so the viewer's level picker gains scale-test levels alongside
the real sample data, without touching the existing sample model. Push it:

    python scripts/gen_sample_plates.py > data/sample-plates-snapshot.json
    curl -X POST --data-binary @data/sample-plates-snapshot.json http://127.0.0.1:5151/rooms

Rooms carry only the `Department` property (sample-project's Department tier),
NOT the Building properties: the real sample rooms resolve no Building either, so
adding one here would split sample-project into a "Synthetic" building vs the
real rooms, auto-select that building, and hide the real hospital data. Leaving
Building unset keeps every level in one picker — you just switch levels — and the
/areas dissolve still works (Building resolves to its `undefined` bucket, with the
real Departments underneath). Distinct level names/elevations avoid level dedup.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_big_plate import build_plate, snapshot  # noqa: E402


def sample_props(building, dept, sub):
    # Only Department (sample-project's Department tier). Building is deliberately
    # left unset — see the module docstring for why a building split is undesirable.
    return {"Department": dept}


def main():
    med_rooms, med_level, next_id = build_plate(
        "synthetic-medium", "Synthetic — Medium", 24000, first_id=500000,
        dept_cols=4, dept_rows=3, room_cols=5, room_rows=5,
        building="Synthetic", props_fn=sample_props)

    lg_rooms, lg_level, _ = build_plate(
        "synthetic-large", "Synthetic — Large", 28000, first_id=next_id,
        dept_cols=9, dept_rows=7, room_cols=9, room_rows=9,
        building="Synthetic", props_fn=sample_props)

    snap = snapshot("sample-project", "Sample Hospital Job",
                    "synthetic-plates", "Synthetic Plates", "2026-07-18T09:00:00Z",
                    [(med_rooms, med_level), (lg_rooms, lg_level)])
    sys.stderr.write(
        f"medium: {len(med_rooms)} rooms, large: {len(lg_rooms)} rooms "
        f"({len(snap['rooms'])} total across 2 new levels)\n")
    json.dump(snap, sys.stdout)


if __name__ == "__main__":
    main()
