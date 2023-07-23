"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit railings. 
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
import System

from duHast.Revit.Common import common as com
from duHast.Revit.Family import family_utils as rFam

# import Autodesk
import Autodesk.Revit.DB as rdb
import Autodesk.Revit.DB.Architecture as rdbA

from duHast.Revit.Railings.Utility.railing_categories import RAILING_CATEGORY_FILTER
from duHast.Revit.Railings.Utility import railings_filter as rRailFilter

# --------------------------------------------- utility functions ------------------


def get_all_railing_types_by_category(doc):
    """
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - In place families or loaded families

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing related types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rRailFilter._get_all_railing_types_by_category(doc)
    return collector


def get_all_railing_types_by_category_excl_in_place(doc):
    """
    Gets a filtered element collector of all Railing types in the model.

    Collector will include types of:
    - Top Rail
    - Rail support
    - Hand rail
    - Rail termination
    - Railing Systems
    - loaded families

    Will exclude any inplace families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A list railing related types
    :rtype: list of types
    """

    multi_cat_filter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    collector = (
        rdb.FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsElementType()
    )
    elements = []
    for c in collector:
        if c.GetType() != rdb.FamilySymbol:
            elements.append(c)
    return elements


def get_railing_types_by_class(doc):
    """
    Gets a filtered element collector of all Railing types in the model:

    Collector will include types of:
    - Railing

    It will therefore not return any top rail or hand rail or in place family types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing types
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = rRailFilter._get_railing_types_by_class(doc)
    return collector


# -------------------------------- none in place Railing types -------------------------------------------------------


def get_all_railing_instances_by_category(doc):
    """
    Gets all Railing elements placed in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    multi_cat_filter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return (
        rdb.FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsNotElementType()
    )


def get_all_railing_instances_by_class(doc):
    """
    Gets all Railing elements placed in model. Ignores any in place families.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdbA.Railing)
        .WhereElementIsNotElementType()
    )


def get_all_railing_type_ids_by_category(doc):
    """
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_cat = get_all_railing_types_by_category(doc)
    ids = com.get_ids_from_element_collector(col_cat)
    return ids


def get_all_railing_type_ids_by_class(doc):
    """
    Gets all railing element type ids available in model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: List Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_class = get_railing_types_by_class(doc)
    ids = com.get_ids_from_element_collector(col_class)
    return ids


def get_all_railing_type_ids_by_class_and_category(doc):
    """
    Gets all Railing element types available in model excluding in place types.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_class = get_railing_types_by_class(doc)
    ids_class = com.get_ids_from_element_collector(col_class)
    col_cat = get_all_railing_types_by_category_excl_in_place(doc)
    ids_cat = com.get_ids_from_element_collector(col_cat)
    for id_class in ids_class:
        if id_class not in ids:
            ids.append(id_class)
    for id_cat in ids_cat:
        if id_cat not in ids:
            ids.append(id_cat)
    return ids


# -------------------------------- In place Railing types -------------------------------------------------------


def get_in_place_railing_family_instances(doc):
    """
    Gets all instances of in place families of category Railing in the model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector of railing instances.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = rdb.ElementMulticategoryFilter(RAILING_CATEGORY_FILTER)
    return (
        rdb.FilteredElementCollector(doc)
        .OfClass(rdb.FamilyInstance)
        .WherePasses(filter)
    )


def get_in_place_railing_type_ids_in_model(doc):
    """
    Gets type ids off all available in place families of category Railing.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids of in place railing types.
    :rtype: list Autodesk.Revit.DB.ElementId
    """

    ids = []
    for cat in RAILING_CATEGORY_FILTER:
        ids_by_cat = rFam.get_all_in_place_type_ids_in_model_of_category(doc, cat)
        if len(ids_by_cat) > 0:
            ids = ids + ids_by_cat
    return ids
