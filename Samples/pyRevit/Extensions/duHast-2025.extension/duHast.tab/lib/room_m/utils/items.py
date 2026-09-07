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
The extraction side of an FF&E ITEM -- what Revit knows that the duHast export
does not carry.

**Deliberately shorter than `room_m.utils.openings`, and the difference is the
point.** An opening pass reads four facts from Revit -- both room references,
the insertion point and the facing -- because the export's own room references
are unusable and its placement had to agree with them. An item pass reads two,
and only one of them is really from Revit:

- the **room**, for the run's single phase, because the export's `rooms` field
  is a list unioned across every phase with nothing saying which entry belongs
  to which, and its third fallback is a geometric lookup computed producer-side
  where the server can no longer report it as derived;
- the **category**, because `DataItem` has no field for it at all -- despite
  `get_all_item_data` walking nine categories and discarding which one each
  instance came from.

Everything else an item needs is in the export and is read from there:
position, rotation, level, type, both property tiers, and (once upstream change
U1 ships) the footprint. That is the standing rule from the door work -- an
extractor that re-measures what the export already carries silently discards
whatever the producer sent, which is exactly how a correct duHast fix produced a
byte-identical bad export.

**There is no nested-component filter here, and its absence is a decision.**
`room_m.utils.openings.nested_opening_ids` drops a door leaf at the producer and
is right to: "is this door leaf a door" has one answer, always. "Is this
component an item" does not -- a joinery handle is not, a chair nested in a
workstation group might be -- so it is a project convention, and it lives in the
server's `[ffe] nested_components`, applied at read time where it can be changed
after the fact and where the count of what it removed is reported. See
`docs/Superseded/PLAN-ffe.md` D10.

The measurement behind that: on House A, 179 of 647 instances had a
super-component, and the same-category test doors use would have caught 10 of
them -- an item's parent is usually in a DIFFERENT category (87 furniture
components of casework, 70 generic models inside electrical fixtures). Nor does
the doors discriminator transfer: 97.8% of those components named a room, where
a nested door component named none.

ASCII only, and no em-dashes: IronPython 2.7 will not parse a file containing
one, not even inside a docstring.
"""

from room_m.utils.generic import (
    element_id_str,
    elements_in_phase,
    phase_by_name,
)

# The direct Revit API use in this module: one collector pass per category,
# because the room reference is phase-indexed and the category is not in the
# export at all.
from Autodesk.Revit.DB import (
    ElementCategoryFilter,
    FamilyInstance,
    FilteredElementCollector,
)

from room_m.utils.room_refs import (
    room_reference,
)


def items_in_phase(doc, phase_name, categories):
    """The ids of every instance of `categories` that exists in `phase_name`.

    The RANGE test, not the equality test rooms use -- an item is placed in one
    phase and may be demolished in a later one, so it exists across a span, the
    same shape a door or a window has. Running items through the room predicate
    would return nothing, silently, which is the failure that cost five empty
    pushes to find and is written down here for the fourth time rather than
    assumed to be common knowledge.

    Unioned across nine categories where an opening filters one, which is the
    only structural difference. `elements_in_phase` raises on an unknown phase
    name, and that guard is the one thing standing between a typo and another
    empty snapshot -- so it is called per category rather than guarded once and
    bypassed."""
    allowed = set()
    for category in categories:
        allowed |= elements_in_phase(doc, phase_name, category)
    return allowed


def item_facts(doc, phase_name, categories):
    """`{item id: {"room", "category"}}` for every instance of `categories`.

    **One collector pass per category, two facts.** They are gathered together
    rather than in two passes for the reason `opening_placements` gives: a
    second walk could silently disagree with this one about which elements it
    saw, and then the category and the room would describe different sets.

    The room is read through the extractor's own `room_reference` with
    `which="Room"` -- the argument that helper has carried since before this
    entity existed, added for exactly this day. `FamilyInstance.get_Room(phase)`
    takes the phase and answers exactly one room, which is what makes the
    contract's single `Option<String>` honest.

    An item whose room lookup raises is recorded with no room rather than
    aborting the model: one unreadable instance must not cost the other
    hundreds, and the server reports it as an item with no room reference --
    visible, in the place a reader would look. An item with no room at all is
    ordinary rather than exceptional; measured on House A, 572 of 647 named one
    in the pushed phase and every one of the rest is a real item.

    The category is `instance.Category.Name` rather than the `BuiltInCategory`
    the collector was given, because they are not the same string and the one a
    reader recognises is the one Revit shows: `"Furniture"`, not
    `"OST_Furniture"`. What goes on the wire is what a `?category=` filter will
    be written against."""
    phase = phase_by_name(doc, phase_name)
    facts = {}
    for category in categories:
        collector = (
            FilteredElementCollector(doc)
            .OfClass(FamilyInstance)
            .WherePasses(ElementCategoryFilter(category))
        )
        for instance in collector:
            try:
                item_id = element_id_str(instance.Id)
            except Exception:
                continue

            room = None
            try:
                room = room_reference(instance, phase, "Room")
            except Exception:
                room = None

            name = None
            try:
                own = getattr(instance, "Category", None)
                name = own.Name if own is not None else None
            except Exception:
                name = None

            facts[item_id] = {"room": room, "category": name}
    return facts
