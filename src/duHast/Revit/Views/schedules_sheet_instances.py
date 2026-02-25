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


from duHast.Revit.Views.sheets import get_titleblock_bounding_box

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    ScheduleSheetInstance,
)

def check_schedules_overlap_titleblock(doc, sheet):
    """
    Checks if any schedule sheet instances on a given sheet overlap with the titleblock.

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