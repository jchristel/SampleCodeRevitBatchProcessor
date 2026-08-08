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
from duHast.Revit.Common.parameter_set_utils import set_parameter_value_simple, set_builtin_parameter_without_transaction_wrapper_by_name
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Utilities.unit_conversion import convert_imperial_feet_to_metric_mm

from pushIt_associated.utils.settings import push_it_shared_parameter_to_build_in_parameter_mapper
from pushIt_associated.utils.parameter_guid import normalise_guid

from Autodesk.Revit.DB import UV, XYZ

# debug flag: when True a detailed parameter match report is printed for the first room created
DEBUG = True

# values reported by duHast get_parameter_value when a parameter on the push it family instance
# holds no value. Attempting to transfer those will either write nonsense or throw.
EMPTY_PARAMETER_VALUES = ["None", "no Value", ""]


def is_empty_parameter_value(value):
    """
    Checks whether a parameter value read of a push it family instance is empty.

    :param value: The parameter value as read by duHast get_parameter_value.
    :type value: str
    :return: True if there is nothing worth transferring, otherwise False.
    :rtype: bool
    """

    if value is None:
        return True
    if value in EMPTY_PARAMETER_VALUES:
        return True
    # get_parameter_value returns any read failure as a string prefixed with 'Exception: '
    if isinstance(value, str) and value.startswith("Exception:"):
        return True
    return False


def set_room_parameter_safely(para, value, parameter_name):
    """
    Sets a single room parameter value and contains any failure to this one parameter.

    duHast set_parameter_value_simple does not handle exceptions ( i.e. int( "None" ) on an
    integer parameter ), so without this wrapper the first bad value aborts the transfer of
    every remaining parameter on the room.

    :param para: The room parameter to be updated.
    :type para: Autodesk.Revit.DB.Parameter
    :param value: The new parameter value as a string.
    :type value: str
    :param parameter_name: The parameter name as per the push it family instance ( reporting only ).
    :type parameter_name: str
    :return: Result class instance. Status False if the value could not be applied.
    :rtype: :class:`.Result`
    """

    return_value = Result()

    # nothing to transfer
    if is_empty_parameter_value(value):
        return return_value

    # a read only parameter on the room ( i.e. a reporting parameter ) will throw on set
    if para.IsReadOnly:
        return_value.update_sep(False, "...failed [{}]: parameter is read only on the room.".format(parameter_name))
        return return_value

    try:
        set_result = set_parameter_value_simple(para, value)
        # only report failures. A success message per parameter per room would swamp the output window
        if set_result.status is False:
            return_value.update(set_result)
    except Exception as e:
        return_value.update_sep(False, "...failed [{}] to: {} with exception: {}".format(parameter_name, value, e))

    return return_value


def report_debug_parameter_match(family_instance, room_paras_by_guid):
    """
    Prints a report of how the push it family instance properties match up against the shared
    parameters available on the newly created room.

    This is the quickest way to tell a guid mismatch ( no properties / no matches ) apart from a
    value conversion failure ( matches, but sets fail ) and a missing parameter binding on the
    Rooms category ( room carries no shared parameters at all ).

    :param family_instance: The push it family instance the room is created from.
    :type family_instance: :class:`.PushItFamilyInstance`
    :param room_paras_by_guid: The rooms shared parameters by normalised guid.
    :type room_paras_by_guid: {str:Autodesk.Revit.DB.Parameter}
    """

    print("DEBUG: push it instance {} carries {} properties to transfer.".format(
        family_instance.revit_element_id_integer_value, len(family_instance.properties)))
    print("DEBUG: room carries {} shared parameters.".format(len(room_paras_by_guid)))

    property_guids = []
    for prop in family_instance.properties:
        prop_guid = normalise_guid(prop.parameter_guid)
        property_guids.append(prop_guid)
        para = room_paras_by_guid.get(prop_guid)
        if para is None:
            print("DEBUG: [no match ] {} guid: {} value: {}".format(
                prop.parameter_name, prop_guid, prop.parameter_value))
        else:
            print("DEBUG: [match   ] {} guid: {} value: {} -> room parameter: {} storage: {} read only: {}".format(
                prop.parameter_name, prop_guid, prop.parameter_value,
                para.Definition.Name, para.StorageType, para.IsReadOnly))

    # any shared parameter on the room which no push it property is pointing at
    for guid, para in room_paras_by_guid.items():
        if guid not in property_guids:
            print("DEBUG: [room only] {} guid: {}".format(para.Definition.Name, guid))


