# Facade Opening To Room

**Panel:** Walls | **Button:** Facade Opening To Room

<img src="Extensions/duHast-2025.extension/duHast.tab/Walls.panel/FacadeOpeningToRoom.pushbutton/Icon.png" width="40" alt="button icon">

Reports the external wall area and the external window opening area for each selected room,
and writes the result to a CSV file. Nothing is created or modified in the model.

## What it does

1. Lists every room in the model and asks you to select the rooms to report on. List entries
   are shown as `number-name_phase_level`.
2. Collects all window opening family instances in the model that belong to one of the
   configured opening families, grouped by the wall hosting them.
3. Works out the boundary segments of each selected room and which wall forms each segment.
4. Keeps only the walls whose **type name** appears in the configured external wall type
   list. Rooms with no such wall are reported as having no match and produce no rows.
5. For each qualifying wall, keeps only the openings that belong to the room — the opening's
   room, `ToRoom` or `FromRoom` in the configured phase must be the room being reported.
6. Calculates the external wall area as `wall segment length x room height` and the combined
   window area from the opening families.
7. Asks for a save location and writes a CSV.

### Report columns

```
room name, room number, room area (sqm), external wall area (sqm),
external window area combined (sqm), room level, room phase, room height (mm),
external wall type name, external window fam name(s)
```

A room with a qualifying external wall but no openings still produces a row, with
`0.0` for the window area and `No window families in room` for the family names.

## When to use this

Use this to produce a facade-to-room area summary — glazing ratios per room, external
envelope area per room, or a check that the modelled openings match the brief.

## Configuration — read this first

The tool is driven by three hard-coded lists in
`Extensions/duHast-2025.extension/duHast.tab/lib/rooms/rooms_facade_openings.py`. They are
project-specific, and if they do not match your model the tool runs to completion and
reports nothing.

| Constant | Purpose | Current value |
|---|---|---|
| `PHASE_NAME` | Phase used to resolve an opening's room | `"Project Scope"` |
| `EXTERNAL_WALL_TYPE_NAMES` | Wall types treated as external | `["P43.E_(125)_PB13_S92 (Insulation) - External Lining"]` |
| `OPENING_FAMILY_NAMEs` | Window opening families to measure | `["WDW_Generic_Window Opening", "WDW_Generic_Window Opening_Instance"]` |

`WINDOW_AREA_CALCULATION_MAPPER` in the same file maps each opening family to the routine
that measures it — one reads the area from the type, the other from the instance. A new
opening family needs an entry in both `OPENING_FAMILY_NAMEs` and the mapper.

## Requirements

- Rooms must be placed and bounded.
- Rooms must have a height value — the external wall area is derived from it.
- The wall types and opening families named above must exist in the model.

## Notes

- Set `DEBUG = True` in the module for a verbose run — selected rooms, every opening found,
  and each wall area calculation are then printed to the output window. Useful when the report
  comes back empty and you need to see which of the three constants is not matching.
- The wall area is a simple `length x height` rectangle. It is not reduced by the openings,
  and it does not account for parapets, spandrels or sloping soffits.
- Room area and height are read in project units and written to the CSV as-is; the column
  headings assume a metric project.
