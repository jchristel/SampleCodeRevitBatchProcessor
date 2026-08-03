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

# The direct Revit API use in this script. duHast exports elements; the room
# boundary location is a document *setting* it has no collector for, and phase
# membership needs the document's phase *ordering*, which nothing else has.
from Autodesk.Revit.DB import (
    AreaVolumeSettings,
    BuiltInCategory,
    BuiltInParameter,
    FilteredElementCollector,
    SpatialElementType,
)

from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Rooms.Export.to_data_room import get_all_room_data
from duHast.Revit.Doors.Export.to_data_door import get_all_door_data
from duHast.Revit.Levels.Export.to_data_level_building import get_all_level_data
from duHast.Revit.Common.Geometry.geometry import get_coordinate_system_translation_and_rotation
from duHast.Utilities.Objects.result import Result
from duHast.Data.Objects.Collectors import data_room as dr
from duHast.Data.Objects.Collectors import data_door as dd
from duHast.Data.Objects.Collectors import data_level_building as dl
from duHast.Data.Utils.data_to_file import build_json_for_file
from duHast.pyRevit.UI.doc_selector import pick_document
from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

from room_m.post_rooms import (
    post_payload_stream,
    fetch_projects,
    coordinate_system_to_affine,
    boundary_location_to_room_boundary,
)
from room_m.post_doors import post_doors_stream


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


def element_id_str(element_id):
    """An ElementId as the string the wire uses. `.Value` is the modern API;
    `.IntegerValue` is what older Revit exposes, and this script has to run on
    both, so neither name is hard-coded."""
    value = getattr(element_id, "Value", None)
    if value is None:
        value = getattr(element_id, "IntegerValue", None)
    return str(value)


def document_phases(doc):
    """This document's phases as an ORDERED list of `{"id", "name"}`.

    The order is the entire point: "does this element exist in phase X" is a
    range test over the phase *sequence*, not an equality check, and `doc.Phases`
    is the only place that sequence exists. Ids are per-document (the same phase
    name has a different id in every model), so the name is what crosses between
    documents and the id is only ever used within one."""
    return [{"id": element_id_str(p.Id), "name": p.Name} for p in doc.Phases]


def exists_in_phase(created, demolished, selected):
    """Revit's phase-membership rule, on phase *sequence indices*:

        created <= selected AND (demolished invalid OR demolished > selected)

    `None` for `demolished` is the "invalid phase id" case - an element that was
    never demolished - which is why an unknown index reads as "still standing"
    rather than as a failure.

    **Not `created == selected`.** Equality would drop every element built in an
    earlier phase and still standing, which on a phased model is most of them.
    That mistake will not show up against a single-phase model, where the two
    agree exactly - which is what makes it worth naming here.

    A `created` that resolves to no known phase excludes the element: it cannot
    be placed in the sequence, so it cannot be shown to be in scope."""
    if created is None or created > selected:
        return False
    return demolished is None or demolished > selected


def choose_phase(selected_docs, forms):
    """The one phase every selected document will be filtered to, by name, or
    `None` to abort the run.

    **Prompted once, not once per document.** `pick_document` is multiselect and
    phases are per-document, so prompting per model would mean five dialogs for
    five models. Instead the choice is offered over the phase names *common to
    every selected document*, and each document then resolves that name against
    its own phases (`rooms_in_phase`) - which is exactly why identity is the
    name and not the id.

    A document lacking the chosen name fails loudly later rather than being
    quietly skipped. No common name at all is a hard stop: there is no single
    phase the run could be scoped to, and pushing per-document phases from one
    run would mean silently mixing them."""
    per_doc = []
    for d in selected_docs:
        per_doc.append([p["name"] for p in document_phases(d)])

    if not per_doc or not per_doc[0]:
        forms.alert("No phases found in the selected model(s).",
                    title="Roommate - push aborted", warn_icon=True)
        return None

    # Ordered by the first document's phase sequence, so the list a user sees
    # runs oldest-to-newest rather than alphabetically.
    common = [name for name in per_doc[0] if all(name in names for names in per_doc[1:])]
    if not common:
        forms.alert(
            "The selected models share no common phase name, so there is no "
            "single phase this push could be scoped to.\n\n"
            "Push them in separate runs, or align the phase names.",
            title="Roommate - push aborted", warn_icon=True)
        return None

    # One shared phase means there is nothing to ask -- the common case for a
    # model that was never phased beyond "New Construction".
    if len(common) == 1:
        return common[0]

    selected = forms.SelectFromList.show(
        common,
        title="Select the phase to push",
        button_name="Push this phase",
        multiselect=False)
    return selected or None


