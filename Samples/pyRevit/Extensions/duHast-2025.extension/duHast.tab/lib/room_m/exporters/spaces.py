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

"""One model's contribution to a run's SPACES bucket, and the push for the whole
bucket.

The fifth entity, and the one that cost the least to extract: duHast already
ships a space export that mirrors the room one, so this module is close to
`exporters.rooms` with a different getter. What it adds is two guards that only
this entity needs, both earned from the RHH run.
"""

from duHast.Revit.Spaces.Export.to_data_space import get_all_space_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_space as ds
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.post_spaces import (
    post_payload_stream,
)

from room_m.utils.spaces import (
    collect_spaces,
    placement_facts,
    spaces_in_phase,
)

from room_m.utils.post_envelope import (
    add_room_boundary,
)


# A space has a boundary regime exactly as a room does, and it is the documented
# cause of the area differences the space-to-room reconciliation reports: an MEP
# space computed to wall centre against an architectural room computed to finish
# face differs by half a wall thickness, which is a difference in what was
# measured rather than a data error. Aliased for `exporters.rooms`' reason -- the
# table wants one name across entities and the signature already matches.
stamp_envelope = add_room_boundary


def export_model(selected_doc, phase_name, return_value):
    """Export one model's spaces and levels as this document's contribution to
    the run's spaces bucket, or None when it could not be read.

    Raises nothing of its own: an export failure is recorded on `return_value`
    and answered with None, so one unreadable document costs its own spaces and
    not the rest of the run's.

    **Two guards here are this entity's alone.**

    The first is a count check. duHast's `get_all_spaces` catches every exception
    and returns `[]`, so a collector failure inside `get_all_space_data` would
    arrive as an empty export -- and for spaces an empty export is a legitimate,
    *reportable* state rather than an error, so nothing downstream would ever
    question it. Comparing duHast's export against our own collector's count
    turns that silence into a failed model.

    The second is the per-model phase report. The push phase is one per RUN, and
    on RHH the mechanical model keeps 1,532 of its 1,533 spaces in a phase called
    `Future` while every sibling uses `New Construction`. A run under the common
    name pushes three full models and one space from the fourth -- a correctly
    filtered push that is almost entirely empty, and nothing about it is an
    error. So the count is reported for every model, always, rather than
    thresholded: the reader is the only one who can tell 1-of-1533 from a small
    model.

    :return: `{"spaces", "levels", "allowed_ids", "unplaced_ids",
        "zero_area_ids"}` -- the two raw duHast exports plus the three facts the
        export does not carry.
    :rtype: dict
    """
    try:
        # Our own collector, walked once and reused: it feeds the phase filter,
        # the placement facts and the count guard below.
        spaces = collect_spaces(selected_doc)
        allowed_ids = spaces_in_phase(selected_doc, phase_name, spaces)
        unplaced_ids, zero_area_ids = placement_facts(spaces)

        space_data = get_all_space_data(selected_doc)
        level_data = get_all_level_data(selected_doc)

        if len(spaces) and not len(space_data):
            raise ValueError(
                "duHast exported 0 of {} spaces this document holds; its collector "
                "swallows exceptions and answers an empty list, so this is a failed "
                "export rather than a model without spaces".format(len(spaces))
            )

        json_formatted_space = build_json_for_file(
            {ds.DataSpace.data_type: space_data}, "{}".format(selected_doc.Title))
        json_formatted_level = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: space export failed: {}".format(selected_doc.Title, e)
        )
        return None

    return_value.append_message(
        "{}: {} of {} spaces are in phase '{}'".format(
            selected_doc.Title, len(allowed_ids), len(spaces), phase_name
        )
    )

    return {
        "spaces": json_formatted_space,
        "levels": json_formatted_level,
        "allowed_ids": allowed_ids,
        "unplaced_ids": unplaced_ids,
        "zero_area_ids": zero_area_ids,
    }


def post_bucket(run_envelope, entries, return_value):
    """Push the run's whole spaces bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    **A push carrying no spaces is sent, not refused**, which is where this
    departs from `exporters.rooms.post_bucket`. There the producer refuses a
    run that kept nothing, because an empty rooms push is a producer fault.
    Here it is the answer: "these services models hold no spaces" is the finding
    requirement 1 buys, and it is a different fact from "these models were never
    pushed" -- one only a push can record. So `status` is never None on this
    path, and a failure here really is a failure.
    """
    if not entries:
        return False

    ok, status, text = post_payload_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        # 202 means at least one model's phase disagrees with what it was first
        # pushed under, so that model's payload is quarantined and nothing reads
        # it until someone activates it. **For spaces that is a recoverable, and
        # expected, state**: a services model usually holds no rooms, so
        # promoting its own quarantined push is the only way its lineage is ever
        # re-phased. Reported distinctly, or a user reads "accepted" and believes
        # every model updated.
        if status == 202:
            return_value.append_message(
                "{}: stored, but NOT every model is live -- {}".format(models, text)
            )
        else:
            return_value.append_message(
                "{}: server accepted spaces ({})".format(models, text)
            )
        return True

    return_value.update_sep(
        False,
        "{}: spaces push failed ({}): {}".format(models, status, text),
    )
    return False
