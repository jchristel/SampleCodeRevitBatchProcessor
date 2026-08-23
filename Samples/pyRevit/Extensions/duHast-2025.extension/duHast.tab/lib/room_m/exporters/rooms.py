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
The ROOMS half of a push: export each selected model's rooms and levels, and
send the whole run as one push.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over. Every
module in this package offers the same three names, which is the whole
interface:

- `export_model(selected_doc, phase_name, return_value)` returning this
  document's contribution to the run's bucket, or None when it could not be
  read.
- `post_bucket(run_envelope, entries, return_value)` sending the accumulated
  bucket, returning whether the push landed.
- `stamp_envelope`, a callable adding this entity's own field to one model's
  envelope block, or None when it has none to add.

**Exporting and posting are separate names because a run is now one push.**
They used to be one call per model, which is what made a doors push depend on
whether its siblings had already been sent. Now every selected document
contributes to a bucket and the bucket is posted once, so the ordering question
does not arise.

Nothing here knows that doors exist, and `room_mate` knows nothing about how
rooms are exported -- which is what lets windows and FF&E arrive as new modules
beside this one rather than as new branches inside the run driver.
"""

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


def export_model(selected_doc, phase_name, return_value):
    """Export one model's rooms and levels as this document's contribution to the
    run's rooms bucket, or None when it could not be read.

    Raises nothing of its own: an export failure is recorded on `return_value`
    and answered with None, so one unreadable document costs its own rooms and
    not the rest of the run's. That is a change from when this also posted --
    there was no successful half to protect then, because the push for this model
    had not happened yet. Now there is: the models already in the bucket.

    :return: `{"rooms", "levels", "allowed_ids"}` -- the two raw duHast exports
        and this document's phase filter, kept unflattened so the streaming path
        can translate one room at a time.
    :rtype: dict
    """
    try:
        # Resolve the run's phase against THIS document's own phases before
        # exporting anything: the name is the identity across models, and a
        # document that doesn't have it fails here rather than contributing an
        # unfiltered, silently-wrong room set.
        allowed_room_ids = rooms_in_phase(selected_doc, phase_name)
        room_data = get_all_room_data(selected_doc)
        level_data = get_all_level_data(selected_doc)

        # duHast's file wrapper, one per export, exactly as before -- the
        # translation side reads the list keys out of these.
        json_formatted_room = build_json_for_file(
            {dr.DataRoom.data_type: room_data}, "{}".format(selected_doc.Title))
        json_formatted_level = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: room export failed: {}".format(selected_doc.Title, e)
        )
        return None

    return {
        "rooms": json_formatted_room,
        "levels": json_formatted_level,
        "allowed_ids": allowed_room_ids,
    }


def post_bucket(run_envelope, entries, return_value):
    """Push the run's whole rooms bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    A failed push flips the overall Result red. It no longer aborts anything:
    there is nothing queued behind it, because the run exports first and posts
    once.

    A `status` of None here is not an unreachable server: `post_payload_stream`
    also refuses to send a push carrying no rooms at all, and reports that
    refusal through this same tuple. Either way it is a failed push whose message
    says which, so there is nothing to branch on."""
    if not entries:
        return False

    # gzip-compressed NDJSON stream, so a >100 MB FFE export never gets buffered
    # whole client-side or server-side (see roommate's HANDOVER-streaming*.md).
    ok, status, text = post_payload_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        # 202 is NOT a plain accept: at least one model's phase disagrees with
        # what it was first pushed under, so that model's payload is stored inert
        # and nothing reads it until someone activates it. Reported distinctly,
        # or a user sees "accepted" and believes every model updated.
        if status == 202:
            return_value.append_message(
                "{}: stored, but NOT every model is live -- {}".format(models, text)
            )
        else:
            return_value.append_message(
                "{}: server accepted rooms ({})".format(models, text)
            )
        return True

    return_value.update_sep(
        False,
        "{}: rooms push failed ({}): {}".format(models, status, text),
    )
    return False
