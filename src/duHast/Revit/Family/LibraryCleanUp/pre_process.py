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


from duHast.Utilities.Objects.timer import Timer
from duHast.Utilities.Objects.result import Result
from duHast.UI.Objects.ProgressBase import ProgressBase
from duHast.Utilities.files_xml import get_all_xml_files_from_directories

from duHast.Revit.Family.family_types_get_data_from_xml import get_family_type_data_from_library

from duHast.Revit.Family.LibraryCleanUp.Utility.directives_create import create_directives
from duHast.Revit.Family.LibraryCleanUp.Utility.directives_write_to_file import write_directives_to_file
from duHast.Revit.Family.LibraryCleanUp.Utility.directives_execute import execute_copy_directives_for_library_families
from duHast.Revit.Family.LibraryCleanUp.Utility.write_task_lists import write_task_lists

def get_family_data_from_file(libraryPath):
    """
    Extracts family type data from XML files in the specified library path.

    :return:
        Result class instance.

        - result.status: XML conversion status will be returned in result.status. False if an exception occurred, otherwise True.
        - result.message will contain which xml file was read and converted into family type data.
        - result.result will be [:class:`FamilyTypeDataStorageManager`]

        On exception

        - Reload.status (bool) will be False
        - Reload.message will contain the exception message
        - Reload.result will be an empty list

    :rtype: :class:`.Result`
    """
    xml_files =  get_all_xml_files_from_directories([libraryPath])

    if len(xml_files) == 0:
        return None
    
    family_data_result = get_family_type_data_from_library(xml_files)
    if (family_data_result.status is False):
        return None
    else:
        return family_data_result.result
    

def pre_process(library_path, output_path, task_list_directory_path, code_descriptor_path):
    """
    Pre-process function to prepare for the family type data extraction.
    
    This function is a placeholder for any pre-processing steps that may be needed before extracting family type data from the library.
    
    :return: Result object indicating the success or failure of the pre-processing step.
    :rtype: Result
    """
    return_value = Result()
    try:
        
        # do some logging to user
        print("Processing family data from library path: {}".format(library_path))

        # get type data from library as [:class:`.FamilyTypeDataStorageManager`]
        family_data = get_family_data_from_file(library_path)
        print("Families {} loaded from library path.".format(len(family_data)))

        # check if anything came back
        if family_data is None:
            return_value.update_sep (False, "No family data found in the specified library path.")
            return return_value
        else:
            return_value.append_message(
                "Found {} families in library path.".format(len(family_data))
            )
            
        # do some logging to user
        print("Creating directives for {} families.".format(len(family_data)))

        directives_result = None
        try:
            # built copy file directives / swap file directives
            directives_result = create_directives(family_data, output_path,  code_descriptor_path)
        except Exception as e:
            return_value.update_sep(
                False,
                "Failed to create directives with exception: {}".format(e),
            )
            print("Failed to create directives with exception: {}".format(e))
            return return_value

        if directives_result is None:
            return return_value
        elif directives_result and directives_result.status is False:
            return_value.update_sep(
                False,
                "Failed to create directives",
            )
            print("Failed to create directives: \n{}".format(directives_result.message))
            return return_value
        else:
            return_value.append_message(
                "Created {} directives.".format(len(directives_result.result))
            )
        
        # get directives
        copy_directives = directives_result.result[0]
        type_maintain_list = directives_result.result[1]
        swap_directives = directives_result.result[2]

        # do some logging to user
        print("Created {} copy directives, {} type maintain directives and {} swap directives.".format(
            len(copy_directives), len(type_maintain_list), len(swap_directives)))

        # write swap directives and type maintain lists to file
        write_directives_result = write_directives_to_file (swap_directives, type_maintain_list,copy_directives, output_path)
        if write_directives_result.status is False:
            return_value.update_sep(
                False,
                "Failed to write directives to file",
            )
            return return_value
        else:
            return_value.append_message(
                "Wrote {} swap directives and {} type maintain directives to file.".format(
                    len(swap_directives), len(type_maintain_list))
            )
        
        print("Wrote swap directives and type maintain directives to file.")

        # execute copy directives
        copy_result = execute_copy_directives_for_library_families(copy_directives)
        if copy_result.status is False:
            print("Failed to execute copy directives: {}".format(copy_result.message))
            return_value.update_sep(
                False,
                "Failed to execute copy directives",
            )
            return return_value
        else:
            return_value.append_message(
                "Executed {} copy directives.".format(len(copy_directives))
            )

        print("Executed copy directives.")

        # write task list to file
        write_task_lists_result = write_task_lists(
            family_directory= library_path, 
            task_list_directory = task_list_directory_path, 
            number_of_task_lists=3)
        
        print(write_task_lists_result)

        return return_value
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get family data with exception: {}".format(e),
        )
        print("Failed to get family data with exception: {}".format(e))
    
    print("Finished!")
    return return_value