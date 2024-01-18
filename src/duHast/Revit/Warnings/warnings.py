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
# Copyright (c) 2021  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
