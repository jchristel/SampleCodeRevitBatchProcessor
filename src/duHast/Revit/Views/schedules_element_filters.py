"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to filters Revit view schedules. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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


def get_schedule_filters(schedule):
    filters = schedule.Definition.GetFilters()
    return filters


def get_schedule_filters_by_field_name(schedule, field_name):
    """
    Gets the filters of a schedule by the field name.

    :param schedule: Revit schedule view.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param field_name: Name of the field to get the filters for.
    :type field_name: str

    :return:
        List of filters that are applied to the schedule for the specified field name. If no filters are found, an empty list is returned.
    :rtype: list of Autodesk.Revit.DB.ScheduleFilter
    """

    filters_for_field = []
    if schedule.Definition.GetFilterCount() > 0:
        filters = get_schedule_filters(schedule)
        for filter in filters:
            schedule_field = schedule.Definition.GetField(filter.FieldId)
            schedule_filed_name = schedule_field.GetName()
            if schedule_filed_name == field_name:
                filters_for_field.append(filter)
    
    return filters_for_field


def get_schedule_filters_and_index_by_field_name(schedule, field_name):
    """
    Gets the filters of a schedule by the field name.

    :param schedule: Revit schedule view.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param field_name: Name of the field to get the filters for.
    :type field_name: str

    :return:
        List of tuples in format(filter, index) that are applied to the schedule for the specified field name. If no filters are found, an empty list is returned.
    :rtype: list of Autodesk.Revit.DB.ScheduleFilter
    """

    filters_for_field = []
    if schedule.Definition.GetFilterCount() > 0:
        index = 0
        filters = get_schedule_filters(schedule)
        for filter in filters:
            schedule_field = schedule.Definition.GetField(filter.FieldId)
            schedule_filed_name = schedule_field.GetName()
            if schedule_filed_name == field_name:
                filters_for_field.append((filter, index))
            index += 1
    
    return filters_for_field