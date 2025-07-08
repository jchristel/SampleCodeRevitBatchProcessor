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

import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import file_exist
from duHast.Revit.Family.family_utils import get_all_loadable_family_ids_through_types
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict, get_symbol_names_of_family
from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import NESTING_SEPARATOR
from duHast.Revit.Family import family_utils as rFamUtil
from duHast.UI.Objects.ProgressBase import ProgressBase



from Autodesk.Revit.DB import Element

def get_families_to_be_loaded_for_swapping(doc, swap_directives):
    """
    Identifies all families required to be loaded into a project for swapping based on the provided swap directives.

    Will check if target family already exists in the project and if so discard it from the list of families to be loaded.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param swap_directives: The swap directives containing family names and paths.
    :type swap_directives: list of dict
    :return: List of loaded family symbols.
    :rtype: list of Autodesk.Revit.DB.FamilySymbol
    """
    
    return_value = Result()

    try:
        # get all loaded families:
        family_ids = get_all_loadable_family_ids_through_types(doc)
        # get family name and category dictionary
        family_name_and_category_dict = get_name_and_category_to_family_dict(doc)

        if len(family_ids) > 0:
            return_value.append_message(
                "Found:  {} loadable families in file.".format(len(family_ids))
            )

            for fam_id in family_ids:
                fam = doc.GetElement(fam_id)
                fam_name = Element.Name.GetValue(fam)
                # get the types in the model
                source_family_symbol_names = get_symbol_names_of_family(fam)
                # return_value.append_message(
                #     "Family: {}, Category: {}".format(
                #         fam_name, fam.FamilyCategory.Name
                #     )
                # )
                for source_family_symbol_name in source_family_symbol_names:
                    #return_value.append_message("...Checking symbol: {}".format(source_family_symbol_name))
                    # symbol has match?
                    symbol_has_match=False
                    # loop over swap directives and try to find a match for the family name and category and type name
                    for swap_directive in swap_directives:
                        #return_value.append_message("......Checking swap directive: {}".format(swap_directive.name, swap_directive.category, swap_directive.source_type_name))
                        if swap_directive.name == fam_name and fam.FamilyCategory.Name == swap_directive.category and swap_directive.source_type_name == source_family_symbol_name:
                            #return_value.append_message(".........Found match")
                            # set flag that we found a match
                            symbol_has_match = True
                        
                            # check if target family already exists in the project
                            target_fam_key = "{}{}{}".format(
                                swap_directive.target_family_name, NESTING_SEPARATOR, swap_directive.category
                            )

                            # check if the target family is already loaded
                            if target_fam_key in family_name_and_category_dict:
                                # family already loaded, skip it only if target type is present, otherwise assume a reload is required
                                # get all type names for this family
                                #return_value.append_message(".........Family {} is loaded, checking symbol.".format(swap_directive.target_family_name))
                                
                                # get the target family symbol names
                                target_family = family_name_and_category_dict[target_fam_key]
                                # get the symbol names of the target family
                                target_family_symbol_names = get_symbol_names_of_family(target_family)
                                
                                # check if the target family symbol is present in the family
                                if  swap_directive.target_family_type_name in  target_family_symbol_names:
                                    return_value.append_message(".........Family {} and type {} already loaded, skipping.".format(swap_directive.target_family_name, swap_directive.target_family_type_name))
                                    # family symbol already loaded, skip it
                                    continue
                                else:
                                    pass
                                    #return_value.append_message(".........Type {} not loaded".format(swap_directive.target_family_type_name))
                            else:
                                pass
                                # family not loaded, we need to load it
                                #return_value.append_message(".........Family {} not loaded, marked for loading.".format(swap_directive.target_family_name))
                                
                            # return_value.append_message(
                            #     "...Family {} and type {} needs swapping to family {} and type {}.".format(swap_directive.name,  swap_directive.source_type_name, swap_directive.target_family_name, swap_directive.target_family_type_name)
                            # )

                            # only add if not there already
                            if(swap_directive.target_family_name not in return_value.result):
                                # add family name to result list
                                return_value.result.append(swap_directive.target_family_name)
                                return_value.append_message(
                                    "...Family {} added to load list.".format(swap_directive.target_family_name)
                                )
                            else:
                                return_value.append_message(
                                    "...Family {} already in load list, skipping.".format(swap_directive.target_family_name)
                                )
                            
                            break  # break out of the loop since we found a match
                    
                    if symbol_has_match == False:
                        pass
                        # return_value.append_message(
                        #     "{},{},{}, not found in swap directives.".format(fam_name, fam.FamilyCategory.Name, symbol_name)
                        # )
                        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to build load families list: {}".format(e),
        )
    
    return return_value


def load_families_required_for_swapping(doc, swap_directives, library_directory, progress_callback=None):
    """
    Loads families required for swapping into the document.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param swap_directives: The swap directives containing family names and paths.
    :type swap_directives: list of dict
    :param library_directory: The directory where family files are located.
    :type library_directory: str
    :param progress_callback: Optional progress callback for UI updates.
    :type progress_callback: ProgressBase or None

    :return: List of loaded family symbols.
    :rtype: list of Autodesk.Revit.DB.FamilySymbol
    """
    
    return_value = Result()

    try:

        # check callback class
        if progress_callback and isinstance(progress_callback, ProgressBase) == False:
            raise TypeError(
                "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                    type(progress_callback)
                )
            )
    
        # get families to be loaded for swapping
        family_load_required_result = get_families_to_be_loaded_for_swapping(doc, swap_directives)

        # DEBUG
        #print(family_load_required_result.message)

        # check if the family load required result is valid
        if family_load_required_result.status == False:
            return_value.update_sep(
                False,
                family_load_required_result.message,
            )
            return return_value
        
        # check if any families are required to be loaded
        if len(family_load_required_result.result) == 0:
            return_value.update_sep(
                True,
                "No families to load required for swapping.",
            )
            return return_value
        
        # progress call back
        callback_counter = 1

        # get the max progress value
        loop_max = len(family_load_required_result.result)

        # load the required families
        for family_name in family_load_required_result.result:

            # update progress
            if progress_callback != None:
                progress_callback.update(callback_counter, loop_max)
            
            # build the family load path
            family_load_path = os.path.join(library_directory, family_name + ".rfa")

            if (file_exist(family_load_path) == False):
                return_value.update_sep(
                    False,
                    "Family file {} does not exist in library directory.".format(family_load_path),
                )
                # skip and move to next family
                continue

            # load families
            result_load = rFamUtil.load_family(doc,family_load_path)
           
            if not result_load.status:
                print("Failed to load family {}: {}".format(family_name, result_load.message))
                return_value.update_sep(
                    False,
                    "Failed to load family {}: {}".format(family_name, result_load.message),
                )
                continue
            
            return_value.append_message("Successfully loaded family: {}".format(family_name))
            return_value.result.append(result_load.result[0])
        
            # update progress
            callback_counter = callback_counter + 1

            # check for progress cancel
            if progress_callback != None:
                if progress_callback.is_cancelled():
                    return_value.append_message("User cancelled!")
                    break
        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to load families for swapping: {}".format(e),
        )
    
    return return_value