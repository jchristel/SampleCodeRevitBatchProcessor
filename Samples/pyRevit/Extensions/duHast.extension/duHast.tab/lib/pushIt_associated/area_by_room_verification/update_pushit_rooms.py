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
from duHast.Revit.Levels.levels import   get_nearest_lowest_level, get_levels_list_ascending
from duHast.Revit.Rooms.rooms_create import create_room
from duHast.Revit.Common.parameter_set_utils import set_parameter_value_simple, set_parameter_value_by_name
from duHast.Revit.Common.parameter_get_utils import get_parameter_value_by_name, getter_double_as_double_converted_to_metric
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.delete import delete_by_element_ids

from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from Autodesk.Revit.DB import ElementId, UV, XYZ

from duHast.pyRevit.console_output import print_header, print_error

from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm, convert_imperial_square_feet_to_metric_square_metre




def apply_transform_to_uv(uv_point, rotation_matrix, translation_vector):
    # Convert UV point to XYZ point (assuming Z = 0)
    xyz_point = XYZ(uv_point.U, uv_point.V, 0)
    
    # Apply rotation (no rotation in this case)
    rotated_u = uv_point.U + rotation_matrix[0]
    rotated_v = uv_point.V + rotation_matrix[1]
    
    # Apply translation (identity translation matrix)
    transformed_u = rotated_u + translation_vector[2][0]  # translation[2][0] should be 0
    transformed_v = rotated_v + translation_vector[2][1]  # translation[2][1] should be 0
    
    return UV(transformed_u, transformed_v)


