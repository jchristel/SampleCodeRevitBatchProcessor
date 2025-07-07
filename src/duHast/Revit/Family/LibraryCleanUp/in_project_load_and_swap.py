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

from duHast.Revit.Family.Utility.family_swap_instances_by_type_utils import get_swap_directives
from duHast.Revit.Family.family_swap_instances_of_types import swap_family_instances_of_types
from duHast.Revit.Family.LibraryCleanUp.Utility.family_load import load_families_required_for_swapping
from duHast.Revit.Common.file_io import  sync_file

from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit


def load_families(doc, directive_directory,  library_path, output, forms):
    """
    Load families required for swapping based on directives.

    :param doc: The Revit document to work with.
    :param directive_directory: Directory containing swap directives.
    :param library_path: Path to the family library.
    :param output: Function to output messages.
    :param forms: Forms module for progress bar.

    :return: Result object containing status and messages.
    """

    return_value = Result()
    try:
        # load swap directives
        swap_directives_result = get_swap_directives(directory_path=directive_directory)

        if not swap_directives_result.status:
            return_value.update_sep(False, "Failed to read swap directives: {}".format(swap_directives_result.message))
            output("Failed to read swap directives: {}".format(swap_directives_result.message))
            return return_value
        
        swap_directives = swap_directives_result.result


        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Loading families: {value} of {max_value}", cancellable=True
            ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            # load families required for swapping
            load_result = load_families_required_for_swapping(
                doc,  
                swap_directives, 
                library_path, 
                progress_callback=progress_callback
            )

            if not load_result.status:
                return_value.update_sep(False, "Failed to load families required for swapping: {}".format(load_result.message))
                #output("Failed to load families required for swapping: {}".format(load_result.message))
                #return return_value
            else:
                return_value.append_message("Families successfully loaded for swapping: {}".format(len(load_result.result)))
            
            output("Families loaded for swapping: {} with status: {}".format(len(load_result.result), load_result.status))

            if( len(load_result.result) == 0):
                return_value.update_sep(True, "No families needing swapping in file")
                output("No families needing swapping in file")
           
    except Exception as e:
        return_value.update_sep(False, "An error occurred: {}".format(str(e)))
        output("An error occurred: {}".format(str(e)))

    return return_value


def swap_families(doc, directive_directory, output,forms):
    """
    Swap family instances in the Revit document based on directives.

    :param doc: The Revit document to work with.
    :param directive_directory: Directory containing swap directives.
    :param output: Function to output messages.
    :param forms: Forms module for progress bar.

    :return: Result object containing status and messages.
    """

    return_value = Result()

    try:
        # set up a pyrevit progress bar
        with forms.ProgressBar(
            title="Swapping family instances: {value} of {max_value}", cancellable=True
            ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)
        
            # swap away
            swap_result = swap_family_instances_of_types(doc, directive_directory, progress_callback=progress_callback)

            # print logs
            output("Swapped families with status: {}".format(swap_result.status))

            # check what came back
            if not swap_result.status:
                return_value.update_sep(False, "Failed to swap families: {}".format(swap_result.message))
                output("Failed to swap families: {}".format(swap_result.message))
                return return_value
            return_value.append_message(swap_result.message)
    except Exception as e:
        return_value.update_sep(False, "An error occurred: {}".format(str(e)))
        output("An error occurred: {}".format(str(e)))

    return return_value


def in_process_project(doc, library_path, directive_directory, output, forms):
    """
    Process the Revit document to load families and swap instances based on directives.

    :param doc: The Revit document to work with.
    :param library_path: Path to the family library.
    :param directive_directory: Directory containing swap directives.
    :param output: Function to output messages.
    :param forms: Forms module for progress bar.

    :return: Result object containing status and messages.
    """

    return_value = Result()

    # find families which need swapping load them and swap them out
    # save family

    try:

        # load families
        load_result = load_families(doc, directive_directory, library_path, output, forms)
        return_value.update(load_result)

        # get out if the user cancelled
        if load_result.message.endswith("User cancelled!"):
            return return_value

        # swap families
        swap_result = swap_families(doc, directive_directory, output,forms)
        return_value.update(swap_result)

        # get out if the user cancelled
        if swap_result.message.endswith("User cancelled!"):
            return return_value

        # sync
        #output("Syncing project file.")
        # save the project
        #save_result = sync_file(
        #     doc=doc,
        #     compact_central_file=True)
        
        # output("Save result: {}".format(save_result.status))

    except Exception as e:
        return_value.update_sep(False, "An error occurred: {}".format(str(e)))
        output("An error occurred: {}".format(str(e)))
        return return_value
    return return_value