"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit sheet schedule instances. 
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


from duHast.Revit.Views.schedules_sheet_instances_overlap import (
    check_schedules_overlap_titleblock, 
    check_schedules_outside_titleblock, 
    check_schedules_overlap_viewports
)


def get_sheets_with_overlapping_schedules(doc, sheets):
    """
    Returns a list of sheets where schedules are overlapping the titleblock, along with the overlapping schedule instances and their required X-axis adjustments.

    Args:
        doc: The Revit document.
        sheets: A list of ViewSheet objects to check.
    Returns:
        list of tuples: [(sheet, {instance_id: delta_x}), ...] where each tuple contains a sheet and a dictionary of overlapping schedule instance IDs and their required X-axis adjustments.
    """
    
    sheets_with_overlaps = []
    for sheet in sheets:
        overlaps = check_schedules_overlap_titleblock(doc, sheet)
        if len(overlaps)>0:
            sheets_with_overlaps.append((sheet, overlaps))
    return sheets_with_overlaps


def get_sheets_with_schedules_outside_titleblock(doc, sheets):
    """
    Checks all provided sheets for schedule instances extending outside the titleblock boundary.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: A list of ViewSheet objects to check.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: A list of tuples containing the sheet and a dictionary of schedule instance IDs and the edges they violate.
    :rtype: list of (Autodesk.Revit.DB.ViewSheet, { instance_id_int: [edge_strings] })
    """
    sheets_with_issues = []
    for sheet in sheets:
        outside = check_schedules_outside_titleblock(doc, sheet)
        if len(outside) > 0:
            sheets_with_issues.append((sheet, outside))
    return sheets_with_issues


def get_sheets_with_schedules_overlapping_viewports(doc, sheets):
    """
    Checks all provided sheets for schedule instances overlapping any viewport.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: A list of ViewSheet objects to check.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: A list of tuples containing the sheet and a dictionary of overlapping schedule instance IDs and their required X movement.
    :rtype: list of (Autodesk.Revit.DB.ViewSheet, { instance_id_int: delta_x_in_feet })
    """
    sheets_with_overlaps = []
    for sheet in sheets:
        overlaps = check_schedules_overlap_viewports(doc, sheet)
        if len(overlaps) > 0:
            sheets_with_overlaps.append((sheet, overlaps))
    return sheets_with_overlaps