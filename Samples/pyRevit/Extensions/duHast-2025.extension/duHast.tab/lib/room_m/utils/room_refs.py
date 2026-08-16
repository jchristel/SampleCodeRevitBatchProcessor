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
Which ROOM does an element point at, in a given phase.

Its own module rather than part of `room_m.utils.rooms`, because it answers a
different question. `rooms.py` extracts rooms as *entities* -- which rooms exist,
and in which phase. This answers, for some other element, which room it is
associated with. Every entity that hangs off a room needs the second question and
none of them need the first, so keeping them apart is what stops `doors.py`
(and, later, `windows.py` and `ffe.py`) from importing the room extractor to
reach one helper.

Nothing Revit-specific is imported here: the phase-indexed properties are
reached by name off whatever instance the caller passes, which is also what makes
one function serve every category.
"""

from room_m.utils.generic import element_id_str


def room_reference(instance, phase, which):
    """One of `instance`'s room references for `phase`, as an id string, or None.

    `which` is the property name -- `"FromRoom"` or `"ToRoom"` for the wall-hosted
    categories (doors, windows), and `"Room"` for an instance that sits *in* one
    room rather than between two (FF&E). The property name is the only thing that
    varies between them, which is why this takes it as an argument instead of
    being written once per category.

    Each of those exists both as a parameterless property (which uses the
    document's *current* phase - not what we want) and as a phase-indexed one.
    IronPython reaches the indexed form through the CLR's `get_` accessor;
    `instance.FromRoom[phase]` binds to the parameterless value first on some
    versions, so the accessor is tried first and the indexer is the fallback.
    Same both-names-are-real discipline as
    `room_m.utils.generic.element_id_str`.

    An element with no room on that side is a normal state (an external door), so
    None here is data, not a failure."""
    accessor = getattr(instance, "get_" + which, None)
    room = accessor(phase) if accessor is not None else getattr(instance, which)[phase]
    return element_id_str(room.Id) if room is not None else None
