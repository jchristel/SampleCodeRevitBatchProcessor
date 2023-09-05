"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to dimensions. 
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

from Autodesk.Revit.DB import (
    BuiltInParameter,
    ElementId,
    FilteredElementCollector,
    DimensionType,
    Dimension,
)

from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Annotation.arrow_heads import (
    get_arrow_head_ids_from_type,
    ARROWHEAD_PARAS_DIM,
)


def get_dim_types(doc):
    """
    Gets all dimension types in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of Dimension Types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of DimensionType
    """

    return FilteredElementCollector(doc).OfClass(DimensionType)


def get_dim_type_ids(doc):
    """
    Gets all dimension type ids in a model
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing Dimension Types
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = FilteredElementCollector(doc).OfClass(DimensionType)
    ids = get_ids_from_element_collector(col)
    return ids


def get_all_dimension_elements(doc):
    """
    Gets all dimension elements placed in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of Dimensions
    :rtype: Autodesk.Revit.DB.FilteredElementCollector of Dimension
    """

    return FilteredElementCollector(doc).OfClass(Dimension)


def get_symbol_ids_from_dim_types(doc):
    """
    Gets all family symbol ids used as centre line symbol from all dim styles in the model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing family symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    dim_ts = get_dim_types(doc)
    for t in dim_ts:
        id = get_built_in_parameter_value(
            t, BuiltInParameter.DIM_STYLE_CENTERLINE_SYMBOL
        )
        if id not in ids and id != ElementId.InvalidElementId and id != None:
            ids.append(id)
    return ids


def get_dim_type_arrow_head_ids(doc):
    """
    Gets all arrow head symbol ids used in dim types in a model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of element ids representing arrow head symbols
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    used_ids = get_arrow_head_ids_from_type(doc, get_dim_types, ARROWHEAD_PARAS_DIM)
    return used_ids
