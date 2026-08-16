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

from collections import namedtuple

from duHast.Utilities.Objects.result import Result
from duHast.pyRevit.UI.doc_selector import pick_document

from room_m.utils.ui import (
    choose_project,
    choose_phase,
)

from room_m.utils.generic import (
    entities_label,
)

from room_m.utils.post_envelope import (
    build_model_envelope,
)

from room_m.exporters import rooms as rooms_exporter
from room_m.exporters import doors as doors_exporter


ROOMS = "rooms"
DOORS = "doors"


EntityExporter = namedtuple(
    "EntityExporter", ["export_and_post", "stamp_envelope", "blocking"])

# What each entity contributes to a run, and the ONLY place an entity is named
# in this module's machinery. `export_and_post_model` dispatches over this table
# rather than branching per entity, so adding windows or FF&E is a new module in
# `room_m.exporters`, one row here, and one entry point -- not another `if` in
# the run driver.
#
# `blocking` is the run policy, not a fact about the entity, which is why it
# lives here rather than in the exporter module. Rooms block: a door's
# from_room/to_room are room ids, so a doors push to a model whose rooms are not
# on the server is refused, and pressing on after a failed rooms push would be
# attempting exactly that. Doors do not block: by the time they run in a combined
# push the rooms have already landed, and discarding that because the door half
# failed would be the wrong trade. Windows and FF&E will reference rooms the same
# way doors do, so they belong on the non-blocking side too.
#
# A blocking exporter is allowed to RAISE rather than return False -- nothing has
# been pushed for the model when it runs, so there is no successful half to
# protect, and `export_entry` catches per model. A non-blocking one must record
# and return False instead, or one entity's failure would abandon the entities
# after it.
ENTITY_EXPORTERS = {
    ROOMS: EntityExporter(
        export_and_post=rooms_exporter.export_and_post,
        stamp_envelope=rooms_exporter.stamp_envelope,
        blocking=True,
    ),
    DOORS: EntityExporter(
        export_and_post=doors_exporter.export_and_post,
        stamp_envelope=doors_exporter.stamp_envelope,
        blocking=False,
    ),
}


def rooms_export_entry(doc, uiapp, output, forms):
    """Push ROOMS AND THEN DOORS -- the full push, and the original entry point.

    Kept combined under its original name deliberately. The pyRevit button that
    calls this lives outside this repository, so narrowing this function to
    rooms would not fail: it would keep succeeding while quietly no longer
    pushing doors, which is the worst shape a behaviour change can take. The
    split lives in the two siblings below instead, where wiring a new button is
    what opts into it.

    :return: Result object with status and message.
    :rtype: Result
    """
    return export_entry(doc, uiapp, output, forms, (ROOMS, DOORS))


def rooms_only_export_entry(doc, uiapp, output, forms):
    """Push ROOMS alone, leaving whatever doors the model already has on the
    server untouched.

    For re-pushing rooms after a plan change without paying for the door export
    and its per-door Revit room-reference reads, which are the slow half of a
    combined run.

    :return: Result object with status and message.
    :rtype: Result
    """
    return export_entry(doc, uiapp, output, forms, (ROOMS,))


def doors_export_entry(doc, uiapp, output, forms):
    """Push DOORS alone, against rooms already on the server.

    The reason this can exist as its own entry: a doors push carries no room
    data, only room *ids*, so it does not need the rooms to be re-sent -- it
    needs them to be *there*. Whether they are is the server's question, not
    this script's, and the server already answers it (a doors push to a model
    with no rooms is refused, naming the reason). Second-guessing that here
    would mean this script deciding what counts as "has rooms", which is exactly
    the check `has_room_snapshot` was fixed for getting wrong.

    :return: Result object with status and message.
    :rtype: Result
    """
    return export_entry(doc, uiapp, output, forms, (DOORS,))


