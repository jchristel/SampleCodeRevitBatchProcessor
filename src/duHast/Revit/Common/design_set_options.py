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
from duHast.Revit.Common.Objects.design_set_property_names import DesignSetPropertyNames

# import Autodesk
from Autodesk.Revit.DB import (
    BuiltInParameter,
    DesignOption,
    Element,
    ElementId,
    FilteredElementCollector,
)

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


def get_active_design_option(doc):
    """
    Get the active design option in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: Active design option in current model, or if no design option is active, None
    :rtype: Autodesk.Revit.DB.DesignOption
    """

    design_option_id = DesignOption.GetActiveDesignOptionId(doc)
    # check if design option is valid ( invalid is indicator for main model active )
    if design_option_id is ElementId.InvalidElementId:
        return None
    design_option = doc.GetElement(design_option_id)
    return design_option


def get_design_set_from_option(doc, design_option):
    """
    Returns the design set of the design option.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param design_option: a revit design option
    :type design_option: Autodesk.Revit.DB.DesignOption

    :return: A revit design set or None if no design option is active
    :rtype: _type_
    """

    # if no option is active
    if design_option == None:
        return None
    design_set = doc.GetElement(
        design_option.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
    )
    return design_set


def get_design_set_of_active_design_option(doc):
    """
    Returns the design set of the current active design option.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: A revit design set or None if no design option is active
    :rtype: _type_
    """

    # get the active design option
    option = get_active_design_option(doc=doc)

    # if no option is active
    if option == None:
        return None
    
    design_set = doc.GetElement(
        option.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
    )
    return design_set


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


def get_design_options_by_design_set(doc):
    """
    Gets all the design options grouped by design sets in a model,

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: A dictionary where key is the Design sets name and value is a list of design options in that set
    :rtype: {str:[Autodesk.Revit.DB.Element]}
    """

    collector = get_design_options(doc=doc)
    design_sets = {}
    for design_option in collector:
        option_set = doc.GetElement(
            design_option.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
        )
        design_set_name = Element.Name.GetValue(option_set)
        if design_set_name not in design_sets:
            design_sets[design_set_name] = [design_option]
        else:
            design_sets[design_set_name].append(design_option)

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
    :return: Dictionary ( for keys refer to :class:`.DesignSetPropertyNames` )
        DesignSetName: (can be either Main Model or the design set name)
        designOptionName:    Design Option Name (empty string if Main Model
        isPrimary:           Indicating whether design option is primary (true also if Main Model)
    :rtype: Dictionary
        designSetName:str
        designOptionName:str
        isPrimary:bool
    """

    # keys match properties in DataDesignSetOption class!!
    new_key = [
        DesignSetPropertyNames.DESIGN_SET_NAME,
        DesignSetPropertyNames.DESIGN_OPTION_NAME,
        DesignSetPropertyNames.DESIGN_OPTION_IS_PRIMARY,
    ]
    new_value = [DesignSetPropertyNames.DESIGN_SET_DEFAULT_NAME, DesignSetPropertyNames.DESIGN_OPTION_DEFAULT_NAME, True]
    dic = dict(zip(new_key, new_value))
    try:
        # this only works for objects inheriting from Autodesk.Revit.DB.Element
        design_option = element.DesignOption
        dic[DesignSetPropertyNames.DESIGN_OPTION_NAME] = design_option.Name
        dic[DesignSetPropertyNames.DESIGN_OPTION_IS_PRIMARY] = design_option.IsPrimary
        e = doc.GetElement(
            design_option.get_Parameter(BuiltInParameter.OPTION_SET_ID).AsElementId()
        )
        dic[DesignSetPropertyNames.DESIGN_SET_NAME] = Element.Name.GetValue(e)
    except Exception as e:
        pass
    return dic


# filters
def get_design_option_ids_of_all_primary_options(doc):
    """
    Get the design option ids of all primary options in a model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of design option ids of all primary options in the model.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    collector = get_design_options(doc=doc)
    primary_options_ids = []
    for do in collector:
        if do.IsPrimary:
            primary_options_ids.append(do.Id)
    return primary_options_ids


def get_design_option_ids_of_all_primary_options_but_the_one_containing_filter_id(
    doc, filter_Id
):
    """
    Get the design option ids of all primary options in a model except the one where the design set contains a design option with the filter id.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param filter_Id: Element Id of the filter.
    :type filter_Id: Autodesk.Revit.DB.ElementId
    :return: List of design option ids of all primary options in the model except the one containing the filter id.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # setup return value
    primary_options_ids = []

    # get a dictionary with design sets as key and design options as values
    design_options_byd_design_set = get_design_options_by_design_set(doc)

    # loop over all design sets and check if the filter id is in the design options
    for design_set, design_options in design_options_byd_design_set.items():
        # set filter match flag
        match = False
        # set default value for primary design option id
        primary_design_option_id = None
        # loop over all design options in the design set
        for design_option in design_options:
            # check if design option is primary
            if design_option.IsPrimary:
                primary_design_option_id = design_option.Id
            # check if design option id is the filter id
            if design_option.Id == filter_Id:
                match = True
                break
        # if no match was found, add the primary design option id to the list
        if not match:
            primary_options_ids.append(primary_design_option_id)
    return primary_options_ids
