"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit flex ducts.
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
import Autodesk.Revit.DB.Mechanical as rdbM

from duHast.Revit.MEP_Systems.Utility.SymbolsInSystemTypes import (
    get_symbol_ids_of_mep_system_types,
    get_unique_ids_of_used_symbols_from_system_type_ids,
)
from duHast.Revit.MEP_Systems.Utility.RevitMEPSystemCategories import (
    CATS_LOADABLE_DUCTS,
)
from duHast.Revit.Common import common as com


def get_all_flex_duct_types_by_category(doc):
    """
    Gets a filtered element collector of all flex duct types in the model.
    - round
    - rectangular
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves)
        .WhereElementIsElementType()
    )
    return collector


def get_all_flex_duct_types_by_class(doc):
    """
    Gets a filtered element collector of all flex duct types in the model.
    - round
    - rectangular
    Will exclude in place families.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return rdb.FilteredElementCollector(doc).OfClass(rdbM.FlexDuctType)


def get_all_flex_duct_instances_in_model_by_category(doc):
    """
    Gets all flex duct elements placed in model.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfCategory(rdb.BuiltInCategory.OST_FlexDuctCurves)
        .WhereElementIsNotElementType()
    )


def get_all_flex_duct_instances_in_model_by_class(doc):
    """
    Gets all flex duct elements placed in model.
    Will exclude in place families.
    TODO: check these actually work...
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A filtered element collector of flex duct instances
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdbM.FlexDuctType)
        .WhereElementIsNotElementType()
    )


def get_all_flex_duct_type_ids_in_model_by_category(doc):
    """
    Gets all flex duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_cat = get_all_flex_duct_types_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids


def get_all_flex_duct_type_ids_in_model_by_class(doc):
    """
    Gets all flex duct type ids available in model.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of ids representing flex duct types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_class = get_all_flex_duct_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids


def get_symbol_ids_used_in_flex_duct_types(doc):
    """
    Gets a list of unique symbol ids used in system type properties of flex duct types.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of unique ids representing family symbols used in flex duct systems.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = []
    tye_ids = get_all_flex_duct_type_ids_in_model_by_category(doc)
    ids = get_unique_ids_of_used_symbols_from_system_type_ids(doc, tye_ids)
    return ids


def get_symbol_ids_for_flex_duct_types_in_model(doc):
    """
    Gets list of symbol ids of the following categories:
    - BuiltInCategory.OST_DuctAccessory,
    - BuiltInCategory.OST_DuctTerminal,
    - BuiltInCategory.OST_DuctFitting
    TODO: flex duct and duct do not differentiate in terms of filtering...one function will get both
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of ids representing family symbols.
    :rtype: list  Autodesk.Revit.DB.ElementId
    """

    ids = get_symbol_ids_of_mep_system_types(
        doc, CATS_LOADABLE_DUCTS, "GetSymbolIdsForDuctTypes"
    )
    return ids
