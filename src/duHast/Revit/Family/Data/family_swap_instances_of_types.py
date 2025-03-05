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


from duHast.Revit.Family import family_swap_instances_by_type_utils as rFamSwapUtils
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.Revit.Family.family_utils import get_family_instances_by_symbol_type_id
from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res

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
    family_key = swap_directive.target_family_name + swap_directive.category

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
            
    return_value.update_sep("...No target type found for: {}".format(swap_directive.target_family_type_name))
    return return_value
    
   
def _get_fam_instances(doc, family, swap_directive):
    """
    Get instances of a family type to be swapped.

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

    # get instances to be swapped
    for fam_symbol_id in family.GetFamilySymbolIds():
        fam_symbol = doc.GetElement(fam_symbol_id)
        fam_symbol_name = Element.Name.GetValue(fam_symbol)
        if fam_symbol_name ==  swap_directive.source_type_name :
            return_value.append_message("...Found symbol: {}".format(fam_symbol_name))
            # get all instances of this type
            instances_collector = get_family_instances_by_symbol_type_id(doc, fam_symbol.Id)
            for instance in instances_collector:
                instances.append(instance)
            return_value.append_message( "...Found {} instances of type: {}".format(len(instances), fam_symbol_name))
            break
    
    # update the return value
    return_value.result = instances

    # check anything was found
    if len(instances) == 0:
        return_value.update_sep(False, "No instances found for type: {}".format(swap_directive.source_type_name))

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
    rename_match_counter = 0

    # progress call back
    callback_counter = 1

    for swap_directive in swap_directives:

        # update progress
        if progress_callback != None:
            progress_callback.update(callback_counter, len(swap_directives))

        # get the family
        family_key = swap_directive.name + swap_directive.category
        
        # check if family is loaded
        if family_key not in families:
            return_value.update_sep(
                False, "Family not found: {}".format(family_key)
            )
            rename_match_counter = rename_match_counter + 1
        
        # revit family
        family = families[family_key]

        # instances in model to be swapped
        instances_result = _get_fam_instances(doc, family, swap_directive)
        return_value.update(instances_result)
        if not instances_result.status:
            # nothing to swap found move on
            continue
        
        # get instances to swap
        instances = instances_result.result

        # get the target type
        target_result = get_target_type(doc, families, swap_directive)
        return_value.update(target_result)
        if not target_result.status:
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
        rename_match_counter = rename_match_counter + 1

        # check for progress cancel?
    

    return return_value


def swap_family_instances_of_types(doc, directory_path):
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
                doc=doc, swap_directives=swap_directives, families=families
            )
            # update return value
            return_value.update(swap_result)
        else:
            return_value.update_sep(True, "Mo loadable families in file.")
    else:
        return_value = swap_directives_result

    return return_value