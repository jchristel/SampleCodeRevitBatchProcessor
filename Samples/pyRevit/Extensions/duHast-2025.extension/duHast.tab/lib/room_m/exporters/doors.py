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
The DOORS half of a push: export one model's doors and send them.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over -- see
`room_m.exporters.rooms` for the two names every module in this package offers.

Doors are not a blocking entity: a failure here is recorded and the run carries
on, because by the time this runs a combined run's rooms push has already
succeeded and losing that would be the wrong trade. `room_mate` owns that
policy; this module only reports honestly which way it went.
"""

import copy

from duHast.Revit.Doors.Export.to_data_door import get_all_door_data
from duHast.Data.Objects.Collectors import data_door as dd
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.post_doors import post_doors_stream

from room_m.utils.doors import (
    door_placements,
    doors_in_phase,
)


# A doors push carries no envelope field of its own: the boundary regime is a
# ROOMS fact and the doors contract has no key for it. None is the honest entry
# in the table, not an oversight.
stamp_envelope = None


def export_and_post(selected_doc, envelope, phase_name, return_value, pb):
    """Export one model's doors and push them, reusing the run's already built
    `envelope` (identity, phase, model_to_shared) so a combined run's pushes
    cannot disagree about what model or phase they describe.

    Returns whether the push landed. Doors are NOT blocking, so a False here
    does not stop the model -- it is reported and the run moves on, having
    already flipped the overall `Result` red. The value is still stated
    honestly rather than always True, because the table is what decides what a
    failure costs, and an exporter that lied about its outcome would take that
    decision away from it.

    Failures are recorded and swallowed rather than raised. In a combined run
    the rooms push has already succeeded by the time this runs, and losing that
    because the door half failed would be the wrong trade; in a doors-only run
    there is nothing to protect, but recording rather than raising keeps one
    model's failure from ending the loop either way. The run still ends red.

    Note this reports a failure for a model with no doors at all -- see
    `post_doors`'s module docstring, which owns that decision and its cost."""
    try:
        allowed_door_ids = doors_in_phase(selected_doc, phase_name)
        # Read from the Revit API, not from the export -- see
        # `door_placements`.
        placements = door_placements(selected_doc, phase_name)

        door_data = get_all_door_data(selected_doc)
        dic_door_data = {dd.DataDoor.data_type: door_data}
        dic_door_data.update(copy.deepcopy(envelope))
        json_formatted_doors = build_json_for_file(dic_door_data, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: door export failed: {}".format(selected_doc.Title, e)
        )
        return False

    # The per-door Revit room-reference reads above are the slow part of a doors
    # push, so the same "cancel during the export, before the post" check the
    # room path makes applies here -- and applies whether or not rooms ran first.
    if pb.cancelled:
        return False

    ok, status, text = post_doors_stream(
        json_formatted_doors, placements, allowed_door_ids=allowed_door_ids
    )
    if ok:
        return_value.append_message(
            "{}: doors accepted ({})".format(selected_doc.Title, text)
        )
        return True
    else:
        # There is no 202 here: unlike rooms, a doors push whose phase
        # disagrees with the model is REFUSED rather than quarantined, because
        # activating it would re-phase the model while its rooms stayed behind.
        # So any non-2xx is a real failure with a message worth surfacing.
        return_value.update_sep(
            False,
            "{}: doors push failed ({}): {}".format(selected_doc.Title, status, text),
        )
        return False
