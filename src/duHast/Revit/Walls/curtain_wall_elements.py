"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit curtain walls helper functions.
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
from System.Collections.Generic import List

from duHast.Revit.Common.common import get_ids_from_element_collector
from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    ElementClassFilter,
    ElementMulticategoryFilter,
    FamilyInstance,
    FamilySymbol,
    FilteredElementCollector,
    Panel,
)

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_CURTAINWALL_ELEMENTS_HEADER = [
    "HOSTFILE",
    "CURTAINWALL_ELEMENT_TYPEID",
    "ReplaceMeTYPENAME",
]
#: Built in family name for empty system panel
CURTAINWALL_PANEL_EMPTY_FAMILY_NAME = "Empty System Panel"
#: Built in family name for empty system panel
CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME = "Empty System Panel"
#: Built in family name for V-shaped mullion
CURTAINWALL_MULLION_V_FAMILY_NAME = "V Corner Mullion"
#: Built in family name for circular mullion
CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME = "Circular Mullion"
#: Built in family name for quad corner mullion
CURTAINWALL_MULLION_QUAD_FAMILY_NAME = "Quad Corner Mullion"
#: Built in family name for L-shaped corner mullion
CURTAINWALL_MULLION_L_FAMILY_NAME = "L Corner Mullion"
#: Built in family name for rectangular mullion
CURTAINWALL_MULLION_RECT_FAMILY_NAME = "Rectangular Mullion"
#: Built in family name for trapezoid corner mullion
CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME = "Trapezoid Corner Mullion"

BUILTIN_TYPE_FAMILY_NAMES = [
    CURTAINWALL_PANEL_EMPTY_FAMILY_NAME,
    CURTAINWALL_PANEL_SYSTEM_FAMILY_NAME,
    CURTAINWALL_MULLION_V_FAMILY_NAME,
    CURTAINWALL_MULLION_CIRCULAR_FAMILY_NAME,
    CURTAINWALL_MULLION_QUAD_FAMILY_NAME,
    CURTAINWALL_MULLION_L_FAMILY_NAME,
    CURTAINWALL_MULLION_RECT_FAMILY_NAME,
    CURTAINWALL_MULLION_TRAPEZ_FAMILY_NAME,
]

#: category filter for all element filters by category
CURTAINWALL_ELEMENTS_CATEGORY_FILTER = List[BuiltInCategory](
    [
        BuiltInCategory.OST_CurtainWallPanels,
        BuiltInCategory.OST_CurtainWallMullions,
    ]
)

# --------------------------------------------- utility functions ------------------


def get_all_curtain_wall_element_types_by_category(doc):
    """
    Gets a filtered element collector of all curtain wall element types in the model:

    Filters by multiple categories.

    - curtain wall panels
    - curtain wall mullions
    - in place family symbols!


    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing curtain wall element types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    multi_cat_filter = ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER)
    collector = (
        FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsElementType()
    )
    return collector


def build_curtain_wall_element_type_dictionary(collector, dic):
    """
    Returns the dictionary past in with keys and or values added retrieved from collector past in.

    Keys are built in curtain wall element type names.
    TODO: this code repeats across a number of modules. Use generic instead!

    :param collector: A filtered element collector containing curtain wall element types.
    :type collector: Autodesk.Revit.DB.FilteredElementCollector
    :param dic: A dictionary containing key: curtain wall element type name, value: list of ids belonging to that type.
    :type dic: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)

    :return: A dictionary containing key: built in curtain wall element type  name, value: list of ids belonging to that type.
    :rtype: dictionary (key str, value list of Autodesk.Revit.DB.ElementId)
    """

    for c in collector:
        if c.FamilyName in dic:
            if c.Id not in dic[c.FamilyName]:
                dic[c.FamilyName].append(c.Id)
        else:
            dic[c.FamilyName] = [c.Id]
    return dic


def sort_curtain_wall_element_types_by_family_name(doc):
    """
    Returns a dictionary containing all curtain wall element types in the model.

    Key values are as per BUILTIN_TYPE_FAMILY_NAMES.
    TODO: This code repeats across a number of modules. Use generic instead!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A dictionary containing key: curtain wall element type family name, value: list of ids.
    :rtype: dic { str: [Autodesk.Revit.DB.ElementId]}
    """

    # get all CurtainWallElement types including in place wall families
    wts_two = get_all_curtain_wall_element_types_by_category(doc)
    used_wts = {}
    used_wts = build_curtain_wall_element_type_dictionary(wts_two, used_wts)
    return used_wts


# -------------------------------- none in place or loadable Curtain Wall Element types -------------------------------------------------------


def get_curtain_wall_element_instances_by_category(doc):
    """
    Gets all CurtainWallElement elements instances placed in model.

    Includes:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A filtered element collector containing curtain wall element types.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    multi_cat_filter = ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER)
    return (
        FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsNotElementType()
    )


