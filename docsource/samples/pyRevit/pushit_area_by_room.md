# Area By Room

**Panel:** PushIt | **Button:** Area By Room

Places temporary Revit rooms alongside mock room family instances and compares the calculated Revit room area against the area stored in the mock room data, as a verification step.

## What it does

- For each mock room, places a reference Revit room at the same location.
- Compares the area calculated by Revit (from the actual model boundaries) with the target area recorded in the mock room's parameter data.
- Reports any discrepancies between the two values.

## When to use this

Use this button to verify that the mock room layout is achieving the intended areas â€” for example, after adjusting wall positions or room boundaries. It is a QA step rather than a permanent modelling operation.

## Notes

- The reference Revit rooms placed by this tool are intended to be temporary; delete them after reviewing the area comparison report.
- Discrepancies between mock room area and calculated room area typically indicate that the surrounding boundary geometry (walls, separation lines) does not match the mock room dimensions.
- Ensure the model is synced and up to date before running so that Revit's area calculations are based on the latest geometry.
