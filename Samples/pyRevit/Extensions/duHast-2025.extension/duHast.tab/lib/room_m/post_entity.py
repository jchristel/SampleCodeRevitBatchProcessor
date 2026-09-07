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
The push side of ANY entity -- both transports, the envelope, the phase filter
and the empty-push refusal -- written once and bound to an entity by
`EntityPush`.

**This was `post_entity` until FF&E arrived, and the rename is the finding.**
Doors and windows differ in four values and nothing else, because their RECORD
is identical -- measured on two real documents, not assumed. That made "an
opening push" a coherent thing to write once. An FF&E item is a different
record, so the module had a choice: a second copy of the transport, or admit
that the transport was never about openings. It was not. Everything from
building the envelope to posting gzipped NDJSON is the same for any entity; the
only thing that ever varied is how one raw export element becomes one contract
element, and that is now `EntityPush.translate`.

The same split the server made at the same time, for the same reason and with
the same shape: `service::entity_scope` holds what every entity's read shares,
and `service::items` holds what an item does differently. Here `post_ffe` holds
the FF&E translation and this file holds the rest.

**What stays per entity lives in `post_doors`, `post_windows` and `post_ffe`**,
which are little more than an `EntityPush` each plus their own module docstring.
The docstrings are not ceremony: the reasoning that made each entity's rules is
the expensive part, and it is genuinely per entity even where the code is not.

Nothing here is Revit-facing. The extraction side lives in `room_m.utils`.
"""

import json

from collections import namedtuple

from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue

from room_m.post_common import (
    build_identity_envelope,
    duhast_object_to_plain,
    duhast_objects_to_plain,
    empty_push_refusal,
    loop_to_points,
    properties_to_map,
    translate_levels,
    write_ndjson_line,
    _post_content,
)

from room_m.utils.phase_filter import (
    in_selected_phase,
)


# Everything that varies between one entity's push and another's.
#
# A table rather than a subclass or a set of arguments, for the reason
# `room_mate.ENTITY_EXPORTERS` is one: the differences are DATA, and writing them
# as data keeps the code below free of any test on which entity is being pushed.
#
# `translate` is the one field that is a function rather than a value, and it is
# the field FF&E added. Doors and windows share a translation because they share
# a record; an item does not, so the choice was a second copy of both transports
# or one more field here. `translate(plain_element, contribution)` takes the raw
# export element already converted to plain types, plus the whole contribution --
# not just the placements -- because what an entity needs from the extraction
# pass is itself per entity: an opening wants room references and a facing read
# from Revit, an item wants its category and its one room.
EntityPush = namedtuple(
    "EntityPush",
    ["entity", "list_key", "schema_version", "url", "url_stream", "nested_reason", "translate"],
)


# Revit's *uninitialized* BoundingBoxXYZ: min +1e30, max -1e30. duHast returns
# one for a family it cannot measure, and its own "did we get a box" and "is the
# loop non-empty" guards both pass -- so the bad value arrives looking like a
# real footprint rather than an absent one.
#
# Tested by magnitude rather than equality with 1e30: the value crosses a float
# round-trip, and the point is to catch the class rather than one bit pattern.
# There is no ambiguity to worry about -- a real model is measured in feet, so
# nothing legitimate is within twenty orders of magnitude of this.
SENTINEL_MAGNITUDE = 1e20


def is_degenerate(loop):
    """Whether a loop is the empty-bounding-box sentinel rather than geometry."""
    return any(abs(coord) >= SENTINEL_MAGNITUDE for point in loop for coord in point)


def loops_from_polygon(polygons):
    """Map a duHast polygon onto the contract's `loops` -- the ROOM convention
    verbatim: `[0]` outer, `[1..]` holes, decimal feet, model space, Y up. One
    renderer and one `model_to_shared` transform then serve every entity.

    Returns `[]` for an opening with no usable footprint, which the contract
    carries deliberately (`Opening.loops`). **Not** `None`: unlike an unplaced
    room, which `translate_room` drops because there is nothing to draw, a
    geometry-less opening still has properties and both room references, so it
    is a real element QA must see. Dropping it would silently lose a
    opening->room link from the report that link exists for.

    The degenerate case is why this is a function rather than a field copy: a
    family duHast cannot measure yields Revit's uninitialized bounding box, and
    pushing it would hand every consumer a polygon 1e30 feet across."""
    if not polygons:
        return []
    poly = polygons[0]
    outer = poly.get("outer_loop") or []
    if not outer or is_degenerate(outer):
        return []
    loops = [{"points": loop_to_points(outer)}]
    for inner in poly.get("inner_loops") or []:
        if inner and not is_degenerate(inner):
            loops.append({"points": loop_to_points(inner)})
    return loops


def stamp_levels(contribution):
    """This document's levels for its envelope block.

    A thin named wrapper so the two push paths cannot drift on where the list
    comes from, and so an older contribution -- one built before an entity
    carried levels, as the fixture generators still do -- yields `[]` rather
    than raising. Empty is a legal value the server reads as "ask the rooms
    snapshot", which is what every model with rooms wants anyway."""
    levels_source = contribution.get("levels")
    if not levels_source:
        return []
    return translate_levels(duhast_objects_to_plain(levels_source))


