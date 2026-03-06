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
    check_schedule_sheet_instances_are_overlapping,
    check_schedules_outside_titleblock, 
    check_schedules_overlap_viewports
)
from duHast.Revit.Views.schedules import  get_schedule_instance_on_sheet

from duHast.UI.Objects.ProgressBase import ProgressBase

from Autodesk.Revit.DB import Element 


def get_sheets_with_overlapping_schedules(doc, sheets, callback_progress=None):
    """
    Returns a list of sheets where schedules are overlapping the titleblock, along with the overlapping schedule instances and their required X-axis adjustments.

    Args:
        doc: The Revit document.
        sheets: A list of ViewSheet objects to check.
    Returns:
        list of tuples: [(sheet, {instance_id: delta_x}), ...] where each tuple contains a sheet and a dictionary of overlapping schedule instance IDs and their required X-axis adjustments.
    """
    
    if isinstance(callback_progress, ProgressBase) == False and callback_progress is not None:
        raise ValueError("callback_progress is not a ProgressBase: {}".format(type(callback_progress)))

    # progress bar data
    max = len(sheets)
    counter = 1

    sheets_with_overlaps = []
    for sheet in sheets:

        # update the progress bar
        counter += 1
        if callback_progress:
            callback_progress.update(counter, max)

        # get the schedule instances on this sheet
        schedules_sheet_instances_on_sheet = get_schedule_instance_on_sheet(doc, sheet)

        # loop over all instances and  heck if they are overlapping with any other schedule instance on the sheet. If they are, add the sheet and the overlapping instances to the list to be returned.
        for schedule_instance in schedules_sheet_instances_on_sheet:
            # get the schedule element for this instance
            owner_schedule = doc.GetElement(schedule_instance.ScheduleId)
            # check if this schedule instance is overlapping with any other schedule instance on the sheet. If it is, add the sheet and the overlapping instances to the list to be returned.
            overlaps = check_schedule_sheet_instances_are_overlapping(doc,  owner_schedule, sheet.Id)

            if len(overlaps)>0:
                sheets_with_overlaps.append((sheet, overlaps))
        
        # Check the progress bar for cancellation after each schedule is processed since this is a pretty slow process and the user may want to cancel it if they see it is taking too long
        if callback_progress and callback_progress.is_cancelled() == True:
            break

    return sheets_with_overlaps


def get_sheets_with_schedules_outside_titleblock(doc, sheets, callback_progress=None):
    """
    Checks all provided sheets for schedule instances extending outside the titleblock boundary.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: A list of ViewSheet objects to check.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: A list of tuples containing the sheet and a dictionary of schedule instance IDs and the edges they violate.
    :rtype: list of (Autodesk.Revit.DB.ViewSheet, { instance_id_int: [edge_strings] })
    """

    if isinstance(callback_progress, ProgressBase) == False and callback_progress is not None:
        raise ValueError("callback_progress is not a ProgressBase: {}".format(type(callback_progress)))

    # progress bar data
    max = len(sheets)
    counter = 1

    sheets_with_issues = []
    for sheet in sheets:
        # update the progress bar
        counter += 1
        if callback_progress:
            callback_progress.update(counter, max)

        outside = check_schedules_outside_titleblock(doc, sheet)
        if len(outside) > 0:
            sheets_with_issues.append((sheet, outside))
        
        # Check the progress bar for cancellation after each schedule is processed since this is a pretty slow process and the user may want to cancel it if they see it is taking too long
        if callback_progress and callback_progress.is_cancelled() == True:
            break

    return sheets_with_issues


def get_sheets_with_schedules_overlapping_viewports(doc, sheets, callback_progress=None):
    """
    Checks all provided sheets for schedule instances overlapping any viewport.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheets: A list of ViewSheet objects to check.
    :type sheets: list of Autodesk.Revit.DB.ViewSheet

    :return: A list of tuples containing the sheet and a dictionary of overlapping schedule instance IDs and their required X movement.
    :rtype: list of (Autodesk.Revit.DB.ViewSheet, { instance_id_int: delta_x_in_feet })
    """

    if isinstance(callback_progress, ProgressBase) == False and callback_progress is not None:
        raise ValueError("callback_progress is not a ProgressBase: {}".format(type(callback_progress)))

    # progress bar data
    max = len(sheets)
    counter = 1

    sheets_with_overlaps = []
    for sheet in sheets:
        # update the progress bar
        counter += 1
        if callback_progress:
            callback_progress.update(counter, max)

        overlaps = check_schedules_overlap_viewports(doc, sheet)
        if len(overlaps) > 0:
            sheets_with_overlaps.append((sheet, overlaps))
        
        # Check the progress bar for cancellation after each schedule is processed since this is a pretty slow process and the user may want to cancel it if they see it is taking too long
        if callback_progress and callback_progress.is_cancelled() == True:
            break

    return sheets_with_overlaps