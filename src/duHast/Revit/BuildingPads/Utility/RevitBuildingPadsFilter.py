"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of base element filter functions relating to Revit building pads. 
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

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory, BuildingPadType, FilteredElementCollector


def _get_all_building_pad_types_by_category(doc):
    """
    Gets a filtered element collector of all BuildingPad types in the model.

    - Basic BuildingPad

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_BuildingPad)
        .WhereElementIsElementType()
    )
    return collector


def _get_building_pad_types_by_class(doc):
    """
    Gets a filtered element collector of all building pad types in the model:

    - Basic BuildingPad

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return FilteredElementCollector(doc).OfClass(BuildingPadType)
