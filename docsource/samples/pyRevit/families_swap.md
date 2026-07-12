# Swap Families

**Panel:** Families | **Menu:** Rename > Swap (also accessible as SwapFamilies)

Tools to replace instances of one family type with instances of another family type within the current Revit project.

---

## Swap By Directives

Swaps family instances based on a CSV file containing explicit swap instructions.

**CSV input:** A mapping of source family/type to target family/type. Each row defines one substitution rule.

- Processes all eligible instances in the project matching the source type.
- Reports any instances inside groups or as nested families that cannot be swapped automatically.

**Use when:** You have a predefined list of substitutions to apply across a project, for example when updating a design from concept families to construction-issue families.

---

## Swap By User Selection List

Swaps family instances using an interactive selection workflow.

1. A dialog presents a list of family types loaded in the project; select the **source** type to replace.
2. A second dialog presents available types; select the **target** type to use instead.
3. All eligible instances of the source type are replaced with the target type.

Instances inside groups or nested families are reported but not swapped.

---

## Swap By User Selection Pick

Similar to **Swap By User Selection List** but uses a pick-in-canvas interaction to identify the source instance before presenting the target type list.

---

## Notes

- Nested families and families inside groups cannot be swapped automatically; resolve those manually.
- Instance parameters are preserved where the parameter exists on the target type; type parameters are taken from the target type.
