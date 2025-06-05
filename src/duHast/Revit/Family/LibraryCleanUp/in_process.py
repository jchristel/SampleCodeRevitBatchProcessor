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

from duHast.Revit.Family.LibraryCleanUp.Utility.directives_read_from_file import read_maintain_types
from duHast.Revit.Family.LibraryCleanUp.Utility.directive_maintain_types_execute import delete_non_conforming_types

def in_process_family(doc, library_path):
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

        # read maintain types from file
        read_maintain_result = read_maintain_types(library_path)

       
        # check if the read operation was successful
        if not read_maintain_result.status:
            return_value.update_sep(False, "Failed to read maintain types: {}".format(read_maintain_result.message))
            print("Failed to read maintain types: {}".format(read_maintain_result.message))
            return return_value
        
        # get the maintain types from the result
        main_tain_types = read_maintain_result.result

        print(len(main_tain_types), "maintain types read from file.")

        # attempt to delete non-conforming types
        delete_non_conforming_types_result = delete_non_conforming_types(doc, main_tain_types)
        if not delete_non_conforming_types_result.status:
            return_value.update_sep(False, "Failed to delete non-conforming types: {}".format(delete_non_conforming_types_result.message))
            return return_value
        
        print(delete_non_conforming_types_result.message)


    except Exception as e:
        return_value.update_sep(False, "An error occurred: {}".format(str(e)))
        print("An error occurred: {}".format(str(e)))
        return return_value
    return return_value