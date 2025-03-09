"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Family elements
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

from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from Autodesk.Revit.DB import Element, FilteredElementCollector, Family


def get_name_to_family_dict(rvt_doc):
    """
    Create a dictionary of family name and the Family element
    :param rvt_doc: Revit document
    :type rvt_doc: Autodesk.Revit.DB.Document
    :return: Dictionary of family name and Family element
    :rtype: dict
    """

    # Get all the families in the model
    all_families = FilteredElementCollector(rvt_doc).OfClass(Family).ToElements()
    # create a dictionary of family name and family object
    family_dict = {fam.Name: fam for fam in all_families}
    return family_dict


def get_name_and_category_to_family_dict(rvt_doc):
    """
    Create a dictionary of family name and category concatenated and the Family element.
    
    Note:
        - The category is concatenated with the family name using the NESTING_SEPARATOR.
    
    This is useful when there are multiple families with the same name but different categories.

    :param rvt_doc: Revit document
    :type rvt_doc: Autodesk.Revit.DB.Document
    :return: Dictionary of family name and category and Family element
    :rtype: dict
    """

    # Get all the families in the model
    all_families = FilteredElementCollector(rvt_doc).OfClass(Family).ToElements()
    
    # create a dictionary of family name and family object
    family_dict = {"{}{}{}".format(fam.Name, NESTING_SEPARATOR, fam.FamilyCategory.Name): fam for fam in all_families}
    
    return family_dict


def get_symbol_names_of_family(family):
    """
    Get all the symbol names of a family

    :param family: Family element
    :type family: Autodesk.Revit.DB.Family
    :return: List of symbol names of the family
    :rtype: list
    """

    symbol_ids = [sym for sym in family.GetFamilySymbolIds()]
    doc = family.Document
    symbol_names = [
        Element.Name.GetValue(doc.GetElement(sym_id)) for sym_id in symbol_ids
    ]
    return symbol_names
