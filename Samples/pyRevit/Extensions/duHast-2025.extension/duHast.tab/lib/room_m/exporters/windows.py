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
The WINDOWS half of a push: export each selected model's windows and send the
whole run as one push.

One of the entity exporters `room_mate.ENTITY_EXPORTERS` dispatches over -- see
`room_m.exporters.rooms` for the three names every module in this package
offers.

Windows depend on nothing else having been pushed. The server resolves an
opening's rooms itself and reports "the rooms have not arrived yet" rather than
refusing, so the rooms, doors and windows buckets are independent and a run may
push any of them alone, in any order.

**The facade model is the one this entity was built for**, and it is worth
knowing before reading anything below: such a file links its interiors rather
than containing them, so it holds windows and no rooms at all. Everything here
that looks like a special case -- levels sent unconditionally, room references
usually absent -- is that model being ordinary rather than exceptional.
"""

from duHast.Revit.Windows.Export.to_data_window import get_all_window_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_window as dw
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from Autodesk.Revit.DB import BuiltInCategory

from room_m.post_windows import post_windows_stream

from room_m.utils.openings import (
    nested_opening_ids,
    opening_placements,
    openings_in_phase,
)


# A windows push carries no envelope field of its own: the boundary regime is a
# ROOMS fact and no opening contract has a key for it. None is the honest entry
# in the table, not an oversight.
stamp_envelope = None


def export_model(selected_doc, phase_name, return_value):
    """Export one model's windows as this document's contribution to the run's
    windows bucket, or None when it could not be read.

    Failures are recorded and swallowed rather than raised, so one unreadable
    document costs its own windows and not the rest of the run's.

    :return: `{"elements", "levels", "placements", "allowed_ids", "nested_ids"}`
        -- the raw duHast exports, the Revit-read placements, this document's
        phase filter, and the windows that are components of another window.
    :rtype: dict
    """
    try:
        allowed_window_ids = openings_in_phase(selected_doc, phase_name, BuiltInCategory.OST_Windows)
        # Two filters, kept apart on purpose: "not in this phase" and "not a
        # window at all" are different fates, and an empty push has to be able
        # to name which one emptied it. See `nested_opening_ids`.
        nested_ids = nested_opening_ids(selected_doc, BuiltInCategory.OST_Windows)
        # Read from the Revit API, not from the export -- see
        # `opening_placements`. Keyed by bare element id and therefore only ever
        # used against ITS OWN model's windows, which is why it rides the
        # contribution rather than being merged into one run-wide map: element
        # ids, like room ids, are unique only within a document.
        placements = opening_placements(selected_doc, phase_name, BuiltInCategory.OST_Windows)

        window_data = get_all_window_data(selected_doc)
        json_formatted_windows = build_json_for_file(
            {dw.DataWindow.data_type: window_data}, "{}".format(selected_doc.Title))

        # Levels ride the WINDOWS envelope unconditionally, and for windows this
        # is load-bearing rather than defensive. A facade model holds windows and
        # no rooms, so there is no rooms snapshot to declare the level set its
        # windows point into -- and without an elevation the server cannot probe
        # an opening's surroundings at all, which is what `room_resolution`
        # depends on. This side cannot tell whether the server already has rooms
        # for the model, so "does it need them" is not a question the producer
        # can answer. Sending them always costs a list of tens of levels; the
        # server prefers the rooms snapshot's copy wherever it has one, so the
        # duplicate can only ever be redundant.
        level_data = get_all_level_data(selected_doc)
        json_formatted_levels = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: window export failed: {}".format(selected_doc.Title, e)
        )
        return None

    return {
        "elements": json_formatted_windows,
        "levels": json_formatted_levels,
        "placements": placements,
        "allowed_ids": allowed_window_ids,
        "nested_ids": nested_ids,
    }


def post_bucket(run_envelope, entries, return_value):
    """Push the run's whole windows bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    Note this reports a failure for a RUN with no windows at all -- see
    `post_windows`'s module docstring, which owns that decision and its cost. It
    does not report one for a *model* with no windows, which is ordinary in a
    multiselect run: a service core or an internal floor legitimately has
    none."""
    if not entries:
        return False

    ok, status, text = post_windows_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        return_value.append_message(
            "{}: server accepted windows ({})".format(models, text)
        )
        return True

    # There is no 202 here: like doors, a windows push whose phase disagrees with
    # the model is REFUSED rather than quarantined, because activating it would
    # re-phase the model while its rooms stayed behind. So any non-2xx is a real
    # failure with a message worth surfacing.
    return_value.update_sep(
        False,
        "{}: windows push failed ({}): {}".format(models, status, text),
    )
    return False
