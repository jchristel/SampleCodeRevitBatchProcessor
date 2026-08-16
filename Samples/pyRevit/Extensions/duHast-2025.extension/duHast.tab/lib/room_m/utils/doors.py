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

import math

from room_m.utils.generic import (
    element_id_str,
    phase_by_name,
    elements_in_phase,
)

# The direct Revit API use in this module: the placement pass walks doors with a
# raw collector, because the phase-indexed room references, the insertion point
# and the facing direction are all read off the live element rather than the
# export (see `door_placements`).
from Autodesk.Revit.DB import (
    BuiltInCategory,
    FilteredElementCollector,
)

from room_m.utils.room_refs import (
    room_reference,
)

def door_through_wall_normal(door):
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
    facing = getattr(door, "FacingOrientation", None)
    if facing is None:
        return None
    x = float(facing.X)
    y = float(facing.Y)
    length = math.sqrt(x * x + y * y)
    if length < 1e-9:
        return None
    return {"x": x / length, "y": y / length}


def door_placements(doc, phase_name):
    """`{door id: {"from_room", "to_room", "insertion_point", "normal"}}` for
    every door in `doc`, read from the Revit API for the chosen phase.

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
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
    )
    for door in collector:
        try:
            from_room = room_reference(door, phase, "FromRoom")
            to_room = room_reference(door, phase, "ToRoom")
        except Exception:
            from_room, to_room = None, None

        try:
            insertion_point = door_insertion_point(door)
        except Exception:
            insertion_point = None

        try:
            normal = door_through_wall_normal(door)
        except Exception:
            normal = None

        placements[element_id_str(door.Id)] = {
            "from_room": from_room,
            "to_room": to_room,
            "insertion_point": insertion_point,
            "normal": normal,
        }
    return placements


def doors_in_phase(doc, phase_name):
    """The door ids in `phase_name`."""
    return elements_in_phase(doc, phase_name, BuiltInCategory.OST_Doors)


def door_insertion_point(door):
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
    location = getattr(door, "Location", None)
    point = getattr(location, "Point", None) if location is not None else None
    if point is None:
        return None
    return {"x": float(point.X), "y": float(point.Y)}