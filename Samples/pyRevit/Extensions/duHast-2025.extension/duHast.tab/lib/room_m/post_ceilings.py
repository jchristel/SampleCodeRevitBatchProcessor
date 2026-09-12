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

"""Translate a run's duHast ceiling exports onto the v1 ceilings contract, and
push them.

**Send EVERY polygon, and let the consumer union them.** This is the one thing
about ceiling geometry that is not obvious, and the first answer was wrong.

`convert_solid_to_flattened_2d_points` walks the HORIZONTAL FACES of a solid,
and a slab has two -- its top and its bottom, near-identical in plan. On House A
that was the whole story: 7 of 30 ceilings exported more than one polygon, the
extras were the same face again (IoU above 0.98), and `polygon[0]` happened to
be the largest. So this module used to take the first and discard the rest.

**RHH proved that general only by accident.** Of its 48 multi-polygon ceilings
the pieces are genuinely DISJOINT. Measured against the union: taking
`polygon[0]` loses 44.0% of the ceiling's area on average and 99.2% at worst --
one 1,457 sqft ceiling whose first piece is 11 sqft -- and taking the LARGEST
piece still loses 25.7% on average, 31 of the 48 losing over 5%.

So every piece goes on the wire and `service::ceilings` unions them, which is
the one operation correct on both documents: it collapses House A's duplicated
faces back to one face and keeps RHH's separate pieces. A SUM would be wrong on
House A for exactly the reason the union is not.

The trap worth remembering past this module: a ratio of summed area to largest
area CANNOT distinguish a duplicated face from two equal disjoint pieces -- both
give `sum` about twice `largest`. Only a real overlap test separates them.

**An unmeasurable ceiling is pushed with empty `loops`, never dropped.** It
still carries a good id, level, phase and both property maps, and dropping it
would make "no such ceiling" and "a ceiling nobody could measure" identical
downstream -- the distinction duHast itself now preserves by returning the data
object with an empty polygon instead of None (fixed upstream 2026-09-10). The
server attributes such a ceiling to no room and says so.

**The level ID is duHast's, never re-derived.** `get_level_data` reads the level
the modeller assigned. The FF&E level trap is what this is avoiding: computing a
level here would silently discard a correct duHast and produce a byte-identical
bad export.

**The height OFFSET is read from Revit, and that is not the same exception.**
duHast carries it on the level block as `offset_from_level`, but as Revit's
display value -- the string `"2700"`, a rounded millimetre figure -- where this
contract wants decimal feet to match `loops`. There is no measurement to
disagree about, only a rendering to avoid parsing; see
`room_m.utils.ceilings.ceiling_offsets`, whose header makes the distinction in
full.
"""

import json

from System.Net.Http import ByteArrayContent, StringContent
from System.Net.Http.Headers import MediaTypeHeaderValue
from System.IO import MemoryStream
from System.IO.Compression import CompressionMode, GZipStream
from System.Text import Encoding

from room_m.post_common import (
    build_identity_envelope,
    loop_to_points,
    duhast_object_to_plain,
    duhast_objects_to_plain,
    properties_to_map,
    translate_levels,
    write_ndjson_line,
    _post_content,
)

from room_m.post_entity import (
    is_degenerate,
)

from room_m.utils.phase_filter import (
    in_selected_phase,
)

SERVER_URL = "http://127.0.0.1:5151/ceilings"
SERVER_URL_STREAM = "http://127.0.0.1:5151/ceilings/stream"
SCHEMA_VERSION = 1

CEILING_LIST_KEY = "ceiling"


def build_envelope(run_envelope, model_blocks):
    """Everything the v1 ceilings contract needs EXCEPT `ceilings`: the run's
    shared identity plus its `models` list, each block already carrying this
    model's `levels`.

    No `room_boundary`, unlike the spaces envelope: a boundary regime describes
    how a ROOM was drawn and is what the area service needs to know how much
    wall sits between two rooms. A ceiling is a slab with its own edges."""
    return build_identity_envelope(run_envelope, model_blocks, "ceilings", SCHEMA_VERSION)


def pieces_from_polygon(polygons):
    """Map duHast's polygon list onto the contract's `polygons` -- EVERY piece,
    each an outer ring plus its holes, in the room convention (decimal feet,
    model space, Y up).

    This is `post_entity.loops_from_polygon` widened from one piece to all of
    them; see the module docstring for the measurement that forced it. The
    degenerate guard is unchanged and applies per piece, because the
    uninitialized-bounding-box sentinel is a property of one face rather than of
    the element -- a ceiling with one bad piece and three good ones keeps the
    three.

    Returns `[]` for a ceiling with nothing measurable, which the contract
    carries deliberately: such a ceiling is still pushed, and attributes to no
    room."""
    pieces = []
    for poly in polygons or []:
        outer = poly.get("outer_loop") or []
        if not outer or is_degenerate(outer):
            continue
        loops = [{"points": loop_to_points(outer)}]
        for inner in poly.get("inner_loops") or []:
            if inner and not is_degenerate(inner):
                loops.append({"points": loop_to_points(inner)})
        pieces.append({"loops": loops})
    return pieces


