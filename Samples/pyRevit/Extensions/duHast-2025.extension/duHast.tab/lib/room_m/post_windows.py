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
The WINDOWS push. Almost all of it is `room_m.post_entity`; what is here is
the four values windows answer differently and the reasoning behind them.

What is genuinely different about windows, and why:

- **Schema version 1**, where doors are 2 and rooms are 7. The three lines move
  independently -- a change to one contract has nothing to say about the others.
  Windows start at 1 even though they arrive already carrying many models per
  push, the change that took rooms 6->7 and doors 1->2, because a version number
  records a contract's OWN history and this one has none. Numbering it 2 to
  signal "same generation" would claim a predecessor that never existed.

- **`levels` matters more here than it does for doors**, and the facade file is
  why. Measured 2026-09-03: 158 windows and 191 doors in a model holding not one
  room, because it links its interiors rather than containing them. The server
  looks an elevation up by `(model_id, level_id)` before it will probe an
  opening's surroundings, so without the level list every window in such a model
  is *unreachable* rather than merely unresolved -- and unreachable is the state
  that makes `[windows] room_resolution` useless exactly where it is needed
  most. Sent unconditionally, as doors send theirs: this side cannot know
  whether the server already holds rooms for the model.

- **Room references are usually absent, and that is not an error.** In the same
  facade file, 0 of 158 windows carried a reference on either side. Revit cannot
  resolve a room across a link, so `FromRoom[phase]` has nothing to answer with.
  A producer that treated the absence as a failure would refuse the model this
  entity was built for.

- **The nested filter is needed but small.** 6 of 158 windows on that model were
  components of another window -- one family, `088123_Glazing-ExteriorGlass-
  Nested`, all children of a single parent, none carrying a Mark or a room. The
  door equivalent was 113 of 205. Counted separately from the phase filter and
  reported separately in an empty push, because "not an opening" and "not in this
  phase" are different fates.

- **No curtain-wall filter, and that is measured rather than overlooked.**
  duHast discriminates curtain-wall doors and has no window equivalent, which
  was the plan's largest open risk. On the facade file it did not materialise:
  the document holds 25 curtain-panel symbols and 51 curtain-wall-hosted doors,
  and **zero** curtain-wall windows. If a model ever does hold them the filter
  belongs beside the nested one, counted the same way -- but adding it now would
  be guarding against a thing no measurement has seen.

- **An empty windows push is refused here, though the server accepts one.**
  Deliberately stricter, and the asymmetry is the point. The server must allow
  zero windows, because it cannot tell a service core or an internal floor from
  a broken export. This side answers a different question -- "someone asked for
  a windows push and there are none" -- and it knows what the server never sees:
  how many the export held and where each one went. **Scoped to the RUN, not to
  one model**, for the reason `post_doors` records: asked per model, a
  windowless document in a multiselect run reddens an otherwise clean run.

Returns the same `(ok, status, text)` tuple shape as every other push, so the
caller's `Result` tracking is identical.
"""

from room_m.post_entity import (
    EntityPush,
    post_buffered,
    post_stream,
    translate as translate_entity,
    translate_opening,
)


WINDOWS = EntityPush(
    entity="windows",
    list_key="window",
    schema_version=1,
    url="http://127.0.0.1:5151/windows",
    url_stream="http://127.0.0.1:5151/windows/stream",
    translate=lambda element, contribution: translate_opening(
        element, contribution["placements"]
    ),
    nested_reason="nested inside another window (glazing, panels, hardware)",
)

# Kept as module constants because callers and tests reference them by name.
SERVER_URL = WINDOWS.url
SERVER_URL_STREAM = WINDOWS.url_stream
SCHEMA_VERSION = WINDOWS.schema_version
WINDOW_LIST_KEY = WINDOWS.list_key


def translate(run_envelope, entries):
    """Map a run's duHast window exports onto the v1 contract as one whole
    payload -- the buffered path, kept for small manual pushes and fixture
    generation."""
    return translate_entity(WINDOWS, run_envelope, entries)


def post_windows_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Stream this run's windows. Returns `(ok, status, text)`."""
    return post_stream(WINDOWS, run_envelope, entries, url)


def post_windows(run_envelope, entries, url=SERVER_URL):
    """Buffered counterpart of `post_windows_stream`. Returns `(ok, status, text)`."""
    return post_buffered(WINDOWS, run_envelope, entries, url)
