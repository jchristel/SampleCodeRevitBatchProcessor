"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to make a schedule for one room from a base schedule and place it on a sheet.
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

from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import ScheduleFilter, ScheduleSheetInstance, ViewDuplicateOption


def duplicate_schedule_without_transaction_wrapper(doc, schedule, new_name):
    """
    Duplicates a schedule (without its sheet placement) and names the copy.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param schedule: The schedule to duplicate.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param new_name: The name of the copy.
    :type new_name: str

    :return: Result class instance. .result holds the new schedule when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        new_id = schedule.Duplicate(ViewDuplicateOption.Duplicate)
        new_schedule = doc.GetElement(new_id)
        new_schedule.Name = new_name
        return_value.append_message("Schedule {} created.".format(new_name))
        return_value.result.append(new_schedule)
    except Exception as e:
        return_value.update_sep(False, "Failed to duplicate schedule with exception: {}".format(e))
    return return_value


def set_first_filter_value_without_transaction_wrapper(schedule, value):
    """
    Sets the value of a schedule's FIRST filter, keeping its field and its comparison. A base schedule
    for rooms has the room number as its first filter, so this limits the copy to one room.

    Changing the model: this needs to run inside a transaction.

    :param schedule: The schedule to change.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param value: The new filter value.
    :type value: str

    :return: Result class instance.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        definition = schedule.Definition
        if definition.GetFilterCount() < 1:
            return_value.update_sep(False, "Schedule {} has no filter to set.".format(schedule.Name))
            return return_value
        current = definition.GetFilter(0)
        definition.SetFilter(0, ScheduleFilter(current.FieldId, current.FilterType, value))
        return_value.append_message("First filter of {} set to {}.".format(schedule.Name, value))
    except Exception as e:
        return_value.update_sep(False, "Failed to set the schedule filter with exception: {}".format(e))
    return return_value


def place_schedule_on_sheet_without_transaction_wrapper(doc, sheet, schedule, point):
    """
    Places a schedule on a sheet.

    Changing the model: this needs to run inside a transaction.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The sheet.
    :type sheet: Autodesk.Revit.DB.ViewSheet
    :param schedule: The schedule to place.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param point: Where the upper left corner of the schedule goes on the sheet, in feet.
    :type point: Autodesk.Revit.DB.XYZ

    :return: Result class instance. .result holds the schedule sheet instance when it was created.
    :rtype: :class:`.Result`
    """

    return_value = Result()
    try:
        instance = ScheduleSheetInstance.Create(doc, sheet.Id, schedule.Id, point)
        return_value.append_message("Schedule {} placed on sheet {}.".format(schedule.Name, sheet.SheetNumber))
        return_value.result.append(instance)
    except Exception as e:
        return_value.update_sep(False, "Failed to place the schedule on the sheet with exception: {}".format(e))
    return return_value
