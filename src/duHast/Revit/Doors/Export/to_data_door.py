"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit door export to DATA class functions. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import (
    BoundingBoxXYZ,
    BuiltInParameter,
    Options,
)


# from duHast.APISamples.Ceilings.Geometry import Geometry
from duHast.Revit.Doors.doors import get_door_instances
from duHast.Data.Objects.Collectors import data_door as dDoor
from duHast.Revit.Common.Geometry.to_data_conversion import (
    convert_bounding_box_to_flattened_2d_points,
    convert_xyz_in_data_geometry_polygons,
)

from duHast.Revit.Common.Geometry.solids import (
    get_oriented_bounding_box_from_family_instance,
)
from duHast.Revit.Exports.export_data import (
    get_bounding_box_z_extents,
    get_level_data,
    get_phasing_data,
    get_model_data,
    get_instance_properties,
    get_room_calculation_point,
    get_type_properties,
    get_design_set_data,
    get_super_component_id,
)
from duHast.Data.Objects.Collectors.Properties.data_room_to_phase import DataRoomToPhase


def _get_room_entries(doc, revit_door, get_room_fn):
    """
    Iterates all project phases and collects DataRoomToPhase entries by calling
    get_room_fn(phase) on the door for each phase.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_door: A Revit door instance.
    :type revit_door: Autodesk.Revit.DB.FamilyInstance
    :param get_room_fn: Bound method accepting a Phase and returning a Room or None.
    :type get_room_fn: callable

    :return: List of room-to-phase pairings, one per phase that returned a room.
    :rtype: list[:class:`.DataRoomToPhase`]
    """
    entries = []
    seen = set()
    for phase in doc.Phases:
        try:
            room = get_room_fn(phase)
            if room is None:
                continue
            key = (phase.Id.Value, room.Id.Value)
            if key in seen:
                continue
            seen.add(key)
            entry = DataRoomToPhase()
            entry.phase_id = phase.Id.Value
            entry.room_id = room.Id.Value
            entries.append(entry)
        except Exception:
            pass
    return entries


def populate_data_door_object(doc, revit_door):
    """
    Returns a custom ceiling data objects populated with some data from the revit model ceiling past in.

    - door id
    - door type name
    - door mark
    - door type mark
    - door level name
    - door level id
    - door offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_door: A revit door instance.
    :type revit_door: Autodesk.Revit.DB.FamilyInstance

    :return: A data door object instance.
    :rtype: :class:`.DataDoor`
    """

    # set up data class object
    data_door = dDoor.DataDoor()
    # get door bounding box
    # set a default option
    opts = Options()

    # ORIENTED, so an instance placed at an angle keeps its angle. The world
    # aligned alternative is the right answer to "what extents does this
    # occupy" and the wrong one to "what shape is this": it is aligned to the
    # model axes, so a door in a wall running at 30 degrees comes out as an
    # upright rectangle lying across it. That cannot be corrected afterwards -
    # an axis aligned box no longer records the angle - so it has to be
    # measured in the instance's own frame here.
    #
    # The placement rides on the box Transform, which
    # convert_bounding_box_to_flattened_2d_points applies to the corners below.
    door_bounding_box = get_oriented_bounding_box_from_family_instance(
        revit_door, opts
    )
    # only export door data if 3D geometry is available
    # if no geometry is available, return None
    # some families of type door do not have any 3D geometry... ignore those for now
    if isinstance(door_bounding_box, BoundingBoxXYZ) == False:
        return None
    revit_door_data_geometry = convert_bounding_box_to_flattened_2d_points(
        door_bounding_box
    )

    if len(revit_door_data_geometry.outer_loop) > 0:
        door_point_groups_as_doubles = []
        data_geo_converted = convert_xyz_in_data_geometry_polygons(
            doc, revit_door_data_geometry
        )
        door_point_groups_as_doubles.append(data_geo_converted)
        data_door.polygon = door_point_groups_as_doubles

        # the Z values a consumer needs to work out which room and level this door
        # belongs to where Revit could not. Exported separately because the polygon
        # above is flattened to 2D, so no elevation survives it.
        data_door.room_calculation_point = get_room_calculation_point(revit_door)
        (
            data_door.bounding_box_min_z,
            data_door.bounding_box_max_z,
        ) = get_bounding_box_z_extents(revit_door, opts)

        # get design set data
        design_set = get_design_set_data(doc=doc, element=revit_door)
        data_door.design_set_and_option = design_set

        # get type properties
        type_props = get_type_properties(doc=doc, element=revit_door)
        data_door.type_properties = type_props

        # get instance properties
        instance_props = get_instance_properties(revit_door)
        data_door.instance_properties = instance_props

        # get level properties
        level = get_level_data(
            doc=doc,
            element=revit_door,
            built_in_parameter_def=BuiltInParameter.ASSOCIATED_LEVEL_OFFSET,  # TODO: check this parameter
        )
        data_door.level = level

        # get the model name
        model = get_model_data(doc=doc)
        data_door.revit_model = model

        # get phasing information
        phase = get_phasing_data(doc=doc, element=revit_door)
        data_door.phasing = phase

        # super component id (populated when door is a shared nested family)
        data_door.super_component_id = get_super_component_id(revit_door)

        # to-room and from-room per phase
        data_door.to_room = _get_room_entries(doc, revit_door, revit_door.get_ToRoom)
        data_door.from_room = _get_room_entries(doc, revit_door, revit_door.get_FromRoom)

        return data_door
    else:
        return None


def get_all_door_data(doc, filter_family_names=[]):
    """
    Gets a list of door data objects for each door element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of data door instances.
    :rtype: list of :class:`.DoorCeiling`
    """

    all_door_data = []
    doors = get_door_instances(doc)
    for door in doors:
        # check if door is in filter list
        if len(filter_family_names) > 0:
            if door.Symbol.FamilyName not in filter_family_names:
                continue
        door_data = populate_data_door_object(doc, door)
        if door_data is not None:
            all_door_data.append(door_data)
    return all_door_data
