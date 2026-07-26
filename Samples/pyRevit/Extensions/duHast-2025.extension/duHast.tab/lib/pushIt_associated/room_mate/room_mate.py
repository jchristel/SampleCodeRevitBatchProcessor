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
import datetime

# The only direct Revit API use in this script. duHast exports elements; the
# room boundary location is a document *setting*, which it has no collector for.
from Autodesk.Revit.DB import AreaVolumeSettings, SpatialElementType

from duHast.Revit.Rooms.Export.to_data_room import get_all_room_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Revit.Common.Geometry.geometry import get_coordinate_system_translation_and_rotation
from duHast.Utilities.Objects.result import Result
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.pyRevit.UI.doc_selector import pick_document

from post_rooms import (
    post_payload_stream,
    fetch_projects,
    coordinate_system_to_affine,
    boundary_location_to_room_boundary,
)


def choose_project(forms):
    """Force a choice of which SERVER-REGISTERED project to push to, from the
    server's registered settings bundles (`fetch_projects`). Returns
    `{"id", "name"}`, or `None` to abort the whole run.

    The project id must match a registered settings bundle on the server or the
    push 422s (and the id becomes a storage path key), so it can't be derived
    from the Revit document -- it has to come from the server. `None` is
    returned (and the caller aborts) when the server is unreachable, has no
    registered projects, or the user cancels; there is deliberately no default
    or skip path, since a wrong/guessed id is exactly what this replaces."""
    ok, status, payload = fetch_projects()
    if not ok:
        forms.alert(
            "Could not load projects from the server.\n\n{}".format(payload),
            title="Roommate - push aborted", warn_icon=True)
        return None
    projects = payload
    if not projects:
        forms.alert(
            "The server has no registered projects.\n\n"
            "A project must be onboarded on the server before rooms can be "
            "pushed to it.",
            title="Roommate - no projects", warn_icon=True)
        return None

    # Label by display name, disambiguating a shared one with its id. Names are
    # free-form (unlike ids, which the server enforces unique across settings
    # files), so two projects CAN share one -- and the selection comes back from
    # the form as its label string, so duplicate labels would silently resolve
    # to whichever project was found first. Only the collided labels carry the
    # id, mirroring how the server flags ambiguous buildings rather than
    # decorating everything.
    name_counts = {}
    for p in projects:
        name_counts[p["name"]] = name_counts.get(p["name"], 0) + 1

    by_label = {}
    for p in projects:
        label = p["name"]
        if name_counts[label] > 1:
            label = "{} ({})".format(p["name"], p["id"])
        by_label[label] = p

    selected = forms.SelectFromList.show(
        sorted(by_label.keys()),
        title="Select a project to push to",
        button_name="Push to this project",
        multiselect=False)
    if not selected:
        return None

    project = by_label.get(selected)
    if project is None:
        return None

    return {"id": project["id"], "name": project["name"]}


