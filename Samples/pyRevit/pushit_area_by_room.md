# Verify Push It Area

**Panel:** PushIt | **Button:** Verify Push It Area

Measures each mock room by briefly placing a real Revit room inside it, writes the measured
area back onto the mock room, and deletes the temporary rooms again.

## What it does

For every mock room in the **active** model:

1. Places a temporary Revit room at the mock room's location.
2. Reads the room's area and perimeter.
3. Calculates the centre-of-wall area as:

   ```
   room area + (room perimeter x half wall thickness)
   ```

   Half wall thickness comes from `duHast_wall_thickness` on the mock room's type, halved.
   If that parameter is absent, **60 mm** is used.
4. Compares the calculated area against `duHast_area_designed_centre_wall` on the mock room:
   - within tolerance — the calculated value is written to
     **`duHast_area_by_revit_room`** on the mock room instance;
   - **below 80 %** of the designed area — `duHast_area_by_revit_room` is set to `0.0` and the
     discrepancy is reported as an error;
   - **above 105 %** of the designed area — `duHast_area_by_revit_room` is set to `0.0` and the
     discrepancy is reported.
5. Deletes all temporary Revit rooms it created.

A mock room whose temporary room comes back with an area of zero — usually because the
location is not enclosed — is reported and left unchanged.

## When to use this

Use this to check the mock room layout against the modelled geometry: after moving walls,
after adjusting mock room dimensions, or before issuing area figures. The
`duHast_area_by_revit_room` values it leaves behind can then be scheduled or exported
alongside the designed areas.

## Requirements

- The mock rooms must be in the **active model**. Unlike **Place Revit Rooms**, this tool does
  not offer a model picker and does not read from links.
- Mock room locations must be enclosed by walls, room separation lines or area boundaries,
  otherwise Revit cannot calculate an area.
- The mock room instances must carry `duHast_area_designed_centre_wall` — without it the tool
  reports that the parameter is missing and skips the update.
- `duHast_area_by_revit_room` must exist on the mock rooms to receive the result.

## Notes

- The temporary rooms are removed automatically, in a transaction named
  *"Push it rooms created by area verification"*. There is no manual cleanup step.
- A value of `0.0` in `duHast_area_by_revit_room` is a **flag, not a measurement** — it means
  the measured area fell outside the tolerance band, so check the surrounding geometry.
- The calculated area is measured to the centre of the enclosing walls, which is why the room
  perimeter and half wall thickness are added to Revit's room area. Comparing it to a
  clear-internal area will always show a difference.
- Progress and every calculation are printed to the pyRevit output window.