def build_envelope(spec, run_envelope, model_blocks):
    """Everything the contract needs EXCEPT the elements.

    Which is the shared identity block plus whatever the caller already stamped
    onto each block -- `levels` among them. No `room_boundary`: that stays a
    rooms fact no opening contract has a key for.

    Kept as a named function rather than inlined into its callers so an entity's
    schema version is stated once, and so the streaming and buffered paths cannot
    end up building different envelopes."""
    return build_identity_envelope(run_envelope, model_blocks, spec.entity, spec.schema_version)


def translate_opening(opening, placements):
    """Map one duHast object onto the `Opening` shape, or return None when it
    carries no id (nothing downstream could key on it).

    `placements` is `{id: {"from_room", "to_room", "insertion_point",
    "normal"}}`, built by `room_m.utils.openings.opening_placements` from the
    Revit API. **Everything in it is read from Revit rather than from the
    export**, and for two different reasons.

    The room references, because the export's own are unusable:

    1. They are arrays holding one entry per phase, tagged with a `phase_id`
       that appears nowhere else in the file and cannot be resolved against
       anything on the wire -- the blocker STRATEGY-ENTITIES records.
    2. `FamilyInstance.FromRoom[phase]` takes the phase and answers exactly one
       room, so asking Revit is both correct and simpler than reconciling an
       array against a phase table that isn't there.

    The position and direction, because they must agree with those references.
    `through_wall_normal` points from the from-room to the to-room, and it is
    `FacingOrientation` -- the same orientation `ToRoom` itself follows. Read
    from one API pass over one phase, the four values cannot describe different
    states of the same element.

    An opening absent from `placements` gets `None` for all four rather than
    raising: that is the honest reading (nothing was resolved) and the server's
    QA reports it as an opening with no room reference, which is exactly where a
    reader should see it. For a facade model that is EVERY element -- 0 of 158
    windows and 0 of 191 doors carried a reference when it was measured, because
    Revit cannot resolve a room across a link -- so this path is the ordinary
    one there, not an error path."""
    instance = opening.get("instance_properties") or {}
    opening_id = instance.get("id")
    if opening_id is None:
        return None
    opening_id = str(opening_id)

    type_props = opening.get("type_properties") or {}
    level = opening.get("level") or {}
    placement = placements.get(opening_id) or {}

    return {
        "id": opening_id,
        "level_id": str(level.get("id", "unknown")),
        "loops": loops_from_polygon(opening.get("polygon")),
        "from_room": placement.get("from_room"),
        "to_room": placement.get("to_room"),
        # Both are sent even when null. The contract accepts their absence (old
        # snapshots predate them) but this producer states what it found either
        # way -- "Revit had no plan direction for this element" and "this
        # producer is too old to have looked" are different facts, and a key
        # that is simply missing cannot tell them apart.
        "insertion_point": placement.get("insertion_point"),
        "through_wall_normal": placement.get("normal"),
        "type_id": str(type_props.get("id", "unknown")),
        "type_name": type_props.get("name", "Unknown Type"),
        "properties": properties_to_map(instance),
        "type_properties": properties_to_map(type_props),
    }


