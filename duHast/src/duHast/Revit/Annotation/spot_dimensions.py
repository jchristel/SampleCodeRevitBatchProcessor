"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to spot annotation. 
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

import Autodesk.Revit.DB as rdb
from duHast.Revit.Annotation import arrow_heads as rArrow
from duHast.Revit.Common import common as com
from duHast.Revit.Common import parameter_get_utils as rParaGet


def get_all_spot_dim_types(doc):
    """
    Gets all spot Dim types in the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of spot dimension types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of spot dimension types
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdb.SpotDimensionType)


def get_symbol_ids_from_spot_types(doc):
    """
    Gets all family symbol ids used as a symbol from all spot elevation type definitions and spot coordinate type definitions.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    dim_ts = get_all_spot_dim_types(doc)
    for t in dim_ts:
        id = rParaGet.get_built_in_parameter_value(
            t, rdb.BuiltInParameter.SPOT_ELEV_SYMBOL
        )
        if id not in ids and id != rdb.ElementId.InvalidElementId and id != None:
            ids.append(id)
    return ids


def get_all_spot_elevation_symbols_in_model(doc):
    """
    Gets all family symbols of category Spot Elevation Symbol in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    col = rdb.FilteredElementCollector(doc).OfCategory(
        rdb.BuiltInCategory.OST_SpotElevSymbols
    )
    return col


def get_all_spot_elevation_symbol_ids_in_model(doc):
    """
    Gets all family symbol ids of category Spot Elevation Symbol in model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    col = get_all_spot_elevation_symbols_in_model(doc)
    ids = com.get_ids_from_element_collector(col)
    return ids


def get_spot_type_arrow_head_ids(doc):
    """
    returns all arrow head ids used in text types in a model
    """
    used_ids = rArrow.get_arrow_head_ids_from_type(
        doc, get_all_spot_dim_types, rArrow.ARROWHEAD_PARAS_SPOT_DIMS
    )
    return used_ids
