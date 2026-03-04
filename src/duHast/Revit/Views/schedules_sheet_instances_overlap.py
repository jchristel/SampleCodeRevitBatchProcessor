"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to moving of Revit sheet schedule instances overlapping. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Views.sheets import get_titleblock_bounding_box

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    ScheduleSheetInstance,
    UnitUtils,
    UnitTypeId,
)

def check_schedule_sheet_instances_are_overlapping(doc, schedule):
    """
    Checks if any segments of a split schedule overlap on their respective sheets.

    Returns a dictionary mapping segment instance IDs (int) to the distance in feet
    they need to move in the X direction to resolve the overlap. If the schedule is
    not split or no overlaps are found, an empty dictionary is returned.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param schedule: The Revit schedule object from which to extract the field index.
    :type schedule: Autodesk.Revit.DB.ViewSchedule

    :return: a dictionary where key is the schedule sheet instance Id as integer and the distance it has to move to avoid overlap with the previous segment.
    :rtype: { instance_id_int: delta_x_in_feet }
    
    """

    SCHEDULE_MARGIN = 0.00695

    if not schedule.IsSplit():
        return {}

    segment_count = schedule.GetSegmentCount()
    bounding_boxes_by_sheet = {}

    for i in range(segment_count):
        instance_ids = schedule.GetScheduleInstances(i)
        for instance_id in instance_ids:
            instance = doc.GetElement(instance_id)
            owner_sheet = doc.GetElement(instance.OwnerViewId)
            sheet_key = instance.OwnerViewId.IntegerValue

            bb = instance.get_BoundingBox(owner_sheet)
            min_x = bb.Min.X + SCHEDULE_MARGIN
            min_y = bb.Min.Y + SCHEDULE_MARGIN
            max_x = bb.Max.X - SCHEDULE_MARGIN
            max_y = bb.Max.Y - SCHEDULE_MARGIN

            if sheet_key not in bounding_boxes_by_sheet:
                bounding_boxes_by_sheet[sheet_key] = []
            bounding_boxes_by_sheet[sheet_key].append((min_x, min_y, max_x, max_y, instance_id))

    segments_to_move = {}  # { instance_id_int: delta_x_in_feet }

    for sheet_id, instances in bounding_boxes_by_sheet.items():
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                i_min_x, i_min_y, i_max_x, i_max_y, i_id = instances[i]
                j_min_x, j_min_y, j_max_x, j_max_y, j_id = instances[j]

                overlap_x = i_min_x < j_max_x and i_max_x > j_min_x
                overlap_y = i_min_y < j_max_y and i_max_y > j_min_y

                if overlap_x and overlap_y:
                    # move the rightmost segment out of the way
                    if j_min_x >= i_min_x:
                        delta = i_max_x - j_min_x + SCHEDULE_MARGIN
                        segments_to_move[j_id.IntegerValue] = delta
                    else:
                        delta = j_max_x - i_min_x + SCHEDULE_MARGIN
                        segments_to_move[i_id.IntegerValue] = delta

    return segments_to_move


def check_schedules_overlap_titleblock(doc, sheet):
    """
    Checks if any schedule sheet instances on a given sheet overlap with the titleblock (inside the title block)

    Returns a dictionary mapping schedule sheet instance IDs (int) to the distance
    in feet they need to move in the X direction to clear the titleblock.

    Args:
        doc: The Revit document.
        sheet: The ViewSheet to check.

    Returns:
        dict: { instance_id (int): delta_x (float) } for each overlapping schedule instance.
    """
    SCHEDULE_MARGIN = 0.00695

    # get titleblock bb
    tb_bb = get_titleblock_bounding_box(doc, sheet)
    if tb_bb is None:
        return {}

    # get all schedule sheet instances on the sheet
    instances = FilteredElementCollector(doc, sheet.Id)\
        .OfClass(ScheduleSheetInstance)\
        .WhereElementIsNotElementType()\
        .ToElements()

    segments_to_move = {}

    for instance in instances:
        if instance.IsTitleblockRevisionSchedule:
            continue

        s_bb = instance.get_BoundingBox(sheet)
        s_min_x = s_bb.Min.X + SCHEDULE_MARGIN
        s_min_y = s_bb.Min.Y + SCHEDULE_MARGIN
        s_max_x = s_bb.Max.X - SCHEDULE_MARGIN
        s_max_y = s_bb.Max.Y - SCHEDULE_MARGIN

        overlap_x = s_min_x < tb_bb.Max.X and s_max_x > tb_bb.Min.X
        overlap_y = s_min_y < tb_bb.Max.Y and s_max_y > tb_bb.Min.Y

        if overlap_x and overlap_y:
            delta = tb_bb.Max.X - s_min_x + SCHEDULE_MARGIN
            segments_to_move[instance.Id.IntegerValue] = delta

    return segments_to_move


