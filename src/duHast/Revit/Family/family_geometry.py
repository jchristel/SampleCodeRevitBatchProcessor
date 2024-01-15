"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit families geometry helper functions.
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

from duHast.Revit.Common.Geometry.solids import (
    get_bounding_box_from_family_geometry,
)
from duHast.Revit.Common.Geometry.geometry import merge_bounding_box_xyz

from Autodesk.Revit.DB import (
    Options,
)


def get_solids_based_bounding_box_from_family_instance(doc, family_instance):
    """
    Returns a bounding box of the family instance based on solids in the family instance geometry only.

    :param doc: The revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to get the bounding box from.
    :type family_instance: Autodesk.Revit.DB.FamilyInstance

    :return: The bounding box of the family instance or None if no solids within the family instance are found.
    :rtype: Autodesk.Revit.DB.BoundingBoxXYZ or None
    """

    # result is a bounding box
    merged_result = None
    # set a default option
    opts = Options()
    # get the host family geometry first
    merged_result = get_bounding_box_from_family_geometry(
        family_instance.get_Geometry(opts)
    )

    # check if any nested shared families are in play
    sub_elements = family_instance.GetSubComponentIds()
    if sub_elements is not None:
        # get the bounding box of the sub elements
        for sub_element in sub_elements:
            sub_element = doc.GetElement(sub_element)
            sub_element_bb = get_bounding_box_from_family_geometry(
                sub_element.get_Geometry(opts)
            )
            # check if the result is None and if so set it to the first sub element bounding box
            # this can happen if the host family has no solids but the nested family has
            if merged_result == None:
                merged_result = sub_element_bb
                continue
            # merge the bounding boxes
            merged_result = merge_bounding_box_xyz(merged_result, sub_element_bb)
    return merged_result
