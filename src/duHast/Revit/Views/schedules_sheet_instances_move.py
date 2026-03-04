"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to moving of Revit sheet schedule instances. 
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

from duHast.Utilities.Objects.result import Result

from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Views.schedules import filter_split_schedules
from duHast.Revit.Views.schedules_sheet_instances_overlap import check_schedule_sheet_instances_are_overlapping

from Autodesk.Revit.DB import (
    Element,
    ElementId,
    ElementTransformUtils,
    Transaction,
    XYZ
    )


def move_schedule_instance_along_x(doc, segments_to_move, schedule_name):
    """
    Moves schedule segment along the X axis by a given distance.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param segments_to_move: A Dictionary containing as key the view schedule segment Id and the distance along the X it is to move in inches
    :type segments_to_move: { instance_id_int: delta_x_in_feet }

    :return: A Result object containing the move status and message for each segment moved.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()
    for segment_id, distance in segments_to_move.items():

        # set up an action to be ruin inside a transaction to move the schedule segment
        def action():
            action_return_value = Result()
            desired_Gap = distance 
            try:
                view_schedule_instance = doc.GetElement(ElementId(segment_id))
                current_pos = view_schedule_instance.Point
                target_pos = XYZ(view_schedule_instance.Point.X + desired_Gap, current_pos.Y, 0)
                translation = target_pos - current_pos
                ElementTransformUtils.MoveElement(doc, view_schedule_instance.Id, translation)
            except Exception as e:
                action_return_value.update_sep(False, "{}".format(e))

        # set up a transaction to move the schedule segment
        tranny = Transaction(doc, "Moving segment of schedule {}".format( schedule_name))
        tranny_result = in_transaction(tranny, action)
        
        # check what came back
        if tranny_result.status:
            return_value.append_message("...Moved schedule segment with id: {} successfully".format(segment_id))
        else:
            return_value.update_sep(False, "Failed to move schedule segment: {} with exception: {}".format(segment_id, tranny_result.message))
    return return_value



def resolve_overlaps(doc, schedule, schedule_name, max_iterations=10):
    """
    Check if schedule segments are overlapping and if so move them iteratively until no more overlaps are detected or max iterations is reached.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document
    :param schedule: The Revit schedule object to check for overlaps.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param schedule_name: The name of the schedule being processed (used for logging).
    :type schedule_name: str
    :param max_iterations: The maximum number of iterations to attempt to resolve overlaps (default is 10).
    :type max_iterations: int

    :return: A Result object containing a list of schedules that were skipped because they did not contain the specified field.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()
    resolved = False

    # loop until conflicts are resolved or max iterations is reached
    for iteration in range(max_iterations):
        
        # check for segments that are overlapping and need to be moved
        segments_to_move = check_schedule_sheet_instances_are_overlapping(doc, schedule)
        
        # if no segments need to be moved then we are done
        if not segments_to_move:
            return_value.append_message("No more overlaps detected after {} iterations.".format(iteration))
            return return_value
        return_value.append_message("Iteration {}: Found {} overlapping segments that need to be moved".format(iteration, len(segments_to_move)))

        # lets start moving them one by one since moving them all at once can cause new overlaps to be detected that would not have been if we had moved them sequentially
        move_result = move_schedule_instance_along_x(doc, segments_to_move, schedule_name)
        
        # check if move was successful
        if not move_result.status:
            return_value.update_sep(False, "Failed to move schedule segments during overlap resolution: {}".format(move_result.message))
            return return_value
        else:
            return_value.append_message("Moved schedule segments successfully during iteration {}".format(iteration))
    
    # epic fail
    if not resolved:
        return_value.update_sep(False, "Warning: max iterations reached, overlaps may still exist")
    
    return return_value


def move_schedule_sheet_instances_in_x_until_no_overlap(doc, schedules):
    """
    Finds any split schedule in the model and moves segments 1 to n (skips 0) by a given distance (the overlap) to the right.

    :param doc: The Revit document object.
    :type doc: Autodesk.Revit.DB.Document

    :return: None
    """

    return_value = Result()

    # get all splitr schedules in model and move segments 1 to n by a given distance to the right to resolve overlaps
    split_schedules = filter_split_schedules(schedules)

    # check if any split schedules were found
    if len(split_schedules)==0:
        return_value.append_message("No split schedules in model")
        return return_value
    
    # loop and resolve overlaps for each split schedule
    for split_schedule in split_schedules:
        schedule_name = Element.Name.GetValue(split_schedule)
        return_value.append_message("Processing schedule {}".format(schedule_name))

        # iteratively fix overlaps
        # this is a pretty slow process since Revit has to re-draw the sheet every time which is an expensive operation, 
        # but it is the only way I have found to reliably resolve overlaps between schedule segments
        resolve_result = resolve_overlaps(doc, split_schedule, schedule_name, max_iterations=10)
    
        # check what came back
        if resolve_result.status:
            return_value.append_message("Successfully resolved overlaps for schedule {}".format(schedule_name))
        else:
            return_value.update_sep(False, "Failed to resolve overlaps for schedule {}: {}".format(schedule_name, resolve_result.message))
    return return_value