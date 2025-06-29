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
from duHast.Revit.Family.LibraryCleanUp.Utility.defaults import SWAP_DIRECTIVE_FILE_NAME, MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX
from duHast.Utilities.files_get import get_files_single_directory

from duHast.Utilities.files_csv import read_csv_file

def read_maintain_types (directory_path):
    return_value = Result()

    try:

        # get type maintain file path
        files = get_files_single_directory(directory_path,MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX, "", ".csv")
           
        if len(files) == 0:
            return_value.update_sep(
                False,
                "No maintain directives found in directory: {}".format(directory_path),
            )
            return return_value
        
        # build the file path for the maintain directives
        file_path = files[0]  # assuming we take the first file found

        return_value.append_message("Reading maintain directives to file: {}".format(file_path))

        # write the maintain directives to the file
        csv_file_result = read_csv_file(file_path=file_path)

        return_value.update(csv_file_result)
        
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to read maintain directives with exception: {}".format(e),
        )
    
    return return_value