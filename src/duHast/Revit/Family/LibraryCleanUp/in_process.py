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
import os

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_io import get_file_name_without_ext

from duHast.Revit.Family.Utility.family_swap_instances_by_type_utils import get_swap_directives
from duHast.Revit.Family.family_parameter_utils import set_parameter_formula
from duHast.Revit.Family.family_swap_instances_of_types import swap_family_instances_of_types
from duHast.Revit.Family.LibraryCleanUp.Utility.directives_read_from_file import read_maintain_types
from duHast.Revit.Family.LibraryCleanUp.Utility.directive_maintain_types_execute import delete_non_conforming_types
from duHast.Revit.Family.LibraryCleanUp.Utility.family_load import load_families_required_for_swapping

from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit
from duHast.Revit.Common.file_io import save_as_family

from duHast.Revit.RBP.Objects.ProgressRBPConsole import ProgressRBPConsole
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Revit.SharedParameters.Objects.shared_parameter_data import ParameterModel

from duHast.Revit.SharedParameters.shared_parameter_add import (
    load_shared_parameter_file, 
    add_shared_parameter_to_family,
)
from duHast.Revit.SharedParameters.shared_parameters_tuple import PARAMETER_DATA

DEBUG = True

from Autodesk.Revit.DB import BuiltInParameterGroup


# shared parameters to add to family
parameters = [
    ParameterModel(
        name = "HSL_REVIEW_STATUS",
        group = "7_Health",
        is_type_parameter = True,
        para_type = "Text",
        visiblity = True,
        property_group = "PG_IDENTITY_DATA",
        shared_parameter_file_path = r"\\proj01\SYD\016713-61A-P\2_Work\2-1_Models\2_Revit\3_Resources\8_SharedParameters\HSL_SharedParameters_Albury.txt"
    ),
]

parameter_to_formula = {
    "HSL_REVIEW_STATUS":'"REVIEW_FINALISED"'
}

def assign_formula_to_shared_parameter(doc, output):
    # get the family manager
    manager = doc.FamilyManager

    # get all family parameters
    family_parameters = manager.GetParameters()

    # loop through all family parameters
    for family_parameter in family_parameters:
       fam_parameter_name = family_parameter.Definition.Name
       if fam_parameter_name in parameter_to_formula:
           set_result = set_parameter_formula(doc, manager, family_parameter, parameter_to_formula[fam_parameter_name])
           output(set_result.message)



def add_shared_parameters_to_family(doc, output):

    
    return_value = Result()
    for para_model in parameters:
       
        # load the definition file
        shared_parameter_file = load_shared_parameter_file(doc, para_model.shared_parameter_file_path)

        # skip to the next parameter if the shared parameter file is not found
        if shared_parameter_file is None:
            print("Shared parameter file not found: {}".format(para_model.shared_parameter_file_path))
            continue

        # get the family manager
        manager = doc.FamilyManager

        # Use reflection to get the enum value
        parameter_group = getattr(BuiltInParameterGroup, para_model.property_group, None)
        if parameter_group is None:
            print("Parameter group not found: {}".format(para_model.property_group))
            continue

        parameter_tuple = PARAMETER_DATA(para_model.name, not(para_model.is_type_parameter) ,parameter_group)

        # add the shared parameter to the family
        add_result = add_shared_parameter_to_family(para=parameter_tuple, mgr = manager, doc=doc, def_file=shared_parameter_file)

        if add_result.status:
            return_value.append_message("Parameter added successfully: {}".format(para_model.name))
        else:
            return_value.update_sep(False, "Parameter not added: {} \n...{}".format(para_model.name, add_result.message))
    

    output(return_value.message)


def in_process_family(doc, library_path, output):
    """
    
    """

    return_value = Result()

    # read maintain list and delete unused types in family
    # export family types (?)

    # find families which need swapping load them and swap them out
    # save family

    try:

        # make sure this really is a family document
        if not doc.IsFamilyDocument:
            return_value.update_sep(False, "The document is not a family document.")
            return return_value

        # add qa parameter
        add_shared_parameters_to_family(doc, output)
        # assign value to qa parameter
        assign_formula_to_shared_parameter(doc, output)

        # read maintain types from file
        read_maintain_result = read_maintain_types(library_path)

        # check if the read operation was successful
        if not read_maintain_result.status:
            return_value.update_sep(False, "Failed to read maintain types: {}".format(read_maintain_result.message))
            output("Failed to read maintain types: {}".format(read_maintain_result.message))
            return return_value
        
        # get the maintain types from the result
        main_tain_types = read_maintain_result.result

        output("{} maintain types read from file.".format(len(main_tain_types)))

        # attempt to delete non-conforming types
        delete_non_conforming_types_result = delete_non_conforming_types(doc, main_tain_types)
        if not delete_non_conforming_types_result.status:
            return_value.update_sep(False, "Failed to delete non-conforming types: {}".format(delete_non_conforming_types_result.message))
            return return_value
        
        output(delete_non_conforming_types_result.message)

        # load swap directives
        swap_directives_result = get_swap_directives(directory_path=library_path)

        if not swap_directives_result.status:
            return_value.update_sep(False, "Failed to read swap directives: {}".format(swap_directives_result.message))
            output("Failed to read swap directives: {}".format(swap_directives_result.message))
            return return_value
        
        swap_directives = swap_directives_result.result

        # load families required for swapping
        load_result = load_families_required_for_swapping(doc,  swap_directives, library_path)

        if not load_result.status:
            return_value.update_sep(False, "Failed to load families required for swapping: {}".format(load_result.message))
            output("Failed to load families required for swapping: {}".format(load_result.message))
            return return_value
        
        output("Families successfully loaded for swapping: {}".format(len(load_result.result)))

        # swap out families if necessary
        if( len(load_result.result) == 0):
            return_value.update_sep(True, "No families needing swapping in file")
            output("No families needing swapping in file")
            #return return_value
        else:
            # swap away
            swap_result = swap_family_instances_of_types(doc, library_path, progress_callback=None)

            # print logs
            output("Swapped families with status: {}".format(swap_result.status))

            # check what came back
            if not swap_result.status:
                return_value.update_sep(False, "Failed to swap families: {}".format(swap_result.message))
                output("Failed to swap families: {}".format(swap_result.message))
                return return_value
       
        
        # if we get here... do a purge unused and than save that family document
        purge_action_result = purge_unused_e_transmit(doc)

        if not purge_action_result.status:
            return_value.update_sep(False, "Failed to purge unused elements: {}".format(purge_action_result.message))
            output("Failed to purge unused elements: {}".format(purge_action_result.message))
            return return_value
        
        output("Purged unused elements successfully.")

        file_name_without_ext = get_file_name_without_ext(doc.PathName)
        
        revit_fam_file_path = os.path.join(library_path, file_name_without_ext + ".rfa")
        output("Saving family to: {}".format(revit_fam_file_path))

        # save the family document
        save_result = save_as_family(
            doc=doc,
            target_directory_path=library_path,
            current_full_file_name= doc.PathName,
            name_data=[[file_name_without_ext, file_name_without_ext]],
            file_extension= ".rfa",
            compact_file=True)
        
        output("Save result: {}".format(save_result.status))


    except Exception as e:
        return_value.update_sep(False, "An error occurred: {}".format(str(e)))
        output("An error occurred: {}".format(str(e)))
        return return_value
    return return_value