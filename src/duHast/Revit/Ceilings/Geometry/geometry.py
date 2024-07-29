"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a Revit ceilings geometry extraction functions. 
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

from Autodesk.Revit.DB import Options, Solid

from duHast.Revit.Ceilings import ceilings as rCeiling
from duHast.Data.Objects.Properties.Geometry import from_revit_conversion as rCon


def get_2d_points_from_revit_ceiling(ceiling):
    """
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings.

    :param ceiling: A revit ceiling instance.
    :type ceiling: Autodesk.Revit.DB.Ceiling

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    """

    all_ceiling_points = []
    # get geometry from ceiling
    opt = Options()
    fr1_geom = ceiling.get_Geometry(opt)
    solids = []
    # check geometry for Solid elements
    # todo check for FamilyInstance geometry ( in place families!)
    for item in fr1_geom:
        if type(item) is Solid:
            solids.append(item)

    # process solids to points
    # in place families may have more then one solid
    for s in solids:
        point_per_ceilings = rCon.convert_solid_to_flattened_2d_points(s)
        if len(point_per_ceilings) > 0:
            for p_lists in point_per_ceilings:
                all_ceiling_points.append(p_lists)
    return all_ceiling_points


def get_2d_points_from_revit_ceilings_in_model(doc):
    """
    Returns a list of lists of points representing the flattened(2D geometry) of the ceiling
    List of Lists because a ceiling can be made up of multiple sketches. Each nested list represents one ceiling sketch.
    Does not work with in place ceilings.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    """

    ceiling_instances = rCeiling.get_all_ceiling_instances_in_model_by_category(doc)
    all_ceiling_points = []
    for c_i in ceiling_instances:
        ceiling_points = get_2d_points_from_revit_ceiling(c_i)
        if len(ceiling_points) > 0:
            all_ceiling_points.append(ceiling_points)
    return all_ceiling_points
