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
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Common import (
    design_set_options as rDesignO,
    parameter_get_utils as rParaGet,
    phases as rPhase,
)
from duHast.Data.Objects import data_room as dRoom
from duHast.Data.Objects.Properties.Geometry import from_revit_conversion as rGeo
from duHast.Revit.Rooms.rooms import get_all_rooms
from duHast.Revit.Rooms.Geometry.geometry import get_2d_points_from_revit_room


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
        design_set_data = rDesignO.get_design_set_option_info(doc, revit_room)
        data_r.design_set_and_option.option_name = design_set_data["designOptionName"]
        data_r.design_set_and_option.set_name = design_set_data["designSetName"]
        data_r.design_set_and_option.is_primary = design_set_data["isPrimary"]

        # get instance properties
        data_r.instance_properties.id = revit_room.Id.IntegerValue
        # custom parameter value getters
        value_getter = {
            rdb.StorageType.Double: rParaGet.getter_double_as_double_converted_to_metric,
            rdb.StorageType.Integer: rParaGet.getter_int_as_int,
            rdb.StorageType.String: rParaGet.getter_string_as_UTF8_string,  # encode ass utf 8 just in case
            rdb.StorageType.ElementId: rParaGet.getter_element_id_as_element_int,  # needs to be an integer for JSON encoding
            str(None): rParaGet.getter_none,
        }
        data_r.instance_properties.properties = (
            rParaGet.get_all_parameters_and_values_wit_custom_getters(
                revit_room, value_getter
            )
        )

        # get the model name
        if doc.IsDetached:
            data_r.revit_model.name = "Detached Model"
        else:
            data_r.revit_model.name = doc.Title

        # get phase name
        data_r.phasing.created = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                revit_room,
                rdb.BuiltInParameter.ROOM_PHASE,
                rParaGet.get_parameter_value_as_element_id,
            ),
        ).encode("utf-8")
        data_r.phasing.demolished = -1

        # get level data
        try:
            data_r.level.name = rdb.Element.Name.GetValue(revit_room.Level).encode(
                "utf-8"
            )
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
