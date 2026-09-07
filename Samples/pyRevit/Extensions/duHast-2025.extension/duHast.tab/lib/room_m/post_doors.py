"""
POC bridge for DOORS: take the duHast door export, translate to the viewer's
v1 doors contract, and POST to the Rust server.

The sibling of `post_rooms.py`, and built alongside it on a shared base rather
than on it -- the transport (`_post_content`), the duHast flattening
(`duhast_object_to_plain`), the NDJSON writer (`write_ndjson_line`) and the
identity envelope (`build_identity_envelope`) all come from `post_common.py`,
imported and never re-implemented, so the two pushes cannot drift on how they
talk to the server or on what they claim to be. This module holds only what is
doors-specific, and knows nothing about rooms.

What is genuinely different, and why:

- **The doors schema versions independently of rooms**, starting at 1. A
  change to the room contract has nothing to say about doors.
- **`levels` rides the envelope, and the reason it now does is narrow.** A
  door's `level_id` normally points into the level set its own model's ROOMS
  snapshot carries, and the server still prefers that copy - so for most models
  this list is redundant, which is the point: a redundancy cannot disagree.
  What it exists for is the model that pushes doors and *no rooms at all*, a
  facade or envelope file whose doors are real and whose rooms live in the
  interior models it links. The server looks an elevation up by
  `(model_id, level_id)` before it will probe a door's surroundings, so without
  this such a model's every door is unreachable rather than merely unresolved.
  Sent unconditionally: this side cannot know whether the server already holds
  rooms for the model, so it cannot answer "are they needed" -- see
  `room_m.exporters.doors.export_model`.
- **The room references, the position and the direction do not come from the
  export.** See `translate_door` -- all four are read from the Revit API by
  `room_m.utils.openings.opening_placements`, in one pass, which is the only side
  that can ask the questions correctly and the only way they are guaranteed to
  agree.
- **A degenerate footprint is dropped**, see `loops_from_polygon`. The bad
  value looks like real geometry, which is why it has to be caught here.
- **A door nested inside another door is dropped**, see
  `room_m.utils.openings.nested_opening_ids`. A door leaf modelled as a nested shared
  family is an independently-collectable `FamilyInstance` of category Doors, so
  the collector returns it beside the door containing it. Counted separately
  from the phase filter and reported separately in an empty push: "not a door"
  and "not in this phase" are different fates, and the refusal message exists
  precisely to stop a reader hunting the wrong one.
- **An empty doors push is refused here, though the server accepts one.**
  Deliberately stricter than `handlers.rs`, and the asymmetry is the point.
  The server must allow zero doors, because it cannot tell a shell or a
  pre-fit-out phase from a broken export. This side is not answering that
  question -- it is answering "someone asked for a doors push and there are no
  doors to push", which is worth stopping whichever of the two it turns out to
  be.

  **Scoped to the whole RUN**, which is what made the rule honest. Asked per
  model it turned a rooms-only document in a multiselect run into a failed push
  and a red run - routine, and wrong. The residual cost is unchanged and still
  accepted: a run whose documents genuinely hold no doors at all cannot record
  that fact through this producer.

Returns the same `(ok, status, text)` tuple shape as the room push, so the
caller's `Result` tracking is identical for both.
"""

from room_m.post_entity import (
    EntityPush,
    post_buffered,
    post_stream,
    translate as translate_entity,
    translate_opening,
)


# The doors binding. Every value here is one this entity answers differently
# from windows; everything else about the push lives in `post_entity`.
#
# Schema 2, not 1, and independently of rooms' 7: versioning doors against the
# room contract would couple two things that move separately, and the bump to 2
# was "one push carries many models". Windows start at 1 because that contract
# has no earlier history to number around.
DOORS = EntityPush(
    entity="doors",
    list_key="door",
    schema_version=2,
    url="http://127.0.0.1:5151/doors",
    url_stream="http://127.0.0.1:5151/doors/stream",
    translate=lambda element, contribution: translate_opening(
        element, contribution["placements"]
    ),
    nested_reason="nested inside another door (leaves, panels, hardware)",
)

# Kept as module constants because callers and tests reference them by name.
SERVER_URL = DOORS.url
SERVER_URL_STREAM = DOORS.url_stream
SCHEMA_VERSION = DOORS.schema_version
DOOR_LIST_KEY = DOORS.list_key


def translate(run_envelope, entries):
    """Map a run's duHast door exports onto the v2 contract as one whole
    payload -- the buffered path, kept for small manual pushes and fixture
    generation."""
    return translate_entity(DOORS, run_envelope, entries)


def post_doors_stream(run_envelope, entries, url=SERVER_URL_STREAM):
    """Stream this run's doors. Returns `(ok, status, text)`."""
    return post_stream(DOORS, run_envelope, entries, url)


def post_doors(run_envelope, entries, url=SERVER_URL):
    """Buffered counterpart of `post_doors_stream`. Returns `(ok, status, text)`."""
    return post_buffered(DOORS, run_envelope, entries, url)
