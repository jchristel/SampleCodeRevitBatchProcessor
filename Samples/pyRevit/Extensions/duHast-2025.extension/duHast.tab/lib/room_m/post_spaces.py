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

"""Translate a run's duHast SPACE exports onto the server's v1 spaces contract
and push them.

A sibling of `post_rooms`, not of `post_entity`, because a space is
room-shaped: it carries `levels` on its model block, it carries a boundary
regime, and it goes through the rooms equality phase filter. What it does NOT
share with `post_rooms` is the one thing that would have to become a branch --

**there is no empty-push refusal here, and its absence is the feature.**
`post_rooms` refuses to send a run that kept no rooms, because a rooms push
happens when someone exported a document that has rooms in it, so an empty one
is a producer fault. A spaces run is asking a different question. "These
services models were audited and hold no spaces" is the answer requirement 1
buys, and it is a different fact from "these models were never pushed" -- which
is a distinction only a push can record. Refusing would delete the finding at
the moment it was found. RHH has such a model (`RHH-JHA-AV-MDL-HOS`, zero
spaces), so this is measured rather than hypothetical.

Both post functions return `(ok, status, text)`, the same tuple every other
entity uses, so the caller needs no second failure channel.
"""

import json
import clr
clr.AddReference("System")
clr.AddReference("System.Net.Http")
from System.IO import MemoryStream
from System.IO.Compression import GZipStream, CompressionMode
from System.Net.Http import StringContent, ByteArrayContent
from System.Net.Http.Headers import MediaTypeHeaderValue
from System.Text import Encoding

from room_m.post_common import (
    build_identity_envelope,
    duhast_object_to_plain,
    duhast_objects_to_plain,
    find_property,
    loop_to_points,
    properties_to_map,
    translate_levels,
    write_ndjson_line,
    _post_content,
)

from room_m.utils.phase_filter import (
    in_selected_phase,
)

SERVER_URL = "http://127.0.0.1:5151/spaces"
SERVER_URL_STREAM = "http://127.0.0.1:5151/spaces/stream"
SCHEMA_VERSION = 1


SPACE_LIST_KEY = "space"


def build_envelope(run_envelope, model_blocks):
    """Everything the v1 spaces contract needs EXCEPT `spaces`: the run's shared
    identity plus its `models` list, each block already carrying this model's
    `levels` and (optionally) its `room_boundary`."""
    return build_identity_envelope(run_envelope, model_blocks, "spaces", SCHEMA_VERSION)


def translate_space(space, unplaced_ids, zero_area_ids):
    """Map one duHast space object onto the contract's `Room` shape, or return
    None for an unplaced space.

    **An unplaced space is dropped and an unenclosed one is kept**, which is the
    whole reason this is not `translate_room`. That function drops both, and
    cannot tell them apart: it decides on the outer loop alone, and both arrive
    with an empty one. The two facts that separate them are not in the export at
    all -- `room_m.utils.spaces.placement_facts` reads them from Revit -- and
    they answer different questions. An unplaced space is not in the building; an
    unenclosed one is in the building and wrong, which is a finding somebody
    wants.

    So `enclosure` is *stated* here, never inferred downstream from empty
    `loops`. Three states, because "no polygon" has two causes that look
    identical on the wire and mean opposite things:

    - `unenclosed` -- Revit reports no area. A MODEL defect.
    - `unmeasured` -- Revit reports area and duHast produced no polygon anyway.
      A PIPELINE defect, and the one the RHH probe found exactly once in 10,570
      spaces.
    - `enclosed` -- there is a footprint.

    Collapsing the first two into one flag would be the +/-1e30 sentinel again: a
    value nothing can distinguish from a real one.
    """
    props = space.get("instance_properties", {})
    space_id = str(props.get("id", "unknown"))
    if space_id in unplaced_ids:
        return None

    polygons = space.get("polygon", [])
    outer = polygons[0].get("outer_loop", []) if polygons else []

    loops = []
    if outer:
        loops.append({"points": loop_to_points(outer)})
        for inner in polygons[0].get("inner_loops", []):
            if inner:
                loops.append({"points": loop_to_points(inner)})

    if loops:
        enclosure = "enclosed"
    elif space_id in zero_area_ids:
        enclosure = "unenclosed"
    else:
        enclosure = "unmeasured"

    number = find_property(props, "Number")
    name = find_property(props, "Name") or "Space"
    label = "{} {}".format(name, number).strip() if number not in (None, "") else name

    lvl = space.get("level", {}) or {}
    level_id = str(lvl.get("id", "unknown"))

    return {
        "id": space_id,
        "name": label,
        "level_id": level_id,
        "loops": loops,
        "enclosure": enclosure,
        "properties": properties_to_map(props),
    }


