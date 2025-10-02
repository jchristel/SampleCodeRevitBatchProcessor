"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to swap instances of a duplicated family to instances of the original family in a revit document.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function will identify duplicated families in the current Revit document based on their names. It will then swap all instances of the duplicated families with instances of the original family, ensuring that the document maintains consistency and avoids redundancy.

Potential issues: 

- the source family does not include the type of the duplicate family

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

from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from family_find_duplicate import *
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap
from duHast.Revit.Family.family_swap_instances_of_types import _swap_loaded_family_instances
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict

from Autodesk.Revit.DB import Element, ElementId, Transaction

DEBUG = False

def get_swap_directive(doc, source_type_id, target_type_id):
    # get the family types
    source_family_type = doc.GetElement(ElementId(source_type_id))
    target_family_type = doc.GetElement(ElementId(target_type_id))

    # get the source family
    source_family = source_family_type.Family
    source_family_category_name = source_family.FamilyCategory.Name
    
    directive = FamilyDirectiveSwap(
        name=Element.Name.GetValue(source_family),
        category=source_family_category_name,
        source_type_name=Element.Name.GetValue(source_family_type),
        target_family_name=Element.Name.GetValue(target_family_type.Family),
        target_family_type_name = Element.Name.GetValue(target_family_type)
    )

    if DEBUG:
        print ("Created directive: \n{}".format(directive.formatted_indented_str(1,"...")))
    
    return directive

def swap_family_instances_of_duplicates(doc, progress_callback=None):
    """
    Entry point for this module. 

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
    
    try:
        # attempt to find duplicate families
        duplicate_families = find_duplicate_families(doc)
        
        if DEBUG:
            print ("there...{}".format(len(duplicate_families)))
            for fam_id, families in duplicate_families.items():
                print ("fam_id: {}: {}".format(fam_id, families))

        # check if any duplicates found
        if len(duplicate_families) == 0:
            return_value.update_sep(True, "No duplicate families found.", [])
            return return_value
        
        
        # list to hold all swap directives
        swap_directives = []

        # find duplicate types in families
        for fam_id, families in duplicate_families.items():
            
            if DEBUG:
                print ("Processing family id: {}".format(fam_id))
            
            # get the target family
            target_family = doc.GetElement(fam_id)

            if DEBUG:
                print ("target_family: {}".format(target_family.Name))

            # get the duplicate families
            for duplicate_family in families:

                if DEBUG:
                    print ("duplicate_family: {}".format(duplicate_family.Name))
                
                # find matching types between families
                target_mapper = find_matching_types_between_families (duplicate_family, target_family)

                # if there are no matching types, skip to next duplicate family
                if len(target_mapper) == 0:
                    msg = "No matching types found between duplicate family: {} and target family: {}. Skipping.".format(duplicate_family.Name, target_family.Name)
                    if DEBUG:
                        print (msg)
                    return_value.append_message(msg)
                    continue
            
                # set up swap directives
                for dup_type_id, target_type_id in target_mapper.items():
                    
                    # build directive
                    directive = get_swap_directive(doc, dup_type_id, target_type_id)

                    # add to overall list of directives
                    swap_directives.append(directive)
                    if DEBUG:
                        print ("Added swap directive: \n{}".format(directive.formatted_indented_str(1,"...")))

        if DEBUG:
            print ("Total swap directives: {}".format(len(swap_directives)))
        
        # swap the instances
        if len(swap_directives)==0:
            return_value.update_sep(True, "No matching family types found between duplicate families and target families. No swaps performed.", [])
            return return_value
        
        # get all family in file
        families = get_name_and_category_to_family_dict(doc)

        # perform swap
        swap_result = _swap_loaded_family_instances(doc, swap_directives, families, progress_callback)

        print (swap_result)

    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to swap family instances due to exception: {}".format(e)
        )
    
    return return_value