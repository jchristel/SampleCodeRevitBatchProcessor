"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Works out which room a window belongs to, across federated models.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a post processing step. It runs on the output of the exporters, not on a
Revit model:

- :func:`.get_all_window_data` for the windows
- :func:`.get_all_room_data` for the rooms
- :func:`.get_all_level_data` for the level elevations

Each may hold data from several models. All three are expected to have been filtered
to a single phase already, so nothing here reasons about phasing.

Why it exists
-------------

Revit resolves the window to room relationship natively, but only WITHIN one model.
Where the windows and the rooms live in different models the relationship never
populates, because the rooms are not in the window's document. This module does that
calculation from the exported geometry instead.

Assumptions
-----------

- All models are inserted origin to origin with no rotation, so coordinates are
  directly comparable between them. Nothing here applies a link transform.
- Window and room polygons are in decimal feet, level elevations in millimetres.
  That is the exporters' convention, not a choice made here.

How a window is resolved
------------------------

1. Where Revit already reported a room - the same model case - that answer is used.
   It accounts for room upper limits and boundary conditions the 2D test below
   cannot see, so it is better information wherever it exists.

2. Otherwise the window is placed geometrically:

   - The storey is the level below the sill, unless the window crosses a level. If
     it does, the window goes to the lowest level it crosses, unless more than half
     of its height sits below that level, in which case it stays on the level below.
     This is self scaling, so it needs no tolerance constant: a floor to ceiling
     window whose sill sits a few millimetres low has almost none of its height
     below the level above, and correctly snaps up rather than dropping a storey.
   - Within that storey the window is tested against each room's boundary polygon in
     plan. The test point is nudged to BOTH sides of the wall, because the window's
     own geometry cannot say which side is the interior: the facing direction of a
     family depends on which side it was placed from and whether it has been
     flipped. Probing both sides sidesteps the question - an external window simply
     finds no room on its outward side.

Outcomes per window: resolved (one room, or several where models overlap), homeless
(measured, but no room matched), or invalid (the geometry could not be measured).

