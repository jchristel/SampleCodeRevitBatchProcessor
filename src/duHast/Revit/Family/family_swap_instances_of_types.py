"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to swap instances of a type of family placed to another type,.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This helper function expect a folder containing swap directive files. For format of those files refer to module RevitFamilyRenameFilesUtils

Note:

- The revit category is used to uniquly identify the family to swap. It is assumed that the target family type belongs to a family of the same category.

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


from duHast.Revit.Family.Utility import family_swap_instances_by_type_utils as rFamSwapUtils
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Revit.Family.family_utils import get_family_instances_by_symbol_type_id
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)

from Autodesk.Revit.DB import Element, Transaction


def get_target_type(doc, families, swap_directive):
    """
    Get the target type to swap to.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param families: dictionary of families where key is concatenated name + category and value is the family element.
    :type families: {str:Autodesk.Revit.DB.Family}
    :param swap_directive: The swap directive.
    :type swap_directive: class:`.FamilyDirectiveSwap`

    :return:
        Result class instance.

        - result.status. True if a single target family type was found, otherwise False.
        - result.message will contain each swap message
        - result.result list of target family types

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to find target type for: ' + swap_directive.target_family_type_name
        - result.result will be empty
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # get the family
    family_key = "{}{}{}".format(swap_directive.target_family_name,NESTING_SEPARATOR, swap_directive.category)

    # check if family is loaded
    if family_key not in families:
        return_value.update_sep(
            False, "Family not found: {}".format(family_key)
        )
        return return_value
    
    target_family = families[family_key]
            
    for fam_symbol_id in target_family.GetFamilySymbolIds():
        fam_symbol = doc.GetElement(fam_symbol_id)
        fam_symbol_name = Element.Name.GetValue(fam_symbol)
        if fam_symbol_name == swap_directive.target_family_type_name:
            return_value.append_message("...Found symbol: {}".format(fam_symbol_name))
            return_value.result.append(fam_symbol)
            return return_value
            
    return_value.update_sep(False, "...No target type found for: {}".format(swap_directive.target_family_type_name))
    return return_value


def get_super_component_id(doc, instance):

    """
    Get the super component id of a family instance.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param instance: The family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return:
        Result class instance.

        - result.status. True if a single super component was found, otherwise False.
        - result.message will contain each swap message
        - result.result list of super component ids (single entry)

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to find super component for: ' + instance.Id
        - result.result will be empty
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    super_component = instance.SuperComponent

    if super_component == None:
        return_value.update_sep(False, "No super component found for: {}".format(instance.Id))
        # return an invalid element id integer
        return_value.result.append(-1)
        return return_value
    
    # get the super component id
    super_component_id = instance.SuperComponent.Id
    if super_component_id != None and super_component_id.IntegerValue > 0:
        return_value.append_message("...Found super component id: {}".format(super_component_id))
        # get the family of the super component
        super_fam_Id_int = super_component.Symbol.Family.Id.IntegerValue
        return_value.result.append(super_fam_Id_int)
    else:
        return_value.append_message("Failed to find super component for: {}".format(instance.Id))
        return_value.result.append(-1)

    return return_value


def get_group_id(doc, instance):
    """
    Get the group id of a family instance.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param instance: The family instance.
    :type instance: Autodesk.Revit.DB.FamilyInstance

    :return:
        Result class instance.

        - result.status. True if at least one group was found, otherwise False.
        - result.message will contain each swap message
        - result.result list of group ids

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to find group for: ' + instance.Id
        - result.result will be empty
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # get the group instance id
    group_id = instance.GroupId

    if group_id == None or group_id.IntegerValue == -1:
        return_value.update_sep(False, "No group found for: {}".format(instance.Id))
        # return an invalid element id integer
        return_value.result.append(-1)
        return return_value
    
    # get the group
    group = doc.GetElement(group_id)
    # get the group type id
    group_type_id_int = group.GroupType.Id.IntegerValue
    if group_type_id_int != None and group_type_id_int > 0:
        return_value.append_message("...Found group type id: {}".format(group_type_id_int))

        # check if there is more than 1 instance of this group
        group_sets = group.GroupType.Groups
        if group_sets.Size > 1:
            return_value.append_message("...Group is placed more than once.")
            return_value.result.append(group_type_id_int)
        else:
            # revit does allow change of group if only one instance is placed
            return_value.update_sep(False,"...Group is placed only once.")
            return_value.result.append(-1)
    else:
        return_value.append_message("Failed to find group for: {}".format(instance.Id))
        return_value.result.append(-1)

    return return_value


def _get_fam_instances(doc, family, swap_directive):
    """
    Get instances of a family type to be swapped.

    Note:
    Will return 3 lists: 
    - instances which can be swapped out.
    - instances which are nested in other families.
    - instances which are in groups, where the group is placed more than once.


    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param family: The family to get instances of.
    :type family: Autodesk.Revit.DB.Family
    :param swap_directive: The swap directive.
    :type swap_directive: class:`.FamilyDirectiveSwap`

    :return:
        Result class instance.

        - result.status. True if a single family type was found, otherwise False.
        - result.message will contain each swap message
        - result.result list of instances

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'No instances found for type: ' + swap_directive.source_type_name
        - result.result will be empty
    
    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    
    # instances in model
    instances = []

    # a dictionary to hold count of instances by super component Family id integervalues
    super_components = {}

    # a dictionary to hold count of instances by group id integervalues
    groups = {}
    

    # get instances to be swapped
    for fam_symbol_id in family.GetFamilySymbolIds():
        fam_symbol = doc.GetElement(fam_symbol_id)
        fam_symbol_name = Element.Name.GetValue(fam_symbol)
        
        if fam_symbol_name ==  swap_directive.source_type_name :
            return_value.append_message("...Found symbol: {}".format(fam_symbol_name))
            # get all instances of this type
            instances_collector = get_family_instances_by_symbol_type_id(doc, fam_symbol.Id)
            for instance in instances_collector:
                
                # set default swap flag
                swap = True

                # check if instance is nested
                super_component_result = get_super_component_id(doc, instance)
                #return_value.update(super_component_result)

                # if this family is nested in another family do not swap
                if super_component_result.status:
                    # set swap flag to false
                    swap = False
                    super_component_id = super_component_result.result[0]
                    if super_component_id in super_components:
                        super_components[super_component_id] = super_components[super_component_id] + 1
                    else:
                        super_components[super_component_id] = 1
                
                # check if instance is in a group
                group_result = get_group_id(doc, instance)
                #return_value.update(group_result)

                # if this family is in a group do not swap
                if group_result.status:
                    # set swap flag to false
                    swap = False
                    group_type_id = group_result.result[0]
                    if group_type_id in groups:
                        groups[group_type_id] = groups[group_type_id] + 1
                    else:
                        groups[group_type_id] = 1
                
                # check if that instance can be swapped
                if swap:
                    instances.append(instance)

            return_value.append_message( "...Found {} instances of type: {}".format(len(instances), fam_symbol_name))
            break
    
    # update the return value as a tuple
    return_value.result.append((instances, super_components, groups))

    return return_value
    

