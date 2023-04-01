'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to spot annotation. 
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

import Autodesk.Revit.DB as rdb
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet



def GetAllSpotDimTypes(doc):
    '''
    Gets all spot Dim types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of spot dimension types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of spot dimension types
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.SpotDimensionType)

def GetSymbolIdsFromSpotTypes(doc):
    '''
    Gets all family symbol ids used as a symbol from all spot elevation type definitions and spot coordinate type definitions.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dimTs = GetAllSpotDimTypes(doc)
    for t in dimTs:
        id = rParaGet.get_built_in_parameter_value (t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids


def GetAllSpotElevationSymbolsInModel(doc):
    '''
    Gets all family symbols of category Spot Elevation Symbol in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_SpotElevSymbols)
    return col


def GetAllSpotElevationSymbolIdsInModel(doc):
    '''
    Gets all family symbol ids of category Spot Elevation Symbol in model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    col = GetAllSpotElevationSymbolsInModel(doc)
    ids = com.GetIdsFromElementCollector(col)
    return ids


def GetSpotTypeArrowHeadIds(doc):
    '''
    returns all arrow head ids used in text types in a model
    '''
    usedIds = rArrow.GetArrowHeadIdsFromType(doc, GetAllSpotDimTypes, rArrow.ARROWHEAD_PARAS_SPOT_DIMS)
    return usedIds