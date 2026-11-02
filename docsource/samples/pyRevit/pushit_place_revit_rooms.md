# Place Revit Rooms

**Panel:** PushIt | **Button:** Place Revit Rooms

<img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/PlaceRevitRooms.pushbutton/Icon.png" width="40" alt="button icon">

Creates native Revit rooms at the locations of mock rooms, copying the mock room data into
them. The mock rooms can live in the current model **or in a Revit link**.

## What it does

1. **Select the source model** — a document picker offers the active document and every loaded
   Revit link. Choose the one holding the mock rooms.
2. **Select the mock rooms** to convert, from a multi-select list.
3. **Select the model insertion method**:
   - **Origin to Origin** — no transform is applied;
   - **By Shared Coordinates** — the source model's translation and rotation are read and
     applied, so the rooms land in the right place.

   This only matters when the mock rooms come from a link. Choose the option matching how the
   link was inserted, or the rooms will be placed in the wrong location.
4. Rooms are created in the **current** model at each mock room's centroid, and the mapped
   parameter values are transferred.

Mock rooms whose centroid cannot be determined are **dropped before placement**, with a count
reported. If none of the selected rooms yields a centroid the tool stops.

## Parameter transfer

Mock room `duHast_*` parameters are mapped onto the equivalent Revit room built-in
parameters, including:

| Mock room parameter | Revit room parameter |
|---|---|
| `duHast_room_number` | Room Number |
| `duHast_room_name` | Room Name |
| `duHast_department_name` | Department |

A room can be created successfully and still fail to receive every parameter value; the
output window reports both counts separately.

## When to use this

Use this when you need native Revit rooms — for area schedules, room tags, or anything that
requires the built-in room element — while continuing to use mock rooms as the design layout
tool.

## Requirements

- Revit rooms need enclosed boundaries to calculate an area. Walls, room separation lines or
  area boundaries must exist at the mock room locations in the **current** model.
- The PushIt data source and unique-ID parameter must be configured; the tool exits with a
  message if either cannot be read.
- When reading from a link, that link must be loaded.

## Notes

- Existing rooms are not detected. Running twice over the same locations creates duplicates —
  check the model afterwards.
- Run [Verify Push It Area](pushit_area_by_room.md) afterwards to check the placed geometry
  against the mock room areas.
