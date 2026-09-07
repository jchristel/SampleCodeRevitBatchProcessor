# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

"""
The extraction side of an OPENING -- a door, a window, and whatever wall-hosted
category comes next.

One module rather than one per category, because measurement said so: a
full-depth diff of real duHast exports from two documents found a window record
and a door record structurally identical, and the four facts read here are read
the same way for both. `category` is the only argument that varies.

The examples in the comments below cite DOORS, deliberately. They are the cases
that decided each rule, and replacing a measured door figure with a vaguer
statement about openings would trade evidence for symmetry. Where windows differ
in degree rather than in kind it is said at the function concerned.
"""

import math

from room_m.utils.generic import (
    element_id_str,
    phase_by_name,
    elements_in_phase,
)

# The direct Revit API use in this module: the placement pass walks the chosen
# category with a raw collector, because the phase-indexed room references, the
# insertion point and the facing direction are all read off the live element
# rather than the export (see `opening_placements`).
from Autodesk.Revit.DB import (
    BuiltInCategory,
    FilteredElementCollector,
)

from room_m.utils.room_refs import (
    room_reference,
)

def opening_through_wall_normal(opening):
    """The unit vector through the wall, from the door's from-room toward its
    to-room, as `{"x", "y"}`, or None.

    `FamilyInstance.FacingOrientation`, projected to plan and normalised.

    **Facing, not the host wall's direction, and that is the whole point.**
    Revit's `ToRoom` follows the door's *orientation*; flipping a door in Revit
    swaps facing and `ToRoom` together, so the two are readings of one fact and
    cannot drift. Deriving the direction from the host wall would introduce a
    second source of truth that could disagree with the room references this
    same pass reads -- and therefore with the server's `owner_rooms`, which is
    computed from them.

    None when the facing has no plan component at all (a hatch in a floor: the
    vector points along Z, and its x/y are both ~0). Returned rather than
    normalised out of a zero-length vector, because the honest answer is that
    this door has no in-plan direction, and the contract says a consumer must
    then draw no arrow instead of guessing one."""
    facing = getattr(opening, "FacingOrientation", None)
    if facing is None:
        return None
    x = float(facing.X)
    y = float(facing.Y)
    length = math.sqrt(x * x + y * y)
    if length < 1e-9:
        return None
    return {"x": x / length, "y": y / length}


def opening_placements(doc, phase_name, category):
    """`{opening id: {"from_room", "to_room", "insertion_point", "normal"}}` for
    every instance of `category` in `doc`, read from the Revit API for the chosen
    phase.

    `category` is a `BuiltInCategory` -- `OST_Doors`, `OST_Windows`. It is the
    only thing that varies between entities here, which is the whole reason this
    is one function: `room_reference` was already written to take the property
    name as an argument for exactly this day.

    **One collector pass, four facts.** These were separate questions once and
    the room references came first; putting the placement reads here rather than
    in a second `FilteredElementCollector` walk is not micro-optimisation, it is
    what guarantees the four values describe the same door in the same phase.
    A second pass could silently disagree with this one about which elements it
    saw.

    **Read here rather than taken from the duHast export, deliberately.** The
    export carries `from_room`/`to_room` as arrays with one entry per phase,
    tagged with a `phase_id` that appears nowhere else in the file and cannot
    be resolved against anything on the wire - the blocker STRATEGY-ENTITIES
    records. `FromRoom[phase]` takes the phase and answers exactly one room, so
    asking Revit is both correct and simpler than reconciling an array against
    a phase table that is not there. It is also what makes the reference
    genuinely one-to-one, which is what the contract's `Option<String>` claims.

    A door whose room lookup raises is recorded as having neither reference
    rather than aborting the model: one unreadable door must not cost the other
    hundreds, and the server's QA reports it as a door with no room reference -
    visible, in the place a reader would look.

    **Each of the four is caught separately**, so an unreadable room reference
    costs the position and direction of that door and nothing more. Catching the
    whole door at once would have been shorter and would throw away three facts
    to lose one -- and the fact most likely to raise (the phase-indexed room
    lookup) is not the one a plan needs to draw the door."""
    phase = phase_by_name(doc, phase_name)
    placements = {}
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(category)
        .WhereElementIsNotElementType()
    )
    for opening in collector:
        try:
            from_room = room_reference(opening, phase, "FromRoom")
            to_room = room_reference(opening, phase, "ToRoom")
        except Exception:
            from_room, to_room = None, None

        try:
            insertion_point = opening_insertion_point(opening)
        except Exception:
            insertion_point = None

        try:
            normal = opening_through_wall_normal(opening)
        except Exception:
            normal = None

        placements[element_id_str(opening.Id)] = {
            "from_room": from_room,
            "to_room": to_room,
            "insertion_point": insertion_point,
            "normal": normal,
        }
    return placements


