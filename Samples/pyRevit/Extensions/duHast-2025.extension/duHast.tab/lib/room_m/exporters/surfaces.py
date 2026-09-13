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

"""One model's contribution to a run's CEILINGS or FLOORS bucket, and the push
for the whole bucket -- written once and bound to an entity by `SurfaceExport`.

What is specific to slabs, and worth knowing before changing anything here:

**The phase filter is the DOORS range test, not the rooms equality test.** A
room BELONGS to one phase (`ROOM_PHASE`); a ceiling or a floor is BUILT in one
and may be demolished in a later one, so it takes `elements_in_phase` /
`exists_in_phase` over `PHASE_CREATED` and `PHASE_DEMOLISHED`. Running rooms
through the range test returns nothing, silently, and cost five empty pushes to
find; this is the same trap facing the other way, and House A cannot catch it
because no ceiling there is demolished -- the two tests agree on that document
by accident.

**Nothing here re-derives the level or the footprint.** duHast reads the level
the modeller assigned and measures the element's own solid; an extractor that
computed either would silently discard a correct duHast and produce a
byte-identical bad export. That is the rule the door footprint and the FF&E
level both cost real time to learn.

**An element that duHast could not measure is still pushed**, with an empty
polygon. See `post_surfaces.translate_surface`.
"""

from collections import namedtuple

from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file

from room_m.utils.generic import (
    elements_in_phase,
)

from room_m.utils.surfaces import (
    host_offsets,
)


# Everything that varies between exporting ceilings and exporting floors.
#
# `collect` answers every instance of the category (the count the export is
# checked against); `export` is duHast's data export for it; `data_type` is the
# key duHast files the exported elements under; `offset_parameter` is the
# BuiltInParameter holding the height above the level; `post_stream` is the
# entity's streamed push. `plural` and `singular` exist only for the messages a
# user reads, which must name the entity they are about.
SurfaceExport = namedtuple(
    "SurfaceExport",
    [
        "plural",
        "singular",
        "category",
        "collect",
        "export",
        "data_type",
        "offset_parameter",
        "post_stream",
    ],
)


def export_model(spec, selected_doc, phase_name, return_value):
    """Export one model's elements and levels as this document's contribution
    to the run's bucket, or None when it could not be read.

    Raises nothing of its own: an export failure is recorded on `return_value`
    and answered with None, so one unreadable document costs its own elements
    and not the rest of the run's.

    **The count guard is the spaces one, and it earns its place here for a
    different reason.** duHast's collectors do not swallow exceptions the way
    `get_all_spaces` does, so the failure mode that guard was written for is
    absent. What is present is the one the ceilings probe measured: until
    2026-09-10 duHast answered None for an element it could not measure and
    dropped it silently, so an export could arrive short of the model's real
    count with nothing saying so. That is fixed upstream for both slabs, and
    this guard is what notices if an older duHast is on the path -- which, given
    the extension runs off a COPY of this package, is a live possibility rather
    than a theoretical one.

    :return: `{"elements", "levels", "allowed_ids", "offsets"}` -- the two raw
        duHast exports plus the two facts the export does not carry usably.
    :rtype: dict
    """
    try:
        collected = list(spec.collect(selected_doc))

        # The DOORS range test. See the module docstring for why this is not
        # `rooms_in_phase`.
        allowed_ids = elements_in_phase(selected_doc, phase_name, spec.category)

        # Read from Revit, not taken from the export: duHast carries this as a
        # rounded millimetre STRING. See `room_m.utils.surfaces`.
        offsets = host_offsets(selected_doc, spec.category, spec.offset_parameter)

        element_data = spec.export(selected_doc)
        level_data = get_all_level_data(selected_doc)

        if len(collected) and not len(element_data):
            raise ValueError(
                "duHast exported 0 of {} {} this document holds; that is a "
                "failed export rather than a model without {}".format(
                    len(collected), spec.plural, spec.plural)
            )
        if len(element_data) < len(collected):
            raise ValueError(
                "duHast exported {} of {} {} this document holds. An older "
                "duHast drops a {} it cannot measure instead of exporting it "
                "with an empty polygon; check which duHast the extension is "
                "running before trusting this push".format(
                    len(element_data), len(collected), spec.plural, spec.singular)
            )

        json_formatted_elements = build_json_for_file(
            {spec.data_type: element_data}, "{}".format(selected_doc.Title))
        json_formatted_level = build_json_for_file(
            {dl.DataLevelBuilding.data_type: level_data}, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: {} export failed: {}".format(selected_doc.Title, spec.singular, e)
        )
        return None

    # Reported for every model, always, rather than thresholded -- the spaces
    # rule, and for the same reason: only the reader can tell a correctly
    # filtered push that kept almost nothing from a small model.
    return_value.append_message(
        "{}: {} of {} {} exist in phase '{}'".format(
            selected_doc.Title, len(allowed_ids), len(collected), spec.plural, phase_name
        )
    )

    return {
        "elements": json_formatted_elements,
        "levels": json_formatted_level,
        "allowed_ids": allowed_ids,
        "offsets": offsets,
    }


def post_bucket(spec, run_envelope, entries, return_value):
    """Push the run's whole bucket -- every selected model, one request.

    `entries` is `[(model_block, contribution), ...]`. Returns whether the push
    landed.

    **An empty push is refused here, though the server accepts one**, which is
    the doors asymmetry rather than the spaces one. The server must allow zero
    because it cannot tell a shell or a base-build package from a broken export.
    This side is answering a different question -- "someone asked for a
    ceilings push and there are none" -- which is worth stopping whichever of
    the two it turns out to be.

    **Scoped to the RUN, not to one model.** Asked per model, a document that
    legitimately holds none would fail the push and redden an otherwise clean
    run. The residual cost is the one doors already accepts: a run whose
    documents genuinely hold none at all cannot record that fact through this
    producer.

    The refusal rides the normal `(ok, status, text)` tuple with `status = None`,
    so callers need no second failure channel.
    """
    if not entries:
        return False

    kept = sum(len(contribution["allowed_ids"]) for _, contribution in entries)
    if not kept:
        held = sum(
            len(contribution["elements"].get(spec.data_type, [])) for _, contribution in entries
        )
        return_value.update_sep(
            False,
            "{} push refused: the {} document(s) in this run exported {} "
            "{}(s) and none exist in phase '{}'. Nothing was pushed.".format(
                spec.plural, len(entries), held, spec.singular, run_envelope.get("phase")
            ),
        )
        return False

    ok, status, text = spec.post_stream(run_envelope, entries)
    models = ", ".join(block["id"] for block, _ in entries)
    if ok:
        # 202 means at least one model's phase disagrees with what it was first
        # pushed under, so that model's payload is quarantined and nothing reads
        # it until someone activates it. Reported distinctly, or a user reads
        # "accepted" and believes every model updated.
        if status == 202:
            return_value.append_message(
                "{}: stored, but NOT every model is live -- {}".format(models, text)
            )
        else:
            return_value.append_message(
                "{}: server accepted {} ({})".format(models, spec.plural, text)
            )
        return True

    return_value.update_sep(
        False,
        "{}: {} push failed ({}): {}".format(models, spec.plural, status, text),
    )
    return False