def apply_transform_to_uv(uv_point, rotation_matrix, translation_vector):
    
    
    # Convert UV point to XYZ point (assuming Z = 0)
    #xyz_point = XYZ(uv_point.U, uv_point.V, 0)
    
    # Note that the rotation and translation are applied in the order of rotation first, then translation.
    # Rotation as a 3 x 3 matrix and the translation as a 1 x 3 matrix of the shared coordinate system active in document.
    
    # check if rotation is None, if so do not apply any transformation
    if rotation_matrix is None:
        rotation_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity matrix for no rotation
            
    # Apply rotation (no rotation in this case)
    rotated_u = uv_point.U * rotation_matrix[0][0] + uv_point.V * rotation_matrix[0][1]
    rotated_v = uv_point.U * rotation_matrix[1][0] + uv_point.V * rotation_matrix[1][1]
    
    # check if translation is None, if so do not apply any transformation
    if translation_vector is None:
        translation_vector = [0, 0, 0]
        
    # Apply translation (identity translation matrix)
    transformed_u = rotated_u + translation_vector[0]  # translation[0] should be 0
    transformed_v = rotated_v + translation_vector[1]  # translation[1] should be 0
    
    return UV(transformed_u, transformed_v)


def create_room_from_push_it_instance(doc, family_instance, levels_ascending, rotation, translation, debug=False):
    """
    Create a room in the Revit document.

    :param doc: The Revit document
    :type doc: Autodesk.Revit.DB.Document
    :param family_instance: The family instance to create the room from
    :type family_instance: Autodesk.Revit.DB.FamilyInstance
    :param levels_ascending: The list of levels in the Revit document
    :type levels_ascending: list
    :param debug: If True a parameter match report is printed for this room.
    :type debug: bool

    :return: Result class instance.
    :rtype: Result
    """

    return_value = Result()

    try:

        # define the action to update room properties
        def modify_action(room):
            action_return_value = Result()
            try:

                # nothing was extracted of the push it family instance in the first place
                if len(family_instance.properties) == 0:
                    action_return_value.update_sep(False, "...push it instance {} carries no properties to transfer.".format(family_instance.revit_element_id_integer_value))
                    return action_return_value

                # build a look up of the rooms shared parameters by normalised guid
                # guids are normalised since a guid coming out of the data source may be upper case
                # and / or wrapped in braces where Revit always reports it in lower case without braces
                paras_room = room.GetOrderedParameters()
                room_paras_by_guid = {}
                for para in paras_room:
                    if para.IsShared:
                        room_paras_by_guid[normalise_guid(para.GUID)] = para

                if debug:
                    report_debug_parameter_match(family_instance, room_paras_by_guid)

                # match up shared parameters
                # note: each parameter is set in isolation so a single failure does not abort the remainder
                match_counter = 0
                unmatched_parameter_names = []
                for prop in family_instance.properties:
                    para = room_paras_by_guid.get(normalise_guid(prop.parameter_guid))
                    if para is None:
                        unmatched_parameter_names.append(prop.parameter_name)
                        continue
                    match_counter = match_counter + 1
                    action_return_value.update(set_room_parameter_safely(para, prop.parameter_value, prop.parameter_name))

                # flag the case where not a single property found a home on the room
                # ( guid mismatch, or the shared parameters are not bound to the Rooms category )
                if match_counter == 0:
                    action_return_value.update_sep(False, "...none of the {} push it properties matched a shared parameter on the room. Room carries {} shared parameters.".format(len(family_instance.properties), len(room_paras_by_guid)))
                elif len(unmatched_parameter_names) > 0:
                    # one summary line per room, the detail is in the debug report of the first room
                    action_return_value.append_message("...{} of {} properties had no matching shared parameter on the room: {}".format(len(unmatched_parameter_names), len(family_instance.properties), ", ".join(unmatched_parameter_names)))

                # match up shared parameters to build in parameters
                for key, value in push_it_shared_parameter_to_build_in_parameter_mapper.items():
                    for prop in family_instance.properties:
                        if prop.parameter_name == key:
                            # nothing to transfer
                            if is_empty_parameter_value(prop.parameter_value):
                                break
                            try:
                                set_result = set_builtin_parameter_without_transaction_wrapper_by_name( room,value,prop.parameter_value)
                                # only report failures to keep the output window readable
                                if set_result.status is False:
                                    action_return_value.update(set_result)
                            except Exception as e:
                                action_return_value.update_sep(False, "...failed to set built in parameter [{}] to: {} with exception: {}".format(key, prop.parameter_value, e))
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


def create_rooms_from_push_it_instances(doc, family_instances, rotation, translation, forms):
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

    try:
        # get all levels in the file
        levels_ascending = get_levels_list_ascending(doc)  

        # set up a progress bar since this can take a moment
        counter = 1
        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Creating rooms: {value} of {max_value}", cancellable=True
        ) as pb:
            # create rooms in the Revit document
            for family_instance in family_instances:
                # increase the progress bar
                pb.update_progress(counter, max_value=len(family_instances))

                # report the parameter match up in detail for the first room only, that is enough
                # to tell a guid mismatch apart from a value conversion or parameter binding issue
                room_result =  create_room_from_push_it_instance(
                    doc,
                    family_instance,
                    levels_ascending,
                    rotation,
                    translation,
                    debug=DEBUG and counter == 1,
                )
                return_value.update(room_result)

                counter += 1

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    print("User cancelled.")
                    break
                
    except Exception as e:
        return_value.update_sep (False,"failed to create rooms: {}".format(e))
        print(e)
       
    return return_value