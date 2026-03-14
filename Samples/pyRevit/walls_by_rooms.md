# Walls By Rooms

**Panel:** Walls | **Button:** Walls By Rooms

Generates wall elements along the boundaries of existing rooms in the current Revit model.

## What it does

- Reads all rooms in the active model.
- For each room boundary segment that does not already have a wall, places a wall of the configured type along that segment.
- Walls are placed at the room's level and extend to the configured height.

## When to use this

Use this button when you want to convert a room-based layout (defined using room separation lines or boundaries) into actual wall geometry — for example, when transitioning from a schematic layout to a more detailed design.

## Requirements

- Rooms must have valid closed boundaries.
- A wall type must be selected or configured before running.

## Notes

- Segments that already have a wall may result in duplicate walls; review the model after running and delete any unintended duplicates.
- The tool creates wall elements as a starting point; wall joins, offsets, and heights may need to be adjusted manually for detailed design.
