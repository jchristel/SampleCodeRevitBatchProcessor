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


from room_m.utils.generic import (
    document_phases,
)

from room_m.post_common import (
    fetch_projects,
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


def choose_phase(selected_docs, forms):
    """The one phase every selected document will be filtered to, by name, or
    `None` to abort the run.

    **Prompted once, not once per document.** `pick_document` is multiselect and
    phases are per-document, so prompting per model would mean five dialogs for
    five models. Instead the choice is offered over the phase names *common to
    every selected document*, and each document then resolves that name against
    its own phases (`room_m.utils.rooms.rooms_in_phase`) - which is exactly why
    identity is the name and not the id.

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