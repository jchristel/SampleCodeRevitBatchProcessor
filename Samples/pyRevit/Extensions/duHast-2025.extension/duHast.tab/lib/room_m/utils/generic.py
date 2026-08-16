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


# The direct Revit API use in this module: phase membership needs the document's
# phase *ordering*, which duHast exposes nowhere, and the range test walks a raw
# collector so it can serve whichever category the caller names.
from Autodesk.Revit.DB import (
    FilteredElementCollector,
)

def element_id_str(element_id):
    """An ElementId as the string the wire uses. `.Value` is the modern API;
    `.IntegerValue` is what older Revit exposes, and this script has to run on
    both, so neither name is hard-coded."""
    value = getattr(element_id, "Value", None)
    if value is None:
        value = getattr(element_id, "IntegerValue", None)
    return str(value)


def document_phases(doc):
    """This document's phases as an ORDERED list of `{"id", "name"}`.

    The order is the entire point: "does this element exist in phase X" is a
    range test over the phase *sequence*, not an equality check, and `doc.Phases`
    is the only place that sequence exists. Ids are per-document (the same phase
    name has a different id in every model), so the name is what crosses between
    documents and the id is only ever used within one."""
    return [{"id": element_id_str(p.Id), "name": p.Name} for p in doc.Phases]


def exists_in_phase(created, demolished, selected):
    """Revit's phase-membership rule, on phase *sequence indices*:

        created <= selected AND (demolished invalid OR demolished > selected)

    `None` for `demolished` is the "invalid phase id" case - an element that was
    never demolished - which is why an unknown index reads as "still standing"
    rather than as a failure.

    **Not `created == selected`.** Equality would drop every element built in an
    earlier phase and still standing, which on a phased model is most of them.
    That mistake will not show up against a single-phase model, where the two
    agree exactly - which is what makes it worth naming here.

    A `created` that resolves to no known phase excludes the element: it cannot
    be placed in the sequence, so it cannot be shown to be in scope."""
    if created is None or created > selected:
        return False
    return demolished is None or demolished > selected


def phase_by_name(doc, phase_name):
    """This document's `Phase` object for `phase_name`.

    Needed because `FamilyInstance.FromRoom` is indexed by a *Phase*, not by a
    name or an id - and the name is what crosses between documents, so the
    lookup has to happen per document. Raises for an unknown name, on the same
    fail-loudly terms as `elements_in_phase`."""
    for phase in doc.Phases:
        if phase.Name == phase_name:
            return phase
    raise ValueError(
        "model has no phase named '{}' (it has: {})".format(
            phase_name, ", ".join(p.Name for p in doc.Phases))
    )
    

def elements_in_phase(doc, phase_name, category):
    """The element ids of `doc`'s elements of `category` that exist in
    `phase_name`, as strings matching the ids the export carries.

    The filter runs here, client-side, because only the live document has the
    phase ordering `exists_in_phase` needs - the server never re-evaluates the
    predicate, which is why the ordered phase list is not on the wire at all.
    It also means strictly *less* extraction, the axis that actually pays.

    **Doors only, despite the generic name.** It was written expecting to serve
    every entity, on the reasoning that `CreatedPhaseId`/`DemolishedPhaseId` are
    `Element` members so the predicate could not be room-specific. That is true
    of the API and false of the model: a room does not span a range of phases,
    it belongs to one, and running rooms through this returned nothing at all
    (see `room_m.utils.rooms.rooms_in_phase`). The name is kept because the range test genuinely is
    category-agnostic for anything built-then-demolished; the assumption that
    every entity works that way is what did not survive.

    Raises when the document has no phase of that name: a model that cannot be
    scoped to the chosen phase must fail loudly rather than push everything."""
    phases = document_phases(doc)
    order_by_name = dict((p["name"], i) for i, p in enumerate(phases))
    order_by_id = dict((p["id"], i) for i, p in enumerate(phases))

    if phase_name not in order_by_name:
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(p["name"] for p in phases))
        )
    selected = order_by_name[phase_name]

    allowed = set()
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(category)
        .WhereElementIsNotElementType()
    )
    for element in collector:
        created = order_by_id.get(element_id_str(element.CreatedPhaseId))
        demolished = order_by_id.get(element_id_str(element.DemolishedPhaseId))
        if exists_in_phase(created, demolished, selected):
            allowed.add(element_id_str(element.Id))
    return allowed


def entities_label(entities):
    """The chosen entities as the noun phrase in "<...> data" -- singular, since
    both names are regular plurals and "rooms data" reads as a typo."""
    return " and ".join(entity[:-1] for entity in entities)
