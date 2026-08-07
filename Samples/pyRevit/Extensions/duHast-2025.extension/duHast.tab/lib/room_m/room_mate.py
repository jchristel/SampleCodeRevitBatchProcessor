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
import math

# The direct Revit API use in this script. duHast exports elements; the room
# boundary location is a document *setting* it has no collector for, and phase
# membership needs the document's phase *ordering*, which nothing else has.
from Autodesk.Revit.DB import (
    AreaVolumeSettings,
    BuiltInCategory,
    BuiltInParameter,
    FilteredElementCollector,
    Options,
    SpatialElementType,
    XYZ,
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
from room_m.post_doors import post_doors_stream, SENTINEL_MAGNITUDE


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

    **Doors only, despite the generic name.** It was written expecting to serve
    every entity, on the reasoning that `CreatedPhaseId`/`DemolishedPhaseId` are
    `Element` members so the predicate could not be room-specific. That is true
    of the API and false of the model: a room does not span a range of phases,
    it belongs to one, and running rooms through this returned nothing at all
    (see `rooms_in_phase`). The name is kept because the range test genuinely is
    category-agnostic for anything built-then-demolished; the assumption that
    every entity works that way is what did not survive.

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
    """The room ids in `phase_name`.

    **Rooms do NOT go through `exists_in_phase`, and that is the one thing to
    understand here.** The design assumed one predicate could serve every
    entity, because `CreatedPhaseId`/`DemolishedPhaseId` are `Element` members.
    Against a real document that produced *zero* rooms, five pushes running --
    exactly the "the filter silently keeps nothing" failure the plan named as
    the first thing to check.

    A room is not a thing that is built in one phase and demolished in another.
    It BELONGS to exactly one phase, named by the `ROOM_PHASE` built-in
    parameter, so membership is an equality test rather than a range test over
    the phase sequence. Doors keep the range test (`doors_in_phase`), and that
    difference is real rather than an inconsistency worth tidying away.

    Returns a `set`: `post_rooms.in_selected_phase` does one membership test per
    room, so a list makes filtering a plate quadratic."""
    order_by_name = dict((p["name"], i) for i, p in enumerate(document_phases(doc)))
    if phase_name not in order_by_name:
        # Fail loudly, on the same terms as `elements_in_phase`. Without this a
        # mistyped or renamed phase yields an empty set, which is indexed,
        # stored and served as "this model has no rooms" -- and that is not a
        # hypothetical: it is what the five empty snapshots above looked like
        # from the outside.
        raise ValueError(
            "model has no phase named '{}' (it has: {})".format(
                phase_name, ", ".join(order_by_name.keys())
            )
        )

    allowed = set()
    for room in get_all_rooms(doc):
        room_phase = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                room,
                BuiltInParameter.ROOM_PHASE,
                rParaGet.get_parameter_value_as_element_id,
            ),
        )
        if room_phase == phase_name:
            allowed.add(element_id_str(room.Id))
    return allowed


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


def door_insertion_point(door):
    """The door's plan position as `{"x", "y"}`, or None.

    Revit's `LocationPoint`, which a placed `FamilyInstance` has. Z is dropped:
    the contract's geometry is 2D plan space throughout, and the level already
    says which floor this is on.

    This is the field that keeps a *geometry-less* door on the drawing. Two of
    the 26 sample doors have no 3D geometry, so their footprint arrives empty
    (see `post_doors.loops_from_polygon`) and nothing else on the wire says
    where they are. Without this they exist in QA and in `/doors` but appear
    nowhere a reader looks at a plan, which reads as "there is no door there"
    rather than "its shape is unknown"."""
    location = getattr(door, "Location", None)
    point = getattr(location, "Point", None) if location is not None else None
    if point is None:
        return None
    return {"x": float(point.X), "y": float(point.Y)}


def door_through_wall_normal(door):
    """The unit vector through the wall, from the door's from-room toward its
    to-room, as `{"x", "y"}`, or None.

    `FamilyInstance.FacingOrientation`, projected to plan and normalised.

    **Facing, not the host wall's direction, and that is the whole point.**
    Revit's `ToRoom` follows the door's *orientation*; flipping a door in Revit
    swaps facing and `ToRoom` together, so the two are readings of one fact and
    cannot drift. Deriving the direction from the host wall would introduce a
    second source of truth that could disagree with the room references this
    same pass reads -- and therefore with the server's `owner_rooms`, which is
    computed from them.

    None when the facing has no plan component at all (a hatch in a floor: the
    vector points along Z, and its x/y are both ~0). Returned rather than
    normalised out of a zero-length vector, because the honest answer is that
    this door has no in-plan direction, and the contract says a consumer must
    then draw no arrow instead of guessing one."""
    facing = getattr(door, "FacingOrientation", None)
    if facing is None:
        return None
    x = float(facing.X)
    y = float(facing.Y)
    length = math.sqrt(x * x + y * y)
    if length < 1e-9:
        return None
    return {"x": x / length, "y": y / length}