def translate(run_envelope, entries):
    """Map a run's duHast space exports onto the v1 contract as one whole
    payload -- the buffered `/spaces` path.

    `entries` is `[(model_block, contribution), ...]`, one per document, as
    `room_m.exporters.spaces.export_model` builds them."""
    blocks = []
    per_model_spaces = []
    for block, contribution in entries:
        levels_source = duhast_objects_to_plain(contribution["levels"])
        spaces_source = duhast_objects_to_plain(contribution["spaces"])
        block = dict(block)
        block["levels"] = translate_levels(levels_source)
        blocks.append(block)

        out_spaces = []
        for space in spaces_source.get(SPACE_LIST_KEY, []):
            out_space = translate_space(space, contribution["unplaced_ids"], contribution["zero_area_ids"])
            if out_space is not None and in_selected_phase(out_space, contribution["allowed_ids"]):
                out_spaces.append(out_space)
        per_model_spaces.append(out_spaces)

    contract = build_envelope(run_envelope, blocks)
    for model, out_spaces in zip(contract["models"], per_model_spaces):
        model["spaces"] = out_spaces
    return contract


def post_payload(run_envelope, entries, url=SERVER_URL):
    """Translate and POST the whole v1 contract as one buffered JSON body.

    **No empty-push guard**, unlike `post_rooms.post_payload` -- see the module
    docstring. Returns `(ok, status, text)`."""
    contract = translate(run_envelope, entries)

    # ensure_ascii=False for the reason `write_ndjson_line` records: under
    # IronPython 2.7 escaping a non-ASCII character means decoding a byte
    # oriented str with the system code page first, which fails on bytes like
    # 0xAE and takes the whole push with it.
    body = json.dumps(contract, ensure_ascii=False)

    content = StringContent(body, Encoding.UTF8, "application/json")
    return _post_content(url, content)


def post_payload_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Gzip-compressed NDJSON stream (line 1 = envelope, one line per space) to
    the server's streaming ingest -- the path a live run uses.

    RHH's four services models carry 10,570 spaces between them, which is why
    the streaming path is the default here rather than an option.

    **Every space line names its own model**, for `post_rooms`' reason: a
    dropped or reordered line would otherwise file a space under the wrong
    model.

    Sends whatever the translation kept, including nothing. Returns
    `(ok, status, text)`."""
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
            for space in contribution["spaces"].get(SPACE_LIST_KEY, []):
                out_space = translate_space(
                    duhast_object_to_plain(space),
                    contribution["unplaced_ids"],
                    contribution["zero_area_ids"],
                )
                if out_space is None:
                    continue
                if not in_selected_phase(out_space, contribution["allowed_ids"]):
                    continue
                out_space["model_id"] = model_id
                write_ndjson_line(gz, out_space)
        gz.Close()  # MUST close to flush the gzip footer; do NOT skip
        body = out.ToArray()
    finally:
        out.Dispose()

    content = ByteArrayContent(body)
    content.Headers.ContentType = MediaTypeHeaderValue("application/x-ndjson")
    content.Headers.Add("Content-Encoding", "gzip")

    return _post_content(url, content)
