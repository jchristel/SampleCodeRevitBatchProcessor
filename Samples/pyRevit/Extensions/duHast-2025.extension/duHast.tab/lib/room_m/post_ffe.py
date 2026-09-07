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
The FF&E push: the item translation, plus the four values FF&E answers
differently. Both transports, the envelope and the empty-push refusal are
`room_m.post_entity`.

**This is the first entity to bring its own translation**, and it is why
`post_entity` has a `translate` field at all. Doors and windows share one
because they share a record; an item does not, and the four differences below
are all in what one raw export element becomes.

What is genuinely different about FF&E, and why:

- **Schema version 1**, independent of rooms' 7, doors' 2 and windows' 1. A
  version records a contract's OWN history and this one has none. Four
  entities, four version lines.

- **The position arrives in MILLIMETRES and is converted here.** duHast's
  `location_point.translation_coord` goes through `convert_XYZ_to_point3`,
  which converts; the polygon path goes through `get_point_as_doubles`, which
  does not. So one exported record holds a footprint in feet and a position in
  mm, six inches apart in the same object. Measured rather than read: 643 House
  A instances measured twice gave a median ratio of 304.8 exactly. `MM_PER_FOOT`
  below is named rather than written as a bare `/ 304.8`, because a silent unit
  mix is how `LEVEL_EPS_FT` came to mean half a millimetre.

- **The rotation is read from the export, not from Revit.** `rotation_coord` is
  a 3x3 matrix whose rows are the instance's basis vectors in world space, and
  BasisX projected to plan is the facing. `FamilyInstance.FacingOrientation`
  would give the same answer from the live document, and asking for it would be
  the mistake the door footprint cost two attempts to learn: an extractor that
  computes what the export already carries silently discards whatever the
  producer sent.

- **`category` is supplied by the extractor**, because `DataItem` has no field
  for it -- the one place this producer adds something the export does not have.
  Not an exception to the rule above: the export does not carry it at all, so
  this fills a gap rather than choosing between two answers.

- **Components are pushed, not filtered.** `super_component_id` rides every
  item and the server's `[ffe] nested_components` decides at read time. 179 of
  647 House A instances are components; dropping them here would put the count
  where nobody can see it, which is exactly how 2236 hardware "doors" stayed
  invisible on one job. `nested_reason` below is therefore never reached, and
  says so.

- **An empty FF&E push is refused here, though the server accepts one.** The
  asymmetry every entity has, for the reason `post_doors` records: the server
  cannot tell a base-build shell from a broken export, and this side can,
  because it knows how many the export held. **Scoped to the RUN, not to one
  model** -- asked per model, a furniture-free plantroom level in a multiselect
  run would redden an otherwise clean run.

Returns the same `(ok, status, text)` tuple shape as every other push, so the
caller's `Result` tracking is identical.

ASCII only: IronPython 2.7 will not parse a file containing an em-dash.
"""

import math

from room_m.post_common import (
    properties_to_map,
)

from room_m.post_entity import (
    EntityPush,
    loops_from_polygon,
    post_buffered,
    post_stream,
    translate as translate_entity,
)


# Millimetres per foot. Named because the export mixes the two units in one
# record and a bare divisor in the middle of a translation is how the mix stops
# being visible -- see the module docstring.
MM_PER_FOOT = 304.8


def plan_point_from_mm(translation):
    """`{"x", "y"}` in decimal feet from duHast's millimetre `translation_coord`,
    or None.

    Z is dropped: the contract's geometry is 2D plan space throughout and the
    level already says which floor this is on -- the same thing
    `opening_insertion_point` does with Revit's `LocationPoint`."""
    if not isinstance(translation, dict):
        return None
    x = translation.get("x")
    y = translation.get("y")
    if x is None or y is None:
        return None
    try:
        return {"x": float(x) / MM_PER_FOOT, "y": float(y) / MM_PER_FOOT}
    except (TypeError, ValueError):
        return None


def facing_from_rotation(rotation):
    """The instance's own X axis projected to plan and normalised, as
    `{"x", "y"}`, or None.

    `rotation_coord` is duHast's `Matrix`: `{"rows", "columns", "data"}` with
    `data` holding one row per basis vector, in world space. Row 0 is BasisX,
    which is the direction the family's own X points -- its facing.

    None when the facing has no plan component at all, which happens for an
    instance whose local X points along Z. Returned rather than normalised out
    of a zero-length vector, because the honest answer is that this item has no
    in-plan direction and the contract says a consumer must then draw no
    orientation rather than guess one. Same rule
    `opening_through_wall_normal` states, for the same reason.

    **Common enough to matter: 44 of 644 House A items have no plan facing.**
    Measured by running this translation over the captured export, which is also
    how the number for a door was got. A consumer that assumed every item had an
    orientation would be wrong about 7% of a house."""
    if not isinstance(rotation, dict):
        return None
    rows = rotation.get("data")
    if not rows:
        return None
    basis_x = rows[0]
    if not basis_x or len(basis_x) < 2:
        return None
    try:
        x = float(basis_x[0])
        y = float(basis_x[1])
    except (TypeError, ValueError):
        return None
    length = math.sqrt(x * x + y * y)
    if length < 1e-9:
        return None
    return {"x": x / length, "y": y / length}


