"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit floors export to DATA class functions.
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

from Autodesk.Revit.DB import BuiltInParameter

from duHast.Revit.Floors import floors as rFloor
from duHast.Data.Objects.Collectors import data_floor as dFloor
from duHast.Revit.Common.Geometry import to_data_conversion as rCon
from duHast.Revit.Common.Geometry import solids as rSolid
from duHast.Revit.Exports.export_data import (
    get_level_data,
    get_phasing_data,
    get_model_data,
    get_instance_properties,
    get_type_properties,
    get_design_set_data,
)


def populate_data_floor_object(doc, revit_floor):
    """
    Returns a custom floor data object populated with some data from the revit model floor passed in.

    - floor id
    - floor type name
    - floor mark
    - floor type mark
    - floor level name
    - floor level id
    - floor offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_floor: A revit floor instance.
    :type revit_floor: Autodesk.Revit.DB.Floor

    :return: A data floor object instance.
    :rtype: :class:`.DataFloor`
    """

    # set up data class object
    data_f = dFloor.DataFloor()
    # get floor geometry (boundary points)
    revit_geometry_point_groups = rSolid.get_2d_points_from_solid(revit_floor)
    if len(revit_geometry_point_groups) > 0:
        floor_point_groups_as_doubles = []
        for all_floor_point_groups in revit_geometry_point_groups:
            data_geo_converted = rCon.convert_xyz_in_data_geometry_polygons(
                doc, all_floor_point_groups
            )
            floor_point_groups_as_doubles.append(data_geo_converted)
        data_f.polygon = floor_point_groups_as_doubles

        # get design set data
        design_set = get_design_set_data(doc=doc, element=revit_floor)
        data_f.design_set_and_option = design_set

        # get type properties
        type_props = get_type_properties(doc=doc, element=revit_floor)
        data_f.type_properties = type_props

        # get instance properties
        instance_props = get_instance_properties(revit_floor)
        data_f.instance_properties = instance_props

        # get level properties
        level = get_level_data(
            doc=doc,
            element=revit_floor,
            built_in_parameter_def=BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM,
        )
        data_f.level = level

        # get the model name
        model = get_model_data(doc=doc)
        data_f.revit_model = model

        # get phasing information
        phase = get_phasing_data(doc=doc, element=revit_floor)
        data_f.phasing = phase

        return data_f
    else:
        return None


def get_all_floor_data(doc):
    """
    Gets a list of floor data objects for each floor element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data floor instances.
    :rtype: list of :class:`.DataFloor`
    """

    all_floor_data = []
    floors = rFloor.get_all_floor_instances_in_model_by_category(doc)
    for floor in floors:
        fd = populate_data_floor_object(doc, floor)
        if fd is not None:
            all_floor_data.append(fd)
    return all_floor_data
