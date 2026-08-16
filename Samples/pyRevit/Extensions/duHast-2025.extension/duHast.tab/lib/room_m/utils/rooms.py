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

from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

from room_m.utils.generic import (
    element_id_str,
    document_phases,
)

# The direct Revit API use in this module: a room's phase is named by the
# ROOM_PHASE built-in parameter, which the duHast room export does not carry.
from Autodesk.Revit.DB import BuiltInParameter

def rooms_in_phase(doc, phase_name):
    """The room ids in `phase_name`.

    **Rooms do NOT go through `exists_in_phase`, and that is the one thing to
    understand here.** The design assumed one predicate could serve every
    entity, because `CreatedPhaseId`/`DemolishedPhaseId` are `Element` members.
    Against a real document that produced *zero* rooms, five pushes running --
    exactly the "the filter silently keeps nothing" failure the plan named as
    the first thing to check.

    A room is not a thing that is built in one phase and demolished in another.
    It BELONGS to exactly one phase, named by the `ROOM_PHASE` built-in
    parameter, so membership is an equality test rather than a range test over
    the phase sequence. Doors keep the range test
    (`room_m.utils.doors.doors_in_phase`), and that difference is real rather
    than an inconsistency worth tidying away.

    Returns a `set`: `post_rooms.in_selected_phase` does one membership test per
    room, so a list makes filtering a plate quadratic."""
    order_by_name = dict((p["name"], i) for i, p in enumerate(document_phases(doc)))
    if phase_name not in order_by_name:
        # Fail loudly, on the same terms as
        # `room_m.utils.generic.elements_in_phase`. Without this a
        # mistyped or renamed phase yields an empty set, which is indexed,
        # stored and served as "this model has no rooms" -- and that is not a
        # hypothetical: it is what the five empty snapshots above looked like
        # from the outside.
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(order_by_name.keys())
            )
        )

    allowed = set()
    for room in get_all_rooms(doc):
        room_phase = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                room,
                BuiltInParameter.ROOM_PHASE,
                rParaGet.get_parameter_value_as_element_id,
            ),
        )
        if room_phase == phase_name:
            allowed.add(element_id_str(room.Id))
    return allowed
