# Facade Opening to Room

**Panel:** Walls | **Button:** Facade Opening to Room

Creates Revit room elements derived from facade opening geometry, allowing facade openings to define room boundaries for area and space calculations.

## What it does

- Reads selected facade opening elements (such as curtain wall openings or void cuts) from the model.
- Creates room boundary geometry at the corresponding floor levels based on the opening shapes.
- Places Revit room elements within those boundaries.

## When to use this

Use this button in projects where the architectural brief defines spaces by their facade opening dimensions rather than internal wall arrangements — for example, in façade-driven residential or hospitality layouts where each unit is defined by its facade module.

## Notes

- The facade openings must be modelled as Revit elements before running this tool.
- Resulting rooms may need parameter data populated via PushIt or manually.
- Review room boundaries after creation to confirm they align with the intended space definitions.
