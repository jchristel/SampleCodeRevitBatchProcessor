"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit doors.
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

from duHast.Revit.Common.common import get_ids_from_element_collector

from Autodesk.Revit.DB import (
    BuiltInCategory,
    ElementCategoryFilter,
    FamilyInstance,
    FamilySymbol,
    FilteredElementCollector,
)

# ---------------- generic door collector functions ------------------------


def get_door_instances(doc):
    """
    Retrieves a list of door instances in a Revit model.

    :param doc: The Revit document object.
    :type doc: Document
    :return: A list of door instances in the Revit model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """
    filter = ElementCategoryFilter(BuiltInCategory.OST_Doors)
    door_instances_in_model = (
        FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)
    )
    return door_instances_in_model


def get_door_symbols(doc):
    """
    Retrieves a list of door symbols in a Revit model.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of door symbols in the Revit model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = ElementCategoryFilter(BuiltInCategory.OST_Doors)
    door_symbols_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    )
    return door_symbols_in_model


def get_door_families(doc):
    """
    Retrieves a list of door families in a Revit model.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of door families in the Revit model.
    :rtype: list
    """

    door_families = []
    door_family_ids = []
    door_symbols = get_door_symbols(doc=doc)
    for door_symbol in door_symbols:
        if door_symbol.Family.Id not in door_family_ids:
            door_family_ids.append(door_symbol.Family.Id)
            door_families.append(door_symbol.Family)
    return door_families


# -------------------------- curtain wall door collector functions -----------------------------


def get_curtain_wall_door_instances(doc):
    """
    Retrieves a list of door instances in a Revit model that are considered curtain wall doors.

    :param doc: The Revit document object. It represents the Revit model.
    :type doc: Revit Document
    :return: A list of door instances in the Revit model that are considered curtain wall doors.
    :rtype: list of Autodesk.Revit.DB.FamilyInstance
    """

    curtain_wall_door_instances = []
    curtain_wall_door_symbols = get_curtain_wall_door_symbols(doc=doc)
    curtain_wall_door_symbol_ids = get_ids_from_element_collector(
        curtain_wall_door_symbols
    )
    door_instances = get_door_instances(doc=doc)

    # loop over instances and check which symbol is a curtain wall door symbol
    for door_instance in door_instances:
        if door_instance.Symbol.Id in curtain_wall_door_symbol_ids:
            curtain_wall_door_instances.append(door_instance)

    return curtain_wall_door_instances


def get_curtain_wall_door_symbols(doc):
    """
    Retrieves a list of door symbols that are considered curtain wall doors in a Revit model.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of door symbols that are considered curtain wall doors in the Revit model.
    :rtype: list
    """

    curtain_wall_door_symbols = []

    # get all door symbols in model
    door_symbols_in_model = get_door_symbols(doc)

    # get all panel symbols in model
    filter_panels = ElementCategoryFilter(BuiltInCategory.OST_CurtainWallPanels)
    panels_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter_panels)
    )

    # convert panel symbols to ids
    panel_ids = get_ids_from_element_collector(col=panels_in_model)

    # check if similar type query returns any panel id...if so then this is a curtain wall door
    for door_symbol in door_symbols_in_model:
        similar_type_ids = door_symbol.GetSimilarTypes()
        for panel_id in panel_ids:
            if panel_id in similar_type_ids:
                # found a curtain wall door
                curtain_wall_door_symbols.append(door_symbol)

    return curtain_wall_door_symbols


def get_curtain_wall_door_families(doc):
    """
    Retrieves a list of curtain wall door families in a Revit model.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :return: A list of curtain wall door families in the Revit model.
    :rtype: list[Autodesk.Revit.DB.Family]
    """

    curtain_wall_door_families = []
    curtain_wall_door_family_ids = []

    # get all curtain wall door symbols in the model
    curtain_wall_door_symbols = get_curtain_wall_door_symbols(doc=doc)

    # loop over symbols and get distinct list of families
    for curtain_wall_door_symbol in curtain_wall_door_symbols:
        if curtain_wall_door_symbol.Family.Id not in curtain_wall_door_family_ids:
            curtain_wall_door_family_ids.append(curtain_wall_door_symbol.Family.Id)
            curtain_wall_door_families.append(curtain_wall_door_symbol.Family)
    return curtain_wall_door_families


# -------------------------- basic wall door collector functions -----------------------------


def get_basic_wall_door_instances(doc):
    """
    Retrieves a list of door instances in a Revit model that are not considered curtain wall doors.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of door instances in the Revit model that are not considered curtain wall doors.
    :rtype: list
    """

    basic_wall_door_instances = []
    curtain_wall_door_symbols = get_curtain_wall_door_symbols(doc=doc)
    curtain_wall_door_symbol_ids = get_ids_from_element_collector(
        curtain_wall_door_symbols
    )
    door_instances = get_door_instances(doc=doc)

    # loop over instances and check which symbol is not a curtain wall door symbol
    for door_instance in door_instances:
        if door_instance.Symbol.Id not in curtain_wall_door_symbol_ids:
            basic_wall_door_instances.append(door_instance)

    return basic_wall_door_instances


def get_basic_wall_door_symbols(doc):
    """
    Returns a list of door symbols that are not curtain wall doors in a Revit model.

    :param doc: The Revit document object.
    :type doc: Document
    :return: A list of door symbols that are not curtain wall doors in the Revit model.
    :rtype: list[FamilySymbol]
    """

    basic_wall_door_symbols = []
    # get all door symbols in model
    door_symbols_in_model = get_curtain_wall_door_symbols(doc=doc)
    # get all curtain wall door symbols
    curtain_wall_door_symbols = get_curtain_wall_door_symbols(doc=doc)
    curtain_wall_door_symbol_ids = get_ids_from_element_collector(
        curtain_wall_door_symbols
    )
    # difference between curtain wall doors and all doors are basic wall door symbols
    for door_symbol in door_symbols_in_model:
        if door_symbol.Id not in curtain_wall_door_symbol_ids:
            basic_wall_door_symbols.append(door_symbol)

    return basic_wall_door_symbols


def get_basic_wall_door_families(doc):
    """
    Retrieves a list of basic wall door families in a Revit model.

    :param doc: The Revit document object.
    :type doc: Document
    :return: A list of basic wall door families in the Revit model.
    :rtype: list
    """

    basic_wall_door_families = []
    basic_wall_door_family_ids = []

    # get all basic wall door symbols in the model
    basic_wall_door_symbols = get_basic_wall_door_symbols(doc=doc)

    # loop over symbols and get distinct list of families
    for basic_wall_door_symbol in basic_wall_door_symbols:
        if basic_wall_door_symbol.Family.Id not in basic_wall_door_family_ids:
            basic_wall_door_family_ids.append(basic_wall_door_symbol.Family.Id)
            basic_wall_door_families.append(basic_wall_door_symbol.Family)
    return basic_wall_door_families
