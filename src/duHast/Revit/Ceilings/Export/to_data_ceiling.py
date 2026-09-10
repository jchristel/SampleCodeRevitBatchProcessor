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

from Autodesk.Revit.DB import BuiltInParameter

# from duHast.APISamples.Ceilings.Geometry import Geometry
from duHast.Revit.Ceilings import ceilings as rCeiling
from duHast.Data.Objects.Collectors import data_ceiling as dCeiling
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

    :return: A data ceiling object instance. Always an object, never None: a
        ceiling whose geometry could not be measured comes back with an empty
        `polygon` and every other field populated. See the body for why.
    :rtype: :class:`.DataCeiling`
    """

    # set up data class object
    data_c = dCeiling.DataCeiling()
    # get ceiling geometry (boundary points)
    revit_geometry_point_groups = rSolid.get_2d_points_from_solid(revit_ceiling)

    # An unmeasurable ceiling is returned with an EMPTY polygon rather than as
    # None, and this used to be the other way round.
    #
    # A ceiling this function cannot measure still has a perfectly good id,
    # level, phase, design option and both property maps. Answering None threw
    # all of that away and, worse, left the caller unable to tell "no such
    # ceiling" from "a ceiling nobody could measure" - the two look identical
    # once the element is missing from the export, and they send a reader to
    # opposite places. One is a model that has no ceiling there; the other is a
    # defect in this pipeline.
    #
    # Same lesson as the uninitialized BoundingBoxXYZ that used to reach
    # consumers as plausible-looking geometry: a value nothing can distinguish
    # from a real one is worse than an explicit empty. The consumer decides what
    # an empty polygon means, exactly as it already does for a space, which is
    # pushed with an empty outline when its bounding elements live in a link.
    if len(revit_geometry_point_groups) > 0:
        ceiling_point_groups_as_doubles = []
        for all_ceiling_point_groups in revit_geometry_point_groups:
            data_geo_converted = rCon.convert_xyz_in_data_geometry_polygons(
                doc, all_ceiling_point_groups
            )
            ceiling_point_groups_as_doubles.append(data_geo_converted)
        data_c.polygon = ceiling_point_groups_as_doubles

    # get design set data
    design_set = get_design_set_data(doc=doc, element=revit_ceiling)
    data_c.design_set_and_option = design_set

    # get type properties
    type_props = get_type_properties(doc=doc, element=revit_ceiling)
    data_c.type_properties = type_props

    # get instance properties
    instance_props = get_instance_properties(revit_ceiling)
    data_c.instance_properties = instance_props

    # get level properties
    level = get_level_data(
        doc=doc,
        element=revit_ceiling,
        built_in_parameter_def=BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM,
    )
    data_c.level = level

    # get the model name
    model = get_model_data(doc=doc)
    data_c.revit_model = model

    # get phasing information
    phase = get_phasing_data(doc=doc, element=revit_ceiling)
    data_c.phasing = phase

    return data_c


def get_all_ceiling_data(doc):
    """
    Gets a list of ceiling data objects for each ceiling element in the model.

    One entry per ceiling in the model, INCLUDING any whose geometry could not
    be measured - those carry an empty `polygon`. The count of this list can
    therefore be compared against the collector's count to find a pipeline
    problem, which was impossible while unmeasurable ceilings were silently
    dropped.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of data ceiling instances.
    :rtype: list of :class:`.DataCeiling`
    """

    all_ceiling_data = []
    ceilings = rCeiling.get_all_ceiling_instances_in_model_by_category(doc)
    for ceiling in ceilings:
        cd = populate_data_ceiling_object(doc, ceiling)
        # `populate_data_ceiling_object` no longer answers None. The guard stays
        # as a cheap backstop rather than being deleted: this loop is the only
        # thing between a future regression there and a list with a None in it,
        # which would fail much further downstream than here.
        if cd is not None:
            all_ceiling_data.append(cd)
    return all_ceiling_data