def create_room_from_push_it_instance_and_update(doc, family_instance, levels_ascending, rotation, translation):
    """
    Create a room in the Revit document.
    
    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to create the room from
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param levels_ascending: The list of levels in the Revit document
    :type levels_ascending: list

    :return: Result class instance.
    :rtype: Result
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
        placement_level = get_nearest_lowest_level(convert_imperial_feet_to_metric_mm(family_instance.location_point[2]), levels_ascending, [])[0]

        # set the placement point
        # use the location point if there is no centroid
        placement_point = UV(family_instance.location_point[0], family_instance.location_point[1]) if family_instance.centroid is None else UV(family_instance.centroid[0], family_instance.centroid[1])

        # apply the rotation and translation to the placement point ( works on shared coordinate projects only)
        #transformed_placement_uv = apply_transform_to_uv(uv_point=placement_point, rotation_matrix=rotation, translation_vector=translation)
       
        # define failure handling for the transaction ( roll back on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=False,
            print_warnings=False,
            roll_back_on_error=False,
            print_errors=False,
        )

        # define the transaction manager overriding any warnings Revit might pop up when placing the room
        def transaction_manager(transaction, action, *args, **kwargs):
            """
            Create a transaction manager for the Revit document.

            :return: Result class instance.
            :rtype: Result
            """

            # execute the transaction with failure handling
            result_transaction = in_transaction_with_failure_handling(
                transaction=transaction,
                action=action,
                failure_config=failure_handling_settings,
            )
            return  result_transaction

        # create the room
        room_result = create_room (
            doc, 
            level=placement_level, 
            location_point = placement_point,
              modify_action = modify_action, 
              transaction_manager = transaction_manager
        )

        # update the return value
        return_value.update(room_result)

    except Exception as e:
        return_value.update_sep (False,"failed to create room: {}".format(e))
        print(e)
    return return_value


def update_push_it_instance(doc, push_it_family_instance,room):
    return_value = Result()

    try:

        # get the created room instance area
        room_area = convert_imperial_square_feet_to_metric_square_metre(room.Area)

        # if room is not bound for whatever reason, return an error message
        if room_area == 0.0:
            return_value.update_sep(False, "Room area is zero for push it instance: {}. Cannot update push it instance area.".format(push_it_family_instance.get_ui_name()))
            print_error("Room area is zero for push it instance: {}. Cannot update push it instance area.".format(push_it_family_instance.get_ui_name()))
            return return_value
        
        room_perimeter = convert_imperial_feet_to_metric_mm(room.Perimeter)/1000 # convert perimeter to meters

        #get the wall thickness parameter value from the push it family instance
        half_wall_thickness_parameter_value = get_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)).Symbol , "HSL_WALL_THICKNESS", getter_double_as_double_converted_to_metric)

        # make sure there is a fallback if no parameter is set
        # make sure retrieved value is converted to meters...
        half_wall_thickness = half_wall_thickness_parameter_value/2/1000 if half_wall_thickness_parameter_value is not None else 0.06 # default to 60mm if not set

        print("Half wall thickness from element: {}".format(half_wall_thickness))

        calculated_area = (room_perimeter * half_wall_thickness) + room_area
        print("Calculated area: {}".format(calculated_area))

         # get the push it instance area stored in Area_Calc ( if that parameter does not exist, pop message and move on )
        push_it_area = get_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)) , "Area_Calc", getter_double_as_double_converted_to_metric)
        print("Push it area: {}".format(push_it_area))

        if push_it_area is None:
            return_value.append_message("Push it instance {} {} does not have Area_Calc parameter. Cannot update area.".format(push_it_family_instance.get_ui_name(), push_it_family_instance.revit_element_id_integer_value))
            print_error("Push it instance {} {} does not have Area_Calc parameter. Cannot update area.".format(push_it_family_instance.get_ui_name(), push_it_family_instance.revit_element_id_integer_value))
            return return_value
        
        # in general the calculated area should not be any larger than the push it room area (assume 5% tolerance for the push it room area)
        # it can be smaller due to columns or other things in the room that are not accounted for in the push it instance area
        # if smaller than check if 20% smaller...as a sanity check threshold

        if calculated_area < ( push_it_area * 0.8):
            return_value.update_sep(False, "Calculated area {} is less than 80% of push it area {}. Cannot update push it instance {} area.".format(calculated_area, push_it_area, push_it_family_instance.get_ui_name()))
            print_error("Calculated area {} is less than 80% of push it area {}. Cannot update push it instance {} area.".format(calculated_area, push_it_area, push_it_family_instance.get_ui_name()))
            set_area_override_result = set_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)), "HSL_AREA_BY_REVIT_ROOM", "0.0")
            print("Setting push it instance {} area override to 0.0".format(push_it_family_instance.get_ui_name()))
            print(set_area_override_result.message)
            return_value.update(set_area_override_result)
            return return_value
        if calculated_area > ( push_it_area * 1.05):
            return_value.append_message("Calculated area {} is greater then push it area {}. Will not update push it instance {} area.".format(calculated_area,  push_it_area, push_it_family_instance.get_ui_name()))
            print("Calculated area {} is greater then push it area {}. Will not update push it instance {} area.".format(calculated_area,  push_it_area, push_it_family_instance.get_ui_name()))
            set_area_override_result = set_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)), "HSL_AREA_BY_REVIT_ROOM", "0.0")
            print("Setting push it instance {} area override to 0.0".format(push_it_family_instance.get_ui_name()))
            print(set_area_override_result.message)
            return_value.update(set_area_override_result)
            return return_value

        # get the push it override area
        push_it_override_area = get_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)) , "HSL_AREA_BY_REVIT_ROOM", getter_double_as_double_converted_to_metric)
        print("Push it override area: {}".format(push_it_override_area))
        
        # compare to one decimal place, if identical do not take any action
        if round(calculated_area, 1) == round(push_it_area, 1):
            return_value.update_sep(True, "Push it instance area is already up to date.")
            print("Push it instance area is already up to date.")

            # check if a previous override needs re-setting
            if push_it_override_area is not None and push_it_override_area != 0.0:
                print("Push it override area needs updating from {} to 0.0".format(push_it_override_area))
                set_area_override_result = set_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)), "HSL_AREA_BY_REVIT_ROOM", "0.0")
                return_value.update(set_area_override_result)
            return return_value
        
        print("Updating push it instance area to: {} from {}".format(calculated_area,  push_it_area ))

        set_result = set_parameter_value_by_name(doc.GetElement(ElementId(push_it_family_instance.revit_element_id_integer_value)), "HSL_AREA_BY_REVIT_ROOM", str(calculated_area))
        return_value.update(set_result)

        print(set_result.message)

        
    except Exception as e:
        return_value.update_sep (False,"failed to update push it mock room: {}".format(e))
        print_error(e)
    return return_value




def update_push_it_instances_from_rooms(doc, family_instances, rotation, translation):
    """
    Create rooms in the Revit document from pushIt family instances.

    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instances: The family instances to create the rooms from
    :type family_instances: list
    :param rotation: The rotation to apply to the family instances based on the source model
    :type rotation: List float
    :param translation: The translation to apply to the family instances based on the source model
    :type translation: List float

    :return: Result class instance.
    :rtype: Result
    """

    return_value = Result()

    # list to store room ids to delete later
    room_ids_to_delete = []

    try:
        # get all levels in the file
        levels_ascending = get_levels_list_ascending(doc)  
        # create rooms in the Revit document
        for family_instance in family_instances:
            room_result =  create_room_from_push_it_instance_and_update(doc, family_instance, levels_ascending, rotation, translation)
            return_value.update(room_result)

            if len(room_result.result)>0:
                # add the room id to the list of room ids to delete later
                room_ids_to_delete.append(room_result.result[0].Id)
           
            # update the family instance with the room area if required
            update_result = update_push_it_instance(doc=doc, push_it_family_instance=family_instance,room=room_result.result[0])
            return_value.update(update_result)

        # delete the rooms after updating the push it instances
        delete_result = delete_by_element_ids(doc, room_ids_to_delete, "Push it rooms created by area verification", "rooms")

        return_value.update(delete_result)
              
    except Exception as e:
        return_value.update_sep (False,"failed to create rooms: {}".format(e))
        print_error(e)
       
    return return_value