def _swap_loaded_family_instances(doc, swap_directives, families, progress_callback=None):
    """
    Loops over nested families and if a match in rename directives is found will rename the family accordingly.

    :param doc: The current family document.
    :type doc: Autodesk.Revit.DB.Document
    :param rename_directives: List of rename directives.
    :type rename_directives: [rename_directive]
    :param family_ids: dictionary of families where key is concatenated name + category and value is the family element.
    :type family_ids: {str:Autodesk.Revit.DB.Family}

    :return:
        Result class instance.

        - result.status. True if all families where renamed successfully, otherwise False.
        - result.message will contain each rename messages in format 'Renamed family from :' +current Name + ' to ' + newName.
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to rename family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    return_value.status = False

    # progress call back
    callback_counter = 1

    for swap_directive in swap_directives:

        # update progress
        if progress_callback != None:
            progress_callback.update(callback_counter, len(swap_directives))

        # get the family
        family_key = "{}{}{}".format(swap_directive.name, NESTING_SEPARATOR, swap_directive.category)
        
        # check if family is loaded
        if family_key not in families:
            return_value.update_sep(
                False, "Family not found: {}".format(family_key)
            )
            callback_counter = callback_counter + 1
            continue
        
        # revit family
        family = families[family_key]

        # instances in model to be swapped
        instances_result = _get_fam_instances(doc, family, swap_directive)
        return_value.update(instances_result)
        
        # get instances to swap from returned tuple at index 0
        instances = instances_result.result[0][0]

        if len(instances) == 0:
            # nothing to swap found move on
            callback_counter = callback_counter + 1
            continue

        # get the target type
        target_result = get_target_type(doc, families, swap_directive)
        return_value.update(target_result)
        if not target_result.status:
            callback_counter = callback_counter + 1
            # no target type found
            continue

        # get the target type to swap to
        target_type = target_result.result[0]

        # set up an action swapping out instancea
        def action():
            action_return_value = res.Result()
            try:
                # swap out the types
                for instance in instances:
                    instance.Symbol = target_type
                    return_value.append_message("......Swapped out type for instance: {}".format(instance.Id))
                action_return_value.update_sep(True, "Swapped out types successfully")
            except Exception as e:
                action_return_value.update_sep(False, "Failed to swap out types with exception: {}".format(e))
            return action_return_value
    
        tranny = Transaction(doc, "swapping out type: {} with {}".format(swap_directive.source_type_name, swap_directive.target_family_type_name))

        swap_result = rTran.in_transaction(tranny=tranny, action=action)
        return_value.update(swap_result)

        # update progress
        callback_counter = callback_counter + 1

        # check for progress cancel
        if progress_callback != None:
            if progress_callback.is_cancelled():
                return_value.append_message("User cancelled!")
                break
    
    return return_value


def swap_family_instances_of_types(doc, directory_path, progress_callback=None):
    """
    Entry point for this module. Will read swap directives files in given directory and attempt to swp out instances of types accordingly.

    Note: for swap directive file structure refer to module family_swap_instances_by_type_utils

    :param directory_path: Fully qualified directory path to where swap directive files are located.
    :type directory_path: str
    :return:
        Result class instance.

        - result.status. True if a single families was swapped successfully, otherwise False.
        - result.message will contain each swap message
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to swap family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )
    
    # get directives from folder
    swap_directives_result = rFamSwapUtils.get_swap_directives(directory_path)
    # check if anything came back
    if swap_directives_result.status:
        # upfate return value
        return_value.update(swap_directives_result)
        swap_directives = swap_directives_result.result

        # get all family in file
        families = get_name_and_category_to_family_dict(doc)
        # check if any families are loaded
        if len(families) > 0:
            # swap instances as per directives
            swap_result= _swap_loaded_family_instances(
                doc=doc, swap_directives=swap_directives, families=families, progress_callback=progress_callback
            )
            # update return value
            return_value.update(swap_result)
        else:
            return_value.update_sep(True, "Mo loadable families in file.")
    else:
        return_value = swap_directives_result

    return return_value