def door_footprint(door):
    """The door's TRUE plan footprint, as four `{"x", "y"}` corners in model
    space (decimal feet, Y up), or None when it cannot be read.

    **Why this exists: the export's footprint is an axis-aligned bounding box,
    and a door in a diagonal wall is not axis-aligned.** duHast hands back
    Revit's `BoundingBoxXYZ` without applying its transform, so the rotation is
    lost before the data reaches the wire. On an orthogonal wall the box happens
    to equal the true footprint, which is why 24 of the 26 House A doors look
    correct and only the two in diagonal walls give it away -- as an upright
    rectangle sitting across a slanted wall.

    An axis-aligned box of a rotated rectangle **cannot** be un-rotated later:
    the two extents plus an angle are three unknowns against two measurements,
    and the system is degenerate at exactly 45 degrees. So no consumer can
    recover this, and the producer has to send it right.

    The fix is the standard pair. `GetOriginalGeometry` returns the family's
    geometry in the family's OWN coordinate system -- where the door is
    axis-aligned by construction, because that is how families are authored --
    and `GetTransform` is the placement that puts it in the model. Taking the
    box in family space and transforming its corners keeps the rotation that
    taking the box in model space throws away.

    Same discipline as `door_placements` reading the room references from the
    API rather than the export: where duHast's answer is lossy, ask Revit.

    None on any failure, and the caller then falls back to the export's polygon
    -- which is exactly today's behaviour, so this can only improve a door, never
    break one. A door family with no 3D geometry returns None here too, and its
    fallback is the `+/-1e30` sentinel that `loops_from_polygon` already drops."""
    try:
        geometry = door.GetOriginalGeometry(Options())
    except Exception:
        return None
    if geometry is None:
        return None

    try:
        box = geometry.GetBoundingBox()
    except Exception:
        return None
    if box is None or box.Min is None or box.Max is None:
        return None

    minimum, maximum = box.Min, box.Max
    # The same uninitialized-BoundingBoxXYZ sentinel the export path guards, and
    # the same constant rather than a second copy of the number: a family with
    # no 3D geometry reaches here too, and its box is +1e30/-1e30.
    for value in (minimum.X, minimum.Y, maximum.X, maximum.Y):
        if abs(value) >= SENTINEL_MAGNITUDE:
            return None
    if maximum.X <= minimum.X or maximum.Y <= minimum.Y:
        return None

    try:
        placement = door.GetTransform()
        # A `BoundingBoxXYZ` carries its own transform as well. It is usually
        # the identity, and composing it costs nothing when it is -- but reading
        # the corners as if it were identity when it is not would misplace the
        # door silently, which is the failure this whole function exists to stop.
        if box.Transform is not None:
            placement = placement.Multiply(box.Transform)
    except Exception:
        return None

    # Wound consistently around the box in family space; the placement is rigid,
    # so the ring stays simple and closed in model space. Z is taken from the
    # box's own floor rather than zero: the transform is 3D, and feeding it a
    # point off the family's own plane would shear the footprint on a door that
    # is not level.
    corners = (
        (minimum.X, minimum.Y),
        (maximum.X, minimum.Y),
        (maximum.X, maximum.Y),
        (minimum.X, maximum.Y),
    )
    out = []
    for x, y in corners:
        point = placement.OfPoint(XYZ(x, y, minimum.Z))
        out.append({"x": float(point.X), "y": float(point.Y)})
    return out


