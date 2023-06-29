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
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import Autodesk.Revit.DB as rdb

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
        data_c.type_properties.name = rdb.Element.Name.GetValue(revit_ceiling).encode(
            "utf-8"
        )
        ceiling_type = doc.GetElement(revit_ceiling.GetTypeId())

        # custom parameter value getters
        value_getter = {
            rdb.StorageType.Double: rParaGet.getter_double_as_double_converted_to_metric,
            rdb.StorageType.Integer: rParaGet.getter_int_as_int,
            rdb.StorageType.String: rParaGet.getter_string_as_UTF8_string,  # encode ass utf 8 just in case
            rdb.StorageType.ElementId: rParaGet.getter_element_id_as_element_int,  # needs to be an integer for JSON encoding
            str(None): rParaGet.getter_none,
        }
        data_c.type_properties.properties = (
            rParaGet.get_all_parameters_and_values_wit_custom_getters(
                ceiling_type, value_getter
            )
        )

        # get instance properties
        data_c.instance_properties.id = revit_ceiling.Id.IntegerValue
        data_c.instance_properties.properties = (
            rParaGet.get_all_parameters_and_values_wit_custom_getters(
                revit_ceiling, value_getter
            )
        )

        # get level properties
        data_c.level.name = rdb.Element.Name.GetValue(
            doc.GetElement(revit_ceiling.LevelId)
        ).encode("utf-8")
        data_c.level.id = revit_ceiling.LevelId.IntegerValue
        data_c.level.offset_from_level = rParaGet.get_built_in_parameter_value(
            revit_ceiling, rdb.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM
        )  # offset from level

        # get the model name
        if doc.IsDetached:
            data_c.revit_model.name = "Detached Model"
        else:
            data_c.revit_model.name = doc.Title

        # get phasing information
        data_c.phasing.created = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                revit_ceiling,
                rdb.BuiltInParameter.PHASE_CREATED,
                rParaGet.get_parameter_value_as_element_id,
            ),
        ).encode("utf-8")
        data_c.phasing.demolished = rPhase.get_phase_name_by_id(
            doc,
            rParaGet.get_built_in_parameter_value(
                revit_ceiling,
                rdb.BuiltInParameter.PHASE_DEMOLISHED,
                rParaGet.get_parameter_value_as_element_id,
            ),
        ).encode("utf-8")

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