def get_all_curtain_wall_element_type_ids_by_category(doc):
    """
    Gets all Curtain Wall Element element type ids available in model.

    Includes:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col_cat = get_all_curtain_wall_element_types_by_category(doc)
    ids = get_ids_from_element_collector(col_cat)
    return ids


def get_all_curtain_wall_element_types_by_category_excl_in_place(doc):
    """
    Gets all Curtain Wall Element element type available in model. Excludes in place family symbols.

    Includes:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementType
    """

    collector = get_all_curtain_wall_element_types_by_category(doc)
    elements = []
    for c in collector:
        if c.GetType() != FamilySymbol:
            elements.append(c)
    return elements


def get_all_curtain_wall_element_type_ids_by_category_excl_symbols(doc):
    """
    Gets all Curtain Wall Element element type ids available in model. Excludes in place family symbols.

    Includes:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall element types.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    collector = get_all_curtain_wall_element_types_by_category(doc)
    ids = []
    for c in collector:
        if c.GetType() != FamilySymbol:
            ids.append(c.Id)
    return ids


# -------------------------------- loadable Curtain Wall Element types -------------------------------------------------------


def get_all_curtain_wall_non_shared_symbol_ids_by_category(doc):
    """
    Gets a list of all loadable, non shared, family symbols (types) in the model of categories:

    - curtain wall panels
    - curtain wall mullions

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of element ids representing curtain wall family symbols.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    multi_cat_filter = ElementMulticategoryFilter(CURTAINWALL_ELEMENTS_CATEGORY_FILTER)
    collector = (
        FilteredElementCollector(doc)
        .WherePasses(multi_cat_filter)
        .WhereElementIsElementType()
    )
    for c in collector:
        if c.GetType() == FamilySymbol:
            fam = c.Family
            p_value = get_built_in_parameter_value(fam, BuiltInParameter.FAMILY_SHARED)
            if p_value != None and p_value == "No" and c.Id not in ids:
                ids.append(c.Id)
    return ids


def get_curtain_wall_panels(doc, curtain_wall_instance):
    """
    Returns a list of panel instances that are hosted in a curtain wall, excluding any family instances.

    :param doc: The current Revit model document.
    :type doc: Document
    :param curtain_wall_instance: The curtain wall instance for which to retrieve the panel instances.
    :type curtain_wall_instance: FamilyInstance
    :return: A list of panel instances hosted in the curtain wall.
    :rtype: list[Panel]
    """

    panels = []
    # get the panels from the curtain walls
    filter = ElementClassFilter(FamilyInstance)
    dependent_family_instance_ids = curtain_wall_instance.GetDependentElements(filter)
    # loop over dependent elements and only return any panel instances
    for id in dependent_family_instance_ids:
        dependent_element = doc.GetElement(id)
        if type(dependent_element) == Panel:
            panels.append(dependent_element)
    return panels
