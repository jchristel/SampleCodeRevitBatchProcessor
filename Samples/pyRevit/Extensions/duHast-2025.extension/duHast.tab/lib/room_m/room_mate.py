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

import copy

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
    build_run_envelope,
    build_model_block,
)

from room_m.exporters import rooms as rooms_exporter
from room_m.exporters import doors as doors_exporter


ROOMS = "rooms"
DOORS = "doors"


EntityExporter = namedtuple(
    "EntityExporter", ["export_model", "post_bucket", "stamp_envelope"])

# What each entity contributes to a run, and the ONLY place an entity is named
# in this module's machinery. `export_entry` dispatches over this table rather
# than branching per entity, so adding windows or FF&E is a new module in
# `room_m.exporters`, one row here, and one entry point -- not another `if` in
# the run driver.
#
# **`blocking` is gone, and its absence is the change.** It used to say that a
# model's rooms had to land before its doors were attempted, because the server
# refused a doors push to a model with no rooms. The server no longer asks: it
# resolves a door's rooms itself, and "the rooms have not arrived yet" is a state
# it reports rather than refuses. So the buckets are independent, and there is no
# ordering left for the table to encode. Windows and FF&E inherit that.
ENTITY_EXPORTERS = {
    ROOMS: EntityExporter(
        export_model=rooms_exporter.export_model,
        post_bucket=rooms_exporter.post_bucket,
        stamp_envelope=rooms_exporter.stamp_envelope,
    ),
    DOORS: EntityExporter(
        export_model=doors_exporter.export_model,
        post_bucket=doors_exporter.post_bucket,
        stamp_envelope=doors_exporter.stamp_envelope,
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
    """Push DOORS alone.

    A doors push carries no room data, only room *ids*, so it never needed the
    rooms re-sent. It used to need them to already be *there* -- the server
    refused otherwise -- and that is no longer true either: the server resolves a
    door's rooms itself and reports "not yet" rather than refusing. So this entry
    is now genuinely independent, and doors may be pushed before their rooms.

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
    `export_model` reads per document.

    **Every selected model is exported first, then each entity is pushed once.**
    A run used to be N pushes per entity, one per model, which meant a doors push
    depended on whether its siblings had already landed and gave the run's models
    N snapshot ids minutes apart. Now the run reads everything, then sends one
    bucket per entity under one snapshot id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :param entities: which `ENTITY_EXPORTERS` keys this run pushes. Order is
        no longer meaningful -- the buckets are independent, see
        `ENTITY_EXPORTERS`.
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

        # One envelope for the whole run: one project, one phase, one moment
        # of reading. Built before the loop so every model in the push shares a
        # snapshot id -- which is what makes "these documents were read
        # together" a thing the store can express.
        run_envelope = build_run_envelope(project, phase_name)

        # get going
        model_counter = 0

        # One bucket per entity, filled model by model and posted once at the
        # end. The export is the slow half and happens per document; the push is
        # one request per entity for the whole run.
        buckets = dict((entity, []) for entity in entities)

        # Read inside the `with` and acted on outside it, rather than reaching
        # for `pb.cancelled` after the progress bar has exited.
        cancelled = False

        # set up a progress bar
        with forms.ProgressBar(
            title="Exporting model: {value} of {max_value}", cancellable=True
        ) as pb:

            # get data for each selected document. Each model's export runs in
            # its own try: one model failing (an export exception, a broken
            # envelope) must not abandon the remaining models. It costs that
            # model's contribution to every bucket and nothing else -- the run
            # still pushes what it did read, and still ends red.
            for selected_doc in selected_docs:

                # update progress bar
                model_counter += 1
                pb.update_progress(model_counter, max_value=len(selected_docs))

                try:
                    export_model(
                        selected_doc, phase_name, return_value, entities, buckets)
                except Exception as e:
                    return_value.update_sep(
                        False, "{}: failed with exception: {}".format(selected_doc.Title, e)
                    )

                # check for cancel
                if pb.cancelled:
                    cancelled = True
                    return_value.update_sep(False, "User cancelled.")
                    break

        # A cancelled run pushes nothing. The alternative -- sending the models
        # read so far -- would store a partial run under one snapshot id, which
        # reads downstream as "these are the documents that were exported
        # together" and would be a lie. Someone who cancels wants nothing sent.
        if cancelled:
            return return_value

        for entity in entities:
            entries = buckets[entity]
            if not entries:
                # Nothing was read for this entity at all -- every model failed,
                # and each failure is already on `return_value`. Posting an empty
                # bucket would only add a second, vaguer complaint.
                continue
            ENTITY_EXPORTERS[entity].post_bucket(run_envelope, entries, return_value)

    except Exception as e:
        message = "Failed to export {} data with exception: {}".format(
            entities_label(entities), e)
        return_value.update_sep(False, message)
        print(message)

    print("Finished")

    return return_value


def export_model(selected_doc, phase_name, return_value, entities, buckets):
    """Export one model's `entities` into the run's `buckets`, scoped to
    `phase_name`, recording any failure on `return_value`.

    Raises on envelope failures -- the caller catches per model so one bad model
    doesn't abandon the rest. An *entity's* export failure is not a raise: the
    exporter records it and answers None, so an unreadable door set does not also
    cost this model's rooms.

    **There is no ordering here, and there used to be.** Rooms had to be pushed
    before doors for the same model, because the server refused a doors push to a
    model with no rooms. It no longer does, so the entities are independent and
    the loop below is genuinely a loop rather than a sequence with a rule in it.

    Each entity gets its own deep copy of the model's envelope block: a rooms
    push stamps `room_boundary` and `levels` onto its copy and a doors push has
    no key for either, and two entities sharing one nested dict is the exact
    cross-contamination the old per-push deep copy existed to prevent."""
    block = build_model_block(selected_doc, return_value)

    for entity in entities:
        exporter = ENTITY_EXPORTERS[entity]
        entity_block = copy.deepcopy(block)

        # Only the entity actually being pushed stamps its own field. A
        # doors-only run therefore never reads the boundary regime -- which
        # would spend a document read to produce a warning about a value nothing
        # on the wire would carry.
        if exporter.stamp_envelope is not None:
            exporter.stamp_envelope(selected_doc, entity_block, return_value)

        contribution = exporter.export_model(selected_doc, phase_name, return_value)
        if contribution is None:
            continue
        buckets[entity].append((entity_block, contribution))
