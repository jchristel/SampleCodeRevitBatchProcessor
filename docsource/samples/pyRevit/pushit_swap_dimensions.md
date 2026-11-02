# Swap Width And Depth

**Panel:** PushIt | **Button:** Swap Width And Depth

<img src="Extensions/duHast-2025.extension/duHast.tab/PushIt.panel/SwapWidthAndDepth.pushbutton/Icon.png" width="40" alt="button icon">

Swaps the width and depth values on picked mock rooms **and rotates them 90 degrees**, so the
room keeps its footprint but changes orientation.

## What it does

1. Starts a pick prompt — *"Select push it rooms"* — filtered to the **Walls** and **Columns**
   categories, which is how mock rooms are modelled.
2. For each picked element, in a cancellable progress bar:
   - reads `duHast_width` and `duHast_depth`;
   - writes each value into the other parameter;
   - **rotates the element 90 degrees about its origin**.

The rotation is the point of the tool: swapping the two dimensions alone would leave the
geometry facing the wrong way, so the element is turned to match.

## When to use this

Use this when a mock room has the right area but its width and depth are the wrong way round
relative to the room data — the long side runs the wrong way.

## Requirements

- The mock rooms must carry instance parameters named exactly **`duHast_width`** and
  **`duHast_depth`**. An element missing either is reported as *"One of the parameters does
  not exist on the selected element. Ignoring pairing"* and left alone.
- The elements must be of category **Walls** or **Columns**; nothing else can be picked.
- **The element's origin must be at its centre**, defined by reference planes. The rotation is
  about the origin, so an off-centre origin moves the mock room as well as turning it.

## Notes

- Selection happens after launching the tool, through the pick prompt. Pre-selecting in the
  canvas is not required.
- If either parameter fails to set, the rotation is skipped for that element so the geometry
  and the values do not fall out of step.
- Each element's before and after values are printed to the output window.
