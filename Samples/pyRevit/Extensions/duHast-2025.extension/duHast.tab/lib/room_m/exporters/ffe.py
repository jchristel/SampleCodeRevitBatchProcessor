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
The FF&E half of a push: export each selected model's furniture, fixtures and
equipment and send the whole run as one push.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over -- see
`room_m.exporters.rooms` for the three names every module in this package
offers.

**FF&E lives in the same document as the rooms it serves, and that is the
premise of the entity rather than a convenience.** Revit cannot schedule FF&E
against rooms; RoomMate performs the join Revit will not. So unlike the windows
exporter, nothing here is shaped around a model that links its interiors: the
rooms are in the file, `get_Room(phase)` has a live room to answer with, and on
House A 572 of 647 items named one.

FF&E depends on nothing else having been pushed. The server resolves an item's
room itself and reports "the rooms have not arrived yet" rather than refusing,
so the buckets stay independent and a run may push any of them alone, in any
order.

ASCII only: IronPython 2.7 will not parse a file containing an em-dash.
"""

from duHast.Revit.Family.Export.to_data_item import (
    get_all_item_data,
    DEFAULT_ITEM_CATEGORIES,
)
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_item as di
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.post_ffe import post_ffe_stream

from room_m.utils.items import (
    item_facts,
    items_in_phase,
)


# An FF&E push carries no envelope field of its own: the boundary regime is a
# ROOMS fact and no other contract has a key for it. None is the honest entry in
# the table, not an oversight.
stamp_envelope = None


def export_model(selected_doc, phase_name, return_value):
    """Export one model's FF&E as this document's contribution to the run's FF&E
    bucket, or None when it could not be read.

    Failures are recorded and swallowed rather than raised, so one unreadable
    document costs its own items and not the rest of the run's.

    **The category list comes from duHast, not from a copy of it here.**
    `get_all_item_data` is called with no category argument so it walks its own
    defaults, and the same `DEFAULT_ITEM_CATEGORIES` drives the Revit pass -- so
    the two cannot describe different populations. That mattered enough to be a
    verdict condition in the probe: a producer walking eight categories while
    the export walked nine would report a drop that was its own.

    :return: `{"elements", "levels", "facts", "allowed_ids"}` -- the raw duHast
        exports, the Revit-read room and category per item, and this document's
        phase filter.
    :rtype: dict
    """
    try:
        allowed_item_ids = items_in_phase(selected_doc, phase_name, DEFAULT_ITEM_CATEGORIES)
        # Read from the Revit API, not from the export -- see `item_facts`.
        # Keyed by bare element id and therefore only ever used against ITS OWN
        # model's items, which is why it rides the contribution rather than
        # being merged into one run-wide map: element ids, like room ids, are
        # unique only within a document.
        #
        # **No nested filter beside it**, unlike the openings exporters. Whether
        # a component is an item is a project convention, so it is the server's
        # `[ffe] nested_components` applied at read time -- where it can change
        # without a re-push and where the count of what it removed is reported.
        facts = item_facts(selected_doc, phase_name, DEFAULT_ITEM_CATEGORIES)

        item_data = get_all_item_data(selected_doc)
        json_formatted_items = build_json_for_file(
            {di.DataItem.data_type: item_data}, "{}".format(selected_doc.Title))

        # Levels ride the FF&E envelope, though they matter less here than they
        # do for windows. A facade model holds windows and no rooms, so without
        # the level list every window in it is unreachable; FF&E lives with its
        # rooms, so the rooms snapshot normally declares the set and this is
        # redundant. Sent anyway because "normally" is not "always": the buckets
        # are independent and an FF&E push may legitimately land before its
        # rooms. The server prefers the rooms snapshot's copy wherever it has
        # one, so the duplicate can only ever be redundant.
        level_data = get_all_level_data(selected_doc)
        json_formatted_levels = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: FF&E export failed: {}".format(selected_doc.Title, e)
        )
        return None

    return {
        "elements": json_formatted_items,
        "levels": json_formatted_levels,
        "facts": facts,
        "allowed_ids": allowed_item_ids,
    }


def post_bucket(run_envelope, entries, return_value):
    """Push the run's whole FF&E bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    Note this reports a failure for a RUN with no FF&E at all -- see `post_ffe`'s
    module docstring, which owns that decision and its cost. It does not report
    one for a *model* with no FF&E, which is ordinary in a multiselect run: a
    plantroom level or a base-build package legitimately has none."""
    if not entries:
        return False

    ok, status, text = post_ffe_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        return_value.append_message(
            "{}: server accepted FF&E ({})".format(models, text)
        )
        return True

    # There is no 202 here: like doors and windows, an FF&E push whose phase
    # disagrees with the model is REFUSED rather than quarantined, because
    # activating it would re-phase the model while its rooms stayed behind. So
    # any non-2xx is a real failure with a message worth surfacing.
    return_value.update_sep(
        False,
        "{}: FF&E push failed ({}): {}".format(models, status, text),
    )
    return False
