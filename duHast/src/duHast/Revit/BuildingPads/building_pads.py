"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit building pads helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

import clr
import System

from duHast.Revit.Common import common as com
from duHast.Revit.BuildingPads.Utility import (
    RevitBuildingPadsFilter as rBuildingPadFilter,
)

# import Autodesk
import Autodesk.Revit.DB as rdb

# --------------------------------------------- utility functions ------------------


def get_all_building_pad_types_by_category(doc):
    """
    Gets a filtered element collector of all BuildingPad types in the model.

    - Basic BuildingPad

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rBuildingPadFilter._get_all_building_pad_types_by_category(doc)
    return collector


def get_building_pad_types_by_class(doc):
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

    collector = rBuildingPadFilter._get_building_pad_types_by_class(doc)
    return collector


# -------------------------------- none in place BuildingPad types -------------------------------------------------------


def get_all_building_pad_instances_in_model_by_category(doc):
    """
    Gets all building pad elements placed in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_BuildingPad)
        .WhereElementIsNotElementType()
    )


def get_all_building_pad_instances_in_model_by_class(doc):
    """
    Gets all building pad elements placed in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing ceiling instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.BuildingPad)
        .WhereElementIsNotElementType()
    )


def get_all_building_pad_type_ids_in_model_by_category(doc):
    """
    Gets all building pad element type ids available in model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    ids = []
    col_cat = get_all_building_pad_types_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids


def get_all_building_pad_type_ids_in_model_by_class(doc):
    """
    Gets all building pad element type ids available in model.

    Filters by class.
    Since there are no in place families of type building pad possible, this should return the same elements as the by category filter.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing building pad type ids.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    ids = []
    col_class = get_building_pad_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids
