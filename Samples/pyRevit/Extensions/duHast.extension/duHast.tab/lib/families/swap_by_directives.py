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

import csv


from duHast.Revit.Family.Data.family_swap_instances_of_types import swap_family_instances_of_types
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Utilities.Objects.result import Result

def swap_instances_by_directives_entry(doc, output, forms):
    """
    Swaps instnaces of types based on directives. This function is the entry point for the pyRevit command.

    :param doc: Revit Document
    :type doc: Document
    :param output: pyRevit output
    :type output: Output
    :param forms: pyRevit forms
    :type forms: Forms

    :return: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        # select swap directives folder
        swap_directive_path = None
        swap_directive_path = forms.pick_folder("Select the folder containing the swap directives")

        # check if anyhting was selected
        if swap_directive_path is None:
            return_value.update_sep(False, "No folder selected")
            print("No folder containing swap directive selected. Exiting!")
            return return_value
        

        # set up a progress tracker


        # swap away
        swap_result = swap_family_instances_of_types(doc, swap_directive_path)

        print(swap_result.message)
    
    except Exception as e:
        return_value.update_sep(
            False, "Failed to report families with exception: {}".format(e)
        )

    print(return_value.message)
    print("Finished")

    return return_value