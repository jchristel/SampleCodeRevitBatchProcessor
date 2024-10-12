"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utility function getting 2D points from element solids.
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

from duHast.Revit.Common.Geometry import solids as rSolid


def get_2d_points_from_revit_element_type_in_model(doc, element_instance_getter):
    """
    Returns a list of lists of points representing the flattened(2D geometry) of the elements
    List of Lists because a elements can be made up of multiple solids. Each nested list represents one solid within the elements geometry.
    Does not work with in place elements.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element_instance_getter: Function returning all element instances of a particular category in the model as an element collector
    :type element_instance_getter: func(doc)

    :return: A list of data geometry instances.
    :rtype: list of :class:`.DataGeometry`
    """

    element_instances = element_instance_getter(doc)
    all_element_points = []
    for element_instance in element_instances:
        element_points = rSolid.get_2d_points_from_solid(element_instance)
        if len(element_points) > 0:
            all_element_points.append(element_points)
    return all_element_points
