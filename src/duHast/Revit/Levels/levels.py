"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit levels helper functions.
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

import clr
import System


clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import common library modules
from duHast.Revit.Common import common as com

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_levels_in_model(doc):
    """
    Get all levels in model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector with all levels in model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Level)
    return collector


# --------------------------------------------- utility functions ------------------


def get_levels_list_ascending(doc):
    """
    Gets a filtered element collector of all levels in the model ascending by project elevation.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of levels
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
        .WhereElementIsNotElementType()
        .ToList()
        .OrderBy(lambda l: l.ProjectElevation)
    )
    return collector


def get_level_elevation_by_name(doc, level_name):
    level_elevation = None
    levels = get_levels_in_model(doc=doc)
    for level in levels:
        if(level.Name == level_name):
            return level.Elevation
    return level_elevation

# ------------------------------------------------- filters --------------------------------------------------------------------


def get_all_level_heads_by_category(doc):
    """
    Gets a filtered element collector of all level head types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level heads
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_LevelHeads)
        .WhereElementIsElementType()
    )
    return collector


def get_all_level_types_by_category(doc):
    """
    Gets a filtered element collector of all level types in the model.

    Filters by category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of level types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
        .WhereElementIsElementType()
    )
    return collector


def get_all_level_type_ids_by_category(doc):
    """
    Gets a list of all level type ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of all level type ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Levels)
        .WhereElementIsElementType()
    )
    ids = com.get_ids_from_element_collector(collector)
    return ids


# -------------------------------------------------  purge --------------------------------------------------------------------


def get_all_level_head_family_type_ids(doc):
    """
    Gets ids of all level head family symbols (types) in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list of symbol ids.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_LevelHeads)
    col = (
        rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    )
    ids = com.get_ids_from_element_collector(col)
    return ids
