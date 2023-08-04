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
#: header used in reports
REPORT_WARNINGS_HEADER = [
    "HOSTFILE",
    "ID",
    "NAME",
    "WARNING TYPE",
    "NUMBER OF WARNINGS",
]

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