def export_entry(doc, uiapp, output, forms, entities):

    """
    Exports `entities` from the selected Revit document(s) and pushes them.

    The single run driver behind all three entry points: document selection,
    the one project, the one phase, and the per-model loop are identical whether
    a run pushes rooms, doors or both, so they are written once. `entities` is
    the only thing that varies, and it varies in one place -- what
    `export_and_post_model` attempts per model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :param entities: which `ENTITY_EXPORTERS` keys this run pushes, in push
        order. Order matters -- see `export_and_post_model`.
    :type entities: tuple

    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # ask user to select active or linked document
        selected_docs = pick_document(
            doc, forms,
            button_name="Select model to collect {} data from".format(entities_label(entities)),
            multiselect=True)
        if not selected_docs or len(selected_docs) == 0:
            return_value.append_message("No document(s) selected")
            return return_value

        # pick ONE server-registered project for this run: every selected
        # model posts under it (matching "several models under one project").
        # None means abort -- server unreachable, nothing registered, or the
        # user cancelled -- so nothing is exported or pushed.
        project = choose_project(forms)
        if project is None:
            return_value.update_sep(False, "Push aborted: no project selected.")
            return return_value

        # Pick ONE phase for the whole run (see choose_phase). Every selected
        # model is filtered to it and declares it on the envelope; the server
        # refuses a push that declares none, and a model whose declared phase
        # disagrees with what it was first pushed under is quarantined rather
        # than made live. Asked once, after the project, because it is a
        # property of what is being pushed rather than of where it goes.
        phase_name = choose_phase(selected_docs, forms)
        if phase_name is None:
            return_value.update_sep(False, "Push aborted: no phase selected.")
            return return_value
        return_value.append_message("Pushing phase '{}'".format(phase_name))

        # get going
        model_counter = 0
        
        # set up a progress bar
        with forms.ProgressBar(
            title="Exporting model: {value} of {max_value}", cancellable=True
        ) as pb:
        
            # get data for each selected document and write to file. Each
            # model's export+post runs in its own try: one model failing
            # (an export exception, a broken envelope) must not abandon the
            # remaining models -- same per-model policy as a failed post.
            for selected_doc in selected_docs:

                # update progress bar
                model_counter += 1
                pb.update_progress(model_counter, max_value=len(selected_docs))

                try:
                    export_and_post_model(
                        selected_doc, project, phase_name, return_value, pb, entities)
                except Exception as e:
                    return_value.update_sep(
                        False, "{}: failed with exception: {}".format(selected_doc.Title, e)
                    )

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    break

    except Exception as e:
        message = "Failed to export {} data with exception: {}".format(
            entities_label(entities), e)
        return_value.update_sep(False, message)
        print(message)

    print("Finished")

    return return_value


def export_and_post_model(selected_doc, project, phase_name, return_value, pb, entities):
    """Export and push one model's `entities` under the picked `project`
    ({"id", "name"}), scoped to `phase_name`, recording the outcome on
    `return_value`. Raises on export/envelope failures -- the caller catches per
    model so one bad model doesn't abandon the rest.

    **The order in `entities` is not decoration.** A doors push to a model whose
    rooms are not on the server is refused (a door's from_room/to_room are room
    ids, and a room id is unique only within a model), so when a run carries
    both, rooms go first and a failed rooms push stops the model there. That is
    also why a failed rooms push returns instead of pressing on: pushing doors
    against rooms that did not land is not something to attempt on a hunch.

    A doors-ONLY run makes no such check and deliberately doesn't: it is asking
    the server about rooms it did not send, and the server is the only side that
    knows the answer."""
    envelope = build_model_envelope(selected_doc, project, phase_name, return_value)

    # Only the entities actually being pushed get to stamp the envelope. A
    # doors-only run therefore never reads the boundary regime -- which would
    # spend a document read to produce a warning about a value nothing on the
    # wire would carry.
    for entity in entities:
        stamp_envelope = ENTITY_EXPORTERS[entity].stamp_envelope
        if stamp_envelope is not None:
            stamp_envelope(selected_doc, envelope, return_value)

    # Don't begin this model's export at all if a cancel landed during the
    # previous model's post. The check that matters more is inside each push --
    # it is the export, not this, that a user waits through long enough to give
    # up during. The caller re-checks after this returns and stops the loop.
    if pb.cancelled:
        return

    for entity in entities:
        exporter = ENTITY_EXPORTERS[entity]
        pushed = exporter.export_and_post(
            selected_doc, envelope, phase_name, return_value, pb)
        if not pushed and exporter.blocking:
            return
