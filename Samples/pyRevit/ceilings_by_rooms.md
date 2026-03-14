# Ceilings By Rooms

**Panel:** Ceilings | **Button:** Ceilings By Rooms

Automatically generates ceiling elements for every room in the current Revit model, using each room's boundary as the ceiling boundary.

## What it does

- Reads all rooms in the active model.
- For each room, creates a ceiling element at the level of the room, matching the room's boundary polygon.
- Uses a configurable ceiling type and height offset.

## When to use this

Use this button at the start of a ceiling design phase when you need a base set of ceilings to match the room layout, saving you from drawing each ceiling boundary manually.

## Requirements

- Rooms must have valid boundaries (closed perimeters) for Revit to calculate the ceiling shape correctly.
- At least one ceiling type must exist in the project before running the tool.

## Notes

- The tool creates ceilings at a default height; adjust individual ceiling heights afterwards if required.
- Rooms without valid boundaries are skipped and reported in the pyRevit output window.
- Run after the room layout is finalised to avoid having to regenerate ceilings after room boundary changes.
