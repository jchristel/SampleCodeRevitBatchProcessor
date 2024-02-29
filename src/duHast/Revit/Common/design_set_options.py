"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of functions around Revit Design Sets and Design Options.
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

# import common library modules
from duHast.Revit.Common import parameter_get_utils as rParaGet


# import Autodesk
from Autodesk.Revit.DB import BuiltInParameter, DesignOption, Element, FilteredElementCollector

# -------------------------------------------- common variables --------------------
#: header used in reports
REPORT_DESIGNSET_HEADER = ["HOSTFILE", "ID", "NAME", "PRIMARY OPTION", "OTHER OPTIONS"]

# --------------------------------------------- utility functions ------------------


def get_design_options(doc):
    """
    Gets all design options in a model,

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Design options in current model
    :rtype: Autodesk.Revit.DB.FilteredElementCollector
    """

    collector = FilteredElementCollector(doc).OfClass(DesignOption)
    return collector


def get_design_sets(doc):
    """
    Gets all the design sets in a model,

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: Design sets in the current model
    :rtype: list of Autodesk.Revit.DB.Element
    """

    collector = get_design_options(doc=doc)
    design_sets = []
    design_set_names = []
    for do in collector:
        e = doc.GetElement(
            do.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
        )
        designSetName = Element.Name.GetValue(e)
        if designSetName not in design_set_names:
            design_sets.append(e)
            design_set_names.append(designSetName)
    return design_sets


def is_design_option_primary(doc, design_set_name, design_option_name):
    """
    Checks whether a design option is the primary option within a design set.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param design_set_name: The name of the design set the option belongs to,
    :type design_set_name: str
    :param design_option_name: The name of the design option to be checked,
    :type design_option_name: str
    :return: True if this option is primary otherwise False
    :rtype: bool
    """

    collector = get_design_options(doc=doc)
    is_primary = False
    # loop over all design options in model, get the set they belong to and check for matches on both, set and option, by name
    for do in collector:
        design_o_name = Element.Name.GetValue(do)
        # check if '< 'in name indicating a primary option, if so remove from name
        index_chevron = design_o_name.find("<")
        if index_chevron > 0:
            design_o_name = design_o_name[: index_chevron - 2]
        # design set
        design_set = doc.GetElement(
            do.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
        )
        design_set_name = Element.Name.GetValue(design_set)
        # check for match on both set and option
        if design_set_name == design_set_name and design_o_name == design_option_name:
            # get isPrimary property on design option
            is_primary = do.IsPrimary
            break
    return is_primary


def get_design_set_option_info(doc, element):
    """
    Get the design set, design option information of an element.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param element: The element of which the design set/option data is to be returned.
    :type element: Autodesk.Revit.DB.Element
    :return: Dictionary
        Design Set Name: (can be either Main Model or the design set name)
        designOptionName:    Design Option Name (empty string if Main Model
        isPrimary:           Indicating whether design option is primary (true also if Main Model)
    :rtype: Dictionary
        designSetName:str
        designOptionName:str
        isPrimary:bool
    """

    # keys match properties in DataDesignSetOption class!!
    new_key = ["designSetName", "designOptionName", "isPrimary"]
    new_value = ["Main Model", "-", True]
    dic = dict(zip(new_key, new_value))
    try:
        # this only works for objects inheriting from Autodesk.Revit.DB.Element
        design_option = element.DesignOption
        dic["designOptionName"] = design_option.Name
        dic["isPrimary"] = design_option.IsPrimary
        e = doc.GetElement(
            design_option.get_Parameter(
                BuiltInParameter.OPTION_SET_ID
            ).AsElementId()
        )
        dic["designSetName"] = Element.Name.GetValue(e)
    except Exception as e:
        pass
    return dic