def translate_item(item, contribution):
    """Map one duHast `DataItem` onto the `Item` shape, or return None when it
    carries no id (nothing downstream could key on it).

    `contribution` is the whole export contribution, and what this reads out of
    it is `facts` -- `{id: {"room", "category"}}` from
    `room_m.utils.items.item_facts`. The whole contribution rather than just
    that map, because `post_entity` hands every entity the same argument and
    what each needs from it is itself per entity.

    **An item absent from `facts` gets no room and no category rather than
    raising.** That is the honest reading (nothing was resolved) and the server
    reports it as an item with no room -- visible, where a reader would look.
    It should not happen: `facts` is built from the same categories the export
    walked. If it does, the cause is the probe's category list having drifted
    from duHast's, which is the one thing that makes both counts describe
    different populations."""
    instance = item.get("instance_properties") or {}
    item_id = instance.get("id")
    if item_id is None:
        return None
    item_id = str(item_id)

    type_props = item.get("type_properties") or {}
    level = item.get("level") or {}
    location = item.get("location_point") or {}
    facts = (contribution.get("facts") or {}).get(item_id) or {}

    # duHast writes -1 for "no super component"; the sentinel is mapped here so
    # it never reaches a consumer, the same way the degenerate bounding box is
    # caught in `loops_from_polygon` rather than downstream.
    parent = item.get("super_component_id")
    if parent is None or str(parent) == "-1":
        parent = None
    else:
        parent = str(parent)

    return {
        "id": item_id,
        # duHast's answer, NOT re-derived here. It is the level the modeller
        # assigned, and it is only that since duHast 2026-09-07 -- before then
        # `to_data_item` derived it geometrically (nearest level at or below the
        # item's bounding box) and disagreed with the Properties palette on any
        # model carrying levels its items are not placed on. RHH's interior
        # models carry exactly that: reference levels mis-elevated onto other
        # storeys' heights, and 9,186 of 15,070 items in one of them exported
        # onto the wrong floor.
        #
        # **If an item ever draws on the wrong level again, check which duHast
        # the extension is running before touching this file.** Computing a
        # level here would silently discard whatever duHast sends, which is how
        # a correct upstream fix produces a byte-identical bad export -- the
        # same trap the door footprint fell into, and it is written up in
        # CLAUDE.md under "Traps in the door export".
        "level_id": str(level.get("id", "unknown")),
        # Absent rather than guessed. A category the extractor could not read is
        # an empty string, which the server's filter reports as Empty rather
        # than Absent -- the field always exists on the record.
        "category": facts.get("category") or "",
        "room": facts.get("room"),
        "insertion_point": plan_point_from_mm(location.get("translation_coord")),
        "facing": facing_from_rotation(location.get("rotation_coord")),
        # Read from the export and NOT measured here -- see the module
        # docstring. Empty stays a legal value: a family with no solid geometry
        # has no footprint, and the viewer draws it as a marker.
        "loops": loops_from_polygon(item.get("polygon")),
        "super_component_id": parent,
        "type_id": str(type_props.get("id", "unknown")),
        "type_name": type_props.get("name", "Unknown Type"),
        "properties": properties_to_map(instance),
        "type_properties": properties_to_map(type_props),
    }


FFE = EntityPush(
    entity="ffe",
    list_key="item",
    schema_version=1,
    url="http://127.0.0.1:5151/ffe",
    url_stream="http://127.0.0.1:5151/ffe/stream",
    translate=translate_item,
    # Never reached: this producer applies no nested filter, because whether a
    # component is an item is a project convention and lives in the server's
    # `[ffe] nested_components`. Stated rather than left empty so an empty push
    # cannot silently report a reason it did not use.
    nested_reason="components are not filtered by this producer",
)

# Kept as module constants because callers and tests reference them by name.
SERVER_URL = FFE.url
SERVER_URL_STREAM = FFE.url_stream
SCHEMA_VERSION = FFE.schema_version
FFE_LIST_KEY = FFE.list_key


def translate(run_envelope, entries):
    """Map a run's duHast item exports onto the v1 contract as one whole payload
    -- the buffered path, kept for small manual pushes and fixture generation.

    The streamed path is the one a real run uses, and for this entity that is
    not a preference: House A alone holds 644 items across nine categories."""
    return translate_entity(FFE, run_envelope, entries)


def post_ffe_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Stream this run's FF&E. Returns `(ok, status, text)`."""
    return post_stream(FFE, run_envelope, entries, url)


def post_ffe(run_envelope, entries, url=SERVER_URL):
    """Buffered counterpart of `post_ffe_stream`. Returns `(ok, status, text)`."""
    return post_buffered(FFE, run_envelope, entries, url)
