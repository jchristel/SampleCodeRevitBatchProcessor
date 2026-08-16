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

import datetime

from duHast.Revit.Common.Geometry.geometry import get_coordinate_system_translation_and_rotation

from room_m.post_common import (
    coordinate_system_to_affine,
)

# The direct Revit API use in this module: the room boundary regime is a
# document *setting* duHast has no collector for.
from Autodesk.Revit.DB import (
    AreaVolumeSettings,
    SpatialElementType,
)


# Revit's document-level room boundary location (Area and Volume Computations)
# mapped onto the two regimes the contract knows (contract.rs `RoomBoundary`).
# Keyed by the *name* of `SpatialElementBoundaryLocation` rather than by the enum
# members themselves: `add_room_boundary` reads the setting off the document and
# this decides what it means on the wire, and a name lookup does not care whether
# a given Revit version exposes every member of that enum.
#
# The server's distinction is only "do neighbouring rooms tile, or is there a
# real gap between them". Both centre variants put both rooms' boundaries on the
# same line, so the gap is zero and there is nothing to bridge; both face
# variants leave the wall -- or its core -- standing between them, so the gap is
# real and positive. Which face it is doesn't change the regime, only how wide
# the gap is, and how wide a gap still counts as a wall is project policy
# (`[areas] max_wall_thickness`), not a producer fact.
BOUNDARY_LOCATION_TO_WIRE = {
    "Center": "centreline",
    "CoreCenter": "centreline",
    "Finish": "finish_face",
    "CoreBoundary": "finish_face",
}


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


def boundary_location_to_room_boundary(location):
    """Map a `SpatialElementBoundaryLocation` (the enum, or its name) onto the
    contract's `room_boundary` -- `"centreline"` or `"finish_face"` -- or None
    when the value isn't one this knows.

    None means "say nothing", never "guess". An absent `room_boundary` is a
    designed-for state: the server falls back to the project's `[areas]
    boundary_location` and then to finish face. Inventing a regime here would
    instead size the server's wall zone off a value nobody declared, and the
    whole point of the field is that the regime stops being a guess."""
    return BOUNDARY_LOCATION_TO_WIRE.get(str(location))


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
