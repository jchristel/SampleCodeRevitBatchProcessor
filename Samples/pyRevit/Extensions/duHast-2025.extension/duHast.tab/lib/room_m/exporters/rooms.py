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
The ROOMS half of a push: export one model's rooms and levels, and send them.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over. Every
module in this package offers the same two names, which is the whole interface:

- `export_and_post(selected_doc, envelope, phase_name, return_value, pb)`
  returning whether the push landed.
- `stamp_envelope`, a callable adding this entity's own field to the per-model
  envelope, or None when it has none to add.

Nothing here knows that doors exist, and `room_mate` knows nothing about how
rooms are exported -- which is what lets windows and FF&E arrive as new modules
beside this one rather than as new branches inside the run driver.
"""

import copy

from duHast.Revit.Rooms.Export.to_data_room import get_all_room_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.post_rooms import (
    post_payload_stream,
)

from room_m.utils.rooms import (
    rooms_in_phase,
)

from room_m.utils.post_envelope import (
    add_room_boundary,
)


# The boundary regime is the one envelope field a ROOMS push carries and the
# others do not, so rooms are the entity that fills in this half of the
# interface. Aliased rather than wrapped: the table wants one name across all
# entities, and `add_room_boundary` already has exactly the right signature.
stamp_envelope = add_room_boundary


def export_and_post(selected_doc, envelope, phase_name, return_value, pb):
    """Export one model's rooms and levels and push them, reusing the already
    built `envelope`.

    Returns whether the push landed. Rooms are a *blocking* entity in
    `room_mate.ENTITY_EXPORTERS`, so False stops the model there and nothing
    queued behind rooms is attempted -- there would be no rooms on the server to
    hang them off. A cancel reads as "didn't land" for that same reason rather
    than as a failure.

    Raises on export failures rather than recording them, unlike the
    non-blocking exporters, and the asymmetry is intentional: nothing has been
    pushed for this model yet when this runs, so there is no successful half to
    protect. `room_mate.export_entry` catches per model."""

    # Resolve the run's phase against THIS document's own phases before
    # exporting anything: the name is the identity across models, and a document
    # that doesn't have it raises here (caught per model) rather than pushing an
    # unfiltered, silently-wrong room set.
    allowed_room_ids = rooms_in_phase(selected_doc, phase_name)
    # get room data
    room_data = get_all_room_data(selected_doc)
    # get level data
    level_data = get_all_level_data(selected_doc)

    # convert into a dictionary. The envelope is deep-copied on
    # every use now that one envelope serves several pushes:
    # .update() shares the nested project/model/snapshot dict
    # instances, and no two exports may be able to
    # cross-contaminate if anything downstream mutates its input.
    dic_room_data = {
        dr.DataRoom.data_type:room_data
    }
    dic_room_data.update(copy.deepcopy(envelope))

    # add some more properties before writing to json
    json_formatted_room = build_json_for_file(dic_room_data, "{}".format(selected_doc.Title))

    # convert into a dictionary
    dic_level_data = {
        dl.DataLevelBuilding.data_type:level_data
    }
    dic_level_data.update(copy.deepcopy(envelope))

    # add some more properties before writing to json
    json_formatted_level = build_json_for_file(dic_level_data, "{}".format(selected_doc.Title))

    # a large export takes a while -- honour a cancel clicked during it before
    # starting the (also slow) post; the caller re-checks pb.cancelled after
    # this returns and stops the loop
    if pb.cancelled:
        return False

    # post to the server: gzip-compressed NDJSON stream, so a
    # >100 MB FFE export never gets buffered whole client-side or
    # server-side (see roommate's HANDOVER-streaming*.md).
    # A failed push flips the overall Result red but does NOT abort
    # the caller's loop -- one bad model shouldn't discard the other
    # models' successful pushes, the run just must not end green.
    #
    # A `status` of None here is not an unreachable server: `post_payload_stream`
    # also refuses to send a push carrying no rooms at all, and reports that
    # refusal through this same tuple. Either way it is a failed push whose
    # message says which, so there is nothing to branch on.
    ok, status, text = post_payload_stream(
        json_formatted_room, json_formatted_level, allowed_room_ids=allowed_room_ids
    )
    if ok:
        # 202 is NOT a plain accept: the phase disagrees with what this model
        # was first pushed under, so the payload is stored inert and nothing
        # reads it until someone activates it. Reported distinctly, or a user
        # sees "accepted" and believes the model updated.
        if status == 202:
            return_value.append_message(
                "{}: stored but NOT live -- {}".format(selected_doc.Title, text)
            )
        else:
            return_value.append_message(
                "{}: server accepted ({})".format(selected_doc.Title, text)
            )
        return True

    return_value.update_sep(
        False,
        "{}: push failed ({}): {}".format(selected_doc.Title, status, text),
    )
    return False