def door_placements(doc, phase_name):
    """`{door id: {"from_room", "to_room", "insertion_point", "normal",
    "footprint"}}` for every door in `doc`, read from the Revit API for the
    chosen phase.

    **One collector pass, five facts.** These were separate questions once and
    the room references came first; putting the placement reads here rather than
    in a second `FilteredElementCollector` walk is not micro-optimisation, it is
    what guarantees the four values describe the same door in the same phase.
    A second pass could silently disagree with this one about which elements it
    saw.

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
    visible, in the place a reader would look.

    **Each read is caught separately**, so an unreadable room reference costs
    the position, direction and footprint of that door and nothing more.
    Catching the whole door at once would have been shorter and would throw away
    four facts to lose one -- and the fact most likely to raise (the
    phase-indexed room lookup) is not the one a plan needs to draw the door."""
    phase = phase_by_name(doc, phase_name)
    placements = {}
    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
    )
    for door in collector:
        try:
            from_room = _room_in_phase(door, phase, "FromRoom")
            to_room = _room_in_phase(door, phase, "ToRoom")
        except Exception:
            from_room, to_room = None, None

        try:
            insertion_point = door_insertion_point(door)
        except Exception:
            insertion_point = None

        try:
            normal = door_through_wall_normal(door)
        except Exception:
            normal = None

        try:
            footprint = door_footprint(door)
        except Exception:
            footprint = None

        placements[element_id_str(door.Id)] = {
            "from_room": from_room,
            "to_room": to_room,
            "insertion_point": insertion_point,
            "normal": normal,
            "footprint": footprint,
        }
    return placements


ROOMS = "rooms"
DOORS = "doors"


def entities_label(entities):
    """The chosen entities as the noun phrase in "<...> data" -- singular, since
    both names are regular plurals and "rooms data" reads as a typo."""
    return " and ".join(entity[:-1] for entity in entities)


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
    :param entities: which of ROOMS / DOORS this run pushes, in push order.
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

    # A ROOMS fact, so it is read only when rooms are being pushed -- the doors
    # contract has no field for it, and reading it for a doors-only run would
    # spend a document read to produce a warning about a value nothing sends.
    if ROOMS in entities:
        add_room_boundary(selected_doc, envelope, return_value)

    # Don't begin this model's export at all if a cancel landed during the
    # previous model's post. The check that matters more is inside each push --
    # it is the export, not this, that a user waits through long enough to give
    # up during. The caller re-checks after this returns and stops the loop.
    if pb.cancelled:
        return

    if ROOMS in entities:
        if not export_and_post_rooms(selected_doc, envelope, phase_name, return_value, pb):
            return

    if DOORS in entities:
        export_and_post_doors(selected_doc, envelope, phase_name, return_value, pb)


def build_model_envelope(selected_doc, project, phase_name, return_value):
    """The envelope fields BOTH pushes carry: identity, phase, and the
    model->shared transform.

    Built once per model and handed to whichever pushes run, so a combined run
    cannot have its two halves disagree about which model, snapshot or phase
    they describe -- and so a doors-only run builds identity by exactly the same
    code as a combined one rather than by a second copy that could drift.

    `room_boundary` is deliberately NOT here: see `add_room_boundary`."""

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

    return envelope


def add_room_boundary(selected_doc, envelope, return_value):
    """Stamp the model's boundary regime onto `envelope`, if it has a readable
    one.

    Split off `build_model_envelope` rather than left beside the transform it
    otherwise resembles, because the two are not the same kind of fact. The
    transform places any geometry, doors included; the boundary regime only
    tells the server how wide a wall zone between ROOMS is, and the doors
    contract has no field to carry it. So a doors-only run skips this, and skips
    the warnings it would otherwise emit about a value nothing on the wire would
    have read."""

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


def export_and_post_rooms(selected_doc, envelope, phase_name, return_value, pb):
    """Export one model's rooms and levels and push them, reusing the already
    built `envelope`. Returns whether the push landed -- the caller gates the
    doors push on it, and a cancel reads as "didn't land" for the same reason a
    failure does: there are no rooms on the server to hang doors off.

    Raises on export failures rather than recording them, unlike its doors
    counterpart, and the asymmetry is intentional: nothing has been pushed for
    this model yet when this runs, so there is no successful half to protect.
    The caller catches per model."""

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


def export_and_post_doors(selected_doc, envelope, phase_name, return_value, pb):
    """Export one model's doors and push them, reusing the run's already built
    `envelope` (identity, phase, model_to_shared) so a combined run's two pushes
    cannot disagree about what model or phase they describe.

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
        return

    # The per-door Revit room-reference reads above are the slow part of a doors
    # push, so the same "cancel during the export, before the post" check the
    # room path makes applies here -- and applies whether or not rooms ran first.
    if pb.cancelled:
        return

    ok, status, text = post_doors_stream(
        json_formatted_doors, placements, allowed_door_ids=allowed_door_ids
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