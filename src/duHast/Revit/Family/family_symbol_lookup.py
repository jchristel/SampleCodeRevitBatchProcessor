"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to find family symbols (types) by their "Family : Type" name, and to activate them.

Title blocks, tags and other annotation symbols are chosen by a person from a list of "Family : Type"
names; these functions turn such a name back into the Revit symbol.
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

from Autodesk.Revit.DB import BuiltInCategory, Element, FamilySymbol, FilteredElementCollector

# the separator used when a family and a type name are written as one string
NAME_SEPARATOR = " : "


def get_symbol_full_name(symbol):
    """
    Returns the name of a family symbol as "Family : Type".

    :param symbol: A family symbol (a type).
    :type symbol: Autodesk.Revit.DB.FamilySymbol

    :return: The family name and the type name joined by " : ".
    :rtype: str
    """

    return "{}{}{}".format(symbol.FamilyName, NAME_SEPARATOR, Element.Name.GetValue(symbol))


def get_family_symbols_by_category(doc, built_in_category):
    """
    Returns all family symbols (types) of a built in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The category, for example BuiltInCategory.OST_TitleBlocks
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: List of family symbols.
    :rtype: list of Autodesk.Revit.DB.FamilySymbol
    """

    collector = (
        FilteredElementCollector(doc)
        .OfCategory(built_in_category)
        .WhereElementIsElementType()
    )
    return [symbol for symbol in collector]


def get_symbol_full_names_by_category(doc, built_in_category):
    """
    Returns the sorted, distinct "Family : Type" names of all symbols of a category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The category, for example BuiltInCategory.OST_RoomTags
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: Sorted names.
    :rtype: list of str
    """

    names = set()
    for symbol in get_family_symbols_by_category(doc, built_in_category):
        try:
            names.add(get_symbol_full_name(symbol))
        except Exception:
            # a symbol without a readable family name is not offered
            pass
    return sorted(names)


def get_family_symbol_by_full_name(doc, built_in_category, full_name):
    """
    Returns the family symbol of a category whose name is "Family : Type" (case and surrounding white space are ignored).

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: The category the symbol belongs to.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory
    :param full_name: The name as "Family : Type".
    :type full_name: str

    :return: The symbol, or None if there is none by that name.
    :rtype: Autodesk.Revit.DB.FamilySymbol or None
    """

    wanted = (full_name or "").strip().lower()
    if wanted == "":
        return None
    for symbol in get_family_symbols_by_category(doc, built_in_category):
        try:
            if get_symbol_full_name(symbol).strip().lower() == wanted:
                return symbol
        except Exception:
            continue
    return None


def get_title_block_symbol_by_name(doc, full_name):
    """
    Returns the title block symbol with the name "Family : Type".

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param full_name: The name as "Family : Type".
    :type full_name: str

    :return: The title block symbol, or None if the model has none by that name.
    :rtype: Autodesk.Revit.DB.FamilySymbol or None
    """

    return get_family_symbol_by_full_name(doc, BuiltInCategory.OST_TitleBlocks, full_name)


def activate_symbol_without_transaction_wrapper(doc, symbol):
    """
    Activates a family symbol if it is not active, which Revit requires before an instance of it can be placed.

    Activating changes the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param symbol: The symbol to activate.
    :type symbol: Autodesk.Revit.DB.FamilySymbol

    :return: True if the symbol was activated by this call, False if it was active already.
    :rtype: bool
    """

    if symbol.IsActive:
        return False
    symbol.Activate()
    doc.Regenerate()
    return True


def get_family_symbols_by_names(doc):
    """
    Returns every family symbol in the model keyed by lower case family name and type name.

    The first symbol wins when two share both names.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: (family name, type name) in lower case mapped to the symbol.
    :rtype: dict
    """

    found = {}
    for symbol in FilteredElementCollector(doc).OfClass(FamilySymbol):
        try:
            key = (
                (symbol.FamilyName or "").strip().lower(),
                (Element.Name.GetValue(symbol) or "").strip().lower(),
            )
            found.setdefault(key, symbol)
        except Exception:
            continue
    return found
