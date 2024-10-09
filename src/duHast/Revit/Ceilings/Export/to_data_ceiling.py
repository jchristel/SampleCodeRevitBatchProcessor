"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ceilings export to DATA class functions. 
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

from Autodesk.Revit.DB import BuiltInParameter, Element, StorageType


from duHast.Revit.Common import (
    design_set_options as rDesignO,
    parameter_get_utils as rParaGet,
    phases as rPhase,
)

# from duHast.APISamples.Ceilings.Geometry import Geometry
from duHast.Revit.Ceilings import ceilings as rCeiling
from duHast.Data.Objects import data_ceiling as dCeiling
from duHast.Data.Objects.Properties.Geometry import from_revit_conversion as rCon
from duHast.Revit.Common.Geometry import solids as rSolid
from duHast.Utilities.utility import encode_utf8
from duHast.Revit.Exports.export_data import get_element_properties, get_phasing_data, get_model_data

def populate_data_ceiling_object(doc, revit_ceiling):
    """
    Returns a custom ceiling data objects populated with some data from the revit model ceiling past in.

    - ceiling id
    - ceiling type name
    - ceiling mark
    - ceiling type mark
    - ceiling level name
    - ceiling level id
    - ceiling offset from level

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param revit_ceiling: A revit ceiling instance.
    :type revit_ceiling: Autodesk.Revit.DB.Ceiling

    :return: A data ceiling object instance.
    :rtype: :class:`.DataCeiling`
    """

    # set up data class object
    data_c = dCeiling.DataCeiling()
    # get ceiling geometry (boundary points)
    revit_geometry_point_groups = rSolid.get_2d_points_from_solid(revit_ceiling)
    # revitGeometryPointGroups = Geometry.Get2DPointsFromRevitCeiling(revitCeiling)
    if len(revit_geometry_point_groups) > 0:
        ceiling_point_groups_as_doubles = []
        for all_ceiling_point_groups in revit_geometry_point_groups:
            data_geo_converted = rCon.convert_xyz_in_data_geometry_polygons(
                doc, all_ceiling_point_groups
            )
            ceiling_point_groups_as_doubles.append(data_geo_converted)
        data_c.polygon = ceiling_point_groups_as_doubles
        # get design set data
        design_set_data = rDesignO.get_design_set_option_info(doc, revit_ceiling)
        data_c.design_set_and_option.option_name = design_set_data["designOptionName"]
        data_c.design_set_and_option.set_name = design_set_data["designSetName"]
        data_c.design_set_and_option.is_primary = design_set_data["isPrimary"]

        # get type properties
        data_c.type_properties.id = revit_ceiling.GetTypeId().IntegerValue
        data_c.type_properties.name = encode_utf8(Element.Name.GetValue(revit_ceiling))
        ceiling_type = doc.GetElement(revit_ceiling.GetTypeId())
        type_properties = get_element_properties(ceiling_type)
        data_c.type_properties.properties = type_properties

        # get instance properties
        data_c.instance_properties.id = revit_ceiling.Id.IntegerValue
        instance_properties = get_element_properties(revit_ceiling)
        data_c.instance_properties.properties = instance_properties

        # get level properties
        data_c.level.name = encode_utf8(
            Element.Name.GetValue(doc.GetElement(revit_ceiling.LevelId))
        )
        data_c.level.id = revit_ceiling.LevelId.IntegerValue
        data_c.level.offset_from_level = rParaGet.get_built_in_parameter_value(
            revit_ceiling, BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM
        )  # offset from level

        # get the model name
        model = get_model_data(doc=doc)
        data_c.revit_model = model

        # get phasing information
        phase = get_phasing_data(doc=doc, element=revit_ceiling)
        data_c.phasing=phase

        return data_c
    else:
        return None


def get_all_ceiling_data(doc):
    """
    Gets a list of ceiling data objects for each ceiling element in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data ceiling instances.
    :rtype: list of :class:`.DataCeiling`
    """

    all_ceiling_data = []
    ceilings = rCeiling.get_all_ceiling_instances_in_model_by_category(doc)
    for ceiling in ceilings:
        cd = populate_data_ceiling_object(doc, ceiling)
        if cd is not None:
            all_ceiling_data.append(cd)
    return all_ceiling_data
