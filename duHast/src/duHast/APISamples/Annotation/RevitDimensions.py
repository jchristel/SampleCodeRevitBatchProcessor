'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to dimensions. 
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

from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Annotation import RevitArrowHeads as rArrow


def GetDimTypes(doc):
    '''
    Gets all dimension types in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of Dimension Types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of DimensionType
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.DimensionType)

def GetDimTypeIds(doc):
    '''
    Gets all dimension type ids in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.DimensionType)
    ids = com.GetIdsFromElementCollector(col)
    return ids


def GetAllDimensionElements(doc):
    '''
    Gets all dimension elements placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of Dimensions
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of Dimension
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.Dimension)

def GetSymbolIdsFromDimTypes(doc):
    '''
    Gets all family symbol ids used as centre line symbol from all dim styles in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dimTs = GetDimTypes(doc)
    for t in dimTs:
        id = rParaGet.get_built_in_parameter_value (t, rdb.BuiltInParameter.DIM_STYLE_CENTERLINE_SYMBOL)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids


def GetDimTypeArrowHeadIds(doc):
    '''
    Gets all arrow head symbol ids used in dim types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    usedIds = rArrow.GetArrowHeadIdsFromType(doc, GetDimTypes, rArrow.ARROWHEAD_PARAS_DIM)
    return usedIds