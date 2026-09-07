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
The DOORS half of a push: export each selected model's doors and send the whole
run as one push.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over -- see
`room_m.exporters.rooms` for the three names every module in this package
offers.

**Doors no longer depend on rooms having been pushed first.** The server used to
refuse a doors push to a model with no rooms; it does not, because it resolves a
door's rooms itself and "the rooms have not arrived yet" is a legitimate state it
reports rather than refuses. So the rooms and doors buckets are independent, and
a run may push either alone, in any order.
"""

from duHast.Revit.Doors.Export.to_data_door import get_all_door_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_door as dd
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.post_doors import post_doors_stream

from room_m.utils.openings import (
    nested_opening_ids,
    opening_placements,
    openings_in_phase,
)

from Autodesk.Revit.DB import BuiltInCategory


# A doors push carries no envelope field of its own: the boundary regime is a
# ROOMS fact and the doors contract has no key for it. None is the honest entry
# in the table, not an oversight.
stamp_envelope = None


def export_model(selected_doc, phase_name, return_value):
    """Export one model's doors as this document's contribution to the run's
    doors bucket, or None when it could not be read.

    Failures are recorded and swallowed rather than raised, so one unreadable
    document costs its own doors and not the rest of the run's.

    :return: `{"elements", "levels", "placements", "allowed_ids", "nested_ids"}` --
        the raw duHast exports, the Revit-read placements, this document's phase
        filter, and the doors that are components of another door.
    :rtype: dict
    """
    try:
        allowed_door_ids = openings_in_phase(selected_doc, phase_name, BuiltInCategory.OST_Doors)
        # Two filters, kept apart on purpose: "not in this phase" and "not a
        # door at all" are different fates, and an empty push has to be able to
        # name which one emptied it. See `nested_opening_ids`.
        nested_ids = nested_opening_ids(selected_doc, BuiltInCategory.OST_Doors)
        # Read from the Revit API, not from the export -- see `opening_placements`.
        # Keyed by bare door id and therefore only ever used against ITS OWN
        # model's doors, which is why it rides the contribution rather than being
        # merged into one run-wide map: door ids, like room ids, are unique only
        # within a document.
        placements = opening_placements(selected_doc, phase_name, BuiltInCategory.OST_Doors)

        door_data = get_all_door_data(selected_doc)
        json_formatted_doors = build_json_for_file(
            {dd.DataDoor.data_type: door_data}, "{}".format(selected_doc.Title))

        # Levels ride the DOORS envelope too, and unconditionally rather than
        # only for a rooms-less document. This side cannot tell whether the
        # server already has rooms for this model -- a doors-only button exists
        # precisely so doors can be pushed against rooms sent by an earlier run
        # -- so "does it need them" is not a question the producer can answer.
        # Sending them always makes a doors push self-sufficient whatever the
        # run held, and costs a list of tens of levels; the server prefers the
        # rooms snapshot's copy wherever it has one, so the duplicate can only
        # ever be redundant.
        level_data = get_all_level_data(selected_doc)
        json_formatted_levels = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: door export failed: {}".format(selected_doc.Title, e)
        )
        return None

    return {
        "elements": json_formatted_doors,
        "levels": json_formatted_levels,
        "placements": placements,
        "allowed_ids": allowed_door_ids,
        "nested_ids": nested_ids,
    }


def post_bucket(run_envelope, entries, return_value):
    """Push the run's whole doors bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    Note this reports a failure for a RUN with no doors at all -- see
    `post_doors`'s module docstring, which owns that decision and its cost. It no
    longer reports one for a *model* with no doors, which is ordinary in a
    multiselect run and used to redden it."""
    if not entries:
        return False

    ok, status, text = post_doors_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        return_value.append_message(
            "{}: server accepted doors ({})".format(models, text)
        )
        return True

    # There is no 202 here: unlike rooms, a doors push whose phase disagrees with
    # the model is REFUSED rather than quarantined, because activating it would
    # re-phase the model while its rooms stayed behind. So any non-2xx is a real
    # failure with a message worth surfacing.
    return_value.update_sep(
        False,
        "{}: doors push failed ({}): {}".format(models, status, text),
    )
    return False
