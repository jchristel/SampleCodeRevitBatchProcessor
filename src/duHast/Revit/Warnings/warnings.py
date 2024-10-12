"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit warnings. 
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

# -------------------------------------------- common variables --------------------


# --------------------------------------------- utility functions ------------------


def get_warnings(doc):
    """
    Returns a list of warnings from the model

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of all failure messages in model.
    :rtype: list of Autodesk.Revit.DB.FailureMessage
    """

    return doc.GetWarnings()


def get_warnings_by_guid(doc, guid):
    """
    Returns all failure message objects where failure definition has matching GUID

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: Filter: Identifying a specific failure of which the corresponding messages are to be returned.
    :type guid: Autodesk.Revit.DB.Guid

    :return: list of all failure messages with matching guid
    :rtype: list of Autodesk.Revit.DB.FailureMessage
    """

    filtered_warnings = []
    warnings = doc.GetWarnings()
    for warning in warnings:
        if str(warning.GetFailureDefinitionId().Guid) == guid:
            filtered_warnings.append(warning)
    return filtered_warnings


def get_unique_warnings_elements_by_guid(doc, guid):
    """
    Returns a list of element ids of all warnings with a specific guid
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: Filter: Identifying a specific failure of which the corresponding messages are to be returned.
    :type guid: string

    :return: List of element ids of all warnings with a specific guid
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get all warning relating to a guid
    warnings = get_warnings_by_guid(doc, guid)
    all_element_ids = []
    for warning in warnings:
        element_ids = warning.GetFailingElements()
        for element_id in element_ids:
            if element_id not in all_element_ids:
                all_element_ids.append(element_id)
    return all_element_ids



def get_single_warnings_elements_by_guid(doc, guid):
    """
    Returns a list of element ids of all warnings with a specific guid
    Returns the first failing element in each warning only!

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: Filter: Identifying a specific failure of which the corresponding messages are to be returned.
    :type guid: string

    :return: List of element ids of all warnings with a specific guid
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    # get all warning relating to a guid
    warnings = get_warnings_by_guid(doc, guid)
    all_element_ids = []
    for warning in warnings:
        element_ids = warning.GetFailingElements()
        if len(element_ids) == 1:
            all_element_ids.append(element_ids[0].IntegerValue)
    return all_element_ids


def get_warnings_grouped_by_relation(doc, guid):
    """
    Returns a dictionary of warnings where all warnings specified by guid related to each other are grouped together.
    Key will be the element with the lowest element id, value will be a list of element ids, in ascending order, of all warnings in the group (including the key!)

    Note:
    Revit must report exactly two elements per warning for this to work

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param guid: Filter: Identifying a specific failure of which the corresponding messages are to be returned.
    :type guid: Autodesk.Revit.DB.Guid

    :return: Dictionary of warnings grouped by element id
    :rtype: dict
    """

    # get all warning relating to a guid
    warnings = get_warnings_by_guid(doc, guid)

    warning_grouping = {}
    counter = 0
    for warning in warnings:
        match = False
        element_ids = warning.GetFailingElements()

        # just in case there are more than 2 elements in the warning
        if len(element_ids) != 2:
            continue

        # initialise the first warning group
        if len(warning_grouping) == 0:
            warning_grouping[counter] = [
                element_ids[0].IntegerValue,
                element_ids[1].IntegerValue,
            ]
            continue

        # check if the warning relates to an existing group
        for key, value in warning_grouping.items():
            if (
                element_ids[0].IntegerValue in value
                and element_ids[1].IntegerValue not in value
            ):
                warning_grouping[key].append(element_ids[1].IntegerValue)
                # print("added {} to group {}".format( element_ids[1].IntegerValue, counter))
                match = True
                break
            elif (
                element_ids[1].IntegerValue in value
                and element_ids[0].IntegerValue not in value
            ):
                warning_grouping[key].append(element_ids[0].IntegerValue)
                # print("added {} to group {}".format( element_ids[0].IntegerValue, counter))
                match = True
                break
            elif (
                element_ids[1].IntegerValue in value
                and element_ids[0].IntegerValue in value
            ):
                # print("matched {} {} to group {} {}".format( element_ids[0].IntegerValue, element_ids[1].IntegerValue, counter, value))
                match = True
                break
            else:
                pass
                # print("no match for {} {} in {}".format(element_ids[0].IntegerValue, element_ids[1].IntegerValue, value))
        if not match:
            counter += 1
            warning_grouping[counter] = [
                element_ids[0].IntegerValue,
                element_ids[1].IntegerValue,
            ]
            # print("new counter group: {} to group {}, {}".format(counter, element_ids[0].IntegerValue, element_ids[1].IntegerValue,))
            # new warning grouping is required

    sorted_warning_grouping = {}
    # sort the values in the dictionary
    for key, value in warning_grouping.items():
        warning_grouping[key] = sorted(value)
        sorted_warning_grouping[sorted(value)[0]] = sorted(value)
    return sorted_warning_grouping
