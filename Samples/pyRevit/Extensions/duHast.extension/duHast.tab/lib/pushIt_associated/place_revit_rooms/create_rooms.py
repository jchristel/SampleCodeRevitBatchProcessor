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


from duHast.Utilities.Objects.result import Result
from duHast.Revit.Levels.levels import  get_nearest_lowest_level, get_levels_list_ascending
from duHast.Revit.Rooms.rooms_create import create_room
from duHast.Revit.Common.parameter_set_utils import set_parameter_value_simple

from Autodesk.Revit.DB import SharedParameterElement, UV




def create_room_from_push_it_instance(doc, family_instance, levels_ascending):
    """
    Create a room in the Revit document.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to create the room from
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :return: The created room
    :rtype: Autodesk.Revit.DB.Room
    """
    return_value = Result()

    try:


        # define the action to update room properties
        def modify_action(room):
            action_return_value = Result()
            try:
                paras_room = room.GetOrderedParameters()
                for prop in family_instance.properties:
                    for para in paras_room:
                       if para.IsShared :
                            if para.GUID.ToString() == prop.parameter_guid:
                                set_result = set_parameter_value_simple(para, prop.parameter_value)
                                action_return_value.append_message("...updated room property: [{}] to {} with status: {}".format(prop.parameter_name, prop.parameter_value, set_result.status))
                                break

            except Exception as e:
                action_return_value.update_sep (False,"failed to modify room: {}".format(e))
                print(e)
            return action_return_value



        # get the nearest level based on the Z value of the family instance location point
        placement_level = get_nearest_lowest_level(family_instance.location_point[2], levels_ascending, [])[0]

        # set the placement point
        # use the location point if there is no centroid
        placement_point = UV(family_instance.location_point[0], family_instance.location_point[1]) if family_instance.centroid is None else UV(family_instance.centroid[0], family_instance.centroid[1])

        # create the room
        room_result = create_room (doc, level=placement_level, location_point = placement_point, modify_action = modify_action,)

        # update the return value
        return_value.update(room_result)

    except Exception as e:
        return_value.update_sep (False,"failed to create room: {}".format(e))
        print(e)
    return return_value


def create_rooms_from_push_it_instances(doc, family_instances):

    return_value = Result()

    try:
        # get all levels in the file
        levels_ascending = get_levels_list_ascending(doc)  
        # create rooms in the Revit document
        for family_instance in family_instances:
            room_result =  create_room_from_push_it_instance(doc, family_instance, levels_ascending)
            return_value.update(room_result)
              
    except Exception as e:
        return_value.update_sep (False,"failed to create rooms: {}".format(e))
        print(e)
       
    return return_value