def check_schedules_outside_titleblock(doc, sheet):
    """
    Checks if any schedule sheet instances on a given sheet extend outside the titleblock boundary.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The ViewSheet to check.
    :type sheet: Autodesk.Revit.DB.ViewSheet

    :return: a dictionary where key is the schedule sheet instance Id as integer and a list of edges it is outside of.
    :rtype: { instance_id_int: [edge_strings] }
    """
    SCHEDULE_MARGIN = 0.00695
    OVERLAP_TOLERANCE = UnitUtils.ConvertToInternalUnits(3.0, UnitTypeId.Millimeters)

    tb_bb = get_titleblock_bounding_box(doc, sheet)
    if tb_bb is None:
        return {}

    instances = FilteredElementCollector(doc, sheet.Id)\
        .OfClass(ScheduleSheetInstance)\
        .WhereElementIsNotElementType()\
        .ToElements()

    segments_outside = {}

    for instance in instances:
        if instance.IsTitleblockRevisionSchedule:
            continue

        s_bb = instance.get_BoundingBox(sheet)
        s_min_x = s_bb.Min.X + SCHEDULE_MARGIN
        s_min_y = s_bb.Min.Y + SCHEDULE_MARGIN
        s_max_x = s_bb.Max.X - SCHEDULE_MARGIN
        s_max_y = s_bb.Max.Y - SCHEDULE_MARGIN

        issues = []
        if s_min_x < tb_bb.Min.X + OVERLAP_TOLERANCE:
            issues.append("left")
        if s_max_x > tb_bb.Max.X - OVERLAP_TOLERANCE:
            issues.append("right")
        if s_min_y < tb_bb.Min.Y + OVERLAP_TOLERANCE:
            issues.append("bottom")
        if s_max_y > tb_bb.Max.Y - OVERLAP_TOLERANCE:
            issues.append("top")

        if issues:
            segments_outside[instance.Id.IntegerValue] = issues

    return segments_outside


def check_schedules_overlap_viewports(doc, sheet):
    """
    Checks if any schedule sheet instances on a given sheet overlap with any viewports.

    Returns a dictionary mapping schedule sheet instance IDs (int) to the distance
    in feet they need to move in the X direction to clear the overlapping viewport.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: The ViewSheet to check.
    :type sheet: Autodesk.Revit.DB.ViewSheet

    :return: a dictionary where key is the schedule sheet instance Id as integer and the distance it has to move to avoid overlap with a viewport.
    :rtype: { instance_id_int: delta_x_in_feet }
    """

    SCHEDULE_MARGIN = 0.00695
    OVERLAP_TOLERANCE = UnitUtils.ConvertToInternalUnits(3.0, UnitTypeId.Millimeters)

    # get all viewports on the sheet
    viewport_ids = sheet.GetAllViewports()
    if not viewport_ids:
        return {}

    # get all schedule sheet instances on the sheet
    instances = FilteredElementCollector(doc, sheet.Id)\
        .OfClass(ScheduleSheetInstance)\
        .WhereElementIsNotElementType()\
        .ToElements()

    if not instances:
        return {}

    segments_to_move = {}

    for instance in instances:
        if instance.IsTitleblockRevisionSchedule:
            continue

        s_bb = instance.get_BoundingBox(sheet)
        s_min_x = s_bb.Min.X + SCHEDULE_MARGIN
        s_min_y = s_bb.Min.Y + SCHEDULE_MARGIN
        s_max_x = s_bb.Max.X - SCHEDULE_MARGIN
        s_max_y = s_bb.Max.Y - SCHEDULE_MARGIN

        # check against every viewport on the sheet
        for vp_id in viewport_ids:
            viewport = doc.GetElement(vp_id)
            vp_outline = viewport.GetBoxOutline()

            vp_min_x = vp_outline.MinimumPoint.X
            vp_min_y = vp_outline.MinimumPoint.Y
            vp_max_x = vp_outline.MaximumPoint.X
            vp_max_y = vp_outline.MaximumPoint.Y

            overlap_x = s_min_x < vp_max_x - OVERLAP_TOLERANCE and s_max_x > vp_min_x + OVERLAP_TOLERANCE
            overlap_y = s_min_y < vp_max_y - OVERLAP_TOLERANCE and s_max_y > vp_min_y + OVERLAP_TOLERANCE

            if overlap_x and overlap_y:
                # take the worst case delta if multiple viewports overlap
                delta = vp_max_x - s_min_x
                instance_key = instance.Id.IntegerValue
                if instance_key not in segments_to_move or delta > segments_to_move[instance_key]:
                    segments_to_move[instance_key] = delta

    return segments_to_move