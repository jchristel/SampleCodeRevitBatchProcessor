"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit windows.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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
    BuiltInCategory,
    ElementCategoryFilter,
    FamilyInstance,
    FamilySymbol,
    FilteredElementCollector,
)

# ---------------- generic window collector functions ------------------------


def get_window_instances(doc):
    """
    Retrieves a list of window instances in a Revit model.

    :param doc: The Revit document object.
    :type doc: Document
    :return: A list of window instances in the Revit model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """
    filter = ElementCategoryFilter(BuiltInCategory.OST_Windows)
    window_instances_in_model = (
        FilteredElementCollector(doc).OfClass(FamilyInstance).WherePasses(filter)
    )
    return window_instances_in_model


def get_window_symbols(doc):
    """
    Retrieves a list of window symbols in a Revit model.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of window symbols in the Revit model.
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    filter = ElementCategoryFilter(BuiltInCategory.OST_Windows)
    window_symbols_in_model = (
        FilteredElementCollector(doc).OfClass(FamilySymbol).WherePasses(filter)
    )
    return window_symbols_in_model


def get_window_families(doc):
    """
    Retrieves a list of window families in a Revit model.

    :param doc: The Revit document object.
    :type doc: Revit Document
    :return: A list of window families in the Revit model.
    :rtype: list
    """

    window_families = []
    window_family_ids = []
    window_symbols = get_window_symbols(doc=doc)
    for window_symbol in window_symbols:
        if window_symbol.Family.Id not in window_family_ids:
            window_family_ids.append(window_symbol.Family.Id)
            window_families.append(window_symbol.Family)
    return window_families
