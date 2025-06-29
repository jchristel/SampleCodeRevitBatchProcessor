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
from duHast.Revit.Family import family_utils as rFamUtil



from Autodesk.Revit.DB import Document, Element, FamilySymbol

def get_families_to_be_loaded_for_swapping(doc, swap_directives):
    """
    Loads families to be swapped into the document.

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

        if len(family_ids) > 0:
            return_value.append_message(
                "Found:  {} loadable families in file.".format(len(family_ids))
            )

            for fam_id in family_ids:
                fam = doc.GetElement(fam_id)
                fam_name = Element.Name.GetValue(fam)
                for swap_directive in swap_directives:
                    if swap_directive.name == fam_name and fam.FamilyCategory.Name == swap_directive.category:
                        return_value.append_message(
                            "Family {}  requires loading.".format(swap_directive.target_family_name)
                        )
                        # only add if not there already
                        if(swap_directive.target_family_name not in return_value.result):
                            # add family name to result list
                            return_value.result.append(swap_directive.target_family_name)
                        

        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to load families: {}".format(e),
        )
    
    return return_value


def load_families_required_for_swapping(doc, swap_directives, library_directory):
    """
    Loads families required for swapping into the document.

    :param doc: The Revit document.
    :type doc: Autodesk.Revit.DB.Document
    :param swap_directives: The swap directives containing family names and paths.
    :type swap_directives: list of dict
    :return: List of loaded family symbols.
    :rtype: list of Autodesk.Revit.DB.FamilySymbol
    """
    
    return_value = Result()

    try:
        # get families to be loaded for swapping
        family_load_required_result = get_families_to_be_loaded_for_swapping(doc, swap_directives)

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
        
        # load the required families
        for family_name in family_load_required_result.result:
            
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
        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to load families for swapping: {}".format(e),
        )
    
    return return_value