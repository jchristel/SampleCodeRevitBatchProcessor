# Swap Width and Depth

**Panel:** PushIt | **Button:** Swap Width and Depth

Swaps the width and depth instance parameter values on selected mock room family instances.

## What it does

- Takes the current **Width** parameter value and assigns it to **Depth**, and vice versa.
- Operates on all selected mock room family instances in one step.
- The family geometry updates immediately to reflect the swapped dimensions.

## When to use this

Use this button when a mock room has been placed with the correct footprint area but its orientation is 90° off from what the room data expects — swapping width and depth corrects the dimensional assignment without moving or recreating the family.

## Notes

- Select one or more mock room family instances in the canvas before running the tool.
- Only instance parameters named **Width** and **Depth** are affected; other parameters are unchanged.
- If the family uses different parameter names for these dimensions, the tool may not produce the expected result.
