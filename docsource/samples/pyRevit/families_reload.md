# Reload Families

**Panel:** Families | **Button:** Reload

Reload one or more families from a library directory into the current Revit project. The tool matches families by name and presents a filterable table showing how each loaded family maps to files found in the library.

## What it does

- Scans a user-selected library directory (including subdirectories) for `.rfa` files whose names match families currently loaded in the project.
- Displays a table of all loaded families with a match status column:
  - **ok** â€” exactly one matching file found in the library; family is eligible for reload.
  - **multiple matches found** â€” more than one file with the same name exists; the family cannot be safely reloaded automatically.
  - **no match** â€” no file with this name was found in the library.
- Reloads all families marked **ok**, overwriting parameter values and using shared subcomponents where applicable.

## Requirements

- A library directory containing `.rfa` files accessible from your workstation.
- The library path can be changed within the tool's UI before reloading.

## Notes

- Only families with a single unambiguous match are reloaded; duplicates must be resolved in the library before reloading.
- The table is sortable and filterable so you can focus on a subset of families.
