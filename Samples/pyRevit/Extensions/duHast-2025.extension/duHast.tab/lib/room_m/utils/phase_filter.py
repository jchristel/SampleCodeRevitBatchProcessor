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
The wire side of the phase filter: does a translated entity survive it.

The *predicate* is not here and cannot be. Deciding whether an element exists in
a phase needs the document's phase ordering, which only the live Revit model
has, so it runs during extraction -- `room_m.utils.rooms.rooms_in_phase` for
rooms (an equality test on `ROOM_PHASE`) and
`room_m.utils.generic.elements_in_phase` for doors (a range test over the phase
sequence). Each hands down a set of ids, and what is left for the push side is a
membership test on ids it can already read.

**Deliberately imports nothing Revit-facing**, unlike its siblings in this
folder. That is the property that lets `post_rooms` and `post_doors` import it
without pulling the Revit assembly into the contract layer -- which they rely on
being free of, so `translate()` can regenerate the dev fixtures. It is also why
this is its own module rather than a function in `utils.generic`, which owns the
other two phase predicates but imports `Autodesk.Revit.DB` to do it.

One implementation for every entity: rooms and doors asked the same question of
the same shape and answered it with the same two lines, and windows and FF&E
would each have added another copy.
"""


def in_selected_phase(out_entity, allowed_ids):
    """Whether a translated entity survives the phase filter.

    `out_entity` is an already-translated contract dict -- anything carrying an
    `"id"` -- and `allowed_ids` the set handed down by the extraction side.
    `None` means no filter was supplied and everything passes, which is what the
    buffered paths use when a caller asks for an unfiltered translation."""
    if allowed_ids is None:
        return True
    return out_entity["id"] in allowed_ids
