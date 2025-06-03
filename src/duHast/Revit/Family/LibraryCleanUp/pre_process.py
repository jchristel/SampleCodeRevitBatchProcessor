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
    xml_files =  get_all_xml_files_from_directories[libraryPath]

    if len(xml_files) == 0:
        return None
    
    family_data_result = get_family_type_data_from_library(xml_files)
    if (family_data_result.status is False):
        return None
    else:
        return family_data_result.result
    

def pre_process(libraryPath) :
    """
    Pre-process function to prepare for the family type data extraction.
    
    This function is a placeholder for any pre-processing steps that may be needed before extracting family type data from the library.
    
    :return: Result object indicating the success or failure of the pre-processing step.
    :rtype: Result
    """
    return_value = Result()
    try:
        
        # get type data from library as [:class:`.FamilyTypeDataStorageManager`]
        family_data = get_family_data_from_file(libraryPath)

        # check if anything came back
        if family_data is None:
            return_value.update_sep (False, "No family data found in the specified library path.")
            return return_value

        # built copy file directives / swap file directives
        directives_result = create_directives(family_data)

        if directives_result.status is False:
            return_value.update_sep(
                False,
                "{}".format(directives_result.message),
            )
            return return_value
        
        # execute copy directives

        # write swap directives to file

        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to get family data with exception: {}".format(e),
        )
    
    return return_value