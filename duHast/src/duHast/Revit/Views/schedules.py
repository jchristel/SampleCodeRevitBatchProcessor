"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedules. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.Revit.Views.Utility.view_types import _get_view_types


def get_schedule_ids_on_sheets(doc):
    """
    Gets view ids of all schedules with instances placed on a sheet
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List containing schedule Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids


def filter_revision_schedules(view):
    """
    Checks whether a view is a revision schedule.
    (not required...schedules have a property flag!!)

    :param view: The view to check.
    :type view: Autodesk.Revit.DB.View
    :return: True if the view name starts with '<', otherwise False
    :rtype: bool
    """

    if view.Name.startswith("<"):
        return False
    else:
        return True


def get_schedules_not_on_sheets(doc):
    """
    Gets all schedules without an instance placed on a sheet.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of schedules without a sheet schedule instance.
    :rtype: list of Autodesk.Revit.DB.View
    """

    schedules_not_on_sheets = []
    # get schedules on sheets
    ids_on_sheets = get_schedule_ids_on_sheets(doc)
    # get all schedules in model
    schedules_in_model = _get_view_types(doc, rdb.ViewType.Schedule)
    # loop and filter out schedules not on sheets
    for schedule in schedules_in_model:
        if schedule.Id not in ids_on_sheets:
            schedules_not_on_sheets.append(schedule)
    return schedules_not_on_sheets