def elements_in_phase(doc, phase_name, category):
    """The element ids of `doc`'s elements of `category` that exist in
    `phase_name`, as strings matching the ids the export carries.

    The filter runs here, client-side, because only the live document has the
    phase ordering `exists_in_phase` needs - the server never re-evaluates the
    predicate, which is why the ordered phase list is not on the wire at all.
    It also means strictly *less* extraction, the axis that actually pays.

    Generalised over the category when doors arrived: `CreatedPhaseId` and
    `DemolishedPhaseId` are `Element` members, so the predicate was never
    room-specific and duplicating it per entity would have been two places to
    get the range test wrong.

    Raises when the document has no phase of that name: a model that cannot be
    scoped to the chosen phase must fail loudly rather than push everything."""
    phases = document_phases(doc)
    order_by_name = dict((p["name"], i) for i, p in enumerate(phases))
    order_by_id = dict((p["id"], i) for i, p in enumerate(phases))

    if phase_name not in order_by_name:
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(p["name"] for p in phases))
        )
    selected = order_by_name[phase_name]

    allowed = set()
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(category)
        .WhereElementIsNotElementType()
    )
    for element in collector:
        created = order_by_id.get(element_id_str(element.CreatedPhaseId))
        demolished = order_by_id.get(element_id_str(element.DemolishedPhaseId))
        if exists_in_phase(created, demolished, selected):
            allowed.add(element_id_str(element.Id))
    return allowed

def rooms_in_phase(doc, phase_name):
    
    rooms_in_phase = []
    rooms = get_all_rooms(doc)
    
    for room in rooms:
        created_phase_name = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                room,
                BuiltInParameter.ROOM_PHASE,
                rParaGet.get_parameter_value_as_element_id,
            ),
        )
        if created_phase_name == phase_name:
            rooms_in_phase.append(element_id_str(room.Id))
    
    print("Found {} rooms in phase {}".format(len(rooms_in_phase), phase_name))
    return rooms_in_phase


def doors_in_phase(doc, phase_name):
    """The door ids in `phase_name`."""
    return elements_in_phase(doc, phase_name, BuiltInCategory.OST_Doors)


def phase_by_name(doc, phase_name):
    """This document's `Phase` object for `phase_name`.

    Needed because `FamilyInstance.FromRoom` is indexed by a *Phase*, not by a
    name or an id - and the name is what crosses between documents, so the
    lookup has to happen per document. Raises for an unknown name, on the same
    fail-loudly terms as `elements_in_phase`."""
    for phase in doc.Phases:
        if phase.Name == phase_name:
            return phase
    raise ValueError(
        "model has no phase named '{}' (it has: {})".format(
            phase_name, ", ".join(p.Name for p in doc.Phases))
    )


def _room_in_phase(door, phase, which):
    """One side of a door's room reference for a given phase, as an id string,
    or None.

    `FromRoom`/`ToRoom` exist both as a parameterless property (which uses the
    document's *current* phase - not what we want) and as a phase-indexed one.
    IronPython reaches the indexed form through the CLR's `get_` accessor;
    `door.FromRoom[phase]` binds to the parameterless value first on some
    versions, so the accessor is tried first and the indexer is the fallback.
    Same both-names-are-real discipline as `element_id_str`."""
    accessor = getattr(door, "get_" + which, None)
    room = accessor(phase) if accessor is not None else getattr(door, which)[phase]
    # A door with no room on that side is a normal state (an external door), so
    # None here is data, not a failure.
    return element_id_str(room.Id) if room is not None else None