def translate(spec, run_envelope, entries):
    """Map a run's duHast exports onto the contract as one whole payload. The
    buffered counterpart of `post_stream`, kept for the same reasons
    `post_rooms.translate` is: small manual pushes and fixture generation.

    `entries` is `[(model_block, contribution), ...]`, one per document."""
    blocks = [dict(block) for block, _ in entries]
    contract = build_envelope(spec, run_envelope, blocks)
    for model, (_, contribution) in zip(contract["models"], entries):
        model["levels"] = stamp_levels(contribution)
        source = duhast_object_to_plain(contribution["elements"])
        out = []
        nested_ids = contribution.get("nested_ids") or set()
        for raw in source.get(spec.list_key, []):
            element = spec.translate(raw, contribution)
            if element is None or element["id"] in nested_ids:
                continue
            if in_selected_phase(element, contribution["allowed_ids"]):
                out.append(element)
        model[spec.entity] = out
    return contract


def post_stream(spec, run_envelope, entries, url=None):
    """Gzip-compress an NDJSON stream (line 1 = envelope, one line per element)
    to the server's streaming ingest, translating one element at a time as it is
    read off the raw export.

    Openings are far fewer than rooms per model, so this is not load-bearing the
    way the room stream is. It is used anyway so one transport serves every push
    -- a producer that streamed rooms and buffered openings would be two code
    paths to keep working for no gain. Returns `(ok, status, text)`.

    Every element line names its own model, for the reason
    `post_rooms.post_payload_stream` gives.

    Sends nothing when no element reaches the wire **across the whole run**,
    counted as the stream is written. See each entity's module docstring for why
    this is stricter than the server, and why the run rather than the model is
    the scope that makes it honest."""
    url = url or spec.url_stream
    blocks = [dict(block) for block, _ in entries]
    for block, (_, contribution) in zip(blocks, entries):
        block["levels"] = stamp_levels(contribution)
    envelope = build_envelope(spec, run_envelope, blocks)

    raw = 0
    no_id = 0
    nested = 0
    out_of_phase = 0
    written = 0

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for block, (_, contribution) in zip(blocks, entries):
            model_id = block["id"]
            nested_ids = contribution.get("nested_ids") or set()
            for raw_element in contribution["elements"].get(spec.list_key, []):
                raw += 1
                element = spec.translate(duhast_object_to_plain(raw_element), contribution)
                if element is None:
                    no_id += 1
                    continue
                # Before the phase test, because a nested component is not an
                # opening in any phase -- counting it as out-of-phase would
                # misreport why the export shrank.
                if element["id"] in nested_ids:
                    nested += 1
                    continue
                if not in_selected_phase(element, contribution["allowed_ids"]):
                    out_of_phase += 1
                    continue
                written += 1
                element["model_id"] = model_id
                write_ndjson_line(gz, element)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    if written == 0:
        return empty_push_refusal(spec.entity, envelope, raw, [
            (no_id, "carrying no element id"),
            (nested, spec.nested_reason),
            (out_of_phase, "outside phase '{}'".format(envelope["phase"])),
        ])

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)


def post_buffered(spec, run_envelope, entries, url=None):
    """Buffered counterpart of `post_stream`. Returns `(ok, status, text)`."""
    url = url or spec.url
    contract = translate(spec, run_envelope, entries)

    # Guarded here rather than in `translate`, matching `post_rooms.post_payload`:
    # translating an empty set is a legitimate thing to ask for, pushing one is
    # not. Counted across the run, matching the streaming path.
    if not sum(len(model[spec.entity]) for model in contract["models"]):
        raw = sum(
            len(duhast_object_to_plain(c["elements"]).get(spec.list_key, [])) for _, c in entries
        )
        return empty_push_refusal(spec.entity, contract, raw, [])

    from System.Net.Http import StringContent
    from System.Text import Encoding

    # ensure_ascii=False, as `write_ndjson_line` and `post_rooms.post_payload`
    # both do: escaping a non-ASCII character under IronPython 2.7 decodes with
    # the system code page and aborts the push. StringContent does it properly.
    body = json.dumps(contract, ensure_ascii=False)
    return _post_content(url, StringContent(body, Encoding.UTF8, "application/json"))