def translate_ceiling(ceiling, offsets):
    """Map one duHast ceiling object onto the contract's `Ceiling` shape.

    **Never returns None.** `translate_room` drops an unplaced room because
    there is nothing to draw and nothing else a room contributes; a ceiling with
    no polygon still contributes its id, level, phase and both property tiers,
    and its absence would be indistinguishable from a ceiling nobody modelled.
    Empty `loops` is the reported state -- see the module docstring."""
    props = ceiling.get("instance_properties", {}) or {}
    type_props = ceiling.get("type_properties", {}) or {}
    level = ceiling.get("level", {}) or {}

    return {
        "id": str(props.get("id", "unknown")),
        "level_id": str(level.get("id", "unknown")),
        # NOT `level.get("offset_from_level")`. duHast carries that, but as
        # Revit's DISPLAY value -- the string "2700", a rounded millimetre
        # figure -- where the contract wants decimal feet to match `loops`.
        # `room_m.utils.ceilings.ceiling_offsets` reads the parameter itself;
        # its header explains why that is not the re-derivation CLAUDE.md
        # forbids. Absent means the export could not say, never zero.
        "height_offset": offsets.get(str(props.get("id"))),
        "polygons": pieces_from_polygon(ceiling.get("polygon", [])),
        "properties": properties_to_map(props),
        "type_properties": properties_to_map(type_props),
        "type_id": str(type_props.get("id")) if type_props.get("id") is not None else None,
        "type_name": None,
    }


def translate(run_envelope, entries):
    """Map a run's duHast ceiling exports onto the v1 contract as one whole
    payload -- the buffered `/ceilings` path.

    `entries` is `[(model_block, contribution), ...]`, one per document, as
    `room_m.exporters.ceilings.export_model` builds them."""
    blocks = []
    per_model_ceilings = []
    for block, contribution in entries:
        levels_source = duhast_objects_to_plain(contribution["levels"])
        ceilings_source = duhast_objects_to_plain(contribution["ceilings"])
        block = dict(block)
        block["levels"] = translate_levels(levels_source)
        blocks.append(block)

        out_ceilings = []
        for ceiling in ceilings_source.get(CEILING_LIST_KEY, []):
            out_ceiling = translate_ceiling(ceiling, contribution["offsets"])
            if in_selected_phase(out_ceiling, contribution["allowed_ids"]):
                out_ceilings.append(out_ceiling)
        per_model_ceilings.append(out_ceilings)

    contract = build_envelope(run_envelope, blocks)
    for model, out_ceilings in zip(contract["models"], per_model_ceilings):
        model["ceilings"] = out_ceilings
    return contract


def post_payload(run_envelope, entries, url=SERVER_URL):
    """Translate and POST the whole v1 contract as one buffered JSON body.

    Returns `(ok, status, text)`. The empty-push refusal lives in
    `exporters.ceilings.post_bucket`, not here, for `post_doors`' reason: it is
    a statement about the RUN rather than about one payload."""
    contract = translate(run_envelope, entries)

    # ensure_ascii=False for the reason `write_ndjson_line` records: under
    # IronPython 2.7 escaping a non-ASCII character means decoding a byte
    # oriented str with the system code page first, which fails on bytes like
    # 0xAE and takes the whole push with it.
    body = json.dumps(contract, ensure_ascii=False)

    content = StringContent(body, Encoding.UTF8, "application/json")
    return _post_content(url, content)


def post_payload_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Gzip-compressed NDJSON stream (line 1 = envelope, one line per ceiling).

    **Every ceiling line names its own model**, for `post_rooms`' reason: a
    dropped or reordered line would otherwise file a ceiling under the wrong
    model -- and for this entity that is worse than a mislabelled row, because
    the room attribution is geometric and a ceiling filed under the wrong model
    is attributed against the wrong model's rooms.

    Returns `(ok, status, text)`."""
    blocks = []
    for block, contribution in entries:
        block = dict(block)
        block["levels"] = translate_levels(duhast_object_to_plain(contribution["levels"]))
        blocks.append(block)
    envelope = build_envelope(run_envelope, blocks)

    out = MemoryStream()
    try:
        # leaveOpen defaults False: closing gz flushes the gzip footer into `out`.
        gz = GZipStream(out, CompressionMode.Compress)
        write_ndjson_line(gz, envelope)
        for block, (_, contribution) in zip(blocks, entries):
            model_id = block["id"]
            for ceiling in contribution["ceilings"].get(CEILING_LIST_KEY, []):
                out_ceiling = translate_ceiling(
                    duhast_object_to_plain(ceiling), contribution["offsets"]
                )
                if not in_selected_phase(out_ceiling, contribution["allowed_ids"]):
                    continue
                out_ceiling["model_id"] = model_id
                write_ndjson_line(gz, out_ceiling)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)
