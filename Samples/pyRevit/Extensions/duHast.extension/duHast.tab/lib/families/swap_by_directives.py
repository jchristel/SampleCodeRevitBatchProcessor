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


from duHast.Revit.Family.family_swap_instances_of_types import swap_family_instances_of_types
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.Utilities.Objects.result import Result

from Autodesk.Revit.DB import ElementId

from families.util.print_table import print_result_table

def get_table_data_from_result(doc, result_list):
    # the result lit is made up of tuples containing three entries

    # 1. the id's of family instances swapped out
    # 2. a dictioanry in format (Host Family Id:[list of instances not swapped because they are hosted in this family])
    # 3. a dictionary in format (Group Type Id:[list of instances not swapped because they are hosted in this group])

    host_fams = []
    host_groups = []
    for data in result_list:
        if (isinstance(data, tuple)):

            if len(data) != 3:
                continue

            for fam_id, instance_count in data[1].items():
                host_fams.append([doc.GetElement(ElementId(fam_id)).Name, instance_count])
            
            for group_id, instance_count in data[2].items():
                host_groups.append([doc.GetElement(ElementId(group_id)).Name, instance_count])
    
    return host_fams, host_groups


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
    
    table_data = None
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
        with forms.ProgressBar(
            title="Swapping: {value} of {max_value}",
            cancellable=True,
        ) as pb:

            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            # swap away
            swap_result = swap_family_instances_of_types(doc, swap_directive_path, progress_callback)

            # print logs
            print(swap_result.message)

            # process results to print tables
            table_data = get_table_data_from_result(doc, swap_result.result)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to swap families with exception: {}".format(e)
        )

    # print swap log
    #print(return_value.message)

    # print tables
    if table_data is not None and len(table_data[0]) >0:
        print_result_table(output, table_data[0], ["Host Family", "Instances not swapped"], "Host Families containing instances not swapped")
    if table_data is not None and len(table_data[1]) >0:
        print_result_table(output, table_data[1], ["Host Group", "Instances not swapped"], "Host Groups containing instances not swapped")

    print("Finished")

    return return_value