def openings_in_phase(doc, phase_name, category):
    """The ids of `category`'s instances in `phase_name`.

    The RANGE test, not the equality test rooms use. A door or a window is built
    in one phase and may be demolished in a later one, so it exists across a
    span; a room belongs to exactly one. Running an opening through the room
    predicate returns nothing, silently -- the failure that cost five empty
    pushes to find."""
    return elements_in_phase(doc, phase_name, category)


def opening_insertion_point(opening):
    """The door's plan position as `{"x", "y"}`, or None.

    Revit's `LocationPoint`, which a placed `FamilyInstance` has. Z is dropped:
    the contract's geometry is 2D plan space throughout, and the level already
    says which floor this is on.

    This is the field that keeps a *geometry-less* door on the drawing. Two of
    the 26 sample doors have no 3D geometry, so their footprint arrives empty
    (see `post_doors.loops_from_polygon`) and nothing else on the wire says
    where they are. Without this they exist in QA and in `/doors` but appear
    nowhere a reader looks at a plan, which reads as "there is no door there"
    rather than "its shape is unknown"."""
    location = getattr(opening, "Location", None)
    point = getattr(location, "Point", None) if location is not None else None
    if point is None:
        return None
    return {"x": float(point.X), "y": float(point.Y)}

def nested_opening_ids(doc, category):
    """The ids of instances that are a *component of another instance of the same
    category*, and so are not openings at all -- they are its leaves, panels,
    glazing and hardware.

    **Measured for both entities, and the scale differs enormously.** On a
    facade file: 113 of 205 collected doors were components (55%), against 6 of
    158 windows (3.8%). The doors were mostly hardware -- one handle family
    accounted for 58 of them. The six windows were all one family, literally
    named `088123_Glazing-ExteriorGlass-Nested`, all children of a single
    parent, and none carried a Mark or a room reference.

    So the filter matters far more for doors than for windows, and it is needed
    for both: 6 openings that name no room would otherwise land in the homeless
    pile and read as a modelling gap rather than as panes of glass.

    **This model family represents a door leaf as a nested shared family**, and
    a nested shared instance is a real, independently-collectable
    `FamilyInstance` carrying the Doors category of the family it was drawn
    from. `FilteredElementCollector.OfCategory(OST_Doors)` therefore returns the
    leaf alongside the door that contains it, and the export counted both.

    What that costs is not a tidy over-count. On the job this was written
    against, 2236 of 4134 exported "doors" were components: `PS`, `PS.V2X8`,
    `PS Aluminium`, and a pull handle typed `3/4" diameter x 10" H x 4" W`.
    **Not one of the 2236 carried a room reference**, and only 41 carried a
    `Mark` -- because a component has neither. They were the bulk of what the
    server then reported as homeless doors, which made a data artifact look
    like a modelling gap.

    **The test is the parent's category, not its family or name.** A door
    hosting a *window*-category or generic-model sub-component is a different
    statement about the model and is left alone; only "a door inside a door"
    means leaf. Compared against `opening.Category`, not against
    `BuiltInCategory.OST_Doors` converted to an int: the collector above has
    already fixed every element's category, so the door in hand IS the
    comparison value, and this avoids the enum-to-id conversion that
    `element_id_str` exists to keep version-proof.

    **Only the immediate `SuperComponent` is tested**, matching Revit's own
    one-step relationship. A leaf nested two deep inside an intermediate
    component that is NOT a door would survive; no such arrangement exists in
    the model this was measured on. Walking `SuperComponent` to the root would
    be a loop here rather than a redesign, if one ever turns up.

    Returned as its own set rather than subtracted from `openings_in_phase`'s,
    deliberately: the two answer different questions, and an empty push has to
    be able to say which of them emptied it. Folding them together would report
    a leaf as "outside phase" in the one message written to stop a reader
    hunting the wrong thing."""
    nested = set()
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(category)
        .WhereElementIsNotElementType()
    )
    for opening in collector:
        parent = getattr(opening, "SuperComponent", None)
        if parent is None:
            continue  # a standalone door, which is the ordinary case
        parent_category = getattr(parent, "Category", None)
        own_category = getattr(opening, "Category", None)
        if parent_category is None or own_category is None:
            continue  # nothing to compare: keep it, absence is not evidence
        if element_id_str(parent_category.Id) == element_id_str(own_category.Id):
            nested.add(element_id_str(opening.Id))
    return nested