def door_room_references(doc, phase_name):
    """`{door id: (from_room_id, to_room_id)}` for every door in `doc`, read
    from the Revit API for the chosen phase.

    **Read here rather than taken from the duHast export, deliberately.** The
    export carries `from_room`/`to_room` as arrays with one entry per phase,
    tagged with a `phase_id` that appears nowhere else in the file and cannot
    be resolved against anything on the wire - the blocker STRATEGY-ENTITIES
    records. `FromRoom[phase]` takes the phase and answers exactly one room, so
    asking Revit is both correct and simpler than reconciling an array against
    a phase table that is not there. It is also what makes the reference
    genuinely one-to-one, which is what the contract's `Option<String>` claims.

    A door whose room lookup raises is recorded as having neither reference
    rather than aborting the model: one unreadable door must not cost the other
    hundreds, and the server's QA reports it as a door with no room reference -
    visible, in the place a reader would look."""
    phase = phase_by_name(doc, phase_name)
    references = {}
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
    )
    for door in collector:
        try:
            references[element_id_str(door.Id)] = (
                _room_in_phase(door, phase, "FromRoom"),
                _room_in_phase(door, phase, "ToRoom"),
            )
        except Exception:
            references[element_id_str(door.Id)] = (None, None)
    return references


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
                    export_and_post_model(selected_doc, project, phase_name, return_value, pb)
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


def export_and_post_model(selected_doc, project, phase_name, return_value, pb):
    """Export one model's rooms and levels and push them to the server under
    the picked `project` ({"id", "name"}), scoped to `phase_name`, recording the
    outcome on `return_value`. Raises on export/envelope failures -- the caller
    catches per model so one bad model doesn't abandon the rest."""

    # Resolve the run's phase against THIS document's own phases before
    # exporting anything: the name is the identity across models, and a document
    # that doesn't have it raises here (caught per model) rather than pushing an
    # unfiltered, silently-wrong room set.
    allowed_room_ids = rooms_in_phase(selected_doc, phase_name)
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
        # The one AUTHORED envelope field: model_to_shared and room_boundary
        # below are both read off the document, but a document has many phases
        # and only the user knows which is being pushed. Required, unlike those
        # two -- the server refuses a push that declares none, because rooms
        # that were never filtered are a mix of every phase.
        "phase": phase_name,
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
    else:
        return_value.update_sep(
            False,
            "{}: push failed ({}): {}".format(selected_doc.Title, status, text),
        )
        # The doors push below would be refused anyway when the rooms push was
        # the model's first (the server requires rooms before doors), and
        # pushing doors against rooms that failed to land is not something to
        # attempt on a hunch. Stop here for this model; the caller carries on
        # with the next one.
        return

    # Doors, after rooms and only after rooms. The server refuses a doors push
    # to a model with no rooms -- a door's from_room/to_room are room ids, and
    # room ids are unique only within one model -- so the order is a hard
    # requirement, not a preference.
    export_and_post_doors(selected_doc, envelope, phase_name, return_value)


def export_and_post_doors(selected_doc, envelope, phase_name, return_value):
    """Export one model's doors and push them, reusing the room push's already
    built `envelope` (identity, phase, model_to_shared) so the two pushes cannot
    disagree about what model or phase they describe.

    Failures are recorded and swallowed rather than raised: the rooms push has
    already succeeded by the time this runs, and losing that because the door
    half failed would be the wrong trade. The run still ends red."""
    try:
        allowed_door_ids = doors_in_phase(selected_doc, phase_name)
        # Read from the Revit API, not from the export -- see
        # `door_room_references`.
        room_references = door_room_references(selected_doc, phase_name)

        door_data = get_all_door_data(selected_doc)
        dic_door_data = {dd.DataDoor.data_type: door_data}
        dic_door_data.update(copy.deepcopy(envelope))
        json_formatted_doors = build_json_for_file(dic_door_data, "{}".format(selected_doc.Title))
    except Exception as e:
        return_value.update_sep(
            False, "{}: door export failed: {}".format(selected_doc.Title, e)
        )
        return

    ok, status, text = post_doors_stream(
        json_formatted_doors, room_references, allowed_door_ids=allowed_door_ids
    )
    if ok:
        return_value.append_message(
            "{}: doors accepted ({})".format(selected_doc.Title, text)
        )
    else:
        # There is no 202 here: unlike rooms, a doors push whose phase
        # disagrees with the model is REFUSED rather than quarantined, because
        # activating it would re-phase the model while its rooms stayed behind.
        # So any non-2xx is a real failure with a message worth surfacing.
        return_value.update_sep(
            False,
            "{}: doors push failed ({}): {}".format(selected_doc.Title, status, text),
        )