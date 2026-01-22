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

from System import Int64 # revit element Id expects 64 bit integer

from duHast.Revit.Rooms.Geometry.room_spatial_elements import get_only_wall_segments_as_walls,  get_room_segments
from duHast.Revit.Rooms.room_common_parameters import get_room_number, get_room_name
from duHast.Revit.Common.transaction import in_transaction
from duHast.pyRevit.console_output import print_header, print_error
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.parameter_set_utils import set_parameter_without_transaction_wrapper_by_name

from rooms.Objects.room_storage import room_storage
from rooms.Objects.wall_storage import wall_storage

from Autodesk.Revit.DB import BuiltInCategory, ElementId,  FilteredElementCollector, Transaction, Wall


WALL_PROPERTY_TO_SAVE_ROOM_NUMBER = "HSL_ID_HOST"


def get_wall_segments_of_room(doc, room, room_number=None, room_name=None):
   
    segments = get_room_segments(room)
    print("found {} segment loop in room {}".format(len(segments), room.Id))
    walls = get_only_wall_segments_as_walls(doc, segments)
    print("found {} walls in room {}".format(len(walls), room.Id))

    # if no walls found, return None
    if len(walls) == 0:
        return None
    
    # create a room storage object to store the wall segments
    rooms_data = room_storage(room_number, room.Id.Value)

    # check get wall segments of the room
    for nested_segments in segments:
        for segment in nested_segments:
           
            # get the host and check if its a wall
            host_element = doc.GetElement(segment.ElementId)

            if isinstance(host_element, Wall) == False:
                # if not a wall move on to next segment
                continue

            # get the curve of the segment
            curve = segment.GetCurve()

            # add the wall id and length to the room storage object
            # here comes the thing:
            # revit splits a wall into multiple segments if that wall is joined with another wall
            # so need to check if that id is already in the dictionary and if so, add the length to the existing length
            if host_element.Id.Value in rooms_data.wall_id_and_length:
                # if wall id already exists, add the length to the existing length
                rooms_data.wall_id_and_length[host_element.Id.Value] += curve.Length
            else:
                rooms_data.wall_id_and_length[host_element.Id.Value] = curve.Length
 
    return rooms_data

def get_wall_segments_of_rooms(doc, rooms, pb=None):

    # set up a status tracker
    return_value = Result()
    all_wall_storage = []
    
    # loop over rooms and get the wall segments of each room
    room_counter = 0
    try:
        # get all bounding wells of the rooms
        for room in rooms:
            #update progress bar counter
            room_counter += 1
            
            # get default room values
            room_name = "No room name found"
            # build the room name
            room_name = get_room_name(room)

            room_number = "No room number found"
            room_number = get_room_number(room)

            # print the room name to the console
            print_header("Processing room: {} {}".format(room_number, room_name))

            # get the wall segments of the room
            wall_storage = get_wall_segments_of_room (
                doc=doc, 
                room=room, 
                room_number=room_number, 
                room_name=room_name)

            # if no wall segments found, continue to next room
            if wall_storage is None:
                continue


            all_wall_storage.append(wall_storage)

            # cancelled?
            if pb is not None and pb.cancelled:
                message = "User cancelled."
                print_error(message)
                return_value.update_sep(False, message=message)
               
               
            if pb is not None:
                # update progress bar
                pb.update_progress(room_counter, len(rooms))
           
    except Exception as e:
        print("Error while getting wall segments of rooms: {}".format(e))
        return_value.update_sep(False, "Error while getting wall segments of rooms: {}".format(e))
        return return_value
    

    return_value.result.append(all_wall_storage)

    return return_value
        

def build_segment_and_room_to_wall_id (walls_by_room):

    # dictionary where the key is the wall id and the value is a list of wall storage objects
    wall_id_and_rooms = {}

    # loop over walls by room dictionary 
    for room_storage in walls_by_room:

        # loop over wall id and length in the room storage object
        for wall_id, length in room_storage.wall_id_and_length.items():

            # check if wall id exists in dictionary already
            if wall_id not in wall_id_and_rooms:
                # if not, add it with an empty list
                wall_id_and_rooms[wall_id] = []
            

            # build a new storage object for the wall
            w_storage = wall_storage(room_storage.room_number,room_storage.room_id, length)

            # add new storage object to the list
            wall_id_and_rooms[wall_id].append( w_storage)
           
       
    # return the dictionary of wall id and rooms
    return wall_id_and_rooms

            

def update_walls_with_room_number_of_longest_segment(doc, wall_id_and_rooms ,pb=None, target_parameter_name=WALL_PROPERTY_TO_SAVE_ROOM_NUMBER):
    """
    Update the walls with the room number of the longest segment the wall is bounding a room by.
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param wall_id_and_rooms: Dictionary of wall id and list of wall storage objects.
    :type wall_id_and_rooms: dict
    """

    # set up a status tracker
    return_value = Result()

    def action():

        action_return_value = Result()
        counter = 0
        try:
            # update all walls with room number of longest segment
            # loop over wall id and rooms
            for wall_id, rooms in wall_id_and_rooms.items():

                #update progress bar counter
                counter += 1

                # get the longest segment
                longest_segment = max(rooms, key=lambda x: x.segment_length)

                # get the wall element by id
                wall_element = doc.GetElement(ElementId(Int64(wall_id)))

                if wall_element is None:
                    continue

                # set the room number parameter to the longest segment's room number
                print("Updating wall {} with room number {}".format(wall_id, longest_segment.room_number))

                set_result = Result()
                try:
                    # set the parameter value
                    set_result = set_parameter_without_transaction_wrapper_by_name(element=wall_element, 
                        parameter_name=target_parameter_name, 
                        parameter_value=longest_segment.room_number)
               
                    action_return_value.update(set_result)
                except Exception as e:
                    message = "Error while setting parameter {} for wall {}: {}".format(
                        target_parameter_name, wall_id, e)
                    action_return_value.update_sep(False, message=message)
                
                # cancelled?
                if pb is not None and pb.cancelled:
                    message = "User cancelled."
                    action_return_value.update_sep(False, message=message)
                    return action_return_value
                    
                # update the progress bar
                if pb is not None:
                    # update progress bar
                    pb.update_progress(counter, len(wall_id_and_rooms))
        except Exception as e:
            action_return_value.update_sep(False, "Error while updating walls with room number: {}".format(e))
            return action_return_value
        
        return action_return_value
    

    # start a transaction and amend the wall parameter values
    transaction = Transaction(doc, "Adding room number to walls")
    return_value = in_transaction(transaction, action)

    return return_value


def get_wall_parameters(doc):
    """
    Get the wall parameters that can be set.
    
    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :return: List of wall parameters that can be set.
    :rtype: list
    """
    
    paras = []
    # get all wall types in the document
    col = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )

    for wall_instance in col:
        # get parameters
        parameters = wall_instance.GetOrderedParameters()

        for p in parameters:
            # check if parameter is writable
            if p.IsReadOnly == False:
                # add parameter name to list
                paras.append(p)

        break
    return paras

def get_wall_parameter_by_id (doc, parameter_id):

    # get all wall types in the document
    col = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
    )

    for wall_instance in col:
        # get parameters
        parameters = wall_instance.GetOrderedParameters()

        for p in parameters:
            # check if parameter is writable
            if p.Id.Value == parameter_id.Value:
                # add parameter name to list
                return p

        break
    return None
