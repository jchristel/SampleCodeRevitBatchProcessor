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

# import workloader utils
from duHast.UI import workloader as wl
from duHast.Utilities.Objects.result import Result

# import file list methods
from duHast.UI import file_list as fl

from duHast.Utilities.files_io import (
    is_back_up_file,
)

def write_task_lists(family_directory, task_list_directory, number_of_task_lists):
    

    return_value = Result()
    try:

        get_data = fl.bucket_to_task_list_file_system
        
        # get revit files in input dir
        revit_files_unfiltered = fl.get_revit_files(
            family_directory, ".rfa"
        )
        
        revit_files = []
        for revit_file in revit_files_unfiltered:
            # remove any back up files from selection
            if is_back_up_file(os.path.basename(revit_file.name)) == False:
                if (
                    len(os.path.dirname(os.path.abspath(revit_file.name))) < 248
                    and len(revit_file.name) < 260
                ):
                    revit_files.append(revit_file)
                else:
                    return_value.append_message(
                        "Max path length violation: {}".format(revit_file.name)
                    )
                    return_value.append_message("File has been removed from selection!")


        # build bucket list
        buckets = wl.distribute_workload(
            number_of_task_lists, revit_files, fl.get_file_size
        )
        # write out file lists
        counter = 0
        for bucket in buckets:
            file_name = os.path.join(
                task_list_directory, "Tasklist_" + str(counter) + ".txt"
            )
            status_write = fl.write_revit_task_file(file_name, bucket, get_data)
            return_value.update(status_write)
            counter += 1
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to write task lists with exception: {}".format(e),
        )
    
    return return_value