"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit rooms export to DATA class functions. 
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

from Autodesk.Revit.DB import BuiltInParameter, Element

from duHast.Revit.Common import (
    parameter_get_utils as rParaGet,
    phases as rPhase,
)
from duHast.Data.Objects import data_room as dRoom
from duHast.Revit.Common.Geometry import to_data_conversion as rGeo
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Rooms.Geometry.geometry import get_2d_points_from_revit_room
from duHast.Revit.Exports.export_data import (
    get_model_data,
    get_instance_properties,
    get_design_set_data,
)

from duHast.Utilities.utility import encode_utf8


def populate_data_room_object(doc, revit_room):
    """
    Returns a custom room data objects populated with some data from the revit model room past in.
    data points:
    - room name, number, id
    - if exists: parameter value of SP_Room_Function_Number
    - level name and id (if not placed 'no level' and -1)
    - Design set and option
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_room: The room.
    :type revit_room: Autodesk.Revit.DB.Architecture.Room

    :return: A room data instance.
    :rtype: :class:`.DataRoom`
    """

    # set up data class object
    data_r = dRoom.DataRoom()
    # get room geometry (boundary points)
    revit_geometry_point_groups = get_2d_points_from_revit_room(revit_room)
    if len(revit_geometry_point_groups) > 0:
        room_point_groups_as_doubles = []
        for room_point_group_by_poly in revit_geometry_point_groups:
            data_geometry_converted = rGeo.convert_xyz_in_data_geometry_polygons(
                doc, room_point_group_by_poly
            )
            room_point_groups_as_doubles.append(data_geometry_converted)
        data_r.polygon = room_point_groups_as_doubles
        
        # get design set data
        design_set = get_design_set_data(doc=doc, element=revit_room)
        data_r.design_set_and_option = design_set

        # get instance properties
        instance_props = get_instance_properties(revit_room)
        data_r.instance_properties = instance_props

        # get the model name
        model = get_model_data(doc=doc)
        data_r.revit_model = model

        # get phase name
        data_r.phasing.created = encode_utf8(
            rPhase.get_phase_name_by_id(
                doc,
                rParaGet.get_built_in_parameter_value(
                    revit_room,
                    BuiltInParameter.ROOM_PHASE,
                    rParaGet.get_parameter_value_as_element_id,
                ),
            )
        )
        data_r.phasing.demolished = -1

        # get level data
        try:
            data_r.level.name = encode_utf8(Element.Name.GetValue(revit_room.Level))
            data_r.level.id = revit_room.Level.Id.IntegerValue
        except:
            data_r.level.name = "no level"
            data_r.level.id = -1
        return data_r

    else:
        return None


def get_all_room_data(doc):
    """
    Returns a list of room data objects for each room in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of room data instances.
    :rtype: list of  :class:`.DataRoom`
    """

    all_room_data = []
    rooms = get_all_rooms(doc)
    for room in rooms:
        rd = populate_data_room_object(doc, room)
        if rd is not None:
            all_room_data.append(rd)
    return all_room_data
