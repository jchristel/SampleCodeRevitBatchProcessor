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

"""What the duHast space export does not carry: which phase each space belongs
to, which spaces are unplaced, and which enclose nothing.

All three are read straight from Revit, which is the rule the door work left
behind -- ask Revit for what the export omits, never re-derive what it already
holds. The footprint is duHast's and is not touched here.
"""

from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

from room_m.utils.generic import (
    element_id_str,
    document_phases,
)

# The direct Revit API use in this module. `BuiltInCategory` because the
# collector is ours rather than duHast's (see `collect_spaces`), and
# `BuiltInParameter` because a space's phase is named by ROOM_PHASE -- which the
# duHast space export does not carry, exactly as it does not for a room.
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, FilteredElementCollector


def collect_spaces(doc):
    """Every space in the document.

    **Deliberately not duHast's `get_all_spaces`, and this is not tidiness.**
    That function catches every exception and returns `[]`, so "this model has no
    spaces" and "the collector raised" are the same answer -- in the one place
    the whole entity's first requirement rests on. An empty spaces push is a
    legitimate, *reportable* state here (the server accepts one on purpose), so a
    swallowed failure would not surface as an error anywhere: it would be stored
    and read as a finding.

    Collecting here instead means a failure raises, `export_model` catches it and
    the model goes red. It also gives `exporters.spaces` a count to check the
    export against, which is the second half of the same guard.
    """
    return list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MEPSpaces).ToElements())


def spaces_in_phase(doc, phase_name, spaces):
    """The space ids in `phase_name`.

    **Spaces take the ROOMS equality test, not the openings range test**, and the
    reason is the one `room_m.utils.rooms.rooms_in_phase` records: a space, like
    a room, BELONGS to exactly one phase, named by `ROOM_PHASE`. It is not built
    in one phase and demolished in a later one the way a door is. Running spaces
    through `elements_in_phase` returns nothing, silently -- the failure that
    cost five empty pushes to find.

    A near-copy of `rooms_in_phase` rather than a shared function taking a
    collector, on the terms `windows.rs` sets for `doors.rs`: the duplication is
    a twenty-line loop the compiler cannot check either way, and the alternative
    was adding a parameter to a function whose whole point is that rooms are the
    equality case. The elements are passed in because `collect_spaces` has
    already walked the document once and there is no reason to walk it twice.

    Returns a `set`: `in_selected_phase` does one membership test per space.
    """
    order_by_name = dict((p["name"], i) for i, p in enumerate(document_phases(doc)))
    if phase_name not in order_by_name:
        # Fail loudly, exactly as the rooms filter does. Without this a mistyped
        # or renamed phase yields an empty set, which is stored and served as
        # "this model has no spaces" -- and for THIS entity that reads as a
        # finding rather than as an error, which makes the silence worse here
        # than anywhere else it has already cost us.
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(order_by_name.keys())
            )
        )

    allowed = set()
    for space in spaces:
        space_phase = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                space,
                BuiltInParameter.ROOM_PHASE,
                rParaGet.get_parameter_value_as_element_id,
            ),
        )
        if space_phase == phase_name:
            allowed.add(element_id_str(space.Id))
    return allowed


def placement_facts(spaces):
    """Which spaces are unplaced, and which enclose nothing.

    **Enclosure is decided from `Area`, never from `GetBoundarySegments`**, and
    that is a measurement rather than a preference. On RHH, 96.3% of spaces
    reported *zero* boundary segments while exporting a perfectly good polygon:
    their bounding elements live in the linked architectural model, so Revit
    reports no segments and duHast measures the solid instead. A segment count is
    therefore not evidence of anything in a services model. `Area` is, and
    `Perimeter` is not either -- it exports as `0.0` for the same reason.

    Two sets rather than one classification, because the third state cannot be
    decided here: whether a placed, non-zero-area space is `unmeasured` depends
    on what duHast produced for it, which only the translation sees. This
    supplies the two facts the export lacks and lets `translate_space` combine
    them.

    :return: `(unplaced_ids, zero_area_ids)`
    :rtype: (set, set)
    """
    unplaced = set()
    zero_area = set()
    for space in spaces:
        space_id = element_id_str(space.Id)
        try:
            placed = space.Location is not None
        except Exception:
            # An element whose Location cannot be read is not evidence of being
            # unplaced; treating it as placed keeps it on the wire, where its
            # missing geometry is reported rather than silently dropped.
            placed = True
        if not placed:
            unplaced.add(space_id)
            continue
        try:
            if float(space.Area) <= 0.0:
                zero_area.add(space_id)
        except Exception:
            pass
    return unplaced, zero_area
