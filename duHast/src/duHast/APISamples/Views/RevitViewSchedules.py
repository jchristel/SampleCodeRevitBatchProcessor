'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedules. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
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

import Autodesk.Revit.DB as rdb

from duHast.APISamples.Views.Utility.ViewTypes import _get_view_types


def get_schedule_ids_on_sheets(doc):
    '''
    Gets view ids of all schedules with instances placed on a sheet
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List containing schedule Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    '''

    ids=[]
    col = rdb.FilteredElementCollector(doc).OfClass(rdb.ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids


def filter_revision_schedules(view):
    '''
    Checks whether a view is a revision schedule.
    (not required...schedules have a property flag!!)

    :param view: The view to check.
    :type view: Autodesk.Revit.DB.View
    :return: True if the view name starts with '<', otherwise False
    :rtype: bool
    '''

    if(view.Name.startswith('<')):
        return False
    else:
        return True


def get_schedules_not_on_sheets(doc):
    '''
    Gets all schedules without an instance placed on a sheet.
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: list of schedules without a sheet schedule instance.
    :rtype: list of Autodesk.Revit.DB.View
    '''

    schedules_not_on_sheets = []
    # get schedules on sheets
    ids_on_sheets = get_schedule_ids_on_sheets(doc)
    # get all schedules in model
    schedules_in_model = _get_view_types(doc, rdb.ViewType.Schedule)
    # loop and filter out schedules not on sheets
    for schedule in schedules_in_model:
        if(schedule.Id not in ids_on_sheets):
            schedules_not_on_sheets.append(schedule)
    return schedules_not_on_sheets