def rooms_export_entry(doc, uiapp, output, forms):

    """
    Exports rooms from the current Revit document to a JSON file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms

    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # ask user to select active or linked document
        selected_docs = pick_document(doc, forms, button_name="Select model to collect room data from", multiselect=True)
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
                    export_and_post_model(selected_doc, project, return_value, pb)
                except Exception as e:
                    return_value.update_sep(
                        False, "{}: failed with exception: {}".format(selected_doc.Title, e)
                    )

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    break

    except Exception as e:
        return_value.update_sep(
            False, "Failed to export room data with exception: {}".format(e)
        )
        print("Failed to export room data with exception: {}".format(e))

    print("Finished")

    return return_value


def export_and_post_model(selected_doc, project, return_value, pb):
    """Export one model's rooms and levels and push them to the server under
    the picked `project` ({"id", "name"}), recording the outcome on
    `return_value`. Raises on export/envelope failures -- the caller catches
    per model so one bad model doesn't abandon the rest."""

    # get room data
    room_data = get_all_room_data(selected_doc)
    # get level data
    level_data = get_all_level_data(selected_doc)

    # v4 identity envelope (STRATEGY.md "Identity"). The project block comes
    # from the run's picked project (choose_project), NOT the Revit document:
    # the id must match a settings bundle the server has registered or the push
    # 422s, and it becomes a storage path key -- a Revit-derived guess can't
    # guarantee either. Model id is a known stopgap: Title, not a GUID -- no
    # stable GUID source exists in duHast for a plain local (non-workshared,
    # non-cloud) file. Two consequences of keying on Title: two different files
    # that share a Title collide into ONE model record on the server, and
    # renaming a file forks its history into a new record. If duHast ever
    # exposes Document.CreationGUID / worksharing GUIDs, switch to those.
    #
    # taken_at carries microseconds: it becomes the snapshot
    # filename server-side, so two pushes of the same model within
    # one second must not collide (the server skips a duplicate
    # timestamp rather than overwriting, but the client shouldn't
    # produce one in normal use). %f is fixed-width, so the string
    # stays lexically sortable -- the server's "lexical max =
    # newest" rule depends on that.
    envelope = {
        "project": {
            "id": project["id"],
            "name": project["name"],
        },
        "model": {
            "id": selected_doc.Title,
            "name": selected_doc.Title,
        },
        "snapshot": {
            "taken_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
    }

    # Model->shared placement transform (HANDOVER-georeferencing.md Phase 1).
    # Read ONCE per model from the document's shared coordinates
    # (ActiveProjectLocation) -- a model-level fact, the same relationship duHast
    # otherwise stamps onto every room polygon, so there is nothing to reconcile
    # across rooms. Reduced to the 2D affine the server's `ModelToShared`
    # carries, and stamped on the envelope (so both the buffered and the
    # streaming push carry it -- the streaming path builds its envelope from this
    # dict minus the room list). Advisory and optional: if the read fails, omit
    # it and still push; the model renders via auto-fit exactly as before, and an
    # identity transform (an un-surveyed model) is emitted normally.
    try:
        rotation, translation = get_coordinate_system_translation_and_rotation(selected_doc)
        envelope["model_to_shared"] = {
            "matrix": coordinate_system_to_affine(rotation, translation),
        }
    except Exception as e:
        return_value.append_message(
            "{}: could not read shared-coordinate transform ({}); "
            "pushing without a georeference".format(selected_doc.Title, e)
        )

    # Which boundary regime this model was drawn to
    # (Superseded/HANDOVER-areas-boundary-location.md Decision 1). Read ONCE per
    # document from Area and Volume Computations, and stamped on the envelope
    # alongside the transform above -- a document setting, so each linked model
    # reports its own, which is why the field is per model and a project-level
    # declaration could only ever be a fallback. Reading a document option is
    # extraction, not computation (STRATEGY.md "Keep the extractor dumb on
    # purpose"): what the regime then MEANS for a wall zone is the server's.
    #
    # Advisory and optional, exactly like the transform: if the setting can't be
    # read, or is one the contract has no regime for, say nothing and still push
    # -- the server falls back to the project's `[areas] boundary_location`,
    # which is what every push did before this field was sent. Both misses are
    # reported rather than swallowed, because "the regime was guessed" is the
    # thing this field exists to stop being silent.
    try:
        location = AreaVolumeSettings.GetAreaVolumeSettings(
            selected_doc
        ).GetSpatialElementBoundaryLocation(SpatialElementType.Room)
        room_boundary = boundary_location_to_room_boundary(location)
        if room_boundary is None:
            return_value.append_message(
                "{}: room boundary location '{}' has no contract regime; "
                "pushing without a declared boundary".format(selected_doc.Title, location)
            )
        else:
            envelope["room_boundary"] = room_boundary
    except Exception as e:
        return_value.append_message(
            "{}: could not read the room boundary location ({}); "
            "pushing without a declared boundary".format(selected_doc.Title, e)
        )

    # a large export takes a while -- honour a cancel clicked
    # during it before starting the (also slow) post; the caller
    # re-checks pb.cancelled after this returns and stops the loop
    if pb.cancelled:
        return

    # convert into a dictionary
    dic_room_data = {
        dr.DataRoom.data_type:room_data
    }
    dic_room_data.update(envelope)

    # add some more properties before writing to json
    json_formatted_room = build_json_for_file(dic_room_data, "{}".format(selected_doc.Title))

    # convert into a dictionary. The envelope is deep-copied for
    # this second use: .update() shares the nested project/model/
    # snapshot dict instances, and the two exports must not be able
    # to cross-contaminate if anything downstream mutates its input.
    dic_level_data = {
        dl.DataLevelBuilding.data_type:level_data
    }
    dic_level_data.update(copy.deepcopy(envelope))

    # add some more properties before writing to json
    json_formatted_level = build_json_for_file(dic_level_data, "{}".format(selected_doc.Title))

    # post to the server: gzip-compressed NDJSON stream, so a
    # >100 MB FFE export never gets buffered whole client-side or
    # server-side (see roommate's HANDOVER-streaming*.md).
    # A failed push flips the overall Result red but does NOT abort
    # the caller's loop -- one bad model shouldn't discard the other
    # models' successful pushes, the run just must not end green.
    ok, status, text = post_payload_stream(json_formatted_room, json_formatted_level)
    if ok:
        return_value.append_message(
            "{}: server accepted ({})".format(selected_doc.Title, text)
        )
    else:
        return_value.update_sep(
            False,
            "{}: push failed ({}): {}".format(selected_doc.Title, status, text),
        )