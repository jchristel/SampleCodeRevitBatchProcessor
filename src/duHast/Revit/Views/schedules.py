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

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Category,
    ElementId,
    FilteredElementCollector,
    FilteredElementCollector, 
    ScheduleSheetInstance,
    ViewSchedule,
    ViewType
    )

from duHast.Revit.Views.views import get_views_of_type


def get_schedule_ids_on_sheets(doc):
    """
    Gets view ids of all schedules with instances placed on a sheet
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List containing schedule Id's.
    :rtype: list of Autodesk.Revit.DB.ElementId
    """

    ids = []
    col = FilteredElementCollector(doc).OfClass(ScheduleSheetInstance)
    for s in col:
        if s.ScheduleId not in ids:
            ids.append(s.ScheduleId)
    return ids


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
    schedules_in_model = get_views_of_type(doc, ViewType.Schedule)
    # loop and filter out schedules not on sheets
    for schedule in schedules_in_model:
        if schedule.Id not in ids_on_sheets:
            schedules_not_on_sheets.append(schedule)
    return schedules_not_on_sheets


def get_schedule_instance_on_sheet(doc, sheet):
    """
    Returns a list containing all schedule sheet instances on a sheet.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: A sheet
    :type sheet: Autodesk.Revit.DB.ViewSheet
    :return: a list of schedule sheet instances or empty list if none found
    :rtype: [Autodesk.revit.DB.ScheduleSheetInstance]
    """

    schedule_instances_on_sheet = []
    col = FilteredElementCollector(doc).OfClass(ScheduleSheetInstance)

    # Filter the instances where the OwnerViewId matches the specified sheet_id
    for schedule_sheet_instance in col:
        if schedule_sheet_instance.OwnerViewId == sheet.Id:
            # rule oout revision schedules...
            schedule = doc.GetElement(schedule_sheet_instance.ScheduleId)
            if not schedule.IsTitleblockRevisionSchedule:
                schedule_instances_on_sheet.append(schedule_sheet_instance)
    
    return schedule_instances_on_sheet


def get_schedules(doc):
    """
    Get all schedules in the current document excluding titleblock revision schedules.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of schedules in the current document.
    :rtype: list[Autodesk.Revit.DB.ViewSchedule]
    """
    schedules_filtered = []
    collector = FilteredElementCollector(doc).OfClass(ViewSchedule)
    
    for schedule in collector:
        if not schedule.IsTitleblockRevisionSchedule:
            schedules_filtered.append(schedule)
    return schedules_filtered


def get_schedules_by_built_in_category (doc, built_in_category):
    """
    Get all schedules in the current document by built-in category.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param built_in_category: Built-in category to filter schedules by.
    :type built_in_category: Autodesk.Revit.DB.BuiltInCategory

    :return: List of schedules in the current document filtered by built-in category.
    :rtype: list[Autodesk.Revit.DB.ViewSchedule]
    """
    
    schedules_filtered = []
    
    # get all schedules in the model
    schedules_in_model = get_schedules(doc)

    # get the category from the built-in category
    cat = Category.GetCategory(doc, built_in_category)

    # filter schedules by category
    for schedule in schedules_in_model:
        if schedule.Definition.CategoryId == cat.Id:
            schedules_filtered.append(schedule)
    
    return schedules_filtered


def get_all_multi_category_schedules(doc):
    """
    Get all multi-category schedules in the current document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of multi-category schedules in the current document.
    :rtype: list[Autodesk.Revit.DB.ViewSchedule]
    """
    
    multi_category_schedules = []
    
    # get all schedules in the model
    schedules_in_model = get_schedules(doc)

    # filter for multi-category schedules (invalid category element id)
    for schedule in schedules_in_model:
        if schedule.Definition.CategoryId == ElementId.InvalidElementId:
            multi_category_schedules.append(schedule)
    
    return multi_category_schedules


def get_all_sheet_schedules(doc):
    """
    Get all schedules that are placed on sheets in the current document.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document

    :return: List of schedules that are placed on sheets.
    :rtype: list[Autodesk.Revit.DB.ViewSchedule]
    """
    
    sheet_schedules = get_schedules_by_built_in_category (
        doc=doc, 
        built_in_category=BuiltInCategory.OST_Sheets
    )
    
    return sheet_schedules