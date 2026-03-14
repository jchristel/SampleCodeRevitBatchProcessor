# Place Revit Rooms

**Panel:** PushIt | **Button:** Place Revit Rooms

Creates native Revit rooms at the locations of existing mock room family instances, using the mock room data to populate room properties.

## What it does

- Reads each mock room family instance's position, boundary, and parameter data.
- Places a native Revit room element at the corresponding location in the model.
- Copies relevant parameter values (room name, number, department, etc.) from the mock room into the Revit room.

## When to use this

Use this button when you need native Revit rooms for area scheduling, room tagging, or other workflows that require the built-in Revit room type — while keeping the mock rooms as the primary design layout tool.

## Notes

- Revit rooms require a closed boundary to calculate area correctly; ensure the mock room locations have valid room boundaries (walls, room separation lines, or area boundaries).
- If a room already exists at a mock room's location, a duplicate may be created — review the model after running.
- Run **Area By Room** after this tool to verify that the placed Revit rooms match the expected areas from the mock room data.
