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
from duHast.APISamples.Annotation import arrow_heads as rArrow
from duHast.APISamples.Common import RevitCommonAPI as com
from duHast.APISamples.Common import RevitElementParameterGetUtils as rParaGet



def get_all_spot_dim_types(doc):
    '''
    Gets all spot Dim types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of spot dimension types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of spot dimension types
    '''

    return rdb.FilteredElementCollector(doc).OfClass(rdb.SpotDimensionType)

def get_symbol_ids_from_spot_types(doc):
    '''
    Gets all family symbol ids used as a symbol from all spot elevation type definitions and spot coordinate type definitions.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids = []
    dim_ts = get_all_spot_dim_types(doc)
    for t in dim_ts:
        id = rParaGet.get_built_in_parameter_value (t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL)
        if(id not in ids and id != rdb.ElementId.InvalidElementId and id != None):
            ids.append(id)
    return ids


def get_all_spot_elevation_symbols_in_model(doc):
    '''
    Gets all family symbols of category Spot Elevation Symbol in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    '''

    col = rdb.FilteredElementCollector(doc).OfCategory(rdb.BuiltInCategory.OST_SpotElevSymbols)
    return col


def get_all_spot_elevation_symbol_ids_in_model(doc):
    '''
    Gets all family symbol ids of category Spot Elevation Symbol in model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    col = get_all_spot_elevation_symbols_in_model(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_spot_type_arrow_head_ids(doc):
    '''
    returns all arrow head ids used in text types in a model
    '''
    used_ids = rArrow.get_arrow_head_ids_from_type(doc, get_all_spot_dim_types, rArrow.ARROWHEAD_PARAS_SPOT_DIMS)
    return used_ids