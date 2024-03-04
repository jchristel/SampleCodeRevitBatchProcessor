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

from Autodesk.Revit.DB import BoundingBoxXYZ, BuiltInParameter, Element, Options, StorageType

from duHast.Revit.Common import (
    design_set_options as rDesignO,
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

# from duHast.APISamples.Ceilings.Geometry import Geometry
from duHast.Revit.Doors.doors import get_door_instances
from duHast.Data.Objects import data_door as dDoor
from duHast.Data.Objects.Properties.Geometry.from_revit_conversion import (
    convert_bounding_box_to_flattened_2d_points,
    convert_xyz_in_data_geometry_polygons,
)

from duHast.Revit.Common.Geometry.solids import get_bounding_box_from_family_geometry


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

    door_bounding_box = get_bounding_box_from_family_geometry(
        revit_door.get_Geometry(opts)
    )
    # only export door data if 3D geometry is available
    # if no geometry is available, return None
    # some families of type door do not have any 3D geometry... ignore those for now
    if (isinstance(door_bounding_box, BoundingBoxXYZ) == False):
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
        # get design set data
        design_set_data = rDesignO.get_design_set_option_info(doc, revit_door)
        data_door.design_set_and_option.option_name = design_set_data[
            "designOptionName"
        ]
        data_door.design_set_and_option.set_name = design_set_data["designSetName"]
        data_door.design_set_and_option.is_primary = design_set_data["isPrimary"]

        # get type properties
        data_door.type_properties.id = revit_door.GetTypeId().IntegerValue
        data_door.type_properties.name = Element.Name.GetValue(revit_door).encode(
            "utf-8"
        )
        ceiling_type = doc.GetElement(revit_door.GetTypeId())

        # custom parameter value getters
        value_getter = {
            StorageType.Double: rParaGet.getter_double_as_double_converted_to_metric,
            StorageType.Integer: rParaGet.getter_int_as_int,
            StorageType.String: rParaGet.getter_string_as_UTF8_string,  # encode ass utf 8 just in case
            StorageType.ElementId: rParaGet.getter_element_id_as_element_int,  # needs to be an integer for JSON encoding
            str(None): rParaGet.getter_none,
        }
        data_door.type_properties.properties = (
            rParaGet.get_all_parameters_and_values_wit_custom_getters(
                ceiling_type, value_getter
            )
        )

        # get instance properties
        data_door.instance_properties.id = revit_door.Id.IntegerValue
        data_door.instance_properties.properties = (
            rParaGet.get_all_parameters_and_values_wit_custom_getters(
                revit_door, value_getter
            )
        )

        # get level properties
        data_door.level.name = Element.Name.GetValue(
            doc.GetElement(revit_door.LevelId)
        ).encode("utf-8")
        data_door.level.id = revit_door.LevelId.IntegerValue
        data_door.level.offset_from_level = rParaGet.get_built_in_parameter_value(
            revit_door, BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM
        )  # offset from level

        # get the model name
        if doc.IsDetached:
            data_door.revit_model.name = "Detached Model"
        else:
            data_door.revit_model.name = doc.Title

        # get phasing information
        data_door.phasing.created = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                revit_door,
                BuiltInParameter.PHASE_CREATED,
                rParaGet.get_parameter_value_as_element_id,
            ),
        ).encode("utf-8")
        data_door.phasing.demolished = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                revit_door,
                BuiltInParameter.PHASE_DEMOLISHED,
                rParaGet.get_parameter_value_as_element_id,
            ),
        ).encode("utf-8")

        return data_door
    else:
        return None


def get_all_door_data(doc, filter_family_names = []):
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