"""

#
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

from duHast.Data.Objects.Collectors.Properties.data_room_to_phase import DataRoomToPhase
from duHast.Revit.Common.Geometry.geometry import point_in_polygon
from duHast.Utilities.Objects.result import Result
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm


#: Share of an opening's height which must sit below the lowest level it crosses for
#: it to stay on the level underneath. At exactly this share it moves up.
LEVEL_CROSSING_MAJORITY = 0.5

#: How far past the edge of a window, in millimetres, each probe point is pushed.
#: Room boundaries are taken at the wall CENTRE LINE by default, so this only has to
#: clear the middle of the wall. Rooms which fell back to their 3D solid - the ones
#: bounded only by linked walls - are bounded at the wall FINISH face instead, and
#: those may need a larger value. Too small shows up as homeless windows, which is
#: visible; too large risks reaching through a thin partition into the next room,
#: which is not.
PROBE_MARGIN_MM = 25.0

#: Values written to DataRoomToPhase.source.
SOURCE_REVIT = "revit"
SOURCE_COMPUTED = "computed"


def _room_key(revit_model_name, room_id):
    """
    Builds the key identifying a room across models.

    An element id is only unique within its own document, so the model name has to
    take part or rooms from different models collide.

    :param revit_model_name: Name of the model holding the room.
    :type revit_model_name: str
    :param room_id: Element id of the room.
    :type room_id: int

    :return: The key.
    :rtype: tuple(str, int)
    """

    return (revit_model_name, room_id)


def get_level_elevation_lookup(level_data):
    """
    Builds a lookup of level elevations keyed by model name and level id.

    :param level_data: Level data, from :func:`.get_all_level_data`, possibly spanning
        several models.
    :type level_data: list[:class:`.DataLevelBuilding`]

    :return: Elevations in millimetres, keyed by (model name, level id).
    :rtype: {(str, int): float}
    """

    lookup = {}
    for level in level_data:
        lookup[(level.revit_model.name, level.id)] = level.elevation
    return lookup


def group_rooms_by_level_elevation(room_data, level_data):
    """
    Groups rooms by the elevation of the level they sit on.

    Grouping on elevation rather than on level id is what makes this work across
    models: level ids and even level names need not agree between models, but with
    everything inserted origin to origin the elevations do.

    Only levels which actually carry a room end up as keys, which is the point of
    deriving the storeys from the rooms. Parapet, top of steel and ceiling datums
    never appear, so they can never be picked as "the level above" a window.

    :param room_data: Room data, already filtered to the phase of interest.
    :type room_data: list[:class:`.DataRoom`]
    :param level_data: Level data, from :func:`.get_all_level_data`.
    :type level_data: list[:class:`.DataLevelBuilding`]

    :return: A tuple of rooms grouped by level elevation in millimetres, and the rooms
        whose level could not be found in the level data.
    :rtype: tuple({float: list[:class:`.DataRoom`]}, list[:class:`.DataRoom`])
    """

    elevation_lookup = get_level_elevation_lookup(level_data)

    rooms_by_elevation = {}
    rooms_without_level = []
    for room in room_data:
        key = (room.revit_model.name, room.level.id)
        if key not in elevation_lookup:
            rooms_without_level.append(room)
            continue
        elevation = elevation_lookup[key]
        rooms_by_elevation.setdefault(elevation, []).append(room)

    return rooms_by_elevation, rooms_without_level


def get_level_elevation_for_opening(sill, head, level_elevations):
    """
    Returns the elevation of the storey an opening belongs to.

    The rules, in order:

    - No level at or below the sill: the lowest level is used. An opening below the
      bottom of the building belongs to the bottom of the building.
    - The opening does not reach the next level up: the level below the sill.
    - The opening crosses one or more levels: the LOWEST level it crosses, unless
      more than :const:`.LEVEL_CROSSING_MAJORITY` of its height sits below that
      level, in which case the level below the sill.

    Taking the lowest CROSSED level rather than the level below the sill for tall
    openings keeps the result monotonic. Were it the level below the sill, making an
    opening taller until it reached a second level would move it back DOWN a storey.

    :param sill: Lowest point of the opening, in millimetres.
    :type sill: float
    :param head: Highest point of the opening, in millimetres.
    :type head: float
    :param level_elevations: Level elevations in millimetres, ascending.
    :type level_elevations: list[float]

    :return: The elevation of the storey, or None when there are no levels at all.
    :rtype: float
    """

    if len(level_elevations) == 0:
        return None

    # the level below, defaulting to the lowest level when the sill is under all of them
    levels_at_or_below = [
        elevation for elevation in level_elevations if elevation <= sill
    ]
    level_below = (
        max(levels_at_or_below) if len(levels_at_or_below) > 0 else level_elevations[0]
    )

    # levels the opening passes through. A head landing exactly ON a level is not a
    # crossing: a window stopping at the slab soffit belongs to the storey below it.
    crossed = [
        elevation for elevation in level_elevations if sill < elevation < head
    ]
    if len(crossed) == 0:
        return level_below

    lowest_crossed = min(crossed)
    share_below = (lowest_crossed - sill) / (head - sill)
    if share_below > LEVEL_CROSSING_MAJORITY:
        return level_below
    return lowest_crossed


def get_opening_test_point(opening):
    """
    Returns the point in plan used to test an opening against room boundaries.

    The room calculation point is preferred where the family carries one: it is placed
    deliberately by the family author to represent where the opening counts as being,
    which is not always the middle of its extents. The centre of the exported footprint
    is the fallback.

    :param opening: A window or door data instance.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`

    :return: The point as (x, y) in decimal feet, or None when the opening has no
        usable geometry.
    :rtype: tuple(float, float)
    """

    # a calculation point is [x, y, z]; anything else means it was not exported
    if len(opening.room_calculation_point) >= 2:
        return (
            opening.room_calculation_point[0],
            opening.room_calculation_point[1],
        )

    outer_loop = _get_outer_loop(opening)
    if outer_loop is None:
        return None

    return (
        sum(point[0] for point in outer_loop) / float(len(outer_loop)),
        sum(point[1] for point in outer_loop) / float(len(outer_loop)),
    )


def _get_outer_loop(opening):
    """
    Returns the outer loop of an opening's first polygon, or None when it has none.

    :param opening: A window or door data instance.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`

    :return: List of [x, y] points, or None.
    :rtype: list
    """

    if len(opening.polygon) == 0:
        return None
    outer_loop = opening.polygon[0].outer_loop
    if len(outer_loop) < 3:
        return None
    return outer_loop


def get_probe_points(opening, test_point, probe_margin_mm=PROBE_MARGIN_MM):
    """
    Returns two points, one either side of the wall the opening sits in.

    Both sides are probed because nothing on the opening says which side is the room.
    A family's facing direction depends on the side it was placed from and whether it
    has since been flipped, so choosing one side would be a guess. Probing both makes
    the question go away: an external window finds no room on its outward side, and an
    opening in a wall between two rooms legitimately finds one on each.

    The direction comes from the SHORT axis of the exported footprint, which is the
    across the wall direction, a window being far wider than the wall is deep. Its sign
    is arbitrary, which does not matter when both directions are used.

    :param opening: A window or door data instance.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`
    :param test_point: The point in plan to probe from, in decimal feet.
    :type test_point: tuple(float, float)
    :param probe_margin_mm: How far past the edge of the opening to probe, in
        millimetres.
    :type probe_margin_mm: float

    :return: Two (x, y) points in decimal feet, or an empty list when the direction
        could not be worked out.
    :rtype: list[tuple(float, float)]
    """

    outer_loop = _get_outer_loop(opening)
    if outer_loop is None or test_point is None:
        return []

    # two adjacent edges of the footprint rectangle
    edges = [
        (outer_loop[1][0] - outer_loop[0][0], outer_loop[1][1] - outer_loop[0][1]),
        (outer_loop[2][0] - outer_loop[1][0], outer_loop[2][1] - outer_loop[1][1]),
    ]
    lengths = [(edge[0] ** 2 + edge[1] ** 2) ** 0.5 for edge in edges]

    # the shorter edge runs across the wall
    short_index = 0 if lengths[0] <= lengths[1] else 1
    short_edge = edges[short_index]
    short_length = lengths[short_index]
    if short_length == 0:
        return []

    direction = (short_edge[0] / short_length, short_edge[1] / short_length)

    # out of the wall, then a margin further into the room. The feet per mm factor is
    # taken from the shared converter rather than written out again here.
    margin_in_feet = probe_margin_mm / convert_imperial_feet_to_metric_mm(1.0)
    distance = short_length / 2.0 + margin_in_feet

    return [
        (
            test_point[0] + direction[0] * distance,
            test_point[1] + direction[1] * distance,
        ),
        (
            test_point[0] - direction[0] * distance,
            test_point[1] - direction[1] * distance,
        ),
    ]


def is_point_in_room(room, point):
    """
    Checks whether a point in plan falls inside a room.

    A point inside an inner loop is in a hole in the room, not in the room.

    :param room: A room data instance.
    :type room: :class:`.DataRoom`
    :param point: The point as (x, y) in decimal feet.
    :type point: tuple(float, float)

    :return: True when the point is inside the room.
    :rtype: bool
    """

    for polygon in room.polygon:
        if len(polygon.outer_loop) < 3:
            continue
        if not point_in_polygon(point, polygon.outer_loop):
            continue
        in_hole = False
        for inner_loop in polygon.inner_loops:
            if len(inner_loop) > 2 and point_in_polygon(point, inner_loop):
                in_hole = True
                break
        if not in_hole:
            return True
    return False


def get_rooms_reported_by_revit(opening, rooms_by_key):
    """
    Returns the rooms Revit itself reported for an opening.

    The to room and from room entries an exporter writes cover EVERY phase in the
    model, so they are narrowed here by keeping only those whose room appears in the
    room data past in. Since a room belongs to exactly one phase, a room surviving
    that intersection is by definition in the phase the data was filtered to - no
    phase id needs decoding to work that out.

    :param opening: A window or door data instance.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`
    :param rooms_by_key: Rooms keyed by (model name, room id).
    :type rooms_by_key: {(str, int): :class:`.DataRoom`}

    :return: The matching rooms.
    :rtype: list[:class:`.DataRoom`]
    """

    rooms = []
    seen = set()
    for entry in list(opening.to_room) + list(opening.from_room):
        # Revit only ever reports rooms in the opening's own model
        key = _room_key(opening.revit_model.name, entry.room_id)
        if key in seen or key not in rooms_by_key:
            continue
        seen.add(key)
        rooms.append(rooms_by_key[key])
    return rooms


def get_rooms_by_geometry(
    opening, rooms_by_elevation, level_elevations, probe_margin_mm=PROBE_MARGIN_MM
):
    """
    Works out which rooms an opening touches, from its geometry.

    :param opening: A window or door data instance.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`
    :param rooms_by_elevation: Rooms grouped by level elevation in millimetres.
    :type rooms_by_elevation: {float: list[:class:`.DataRoom`]}
    :param level_elevations: Level elevations in millimetres, ascending.
    :type level_elevations: list[float]
    :param probe_margin_mm: How far past the edge of the opening to probe.
    :type probe_margin_mm: float

    :return: A tuple of the matching rooms and a note describing the outcome. The note
        is empty when the opening was measured successfully, whether or not a room was
        found, and describes the problem when it was not.
    :rtype: tuple(list[:class:`.DataRoom`], str)
    """

    if opening.bounding_box_min_z is None or opening.bounding_box_max_z is None:
        return [], "no solid geometry to measure"

    sill = convert_imperial_feet_to_metric_mm(opening.bounding_box_min_z)
    head = convert_imperial_feet_to_metric_mm(opening.bounding_box_max_z)
    if head <= sill:
        return [], "zero or negative height (sill {:.1f} mm, head {:.1f} mm)".format(
            sill, head
        )

    elevation = get_level_elevation_for_opening(sill, head, level_elevations)
    if elevation is None:
        return [], "no levels available to place the opening on"

    test_point = get_opening_test_point(opening)
    if test_point is None:
        return [], "no room calculation point and no usable footprint"

    probe_points = get_probe_points(opening, test_point, probe_margin_mm)
    if len(probe_points) == 0:
        return [], "footprint too degenerate to work out a probe direction"

    rooms = []
    for room in rooms_by_elevation.get(elevation, []):
        for probe_point in probe_points:
            if is_point_in_room(room, probe_point):
                rooms.append(room)
                break

    return rooms, ""


def _build_room_entry(opening, room, source):
    """
    Builds a room to phase entry pointing at a room.

    :param opening: The opening the entry belongs to.
    :type opening: :class:`.DataWindow` | :class:`.DataDoor`
    :param room: The room being pointed at.
    :type room: :class:`.DataRoom`
    :param source: Either SOURCE_REVIT or SOURCE_COMPUTED.
    :type source: str

    :return: The entry.
    :rtype: :class:`.DataRoomToPhase`
    """

    entry = DataRoomToPhase()
    entry.room_id = room.instance_properties.id
    entry.source = source
    # only name the model when it differs from the opening's own
    if room.revit_model.name != opening.revit_model.name:
        entry.revit_model_name = room.revit_model.name
    return entry


def augment_windows_with_rooms(
    window_data, room_data, level_data, probe_margin_mm=PROBE_MARGIN_MM
):
    """
    Fills in which room each window belongs to, and returns the windows.

    All three inputs may span several models, and are expected to have been filtered
    to a single phase already.

    Windows are augmented in place. Where a room was found, an entry naming it is
    written to the window's to_room, tagged with how it was arrived at. Entries
    computed from geometry carry no to/from direction: the exported footprint cannot
    say which side of the wall Revit would have called "to", so a window found to
    touch two rooms reports both without ordering them.

    :param window_data: Window data, from :func:`.get_all_window_data`, filtered to one
        phase.
    :type window_data: list[:class:`.DataWindow`]
    :param room_data: Room data, from :func:`.get_all_room_data`, filtered to the same
        phase.
    :type room_data: list[:class:`.DataRoom`]
    :param level_data: Level data, from :func:`.get_all_level_data`.
    :type level_data: list[:class:`.DataLevelBuilding`]
    :param probe_margin_mm: How far past the edge of a window to probe, in millimetres.
    :type probe_margin_mm: float

    :return:
        Result class instance.

        - result.status is False only when the inputs made the job impossible.
        - result.message holds a summary, then a line per window which could not be
          placed.
        - result.result holds the augmented window data instances.

    :rtype: :class:`.Result`
    """

    return_value = Result()
    return_value.result = window_data

    if len(room_data) == 0:
        return_value.update_sep(
            False, "No room data supplied. No window can be placed."
        )
        return return_value

    rooms_by_elevation, rooms_without_level = group_rooms_by_level_elevation(
        room_data, level_data
    )
    if len(rooms_without_level) > 0:
        return_value.append_message(
            "{} of {} rooms were dropped: their level is not in the level data supplied.".format(
                len(rooms_without_level), len(room_data)
            )
        )
    if len(rooms_by_elevation) == 0:
        return_value.update_sep(
            False,
            "No room could be matched to a level. Check the level data covers every model the rooms came from.",
        )
        return return_value

    level_elevations = sorted(rooms_by_elevation.keys())
    rooms_by_key = {}
    for rooms in rooms_by_elevation.values():
        for room in rooms:
            rooms_by_key[
                _room_key(room.revit_model.name, room.instance_properties.id)
            ] = room

    from_revit = 0
    computed = 0
    homeless = 0
    invalid = 0
    issues = []

    for window in window_data:
        rooms = get_rooms_reported_by_revit(window, rooms_by_key)
        source = SOURCE_REVIT
        note = ""

        if len(rooms) == 0:
            # nothing from Revit, so this window's room has to be worked out. Its
            # calculation point is no help here: a calculation point which produced no
            # room association is not evidence of anything.
            rooms, note = get_rooms_by_geometry(
                window, rooms_by_elevation, level_elevations, probe_margin_mm
            )
            source = SOURCE_COMPUTED

        if note != "":
            invalid += 1
            issues.append(
                "invalid  : window id {} in {} - {}".format(
                    window.instance_properties.id, window.revit_model.name, note
                )
            )
            continue

        if len(rooms) == 0:
            homeless += 1
            issues.append(
                "homeless : window id {} in {} - measured, but no room contains it".format(
                    window.instance_properties.id, window.revit_model.name
                )
            )
            continue

        if source == SOURCE_COMPUTED:
            computed += 1
            entries = list(window.to_room)
            for room in rooms:
                entries.append(_build_room_entry(window, room, source))
            window.to_room = entries
        else:
            from_revit += 1

    return_value.append_message(
        "{} windows: {} already reported by Revit, {} computed, {} homeless, {} invalid.".format(
            len(window_data), from_revit, computed, homeless, invalid
        )
    )
    for issue in issues:
        return_value.append_message(issue)

    return return_value
