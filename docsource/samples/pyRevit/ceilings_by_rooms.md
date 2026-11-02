# Ceilings By Room

**Panel:** Ceilings | **Button:** Ceilings By Room

<img src="Extensions/duHast-2025.extension/duHast.tab/Ceilings.panel/CeilingsByRooms.pushbutton/Icon.png" width="40" alt="button icon">

Creates a ceiling matching the boundary of each selected room.

## What it does

1. Lists every room in the model and asks you to select the rooms to model ceilings for.
   List entries are shown as `number-name_phase_level`.
2. For each selected room, in a cancellable progress bar:
   - resolves the ceiling type to use (see below);
   - takes the room's boundary at the **finish** face and converts it to closed curve loops;
   - creates a ceiling on the room's level from those loops.

## How the ceiling type is chosen

1. The room's **`Ceiling Finish`** parameter is read.
2. Its value is matched against the type mark of the ceiling types in the model.
3. If there is no value, or no type matches it, the tool falls back to a default type — which
   is whichever ceiling type happens to be **second** in the collector. This is arbitrary,
   so check the result when the fallback is used; the type actually used is reported per room
   in the output window.

## Hard-coded values

Two values are fixed in
`Extensions/duHast-2025.extension/duHast.tab/lib/rooms/ceilings_create.py` and are not
exposed in the UI:

| Constant | Purpose | Current value |
|---|---|---|
| `PHASE_NAME` | Phase the ceilings are created in | `"Project Scope"` |
| (elevation argument) | Height offset from the room's level | `2700` |

The parameter the ceiling type code is read from is also fixed:
`ROOM_CEILING_TYPE_PARAMETER_NAME = "Ceiling Finish"`.

Edit these to suit the project before first use.

## When to use this

Use it at the start of a ceiling design phase to get a base set of ceilings matching the room
layout, rather than tracing each boundary by hand.

## Requirements

- Rooms must be placed and bounded so Revit returns closed boundary loops.
- At least one ceiling type must exist in the project.
- A phase named as per `PHASE_NAME` must exist, otherwise the ceiling is created without a
  phase set.

## Notes

- Rooms whose boundary cannot be converted to a closed loop are reported and skipped.
- All ceilings are created at the same offset; adjust individual heights afterwards.
- Run after the room layout is settled — the ceilings are not associative, so later room
  boundary changes will not update them.
