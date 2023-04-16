'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit grids helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import clr

clr.AddReference("System.Core")
from System import Linq
clr.ImportExtensions(Linq)

import System

# import common library modules
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet

# import Autodesk
import Autodesk.Revit.DB as rdb

def get_grids_in_model(doc):
  '''
  Get all grids in model

  :param doc: The current model document.
  :type doc: Autodesk.Revit.DB.Document
  :return: A collector with all grids in model.
  :rtype: _type_
  '''

  collector = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid)
  return collector

# --------------------------------------------- utility functions ------------------

def get_all_grid_heads_by_category(doc):
    '''
    Gets all grid head types in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid head types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_GridHeads).WhereElementIsElementType()
    return collector

def get_all_grid_types_by_category(doc):
    '''
    Gets all grid types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_Grids).WhereElementIsElementType()
    return collector

def get_all_grid_type_ids_by_category(doc):
    '''
    Gets all grid types ids in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector with grid type ids
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    collector = get_all_grid_types_by_category(doc)
    ids = com.get_ids_from_element_collector(collector)
    return ids

def get_grid_type_names (doc, g):
    '''
    Gets all valid grid types, based on a past in grid, available in model.

    Uses grid.GetValidTypes() to get the grid types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid
    :type g: Autodesk.Revit.DB.Grid
    :return: A nested set of lists containing grid type id and grid type name
    :rtype: list of lists [[GridTypeId as Revit ElementId, grid type name as string],[...]]
    '''

    validGridTypes = []
    validGridTypeIds = g.GetValidTypes()
    for validGridTypeId in validGridTypeIds:
        gridData = []
        gtypeT = doc.GetElement(validGridTypeId)
        gridData.append(validGridTypeId)
        gridData.append(rdb.Element.Name.GetValue(gtypeT))
        validGridTypes.append(gridData)
    return validGridTypes

def get_grid_type_name (doc, g):
    '''
    Gets the grid type name of a grid.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: The grid type name.
    :rtype: str
    '''

    value = 'unknown'
    gtypeT = doc.GetElement(g.GetTypeId())
    value = rdb.Element.Name.GetValue(gtypeT)
    return value

def get_grid_type_id_by_name (doc, gridTypeName):
    '''
    Gets the grid type Id based on it's name, if no match found it returns the Revit Invalid Element Id

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param gridTypeName: The grid type name.
    :type gridTypeName: str
    :return: The grids type Id or if not match is found Autodesk.Revit.DB.ElementId.InvalidElementId
    :rtype: Autodesk.Revit.DB.ElementId
    '''

    id = rdb.ElementId.InvalidElementId
    grids = rdb.FilteredElementCollector(doc).OfClass(rdb.Grid).ToList()
    if(len(grids) > 0):
        g = grids[0]
        validGridTypeIds = g.GetValidTypes()
        for gridTypId in validGridTypeIds:
            gtypeTName = rdb.Element.Name.GetValue(doc.GetElement(gridTypId))
            if(gtypeTName ==  gridTypeName):
                id = gridTypId
                break
    return id

def grid_check_parameter_value(g, paraName, paraCondition, conditionValue):
    '''
    Returns true if a given parameter on a grid has a value meeting the parameter condition.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :param paraName: A parameter Name.
    :type paraName: str
    :param paraCondition: A function evaluating the parameter value. First argument is the value to be checked against. Second argument is the actual parameter value.
    :type paraCondition: func(arg1,arg2)
    :param conditionValue: The value to be checked against.
    :type conditionValue: var
    :return: True if parameter value is evaluated to True otherwise False.
    :rtype: bool
    '''

    ruleMatch = False
    pValue = rParaGet.get_parameter_value_by_name (g, paraName)
    if (pValue != None):
        ruleMatch = rParaGet.check_parameter_value(g, paraCondition, conditionValue)
    return ruleMatch

def get_max_extent_as_string(g):
    '''
    Gets the maximum extent of a grid.

    :param g: A grid.
    :type g: Autodesk.Revit.DB.Grid
    :return: A string in format [maxX,maxY,maxZ]<tab>[minX,minY,minZ]
    :rtype: str
    '''

    ex = g.GetExtents()
    max = '['+ ','.join([str(ex.MaximumPoint.X), str(ex.MaximumPoint.Y), str(ex.MaximumPoint.Z)]) + ']'
    min = '['+ ','.join([str(ex.MinimumPoint.X), str(ex.MinimumPoint.Y), str(ex.MinimumPoint.Z)]) + ']'    
    return '\t'.join([min, max])


def get_all_grid_head_family_type_ids(doc):
    ''' 
    This will return all ids grid head family types in the model
    '''

    ids = []
    filter = rdb.ElementCategoryFilter(rdb.BuiltInCategory.OST_GridHeads)
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.FamilySymbol).WherePasses(filter)
    ids = com.get_ids_from_element_collector(col)
    return ids






