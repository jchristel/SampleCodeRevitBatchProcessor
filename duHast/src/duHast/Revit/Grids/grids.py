"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

import System

# import common library modules
from duHast.Revit.Common import common as com
from duHast.Revit.Common import parameter_get_utils as rParaGet

# import Autodesk
import Autodesk.Revit.DB as rdb


def get_grids_in_model(doc):
    """
    Get all grids in model

    :param doc: The current model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A collector with all grids in model.
    :rtype: _type_
    """

    collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
    return collector


# --------------------------------------------- utility functions ------------------


def get_all_grid_heads_by_category(doc):
    """
    Gets all grid head types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid head types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_GridHeads)
        .WhereElementIsElementType()
    )
    return collector


def get_all_grid_types_by_category(doc):
    """
    Gets all grid types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_Grids)
        .WhereElementIsElementType()
    )
    return collector


def get_all_grid_type_ids_by_category(doc):
    """
    Gets all grid types ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid type ids
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = get_all_grid_types_by_category(doc)
    ids = com.get_ids_from_element_collector(collector)
    return ids


def get_grid_type_names(doc, g):
    """
    Gets all valid grid types, based on a past in grid, available in model.

    Uses grid.GetValidTypes() to get the grid types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid
    :type g: Autodesk.Revit.DB.Grid
    :return: A nested set of lists containing grid type id and grid type name
    :rtype: list of lists [[GridTypeId as Revit ElementId, grid type name as string],[...]]
    """

    valid_grid_types = []
    valid_grid_type_ids = g.GetValidTypes()
    for valid_grid_type_id in valid_grid_type_ids:
        grid_data = []
        grid_type_t = doc.GetElement(valid_grid_type_id)
        grid_data.append(valid_grid_type_id)
        grid_data.append(rdb.Element.Name.GetValue(grid_type_t))
        valid_grid_types.append(grid_data)
    return valid_grid_types


def get_grid_type_name(doc, g):
    """
    Gets the grid type name of a grid.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: The grid type name.
    :rtype: str
    """

    value = "unknown"
    grid_type_T = doc.GetElement(g.GetTypeId())
    value = rdb.Element.Name.GetValue(grid_type_T)
    return value


def get_grid_type_id_by_name(doc, grid_type_name):
    """
    Gets the grid type Id based on it's name, if no match found it returns the Revit Invalid Element Id

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param grid_type_name: The grid type name.
    :type grid_type_name: str
    :return: The grids type Id or if not match is found Autodesk.Revit.DB.ElementId.InvalidElementId
    :rtype: Autodesk.Revit.DB.ElementId
    """

    id = rdb.ElementId.InvalidElementId
    grids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).ToList()
    if len(grids) > 0:
        g = grids[0]
        valid_grid_type_ids = g.GetValidTypes()
        for grid_typ_id in valid_grid_type_ids:
            g_type_name = rdb.Element.Name.GetValue(doc.GetElement(grid_typ_id))
            if g_type_name == grid_type_name:
                id = grid_typ_id
                break
    return id


def grid_check_parameter_value(g, para_name, para_condition, condition_value):
    """
    Returns true if a given parameter on a grid has a value meeting the parameter condition.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :param para_name: A parameter Name.
    :type para_name: str
    :param para_condition: A function evaluating the parameter value. First argument is the value to be checked against. Second argument is the actual parameter value.
    :type para_condition: func(arg1,arg2)
    :param condition_value: The value to be checked against.
    :type condition_value: var
    :return: True if parameter value is evaluated to True otherwise False.
    :rtype: bool
    """

    rule_match = False
    p_value = rParaGet.get_parameter_value_by_name(g, para_name)
    if p_value != None:
        rule_match = rParaGet.check_parameter_value(g, para_condition, condition_value)
    return rule_match


def get_max_extent_as_string(g):
    """
    Gets the maximum extent of a grid.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: A string in format [maxX,maxY,maxZ]
    :rtype: str
    """

    ex = g.GetExtents()
    max = "[{}]".format(
        ",".join(
            [str(ex.MaximumPoint.X), str(ex.MaximumPoint.Y), str(ex.MaximumPoint.Z)]
        )
    )
    return max


def get_min_extent_as_string(g):
    """
    Gets the minimum extent of a grid.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: A string in format [minX,minY,minZ]
    :rtype: str
    """

    ex = g.GetExtents()
    min = "[{}]".format(
        ",".join(
            [str(ex.MinimumPoint.X), str(ex.MinimumPoint.Y), str(ex.MinimumPoint.Z)]
        )
    )
    return min


def get_all_grid_head_family_type_ids(doc):
    """
    This will return all ids grid head family types in the model
    """

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_GridHeads)
    col = (
        rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    )
    ids = com.get_ids_from_element_collector(col)
    return ids
