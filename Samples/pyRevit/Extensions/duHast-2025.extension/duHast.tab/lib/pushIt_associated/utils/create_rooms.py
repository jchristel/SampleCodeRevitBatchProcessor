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
from duHast.Revit.Levels.levels import  get_nearest_lowest_level
from duHast.Revit.Rooms.rooms_create import create_room
from duHast.Revit.Common.parameter_set_utils import set_parameter_value_simple
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling

from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)

from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from Autodesk.Revit.DB import UV

def apply_transform_to_uv(uv_point, rotation_matrix, translation_vector):
    """
    Apply rotation and translation to a UV point.
    :param uv_point: The UV point to transform
    :type uv_point: Autodesk.Revit.DB.UV
    :param rotation_matrix: The rotation matrix to apply
    :type rotation_matrix: list
    :param translation_vector: The translation vector to apply
    :type translation_vector: list
    :return: The transformed UV point
    :rtype: Autodesk.Revit.DB.UV
    """
    
    # Apply rotation (no rotation in this case)
    rotated_u = uv_point.U + rotation_matrix[0]
    rotated_v = uv_point.V + rotation_matrix[1]
    
    # Apply translation (identity translation matrix)
    transformed_u = rotated_u + translation_vector[2][0]  # translation[2][0] should be 0
    transformed_v = rotated_v + translation_vector[2][1]  # translation[2][1] should be 0
    
    return UV(transformed_u, transformed_v)


def create_room_from_push_it_instance(doc, family_instance, levels_ascending, rotation, translation):
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

        # get the nearest level based on the Z value, converted to mm since that is what the function requires, of the family instance location point 
        placement_level = get_nearest_lowest_level(convert_imperial_feet_to_metric_mm(family_instance.location_point[2]), levels_ascending, [])[0]

        # set the placement point
        # use the location point if there is no centroid
        placement_point = UV(family_instance.location_point[0], family_instance.location_point[1]) if family_instance.centroid is None else UV(family_instance.centroid[0], family_instance.centroid[1])

        # apply the rotation and translation to the placement point ( works on shard coordinate projects only)
        transformed_placement_uv = apply_transform_to_uv(uv_point=placement_point, rotation_matrix=rotation, translation_vector=translation)
       
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
            location_point = transformed_placement_uv,
              modify_action = modify_action, 
              transaction_manager = transaction_manager
        )

        # update the return value
        return_value.update(room_result)

    except Exception as e:
        return_value.update_sep (False,"failed to create room: {}".format(e))
        print(e)
    return return_value
