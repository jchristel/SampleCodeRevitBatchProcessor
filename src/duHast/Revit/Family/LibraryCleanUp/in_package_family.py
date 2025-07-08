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
from duHast.Revit.Family.family_swap_instances_of_types import swap_family_instances_of_types
from duHast.Revit.Family.LibraryCleanUp.Utility.family_load import load_families_required_for_swapping

from duHast.Revit.Purge.purge_unused_e_transmit import purge_unused_e_transmit
from duHast.Revit.Common.file_io import save_as_family

from duHast.Revit.RBP.Objects.ProgressRBPConsole import ProgressRBPConsole
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit


DEBUG = True



def in_package_family(doc, library_path, output_directory, output):
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

        # load swap directives
        swap_directives_result = get_swap_directives(directory_path=library_path)

        if not swap_directives_result.status:
            return_value.update_sep(False, "Failed to read swap directives: {}".format(swap_directives_result.message))
            output("Failed to read swap directives: {}".format(swap_directives_result.message))
            return return_value
        
        output("Swap directives loaded successfully. Found {} directives.".format(len(swap_directives_result.result)))
        swap_directives = swap_directives_result.result

        #output("Loading families required for swapping...")
        #output("Swap directives: {}".format(swap_directives))
        #output("Library path: {}".format(library_path))
        # load families required for swapping
        load_result = load_families_required_for_swapping(doc, swap_directives, library_path)
        

        if not load_result.status:
            return_value.update_sep(False, "Failed to load families required for swapping: {}".format(load_result.message))
            output("Failed to load families required for swapping: {}".format(load_result.message))
            return return_value
        
        #output("Families successfully loaded for swapping: {}".format(len(load_result.result)))
        #output("Families loaded: {}".format([fam.Name for fam in load_result.result]))

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
        
        revit_fam_file_path = os.path.join( output_directory, file_name_without_ext + ".rfa")
        output("Saving family to: {}".format(revit_fam_file_path))

        # save the family document
        save_result = save_as_family(
            doc=doc,
            target_directory_path= output_directory,
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