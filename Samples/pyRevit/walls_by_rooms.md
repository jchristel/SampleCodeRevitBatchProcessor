# Walls By Room

**Panel:** Walls | **Button:** Walls By Room

<img src="Extensions/duHast-2025.extension/duHast.tab/Walls.panel/WallsByRooms.pushbutton/Icon.png" width="40" alt="button icon">

Writes the room number of a room into a parameter on the walls bounding that room. Nothing
is created or moved — this tool only sets parameter values on existing walls.

## What it does

1. Lists every room in the model and asks you to select the rooms to process. List entries
   are shown as `number-name_phase_level`.
2. Asks you to select **one** parameter available on walls. This is the parameter that will
   receive the room number. Entries are shown as `parameter name (element id)`.
3. Works out the boundary segments of each selected room and which wall forms each segment.
4. For every wall found, writes the number of the room it bounds by its **longest** shared
   boundary segment into the selected parameter.

A wall that bounds several rooms therefore ends up carrying the number of the room it
shares the most boundary length with — one wall gets one room number, not a list.

## When to use this

Use this when you need walls to know which room they belong to: for wall schedules and
finishes take-offs, for filters or view templates driven by room number, or as a
preparation step for downstream reporting that groups walls by room.

## Requirements

- The rooms must be placed and bounded so Revit can return boundary segments for them.
- A **writable text parameter on walls** must exist before running — a project parameter or
  shared parameter bound to the Walls category. The tool only offers parameters it finds on
  walls; it does not create one for you.

## Notes

- Selection happens inside the tool. There is no need to pre-select anything in the model.
- Progress is shown in a cancellable progress bar; results are printed to the pyRevit output
  window.
- Re-running the tool overwrites any value previously written into the chosen parameter.
- Because the assignment is by longest segment, a wall shared roughly equally between two
  rooms will be assigned to whichever room wins by a small margin. Review those cases if the
  result matters.
